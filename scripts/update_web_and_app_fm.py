import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

fm_hubs_data = [
    {"name": "125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh", "code": "PNTU", "amount": 543750},
    {"name": "18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM", "code": "PNTU", "amount": 141921000},
    {"name": "34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh", "code": "PNTU", "amount": 483600},
    {"name": "97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh", "code": "PNTU", "amount": 608100},
    {"name": "Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh", "code": "PNTU", "amount": 589017600},
    {"name": "G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh", "code": "PNTU", "amount": 633600}
]

print("Starting Web & App update for FamilyMart Hubs...")

# ==============================================================================
# 1. UPDATE lib/excel-builder.js
# ==============================================================================
print("1. Updating lib/excel-builder.js...")
with open('lib/excel-builder.js', 'r', encoding='utf-8') as f:
    eb = f.read()

# Pattern for Sheet 6 in excel-builder.js
m_ws6 = re.search(r'// SHEET 6: CHI TIẾT SKU FAMILYMART.*?return wb;\s*\}', eb, re.DOTALL)
if m_ws6:
    new_sheet6 = '''// SHEET 6: CHI TIẾT HUBS & PHÂN BỔ FAMILYMART (HIỂN THỊ GIỐNG BÁCH HÓA XANH)
        // -------------------------------------------------------------
        const ws6 = wb.addWorksheet('Chi tiết FamilyMart', { properties: { tabColor: { argb: 'FFED7D31' } } });
        ws6.columns = [
          { width: 8 },  // A: STT
          { width: 50 }, // B: Tên Hub / Nhân viên
          { width: 22 }, // C: Doanh số Hub / Số CH
          { width: 22 }, // D: Ghi chú / TB CH
          { width: 26 }, // E: Doanh số phân bổ
          { width: 16 }  // F: % Tỷ trọng
        ];

        // Row 1: Title Banner
        ws6.mergeCells('A1:F1');
        const t6 = ws6.getCell('A1');
        t6.value = '🏪 BÁO CÁO CHI TIẾT HUBS & PHÂN BỔ DOANH SỐ - CHUỖI FAMILYMART';
        t6.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFFFF' } };
        t6.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        t6.alignment = { horizontal: 'center', vertical: 'middle' };
        ws6.getRow(1).height = 28;

        const fmHubsList = p.fm_hubs || [
          { name: '125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 543750 },
          { name: '18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM', code: 'PNTU', amount: 141921000 },
          { name: '34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh', code: 'PNTU', amount: 483600 },
          { name: '97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 608100 },
          { name: 'Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh', code: 'PNTU', amount: 589017600 },
          { name: 'G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh', code: 'PNTU', amount: 633600 }
        ];
        const totFmHubs = p.total_actual_fm_hubs || fmHubsList.reduce((a, b) => a + (b.amount || 0), 0);
        const totStoresFmSys = p.total_stores_fm || 196;
        const fmUnitPrice = p.fm_per_store || Math.round(totFmHubs / totStoresFmSys);

        const setFmTop = (row, lbl, val, fmt, isRed) => {
          const a = ws6.getCell('A' + row);
          a.value = lbl;
          a.font = { name: 'Calibri', bold: true };
          a.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF2CC' } };
          a.border = thinBorder;

          const b = ws6.getCell('B' + row);
          b.value = val;
          if (fmt) b.numFmt = fmt;
          b.font = { name: 'Calibri', bold: true, color: { argb: isRed ? 'FFC00000' : 'FF000000' } };
          b.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF9E6' } };
          b.border = thinBorder;
        };

        setFmTop(3, 'Tổng DS 6 Hubs Hệ Thống:', totFmHubs, '#,##0', true);
        setFmTop(4, 'Tổng số CH hệ thống:', totStoresFmSys, null, false);
        setFmTop(5, 'TB doanh số/CH:', { formula: 'B3/B4', result: fmUnitPrice }, '#,##0', true);

        // BẢNG 1: 6 HUBS FAMILYMART
        ws6.mergeCells('A7:D7');
        const hFm1 = ws6.getCell('A7');
        hFm1.value = '1. CHI TIẾT 6 HUBS XUẤT HÀNG FAMILYMART (PNTU / GIA ĐÌNH VIỆT NAM)';
        hFm1.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
        hFm1.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
        hFm1.alignment = { horizontal: 'left', vertical: 'middle' };
        ws6.getRow(7).height = 22;

        const hubHdrs = ['STT', 'Tên Hub / Địa Chỉ Hub FamilyMart', 'Doanh Số Thực Tế (VNĐ)', 'Ghi Chú'];
        ['A', 'B', 'C', 'D'].forEach((col, idx) => {
          const c = ws6.getCell(col + '8');
          c.value = hubHdrs[idx];
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF333F48' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws6.getRow(8).height = 22;

        fmHubsList.forEach((h, idx) => {
          const r = 9 + idx;
          const ca = ws6.getCell('A' + r); ca.value = idx + 1; ca.alignment = { horizontal: 'center' }; ca.border = thinBorder;
          const cb = ws6.getCell('B' + r); cb.value = h.name; cb.border = thinBorder;
          const cc = ws6.getCell('C' + r); cc.value = h.amount; cc.numFmt = '#,##0'; cc.font = { bold: true }; cc.alignment = { horizontal: 'right' }; cc.border = thinBorder;
          const cd = ws6.getCell('D' + r); cd.value = 'Mã GS: ' + (h.code || 'PNTU'); cd.alignment = { horizontal: 'center' }; cd.border = thinBorder;
          ws6.getRow(r).height = 20;
        });

        const hubTotR = 9 + fmHubsList.length;
        ws6.mergeCells(`A${hubTotR}:B${hubTotR}`);
        const cTotHubLbl = ws6.getCell(`A${hubTotR}`);
        cTotHubLbl.value = 'TỔNG 6 HUBS FAMILYMART (HỆ THỐNG)';
        cTotHubLbl.font = { name: 'Calibri', bold: true };
        cTotHubLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubLbl.alignment = { horizontal: 'center' };
        cTotHubLbl.border = thinBorder;
        ws6.getCell(`B${hubTotR}`).border = thinBorder;

        const cTotHubVal = ws6.getCell(`C${hubTotR}`);
        cTotHubVal.value = { formula: `SUM(C9:C${hubTotR-1})`, result: totFmHubs };
        cTotHubVal.numFmt = '#,##0';
        cTotHubVal.font = { name: 'Calibri', bold: true, color: { argb: 'FFC00000' } };
        cTotHubVal.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubVal.alignment = { horizontal: 'right' };
        cTotHubVal.border = thinBorder;

        const cTotHubNote = ws6.getCell(`D${hubTotR}`);
        cTotHubNote.value = `Đơn giá: ${fmUnitPrice.toLocaleString('vi-VN')} đ/CH`;
        cTotHubNote.font = { name: 'Calibri', bold: true };
        cTotHubNote.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubNote.alignment = { horizontal: 'center' };
        cTotHubNote.border = thinBorder;
        ws6.getRow(hubTotR).height = 22;

        // BẢNG 2: PHÂN BỔ FAMILYMART THEO NHÂN VIÊN (36 CH)
        const distStartR = hubTotR + 3;
        ws6.mergeCells(`A${distStartR-1}:F${distStartR-1}`);
        const hFm2 = ws6.getCell(`A${distStartR-1}`);
        hFm2.value = '2. PHÂN BỔ DOANH SỐ FAMILYMART THEO NHÂN VIÊN (36 CỬA HÀNG KHU VỰC)';
        hFm2.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
        hFm2.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
        hFm2.alignment = { horizontal: 'left', vertical: 'middle' };
        ws6.getRow(distStartR-1).height = 22;

        const distHdrs = ['STT', 'Nhân Viên / Điểm Bán', 'Số CH FM', 'TB/CH', 'Doanh Số FM Phân Bổ', '% FM/Team'];
        distHdrs.forEach((bh, idx) => {
          const colLetter = String.fromCharCode(65 + idx);
          const c = ws6.getCell(colLetter + distStartR);
          c.value = bh;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws6.getRow(distStartR).height = 22;

        const fmDistList = [
          { name: 'Nguyễn Đức Hoà', count: 24, amount: Math.round(fmUnitPrice * 24) },
          { name: 'Nguyễn Thị Thanh Thủy', count: 7, amount: Math.round(fmUnitPrice * 7) },
          { name: 'Não Thị Anh Đào', count: 3, amount: Math.round(fmUnitPrice * 3) },
          { name: 'Kim Hoàng Khang', count: 1, amount: Math.round(fmUnitPrice * 1) },
          { name: 'Chưa phân bổ nhân sự (Căn 03 Marina Swanbay)', count: 1, amount: fmUnitPrice }
        ];

        const fmDistTotR = distStartR + 1 + fmDistList.length;

        fmDistList.forEach((d, idx) => {
          const r = distStartR + 1 + idx;
          const ca = ws6.getCell('A' + r); ca.value = idx + 1; ca.alignment = { horizontal: 'center' }; ca.border = thinBorder;
          const cb = ws6.getCell('B' + r); cb.value = d.name; cb.font = { bold: true }; cb.border = thinBorder;
          const cc = ws6.getCell('C' + r); cc.value = d.count; cc.alignment = { horizontal: 'center' }; cc.border = thinBorder;
          const cd = ws6.getCell('D' + r); cd.value = { formula: '$B$5', result: fmUnitPrice }; cd.numFmt = '#,##0'; cd.alignment = { horizontal: 'right' }; cd.border = thinBorder;
          const ce = ws6.getCell('E' + r); ce.value = { formula: `C${r}*D${r}`, result: d.amount }; ce.numFmt = '#,##0'; ce.font = { bold: true }; ce.alignment = { horizontal: 'right' }; ce.border = thinBorder;
          const cf = ws6.getCell('F' + r); cf.value = { formula: `E${r}/$E$${fmDistTotR}`, result: d.count / 36 }; cf.numFmt = '0.0%'; cf.alignment = { horizontal: 'center' }; cf.border = thinBorder;
          ws6.getRow(r).height = 20;
        });

        ws6.mergeCells(`A${fmDistTotR}:B${fmDistTotR}`);
        const fTotLbl = ws6.getCell(`A${fmDistTotR}`);
        fTotLbl.value = 'TỔNG CỘNG KHU VỰC (36 CỬA HÀNG)';
        fTotLbl.font = { name: 'Calibri', bold: true };
        fTotLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotLbl.alignment = { horizontal: 'center' };
        fTotLbl.border = thinBorder;
        ws6.getCell(`B${fmDistTotR}`).border = thinBorder;

        const fTotC = ws6.getCell(`C${fmDistTotR}`);
        fTotC.value = { formula: `SUM(C${distStartR+1}:C${fmDistTotR-1})`, result: 36 };
        fTotC.font = { name: 'Calibri', bold: true };
        fTotC.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotC.alignment = { horizontal: 'center' };
        fTotC.border = thinBorder;

        const fTotD = ws6.getCell(`D${fmDistTotR}`);
        fTotD.value = { formula: '$B$5', result: fmUnitPrice };
        fTotD.numFmt = '#,##0';
        fTotD.font = { name: 'Calibri', bold: true };
        fTotD.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotD.alignment = { horizontal: 'right' };
        fTotD.border = thinBorder;

        const fTotE = ws6.getCell(`E${fmDistTotR}`);
        const totFmDistAmt = fmDistList.reduce((a, b) => a + b.amount, 0);
        fTotE.value = { formula: `SUM(E${distStartR+1}:E${fmDistTotR-1})`, result: totFmDistAmt };
        fTotE.numFmt = '#,##0';
        fTotE.font = { name: 'Calibri', bold: true, color: { argb: 'FFC00000' } };
        fTotE.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotE.alignment = { horizontal: 'right' };
        fTotE.border = thinBorder;

        const fTotF = ws6.getCell(`F${fmDistTotR}`);
        fTotF.value = { formula: `SUM(F${distStartR+1}:F${fmDistTotR-1})`, result: 1 };
        fTotF.numFmt = '0.0%';
        fTotF.font = { name: 'Calibri', bold: true };
        fTotF.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotF.alignment = { horizontal: 'center' };
        fTotF.border = thinBorder;
        ws6.getRow(fmDistTotR).height = 24;

        return wb;
    }'''
    eb = eb[:m_ws6.start()] + new_sheet6 + eb[m_ws6.end():]
    with open('lib/excel-builder.js', 'w', encoding='utf-8') as f:
        f.write(eb)
    print("lib/excel-builder.js updated!")
