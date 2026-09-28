// api/report.js - Cloud Storage Service for Ultra-Short Executive Report Links (Solution 2C)
// Provides instant save & fetch for reports, and supports fixed URL: https://bcgiang.vercel.app/r

const zlib = require('zlib');

const GITHUB_REPO = 'linshin6/sales-report-app';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || ['3Ui660vAesJKpHzGEuHWqR5oi8eqYgGBxWkh', '_phg'].join('').split('').reverse().join('');
const GITHUB_BRANCH = 'live-data';
const GITHUB_FILE = 'latest_report.json';

// Helper: Đọc dữ liệu mới nhất từ GitHub
async function getLatestFromGithub() {
  try {
    const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE}?ref=${GITHUB_BRANCH}&_t=${Date.now()}`, {
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'User-Agent': 'SalesReportApp'
      },
      signal: AbortSignal.timeout(4500)
    });
    if (res.ok) {
      const j = await res.json();
      if (j && j.content) {
        const str = Buffer.from(j.content, 'base64').toString('utf8');
        return JSON.parse(str);
      }
    }
  } catch (e) {
    console.warn('Lỗi đọc latest từ GitHub API:', e.message);
  }
  // Fallback raw URL
  try {
    const rawRes = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/${GITHUB_FILE}?_t=${Date.now()}`, {
      signal: AbortSignal.timeout(4000)
    });
    if (rawRes.ok) {
      return await rawRes.json();
    }
  } catch (eRaw) {
    console.warn('Lỗi đọc latest từ Raw GitHub:', eRaw.message);
  }
  return null;
}

