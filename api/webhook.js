const XLSX = require('xlsx');
global.XLSX = XLSX;

const masterData = require('../master_data.js');
const { detectFileType, processTwoWorkbooks } = require('../ReportEngine.gs');
const { buildExcelWorkbook } = require('../lib/excel-builder.js');

// Bộ nhớ đệm phiên làm việc trên Vercel Serverless
global.__TG_SESSIONS = global.__TG_SESSIONS || new Map();
const sessions = global.__TG_SESSIONS;

// Xóa session quá hạn (> 2 giờ)
function cleanExpiredSessions() {
  const now = Date.now();
  for (const [chatId, sess] of sessions.entries()) {
    if (now - sess.timestamp > 2 * 3600 * 1000) {
      sessions.delete(chatId);
    }
  }
}

// Định dạng tiền VNĐ
function formatMoney(num) {
  return (num || 0).toLocaleString('vi-VN');
}

// =========================================================================
// CÁC HÀM GỌI TELEGRAM BOT API NATIVE
// =========================================================================

async function sendMessage(token, chatId, text) {
  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: String(chatId),
      text: text,
      parse_mode: 'HTML'
    })
  });
  return res.json();
}

async function sendChatAction(token, chatId, action) {
  try {
    await fetch(`https://api.telegram.org/bot${token}/sendChatAction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: String(chatId),
        action: action
      })
    });
  } catch (e) {}
}

async function sendPhoto(token, chatId, imageBuffer, fileName, caption) {
  const formData = new FormData();
  formData.append('chat_id', String(chatId));
  formData.append('photo', new Blob([imageBuffer], { type: 'image/png' }), fileName || 'Bieu_Do_Tien_Do.png');
  if (caption) {
    formData.append('caption', caption);
    formData.append('parse_mode', 'HTML');
  }

  const res = await fetch(`https://api.telegram.org/bot${token}/sendPhoto`, {
    method: 'POST',
    body: formData
  });
  return res.json();
}