else:
    print("Could not find Sheet 6 in lib/excel-builder.js")

# ==============================================================================
# 2. UPDATE view.html
# ==============================================================================
print("2. Updating view.html...")
with open('view.html', 'r', encoding='utf-8') as f:
    vhtml = f.read()

# Replace Tab 5 Button
vhtml = vhtml.replace(
    '<button class="tab-btn" onclick="switchTab(\'tabFmSku\')">🛒 Chi Tiết SKU Cửa Hàng FamilyMart</button>',
    '<button class="tab-btn" onclick="switchTab(\'tabFmHubs\')">🏪 5. Phân Bổ 6 Hubs FamilyMart</button>'
)

# Replace Tab 5 Panel
old_tab5_panel = re.search(r'<!-- TAB 5: CHI TIẾT SKU CỬA HÀNG FAMILYMART -->.*?</div>\s*</div>\s*</div>\s*</main>', vhtml, re.DOTALL)
if old_tab5_panel:
    new_tab5_panel = '''<!-- TAB 5: PHÂN BỔ 6 HUBS FAMILYMART (TƯƠNG TỰ BÁCH HÓA XANH) -->
      <div class="tab-panel" id="tabFmHubs">
        <!-- BẢNG 1: 6 HUBS FAMILYMART -->
        <div class="panel-toolbar" style="margin-bottom: 8px;">
          <div style="font-weight:700; color:#0F172A; font-size:14px;">1. Chi Tiết 6 Hubs Xuất Hàng FamilyMart (Toàn Hệ Thống):</div>
          <button class="btn-action" style="background:#E2E8F0; color:#1E293B;" onclick="captureTable('tableFmHubs', '6_Hubs_FamilyMart')">📸 Copy Bảng Hubs</button>
        </div>
        <div class="table-responsive" style="margin-bottom: 24px;">
          <table id="tableFmHubs">
            <thead>
              <tr>
                <th class="text-center" style="width:50px;">STT</th>
                <th>HUB FAMILYMART (CÔNG TY TNHH CHTL GIA ĐÌNH VIỆT NAM)</th>
                <th class="text-right" style="color:#86EFAC; width:220px;">DOANH SỐ THỰC TẾ (VNĐ)</th>
                <th style="width:200px;">GHI CHÚ</th>
              </tr>
            </thead>
            <tbody id="tbodyFmHubs"></tbody>
            <tfoot id="tfootFmHubs"></tfoot>
          </table>
        </div>

        <!-- BẢNG 2: PHÂN BỔ FAMILYMART THEO NHÂN VIÊN -->
        <div class="panel-toolbar" style="margin-bottom: 8px;">
          <div style="font-weight:700; color:#0F172A; font-size:14px;">2. Phân Bổ Doanh Số FamilyMart Theo Nhân Viên (36 Cửa Hàng):</div>
          <button class="btn-action" style="background:#E2E8F0; color:#1E293B;" onclick="captureTable('tableFmDist', 'Phan_Bo_FamilyMart_Team')">📸 Copy Bảng Phân Bổ</button>
        </div>
        <div class="table-responsive">
          <table id="tableFmDist">
            <thead>
              <tr>
                <th class="text-center" style="width:45px;">STT</th>
                <th>NHÂN VIÊN / ĐIỂM BÁN</th>
                <th class="text-center">SỐ CỬA HÀNG QUẢN LÝ</th>
                <th class="text-right">ĐƠN GIÁ/CH</th>
                <th class="text-right" style="color:#86EFAC;">DOANH SỐ FM PHÂN BỔ (VNĐ)</th>
                <th class="text-center" style="color:#FDE047;">% TỶ TRỌNG FM/TEAM</th>
              </tr>
            </thead>
            <tbody id="tbodyFmDist"></tbody>
            <tfoot id="tfootFmDist"></tfoot>
          </table>
        </div>
      </div>

    </div>
  </main>'''
    vhtml = vhtml[:old_tab5_panel.start()] + new_tab5_panel + vhtml[old_tab5_panel.end():]
    print("Tab 5 HTML replaced in view.html!")

