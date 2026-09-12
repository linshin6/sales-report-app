const zlib = require('zlib');

/**
 * Nén dữ liệu báo cáo thành chuỗi base64url siêu ngắn (~1 KB)
 * Tận dụng master_data có sẵn trong ứng dụng để chỉ gửi phần số liệu phát sinh.
 */
function encodeReportForShare(payload) {
  if (!payload) return '';

  const activeStores = (payload.stores || payload.cvs_stores || [])
    .filter(s => (s.actual_sales || s.actual || 0) > 0)
    .map(s => [s.store_code || s.id, s.actual_sales || s.actual || 0]);

  const fmStores = (payload.fm_sku_matrix && payload.fm_sku_matrix.stores) ? payload.fm_sku_matrix.stores : [];
  const activeFm = fmStores.map(s => [s.actual || 0, s.orders || {}]);

  const compactObj = {
    tl: payload.team_lead || 'Trần Thị Cẩm Giang',
    m: payload.month || (new Date().getMonth() + 1),
    y: payload.year || new Date().getFullYear(),
    tg: payload.timegone || 0,
    bhx: payload.total_actual_bhx || 0,
    cvs: payload.total_cvs || 0,
    tot: payload.total_actual || 0,
    sbhx: payload.total_stores_bhx_team || 178,
    pbhx: payload.bhx_per_store || 0,
    emps: (payload.employees || []).map(e => [
      e.name,
      e.bhx_actual || 0,
      e.gs25_actual || 0,
      e.se_actual || 0,
      e.fm_actual || 0,
      e.ck_actual || 0,
      e.hd_actual || 0,
      e.wmp_actual || 0,
      e.total_actual || 0,
      e.bhx_stores || 0
    ]),
    hubs: (payload.bhx_hubs || []).map((h, idx) => [
      h.name || h.hub || ('Hub ' + (idx + 1)),
      h.amount !== undefined ? h.amount : (h.actual_sales || 0)
    ]),
    stores: activeStores,
    fm: activeFm
  };

  const jsonStr = JSON.stringify(compactObj);
  const compressed = zlib.deflateSync(Buffer.from(jsonStr, 'utf8'));
  return compressed.toString('base64url');
}

/**
 * Tự động tạo link xem trực tiếp trên Vercel theo domain hiện tại
 */
function generateReportUrl(req, payload) {
  const host = (req && req.headers) ? (req.headers['x-forwarded-host'] || req.headers.host) : 'sales-report-app.vercel.app';
  const proto = (req && req.headers) ? (req.headers['x-forwarded-proto'] || 'https') : 'https';
  const baseUrl = `${proto}://${host}`;
  const encoded = encodeReportForShare(payload);
  return `${baseUrl}/view.html#d=${encoded}`;
}

module.exports = {
  encodeReportForShare,
  generateReportUrl
};