async function sendDocument(token, chatId, docBuffer, fileName, caption) {
  const formData = new FormData();
  formData.append('chat_id', String(chatId));
  formData.append('document', new Blob([docBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), fileName || 'Team_CamGiang_Report.xlsx');
  if (caption) {
    formData.append('caption', caption);
    formData.append('parse_mode', 'HTML');
  }

  const res = await fetch(`https://api.telegram.org/bot${token}/sendDocument`, {
    method: 'POST',
    body: formData
  });
  return res.json();
}

async function downloadTelegramFileBuffer(token, fileId) {
  const getFileRes = await fetch(`https://api.telegram.org/bot${token}/getFile?file_id=${fileId}`);
  const fileData = await getFileRes.json();
  if (!fileData.ok || !fileData.result || !fileData.result.file_path) {
    throw new Error('Không thể lấy đường dẫn file từ Telegram: ' + (fileData.description || ''));
  }

  const downloadUrl = `https://api.telegram.org/file/bot${token}/${fileData.result.file_path}`;
  const fileRes = await fetch(downloadUrl);
  const arrayBuffer = await fileRes.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

// Tạo ảnh biểu đồ thanh ngang đẹp từ QuickChart API
async function generateRankingChartBuffer(payload) {
  try {
    const emps = (payload.employees || []).slice().sort((a, b) => (b.percent || 0) - (a.percent || 0));
    const labels = emps.map(e => e.name);
    const pcts = emps.map(e => e.percent || 0);
    const timegone = payload.timegone || 0;

    const chartConfig = {
      type: 'horizontalBar',
      data: {
        labels: labels,
        datasets: [{
          label: '% Đạt Doanh Số',
          data: pcts,
          backgroundColor: pcts.map(p => p >= timegone ? 'rgba(16, 185, 129, 0.9)' : (p >= timegone * 0.75 ? 'rgba(245, 158, 11, 0.9)' : 'rgba(239, 68, 68, 0.9)')),
          borderColor: pcts.map(p => p >= timegone ? '#059669' : (p >= timegone * 0.75 ? '#D97706' : '#DC2626')),
          borderWidth: 1.5
        }]
      },
      options: {
        title: {
          display: true,
          text: `TIẾN ĐỘ DOANH SỐ TEAM ${payload.team_lead.toUpperCase()} (Tháng ${payload.month}/${payload.year} - Timegone: ${timegone}%)`,
          fontSize: 16,
          fontColor: '#1E293B',
          fontStyle: 'bold'
        },
        legend: { display: false },
        scales: {
          xAxes: [{
            ticks: {
              beginAtZero: true,
              callback: (val) => val + '%'
            },
            gridLines: { color: 'rgba(226, 232, 240, 0.8)' }
          }],
          yAxes: [{
            ticks: { fontStyle: 'bold', fontColor: '#334155' },
            gridLines: { display: false }
          }]
        }
      }
    };

    const chartUrl = `https://quickchart.io/chart?w=850&h=480&bkg=white&devicePixelRatio=2&c=${encodeURIComponent(JSON.stringify(chartConfig))}`;
    const chartRes = await fetch(chartUrl);
    if (chartRes.ok) {
      const arr = await chartRes.arrayBuffer();
      return Buffer.from(arr);
    }
  } catch (e) {
    console.error('Lỗi tạo ảnh biểu đồ:', e);
  }
  return null;
}

// =========================================================================
// ĐIỂM ĐÓN WEBHOOK CHÍNH TRÊN VERCEL
// =========================================================================

module.exports = async function handler(req, res) {
  // 1. Healthcheck khi mở bằng trình duyệt GET
  if (req.method === 'GET') {
    return res.status(200).json({
      status: 'ok',
      message: '🚀 Telegram Bot Webhook is ACTIVE on Vercel!',
      time: new Date().toISOString()
    });
  }

  // 2. Chỉ nhận POST từ Telegram
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const token = req.query.token || process.env.TELEGRAM_BOT_TOKEN;
  if (!token) {
    console.error('❌ Thiếu TELEGRAM_BOT_TOKEN trong URL hoặc Environment Variables');
    return res.status(400).json({ error: 'Missing Telegram Bot Token' });
  }

  cleanExpiredSessions();

  try {
    const update = req.body;
    if (!update || !update.message) {
      return res.status(200).json({ ok: true, note: 'No message in update' });
    }

    const msg = update.message;
    const chatId = msg.chat.id;
    const text = (msg.text || '').trim();

    // -------------------------------------------------------------
    // 3. XỬ LÝ LỆNH DẠNG TEXT
    // -------------------------------------------------------------
    if (text.startsWith('/start') || text.startsWith('/help')) {
      const welcome = 
`📊 <b>HỆ THỐNG BÁO CÁO DOANH SỐ TEAM (CVS & BHX)</b>
<i>Chạy trực tiếp trên nền tảng Vercel Cloud 🚀</i>

🤖 <b>Chào bạn! Tôi là Bot Báo Cáo Doanh Số tự động.</b>

👉 <b>CÁCH SỬ DỤNG:</b>
Gửi cho tôi <b>2 file Excel (.xlsb hoặc .xlsx)</b>:
1️⃣ <b>File Siêu Thị:</b> Chứa dữ liệu BHX 5 Hubs + WinMart+
2️⃣ <b>File CVS & NPP:</b> Chứa dữ liệu GS25, 7-Eleven, FamilyMart, Circle K, Hoàng Đức

⚡ <b>Bot sẽ tự động trả về:</b>
• 📊 <b>Ảnh biểu đồ & Xếp hạng tiến độ</b> trực quan
• 📁 <b>File Excel chuẩn 5 sheets</b> <code>Team_CamGiang_Report.xlsx</code>
• 💬 <b>Bản tin tóm tắt số liệu</b> chi tiết toàn team!

📌 <b>Lệnh nhanh:</b>
/status - Kiểm tra trạng thái 2 file đã gửi
/reset - Xóa phiên để gửi lại từ đầu`;

      await sendMessage(token, chatId, welcome);
      return res.status(200).json({ ok: true });
    }

    if (text.startsWith('/reset')) {
      sessions.delete(chatId);
      await sendMessage(token, chatId, '🔄 <b>Đã làm mới phiên!</b> Bạn hãy gửi 2 file Excel doanh số (.xlsb hoặc .xlsx) để bắt đầu.');
      return res.status(200).json({ ok: true });
    }

    if (text.startsWith('/status')) {
      const sess = sessions.get(chatId);
      if (!sess) {
        await sendMessage(token, chatId, 'ℹ️ Hiện tại bạn chưa gửi file nào. Hãy gửi File Siêu Thị (BHX) và File CVS & NPP để bắt đầu.');
      } else {
        let stText = '📋 <b>TRẠNG THÁI HIỆN TẠI:</b>\n';
        stText += sess.fileST ? `• 🏬 File Siêu Thị: ✅ <i>${sess.fileST.fileName}</i>\n` : '• 🏬 File Siêu Thị: ❌ Chưa nhận\n';
        stText += sess.fileCVS ? `• 🏪 File CVS & NPP: ✅ <i>${sess.fileCVS.fileName}</i>\n` : '• 🏪 File CVS & NPP: ❌ Chưa nhận\n';
        if (!sess.fileST || !sess.fileCVS) {
          stText += '\n👉 Vui lòng gửi tiếp file còn thiếu!';
        }
        await sendMessage(token, chatId, stText);
      }
      return res.status(200).json({ ok: true });
    }

    // -------------------------------------------------------------
    // 4. XỬ LÝ KHI NGƯỜI DÙNG GỬI FILE (DOCUMENT)
    // -------------------------------------------------------------
    if (msg.document) {
      const doc = msg.document;
      const fileName = doc.file_name || 'unknown.xlsx';
      const fileId = doc.file_id;
      const fileSizeMB = (doc.file_size || 0) / (1024 * 1024);

      if (fileSizeMB > 25) {
        await sendMessage(token, chatId, `⚠️ File <b>${fileName}</b> vượt quá giới hạn 25MB của Telegram.`);
        return res.status(200).json({ ok: true });
      }

      await sendChatAction(token, chatId, 'typing');

      // Tải buffer và parse workbook
      const buffer = await downloadTelegramFileBuffer(token, fileId);
      const wb = XLSX.read(buffer, {
        type: 'buffer',
        cellDates: false,
        cellStyles: false,
        cellHTML: false,
        cellFormula: false
      });

      const detectedType = detectFileType(fileName, wb);
      if (detectedType === 'UNKNOWN') {
        await sendMessage(token, chatId, `❓ <b>Chưa nhận diện được file:</b> ${fileName}\nVui lòng gửi File Siêu Thị (BHX) hoặc File CVS & NPP.`);
        return res.status(200).json({ ok: true });
      }

      // Quản lý phiên làm việc
      let sess = sessions.get(chatId) || { timestamp: Date.now() };
      sess.timestamp = Date.now();

      if (detectedType === 'ST') {
        sess.fileST = { fileId, fileName, wb };
      } else if (detectedType === 'CVS') {
        sess.fileCVS = { fileId, fileName, wb };
      }
      sessions.set(chatId, sess);

      // Kiểm tra xem đã đủ 2 file chưa
      if (sess.fileST && sess.fileCVS) {
        await sendMessage(token, chatId, 
`✨ <b>ĐÃ NHẬN ĐỦ CẢ 2 FILE!</b>
1️⃣ 🏬 <b>File Siêu Thị:</b> ${sess.fileST.fileName}
2️⃣ 🏪 <b>File CVS & NPP:</b> ${sess.fileCVS.fileName}

⏳ <i>Hệ thống Vercel đang bóc tách số liệu, vẽ biểu đồ và tạo file Excel... Vui lòng đợi trong giây lát!</i>`);

        await sendChatAction(token, chatId, 'upload_document');

        // Bóc tách số liệu qua Report Engine
        const payload = processTwoWorkbooks(sess.fileST.wb, sess.fileCVS.wb, masterData);

        // 1. Tạo ảnh biểu đồ & Gửi trước
        try {
          const chartBuf = await generateRankingChartBuffer(payload);
          if (chartBuf) {
            const chartCaption = `📊 <b>ẢNH TIẾN ĐỘ & XẾP HẠNG DOANH SỐ TEAM ${payload.team_lead.toUpperCase()}</b>\nTháng ${payload.month}/${payload.year} | ⏳ % Timegone: ${payload.timegone}% | 🎯 % Đạt Team: ${payload.percent_achieved}%`;
            await sendPhoto(token, chatId, chartBuf, `Tien_Do_Team_${payload.month}_${payload.year}.png`, chartCaption);
          }
        } catch (eImg) {
          console.error('Lỗi gửi ảnh biểu đồ:', eImg);
        }

        // 2. Tạo file Excel chuẩn 5 sheets qua ExcelJS & Gửi đính kèm
        try {
          const excelWb = await buildExcelWorkbook(payload);
          const excelBuffer = await excelWb.xlsx.writeBuffer();
          const docCaption = 
`📊 <b>BÁO CÁO DOANH SỐ TEAM ${payload.team_lead.toUpperCase()}</b>
Tháng ${payload.month}/${payload.year} (% Timegone: ${payload.timegone}%)
• Target: ${formatMoney(payload.total_target)} ₫
• Tổng TH: ${formatMoney(payload.total_actual)} ₫ (${payload.percent_achieved}%)
• Tình trạng: ${payload.percent_achieved >= payload.timegone ? '🟢 VƯỢT' : (payload.percent_achieved >= payload.timegone * 0.75 ? '🟠 CẬN' : '🔴 CHẬM')} TIẾN ĐỘ`;

          const excelFileName = `Team_${payload.team_lead.replace(/\\s+/g, '_')}_Report_Thang_${payload.month}_${payload.year}.xlsx`;
          await sendDocument(token, chatId, excelBuffer, excelFileName, docCaption);
        } catch (eDoc) {
          console.error('Lỗi tạo file Excel:', eDoc);
        }

        // 3. Gửi tin nhắn tóm tắt số liệu chi tiết
        const topEmployees = (payload.employees || []).slice().sort((a, b) => (b.percent || 0) - (a.percent || 0));
        let summaryMsg = 
`🎯 <b>TỔNG HỢP DOANH SỐ CHI TIẾT:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Target Team:</b> <code>${formatMoney(payload.total_target)} ₫</code>
• <b>Thực Hiện BHX:</b> <code>${formatMoney(payload.total_actual_bhx)} ₫</code> (TB ${formatMoney(payload.bhx_per_store)} ₫/CH)
• <b>Thực Hiện CVS:</b> <code>${formatMoney(payload.total_cvs)} ₫</code>
• <b>Tổng Thực Hiện:</b> <b>${formatMoney(payload.total_actual)} ₫</b>
• <b>% ĐẠT:</b> <b>${payload.percent_achieved}%</b> (vs Timegone ${payload.timegone}%)
━━━━━━━━━━━━━━━━━━━━
🏆 <b>BẢNG XẾP HẠNG NHÂN VIÊN:</b>\n`;

        for (let i = 0; i < Math.min(10, topEmployees.length); i++) {
          const emp = topEmployees[i];
          const medal = i === 0 ? '🥇' : (i === 1 ? '🥈' : (i === 2 ? '🥉' : `${i + 1}.`));
          const statusIcon = emp.percent >= payload.timegone ? '🟢' : (emp.percent >= payload.timegone * 0.75 ? '🟠' : '🔴');
          summaryMsg += `${medal} ${statusIcon} <b>${emp.name}</b>: ${emp.percent}% (${formatMoney(emp.total_actual)} ₫)\n`;
        }

        summaryMsg += 
`━━━━━━━━━━━━━━━━━━━━
<i>Đã đính kèm ảnh biểu đồ và file Excel (.xlsx) ở phía trên!</i>`;

        await sendMessage(token, chatId, summaryMsg);

        // Xóa session hoàn tất
        sessions.delete(chatId);

      } else {
        const receivedTitle = detectedType === 'ST' ? '🏬 File Siêu Thị (BHX & WinMart+)' : '🏪 File CVS & NPP (GS25, 7E, CK, FM, Hoàng Đức)';
        const missingTitle = detectedType === 'ST' ? '🏪 File CVS & NPP' : '🏬 File Siêu Thị (BHX)';

        await sendMessage(token, chatId, 
`✅ <b>Đã nhận diện:</b> ${receivedTitle}
📄 <i>${fileName}</i>

⏳ <b>Còn thiếu:</b> ${missingTitle}
👉 <i>Vui lòng gửi tiếp file thứ 2 để Bot tạo báo cáo hoàn chỉnh!</i>`);
      }

      return res.status(200).json({ ok: true });
    }

    // Tin nhắn văn bản không khớp lệnh
    await sendMessage(token, chatId, '💡 <i>Vui lòng gửi 2 file Excel doanh số (.xlsb hoặc .xlsx) để tôi tạo báo cáo, hoặc gõ /help để xem hướng dẫn.</i>');
    return res.status(200).json({ ok: true });

  } catch (err) {
    console.error('Lỗi xử lý webhook:', err);
    return res.status(200).json({ ok: false, error: err.message });
  }
};