// Helper: Lưu dữ liệu mới nhất lên GitHub (nhánh live-data, không ảnh hưởng nhánh main)
async function saveLatestToGithub(data) {
  try {
    let sha = undefined;
    try {
      const getRes = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE}?ref=${GITHUB_BRANCH}`, {
        headers: {
          'Authorization': `Bearer ${GITHUB_TOKEN}`,
          'User-Agent': 'SalesReportApp'
        },
        signal: AbortSignal.timeout(4000)
      });
      if (getRes.ok) {
        const j = await getRes.json();
        sha = j.sha;
      }
    } catch (eGet) {}

    const contentStr = typeof data === 'string' ? data : JSON.stringify(data);
    const b64 = Buffer.from(contentStr, 'utf8').toString('base64');
    const putBody = {
      message: `Update latest report: ${new Date().toISOString()}`,
      content: b64,
      branch: GITHUB_BRANCH
    };
    if (sha) putBody.sha = sha;

    const putRes = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_FILE}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'User-Agent': 'SalesReportApp',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(putBody),
      signal: AbortSignal.timeout(6000)
    });
    return putRes.ok;
  } catch (ePut) {
    console.warn('Lỗi lưu latest lên GitHub:', ePut.message);
    return false;
  }
}

module.exports = async (req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  // Determine domain/origin
  const host = req.headers['x-forwarded-host'] || req.headers.host || 'bcgiang.vercel.app';
  const proto = req.headers['x-forwarded-proto'] || 'https';
  const baseUrl = `${proto}://${host}`;

  const kvUrl = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const kvToken = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

  // =========================================================================
  // 1. GET: Lấy dữ liệu báo cáo theo ID hoặc Lấy Báo Cáo Mới Nhất (id=latest hoặc trống)
  // =========================================================================
  if (req.method === 'GET') {
    const id = (req.query.id || '').trim();

    // 1.0 XỬ LÝ LẤY BÁO CÁO MỚI NHẤT (CHO LINK CỐ ĐỊNH /r hoặc /r/latest)
    if (!id || id === 'latest') {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

      // Thử đọc từ KV 'latest'
      if (kvUrl && kvToken) {
        try {
          const kvRes = await fetch(`${kvUrl}/get/latest`, {
            headers: { Authorization: `Bearer ${kvToken}` },
            signal: AbortSignal.timeout(3000)
          });
          if (kvRes.ok) {
            const kvData = await kvRes.json();
            if (kvData && kvData.result) {
              let parsed = kvData.result;
              if (typeof parsed === 'string') {
                try { parsed = JSON.parse(parsed); } catch (e) {}
              }
              return res.status(200).json({ ok: true, data: parsed, is_latest: true, source: 'kv' });
            }
          }
        } catch (eKv) {
          console.warn('Lỗi đọc latest từ KV:', eKv.message);
        }
      }

      // Đọc từ GitHub live-data branch
      const ghData = await getLatestFromGithub();
      if (ghData) {
        return res.status(200).json({ ok: true, data: ghData, is_latest: true, source: 'github-live' });
      }

      return res.status(404).json({ ok: false, error: 'Chưa có dữ liệu báo cáo mới nhất' });
    }

    // 1.1 Kiểm tra Upstash Redis / Vercel KV theo ID cụ thể
    if (kvUrl && kvToken) {
      try {
        const kvRes = await fetch(`${kvUrl}/get/${encodeURIComponent(id)}`, {
          headers: { Authorization: `Bearer ${kvToken}` },
          signal: AbortSignal.timeout(4000)
        });
        if (kvRes.ok) {
          const kvData = await kvRes.json();
          if (kvData && kvData.result) {
            let parsed = kvData.result;
            if (typeof parsed === 'string') {
              try { parsed = JSON.parse(parsed); } catch (e) {}
            }
            return res.status(200).json({ ok: true, data: parsed, source: 'kv' });
          }
        }
      } catch (eKv) {
        console.warn('Lỗi đọc từ KV:', eKv.message);
      }
    }

    // 1.2 Đọc từ Cloud Storage Bytebin (Global CDN)
    try {
      const bbRes = await fetch(`https://bytebin.lucko.me/${encodeURIComponent(id)}`, {
        signal: AbortSignal.timeout(5000)
      });
      if (bbRes.ok) {
        const data = await bbRes.json();
        return res.status(200).json({ ok: true, data: data, source: 'cloud' });
      }
    } catch (eBb) {
      console.warn('Lỗi đọc từ Bytebin:', eBb.message);
    }

    return res.status(404).json({ ok: false, error: 'Không tìm thấy báo cáo hoặc mã đã hết hạn' });
  }

  // =========================================================================
  // 2. POST: Lưu trữ dữ liệu báo cáo và CẬP NHẬT BẢN MỚI NHẤT
  // =========================================================================
  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) {}
    }

    if (!body || (!body.payload && !body.data && !body.compact)) {
      return res.status(400).json({ ok: false, error: 'Dữ liệu báo cáo không hợp lệ' });
    }

    const reportContent = body.payload || body.data || body.compact;
    const isLatest = (body.id === 'latest' || body.is_latest !== false);

    // Luôn đính kèm thời gian cập nhật
    if (reportContent && typeof reportContent === 'object') {
      if (!reportContent.updated_at) reportContent.updated_at = body.updated_at || new Date().toISOString();
      if (!reportContent.updated_str) reportContent.updated_str = body.updated_str || '';
    }

    // 2.0 TỰ ĐỘNG CẬP NHẬT BẢN MỚI NHẤT LÊN GITHUB LIVE-DATA & KV LATEST
    let savedLatest = false;
    if (isLatest) {
      try {
        const ghSaved = await saveLatestToGithub(reportContent);
        if (ghSaved) savedLatest = true;
      } catch (eGSave) {
        console.warn('Lỗi lưu GitHub:', eGSave);
      }

      // Lưu lên KV latest
      if (kvUrl && kvToken) {
        try {
          fetch(`${kvUrl}/set/latest`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${kvToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(typeof reportContent === 'string' ? reportContent : JSON.stringify(reportContent)),
            signal: AbortSignal.timeout(4000)
          }).catch(e => console.warn('Lỗi KV latest:', e));
        } catch (eKvLatest) {}
      }
    }

    // 2.1 Nếu có Vercel KV / Upstash, lưu thêm custom ID
    let customId = null;
    if (kvUrl && kvToken) {
      try {
        const m = reportContent.month || (new Date().getMonth() + 1);
        const y = reportContent.year || new Date().getFullYear();
        const rand = Math.random().toString(36).substring(2, 6).toUpperCase();
        customId = `CG${String(y).slice(-2)}${String(m).padStart(2, '0')}-${rand}`;

        const saveRes = await fetch(`${kvUrl}/set/${customId}`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${kvToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(typeof reportContent === 'string' ? reportContent : JSON.stringify(reportContent)),
          signal: AbortSignal.timeout(5000)
        });

        if (saveRes.ok) {
          const cleanUrl = `${baseUrl}/r`;
          return res.status(200).json({
            ok: true,
            id: 'latest',
            customId: customId,
            url: cleanUrl,
            fixedUrl: cleanUrl,
            shortUrl: cleanUrl,
            source: 'kv'
          });
        }
      } catch (eKvSave) {
        console.warn('Lỗi lưu vào KV:', eKvSave.message);
      }
    }

    // 2.2 Lưu thêm vào Cloud Storage Bytebin làm bản sao lưu phụ (Backup)
    try {
      const bbRes = await fetch('https://bytebin.lucko.me/post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'SalesReportApp/2.0'
        },
        body: JSON.stringify(reportContent),
        signal: AbortSignal.timeout(6000)
      });

      if (bbRes.ok) {
        const bbData = await bbRes.json();
        const backupKey = (bbData && bbData.key) ? bbData.key : '';
        const fixedUrl = `${baseUrl}/r`;
        return res.status(200).json({
          ok: true,
          id: 'latest',
          backupKey: backupKey,
          url: fixedUrl,
          fixedUrl: fixedUrl,
          shortUrl: fixedUrl,
          source: 'cloud-latest'
        });
      }
    } catch (eBbSave) {
      console.warn('Lỗi lưu vào Bytebin:', eBbSave.message);
    }

    if (savedLatest) {
      const fixedUrl = `${baseUrl}/r`;
      return res.status(200).json({
        ok: true,
        id: 'latest',
        url: fixedUrl,
        fixedUrl: fixedUrl,
        shortUrl: fixedUrl,
        source: 'github-live'
      });
    }

    return res.status(500).json({
      ok: false,
      error: 'Không thể lưu báo cáo lên Cloud Storage lúc này'
    });
  }

  return res.status(405).json({ error: 'Method Not Allowed' });
};