# Add JS functions renderTableFmHubs and renderTableFmDist in view.html
if 'function renderTableFmHubs' not in vhtml:
    render_funcs = '''
    function renderTableFmHubs(data) {
      const tbody = document.getElementById('tbodyFmHubs');
      const tfoot = document.getElementById('tfootFmHubs');
      if (!tbody || !tfoot) return;
      tbody.innerHTML = '';

      const hubs = data.fm_hubs || [
        { name: '125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 543750 },
        { name: '18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM', code: 'PNTU', amount: 141921000 },
        { name: '34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh', code: 'PNTU', amount: 483600 },
        { name: '97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 608100 },
        { name: 'Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh', code: 'PNTU', amount: 589017600 },
        { name: 'G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh', code: 'PNTU', amount: 633600 }
      ];

      let sum = 0;
      hubs.forEach((h, idx) => {
        sum += (h.amount || 0);
        tbody.innerHTML += `
          <tr>
            <td class="text-center font-bold">${idx + 1}</td>
            <td class="font-bold">${h.name}</td>
            <td class="text-right font-bold" style="color:#059669;">${formatMoney(h.amount)}</td>
            <td>Mã GS: ${h.code || 'PNTU'}</td>
          </tr>
        `;
      });

      const totStores = data.total_stores_fm || 196;
      const unitPrice = data.fm_per_store || Math.round(sum / totStores);

      tfoot.innerHTML = `
        <tr>
          <td colspan="2" class="text-center font-bold">TỔNG 6 HUBS FAMILYMART (TOÀN HỆ THỐNG)</td>
          <td class="text-right font-bold" style="color:#86EFAC !important;">${formatMoney(sum)}</td>
          <td class="font-bold" style="color:#FDE047 !important;">Đơn giá: ${formatMoney(unitPrice)} / CH (÷ ${totStores} CH)</td>
        </tr>
      `;
    }

    function renderTableFmDist(data) {
      const tbody = document.getElementById('tbodyFmDist');
      const tfoot = document.getElementById('tfootFmDist');
      if (!tbody || !tfoot) return;
      tbody.innerHTML = '';

      const unitPrice = data.fm_per_store || 3740855;
      const dist = data.fm_dist || [
        { name: 'Nguyễn Đức Hoà', count: 24, amount: 89780529, pct: 24 / 36 },
        { name: 'Nguyễn Thị Thanh Thủy', count: 7, amount: 26185988, pct: 7 / 36 },
        { name: 'Não Thị Anh Đào', count: 3, amount: 11222566, pct: 3 / 36 },
        { name: 'Kim Hoàng Khang', count: 1, amount: 3740855, pct: 1 / 36 },
        { name: 'Chưa phân bổ nhân sự (Căn 03 Marina Swanbay)', count: 1, amount: 3740855, pct: 1 / 36 }
      ];

      let totCount = 0, totAmt = 0;
      dist.forEach((d, idx) => {
        totCount += d.count;
        totAmt += d.amount;
        tbody.innerHTML += `
          <tr>
            <td class="text-center font-bold">${idx + 1}</td>
            <td class="font-bold">${d.name}</td>
            <td class="text-center font-bold">${d.count} CH</td>
            <td class="text-right">${formatMoney(unitPrice)}</td>
            <td class="text-right font-bold" style="color:#059669;">${formatMoney(d.amount)}</td>
            <td class="text-center font-bold" style="color:#0F766E;">${(d.pct * 100).toFixed(1)}%</td>
          </tr>
        `;
      });

      tfoot.innerHTML = `
        <tr>
          <td colspan="2" class="text-center font-bold">TỔNG CỘNG KHU VỰC (36 CỬA HÀNG)</td>
          <td class="text-center font-bold" style="color:#FFFFFF !important;">${totCount} CH</td>
          <td class="text-right font-bold" style="color:#FFFFFF !important;">${formatMoney(unitPrice)}</td>
          <td class="text-right font-bold" style="color:#86EFAC !important;">${formatMoney(totAmt)}</td>
          <td class="text-center font-bold" style="color:#FDE047 !important;">100.0%</td>
        </tr>
      `;
    }
'''
    vhtml = vhtml.replace('function renderTableFm(data) {', render_funcs + '\n    function renderTableFm(data) {')
    vhtml = vhtml.replace('renderTableFm(data);', 'renderTableFmHubs(data);\n      renderTableFmDist(data);')
    print("Added renderTableFmHubs & renderTableFmDist to view.html!")

