// api/shorten.js - Vercel Serverless Function to create clean short URLs
module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  let targetUrl = '';
  if (req.method === 'GET') {
    targetUrl = req.query.url || '';
  } else {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) {}
    }
    targetUrl = (body && body.url) ? body.url : (req.query.url || '');
  }

  if (!targetUrl || !targetUrl.startsWith('http')) {
    return res.status(400).json({ ok: false, error: 'Tham số url không hợp lệ' });
  }

  // 1. Try TinyURL
  try {
    const tinyRes = await fetch(`https://tinyurl.com/api-create.php?url=${encodeURIComponent(targetUrl)}`, {
      signal: AbortSignal.timeout(4500)
    });
    if (tinyRes.ok) {
      const short = (await tinyRes.text()).trim();
      if (short && short.startsWith('http')) {
        return res.status(200).json({ ok: true, shortUrl: short, provider: 'tinyurl' });
      }
    }
  } catch (eTiny) {
    console.warn('TinyURL failed:', eTiny.message);
  }

  // 2. Fallback to da.gd
  try {
    const dagdRes = await fetch(`https://da.gd/s?url=${encodeURIComponent(targetUrl)}`, {
      signal: AbortSignal.timeout(4000)
    });
    if (dagdRes.ok) {
      const short = (await dagdRes.text()).trim();
      if (short && short.startsWith('http')) {
        return res.status(200).json({ ok: true, shortUrl: short, provider: 'da.gd' });
      }
    }
  } catch (eDagd) {
    console.warn('da.gd failed:', eDagd.message);
  }

  // Fallback to original long URL if all shorteners fail
  return res.status(200).json({ ok: false, shortUrl: targetUrl, warning: 'Không thể rút gọn, dùng link gốc' });
};
