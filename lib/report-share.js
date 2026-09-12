const zlib = require('zlib');
const masterData = require('../master_data.js');

let allSkus = [];
if (masterData && masterData.fm_categories) {
  masterData.fm_categories.forEach(cat => allSkus.push(...cat.skus));
}

/**
 * Nén dữ liệu báo cáo thành chuỗi base64url siêu ngắn (~300 - 450 ký tự)
 * Tận dụng master_data có sẵn trong ứng dụng để chỉ lưu index và số liệu phát sinh.
 */
function encodeReportForShare(payload) {
  if (!payload) return '';

  // 1. Hubs (5 số)
  const h = (payload.bhx_hubs || []).map(hub => hub.amount !== undefined ? hub.amount : (hub.actual_sales || 0));

  // 2. Stores [ [storeIndex, sales], ... ]
  const s = [];
  (payload.stores || payload.cvs_stores || []).forEach((st, idx) => {
    const val = st.actual_sales || st.actual || 0;
    if (val > 0) {
      let storeIdx = idx;
      if (st.store_code && masterData && masterData.stores) {
        const found = masterData.stores.findIndex(ms => ms.store_code === st.store_code);
        if (found !== -1) storeIdx = found;
      }
      s.push([storeIdx, val]);
    }
  });

  // 3. FM matrix [ [fmStoreIndex, [ [skuIdx, amt], ... ]] ]
  const f = [];
  const fmStores = (payload.fm_sku_matrix && payload.fm_sku_matrix.stores) ? payload.fm_sku_matrix.stores : [];
  fmStores.forEach((st, sIdx) => {
    if (st.orders) {
      const ordersList = [];
      allSkus.forEach((sku, skuIdx) => {
        const amt = st.orders[sku.code] || 0;
        if (amt > 0) {
          ordersList.push([skuIdx, amt]);
        }
      });
      if (ordersList.length > 0) {
        f.push([sIdx, ordersList]);
      }
    }
  });

  const compactObj = {
    v: 2,
    m: payload.month || (new Date().getMonth() + 1),
    y: payload.year || new Date().getFullYear(),
    tg: payload.timegone || 0,
    h, s, f
  };

  const jsonStr = JSON.stringify(compactObj);
  const compressed = zlib.deflateSync(Buffer.from(jsonStr, 'utf8'));
  return compressed.toString('base64url');
}

/**
 * Tự động tạo link rút gọn /r đẹp mắt trên Vercel theo domain hiện tại
 */
function generateReportUrl(req, payload) {
  const host = (req && req.headers) ? (req.headers['x-forwarded-host'] || req.headers.host) : 'sales-report-app.vercel.app';
  const proto = (req && req.headers) ? (req.headers['x-forwarded-proto'] || 'https') : 'https';
  const baseUrl = `${proto}://${host}`;
  const encoded = encodeReportForShare(payload);
  return `${baseUrl}/r#d=${encoded}`;
}

async function shortenReportUrl(longUrl) {
  if (!longUrl) return '';
  try {
    const tinyRes = await fetch(`https://tinyurl.com/api-create.php?url=${encodeURIComponent(longUrl)}`, {
      signal: AbortSignal.timeout(4500)
    });
    if (tinyRes.ok) {
      const short = (await tinyRes.text()).trim();
      if (short && short.startsWith('http')) return short;
    }
  } catch (e) {}

  try {
    const dagdRes = await fetch(`https://da.gd/s?url=${encodeURIComponent(longUrl)}`, {
      signal: AbortSignal.timeout(4000)
    });
    if (dagdRes.ok) {
      const short = (await dagdRes.text()).trim();
      if (short && short.startsWith('http')) return short;
    }
  } catch (e) {}

  return longUrl;
}

module.exports = {
  encodeReportForShare,
  generateReportUrl,
  shortenReportUrl
};