# Replace Sheet 6 in view.html Excel export
m_vws6 = re.search(r'// SHEET 6: CHI TIẾT SKU FAMILYMART.*?return wb;\s*\}', vhtml, re.DOTALL)
if m_vws6:
    vhtml = vhtml[:m_vws6.start()] + new_sheet6 + vhtml[m_vws6.end():]
    print("Updated Sheet 6 in view.html!")

with open('view.html', 'w', encoding='utf-8') as f:
    f.write(vhtml)

# ==============================================================================
# 3. UPDATE index.html
# ==============================================================================
print("3. Updating index.html...")
with open('index.html', 'r', encoding='utf-8') as f:
    ihtml = f.read()

# Update SYSTEM_CONFIG in index.html
ihtml = ihtml.replace(
    'TOTAL_BHX_SYSTEM: 232,',
    'TOTAL_BHX_SYSTEM: 232,\n      TOTAL_FM_SYSTEM: 196,\n      FM_TEAM_STORES: 36,'
)

# Update DEFAULT_MASTER in index.html
if 'fm_hubs:' not in ihtml:
    ihtml = ihtml.replace(
        'bhx_hubs: [',
        f'total_stores_fm: 196,\n      total_stores_fm_team: 36,\n      fm_hubs: {json.dumps(fm_hubs_data, indent=8)},\n      bhx_hubs: ['
    )

# Replace Tab 5 Button in index.html
ihtml = ihtml.replace(
    '<button class="tab-btn" onclick="switchTab(\'tabFmSku\')">🛒 Chi Tiết SKU Cửa Hàng FamilyMart</button>',
    '<button class="tab-btn" onclick="switchTab(\'tabFmHubs\')">🏪 5. Phân Bổ 6 Hubs FamilyMart</button>'
)

# Replace Tab 5 Panel in index.html if present
old_tab5_index = re.search(r'<!-- TAB 5: CHI TIẾT SKU CỬA HÀNG FAMILYMART -->.*?</div>\s*</div>\s*</div>\s*</main>', ihtml, re.DOTALL)
if old_tab5_index:
    ihtml = ihtml[:old_tab5_index.start()] + new_tab5_panel + ihtml[old_tab5_index.end():]
    print("Tab 5 HTML replaced in index.html!")

# Add JS functions in index.html
if 'function renderTableFmHubs' not in ihtml:
    ihtml = ihtml.replace('function renderTableFm(data) {', render_funcs + '\n    function renderTableFm(data) {')
    ihtml = ihtml.replace('renderTableFm(data);', 'renderTableFmHubs(data);\n      renderTableFmDist(data);')

# Replace Sheet 6 in index.html if present
m_iws6 = re.search(r'// SHEET 6: CHI TIẾT SKU FAMILYMART.*?return wb;\s*\}', ihtml, re.DOTALL)
if m_iws6:
    ihtml = ihtml[:m_iws6.start()] + new_sheet6 + ihtml[m_iws6.end():]
    print("Updated Sheet 6 in index.html!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(ihtml)

print("Web & App updates completed successfully!")
