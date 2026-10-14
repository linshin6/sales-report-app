# -*- coding: utf-8 -*-
import re
import json
import shutil
import os

print("=== STARTING COMPREHENSIVE UPDATE: BHX 240, FM HUBS TAB, CVS TABLE ===")

# 1. UPDATE master_data.js
with open('master_data.js', 'r', encoding='utf-8') as f:
    m_content = f.read()

m_content = re.sub(r'"total_stores_bhx":\s*\d+', '"total_stores_bhx": 240', m_content)
with open('master_data.js', 'w', encoding='utf-8') as f:
    f.write(m_content)
print("Updated master_data.js (total_stores_bhx: 240)")

# 2. UPDATE lib/excel-builder.js
with open('lib/excel-builder.js', 'r', encoding='utf-8') as f:
    eb_content = f.read()

eb_content = eb_content.replace('p.total_stores_bhx || 232', 'p.total_stores_bhx || 240')
with open('lib/excel-builder.js', 'w', encoding='utf-8') as f:
    f.write(eb_content)
print("Updated lib/excel-builder.js (BHX system stores 240)")

# 3. UPDATE view.html
with open('view.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

# Replace 232 with 240 in view.html
v_content = v_content.replace('p.total_stores_bhx || 232', 'p.total_stores_bhx || 240')
v_content = v_content.replace('🏪 5. Phân Bổ 6 Hubs FamilyMart', '🏪 5. Phân Bổ FamilyMart')

# Remove Địa Chỉ header from tableCvs in view.html
old_v_cvs_thead = """              <tr>
                <th class="text-center" style="width:45px;">STT</th>
                <th>CHUỖI</th>
                <th>NHÂN VIÊN QUẢN LÝ</th>
                <th>MÃ CỬA HÀNG</th>
                <th>TÊN CỬA HÀNG</th>
                <th style="max-width:350px;">ĐỊA CHỈ</th>
                <th class="text-right" style="color:#93C5FD;">DOANH SỐ (VNĐ)</th>
              </tr>"""

new_v_cvs_thead = """              <tr>
                <th class="text-center" style="width:45px;">STT</th>
                <th class="text-center">CHUỖI</th>
                <th>NHÂN VIÊN QUẢN LÝ</th>
                <th>MÃ CỬA HÀNG</th>
                <th>TÊN CỬA HÀNG</th>
                <th class="text-right" style="color:#93C5FD;">DOANH SỐ (VNĐ)</th>
              </tr>"""

if old_v_cvs_thead in v_content:
    v_content = v_content.replace(old_v_cvs_thead, new_v_cvs_thead)
    print("Replaced view.html CVS thead")
else:
    print("Warning: old_v_cvs_thead not found exactly, using regex")
    v_content = re.sub(
        r'<tr>\s*<th class="text-center"[^>]*>STT</th>\s*<th>CHUỖI</th>\s*<th>NHÂN VIÊN QUẢN LÝ</th>\s*<th>MÃ CỬA HÀNG</th>\s*<th>TÊN CỬA HÀNG</th>\s*<th[^>]*>ĐỊA CHỈ</th>\s*<th class="text-right"[^>]*>DOANH SỐ \(VNĐ\)</th>\s*</tr>',
        new_v_cvs_thead,
        v_content
    )

# In view.html renderTableCvs tbody:
old_v_row = """          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center font-bold" style="color:#64748B;">${idx + 1}</td>
            <td>${getCvsChainBadge(s.chain)}</td>
            <td>${empCell}</td>
            <td class="font-bold" style="color:#1E293B;"><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600;">${displayName}</td>
            <td style="max-width:350px; font-size:11.5px; color:#475569;">${displayAddr}</td>
            <td class="text-right font-bold" style="color:#0F766E; font-size:13px;">${formatMoney(val)}</td>
          </tr>"""

new_v_row = """          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center font-bold" style="color:#64748B;">${idx + 1}</td>
            <td class="text-center">${getCvsChainBadge(s.chain)}</td>
            <td>${empCell}</td>
            <td class="font-bold" style="color:#1E293B;"><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600;">${displayName}</td>
            <td class="text-right font-bold" style="color:#0F766E; font-size:13px;">${formatMoney(val)}</td>
          </tr>"""

if old_v_row in v_content:
    v_content = v_content.replace(old_v_row, new_v_row)
    print("Replaced view.html CVS tbody row")
else:
    print("Warning: old_v_row not found exactly, using regex")
    v_content = re.sub(
        r'<td style="max-width:350px; font-size:11\.5px; color:#475569;">\$\{displayAddr\}</td>\s*',
        '',
        v_content
    )

# In view.html tfoot and isNewEmp:
v_content = v_content.replace('<td colspan="7" style="height:14px; padding:0; background:#EEF2F6;', '<td colspan="6" style="height:14px; padding:0; background:#EEF2F6;')
v_content = v_content.replace('<td colspan="6" class="text-center font-bold">TỔNG (${filtered.length} CỬA HÀNG)</td>', '<td colspan="5" class="text-center font-bold">TỔNG (${filtered.length} CỬA HÀNG)</td>')

with open('view.html', 'w', encoding='utf-8') as f:
    f.write(v_content)
print("Updated view.html successfully")

# 4. UPDATE index.html
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# A. BHX 240 stores logic:
idx_content = idx_content.replace('TOTAL_BHX_SYSTEM: 232', 'TOTAL_BHX_SYSTEM: 240')
idx_content = idx_content.replace('total_stores_bhx: 232', 'total_stores_bhx: 240')
idx_content = idx_content.replace('TOTAL_BHX_SYSTEM: 232 CH', 'TOTAL_BHX_SYSTEM: 240 CH')
idx_content = idx_content.replace('currentMaster.total_stores_bhx = 232;', 'currentMaster.total_stores_bhx = 240;')
idx_content = idx_content.replace('currentMaster.total_stores_bhx || 232', 'currentMaster.total_stores_bhx || 240')
idx_content = idx_content.replace('data.total_stores_bhx || 232', 'data.total_stores_bhx || 240')
idx_content = idx_content.replace('p.total_stores_bhx || 232', 'p.total_stores_bhx || 240')

# In handleTargetFile, prioritize curSheetTotalBhxRows >= 50 so 240 is detected:
old_target_count_logic = """                let curTotalSysBhx = 0;
                if (curSheetUniqueBhxCodes.size >= 50) {
                  curTotalSysBhx = curSheetUniqueBhxCodes.size;
                } else if (curSheetTotalBhxRows >= 50) {
                  curTotalSysBhx = curSheetTotalBhxRows;
                } else if (curSheetSumBhxCol >= 50) {
                  curTotalSysBhx = curSheetSumBhxCol;
                }"""

new_target_count_logic = """                let curTotalSysBhx = 0;
                if (curSheetTotalBhxRows >= 50) {
                  curTotalSysBhx = curSheetTotalBhxRows;
                } else if (curSheetUniqueBhxCodes.size >= 50) {
                  curTotalSysBhx = curSheetUniqueBhxCodes.size;
                } else if (curSheetSumBhxCol >= 50) {
                  curTotalSysBhx = curSheetSumBhxCol;
                }"""

if old_target_count_logic in idx_content:
    idx_content = idx_content.replace(old_target_count_logic, new_target_count_logic)
    print("Replaced handleTargetFile count logic in index.html")

# B. Rename Tab 5 Button:
idx_content = idx_content.replace(
    '<button class="tab-btn" onclick="switchTab(\'tabFmSku\', this)">🛒 Chi Tiết SKU Cửa Hàng FamilyMart</button>',
    '<button class="tab-btn" onclick="switchTab(\'tabFmHubs\', this)">🏪 Phân Bổ FamilyMart</button>'
)

# C. Update CVS Table Header in index.html (remove Địa Chỉ):
old_idx_cvs_thead = """            <thead>
              <tr>
                <th class="text-center" style="width:45px;">STT</th>
                <th>Chuỗi</th>
                <th>Nhân Viên Quản Lý</th>
                <th>Mã CH</th>
                <th>Tên Cửa Hàng</th>
                <th>Địa Chỉ</th>
                <th class="text-right">Doanh Số (VNĐ)</th>
              </tr>
            </thead>"""

new_idx_cvs_thead = """            <thead>
              <tr>
                <th class="text-center" style="width:45px;">STT</th>
                <th class="text-center">Chuỗi</th>
                <th>Nhân Viên Quản Lý</th>
                <th>Mã CH</th>
                <th>Tên Cửa Hàng</th>
                <th class="text-right">Doanh Số (VNĐ)</th>
              </tr>
            </thead>"""

if old_idx_cvs_thead in idx_content:
    idx_content = idx_content.replace(old_idx_cvs_thead, new_idx_cvs_thead)
    print("Replaced index.html CVS thead")

# D. Update renderStoresTable in index.html:
old_render_stores = """        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center" style="color:#64748B; font-weight:700;">${idx + 1}</td>
            <td>${empCell}</td>
            <td class="text-center">${getChainBadgeLocal(s.chain)}</td>
            <td><code>${s.store_code || '-'}</code></td>
            <td style="max-width:380px; overflow:hidden; text-overflow:ellipsis;">${s.store_address}</td>
            <td class="text-right font-bold" style="color:#0F766E;">${formatNumber(s.actual)}</td>
          </tr>
        `;
      });
    }"""

new_render_stores = """        const displayName = (s.store_name && s.store_name !== 'undefined') ? s.store_name : (s.chain + (s.store_code ? (' - ' + s.store_code) : ''));

        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center" style="color:#64748B; font-weight:700;">${idx + 1}</td>
            <td class="text-center">${getChainBadgeLocal(s.chain)}</td>
            <td>${empCell}</td>
            <td><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600; color:#0F172A; max-width:380px; overflow:hidden; text-overflow:ellipsis;">${displayName}</td>
            <td class="text-right font-bold" style="color:#0F766E;">${formatNumber(s.actual)}</td>
          </tr>
        `;
      });

      const tfoot = document.getElementById('storesTableFoot');
      if (tfoot) {
        const sumCvs = sortedStores.reduce((acc, s) => acc + (s.actual || 0), 0);
        tfoot.innerHTML = `
          <tr>
            <td colspan="5" class="text-center font-bold">TỔNG (${sortedStores.length} CỬA HÀNG)</td>
            <td class="text-right font-bold" style="color:#93C5FD !important;">${formatNumber(sumCvs)}</td>
          </tr>
        `;
      }
    }"""

if old_render_stores in idx_content:
    idx_content = idx_content.replace(old_render_stores, new_render_stores)
    print("Replaced index.html renderStoresTable rows and added tfoot")

# E. Replace Tab 5 DOM container in index.html (replace tabFmSku with tabFmHubs):
tab5_pattern = r'<!-- Tab 5: Chi Tiết SKU FamilyMart -->\s*<div id="tabFmSku" class="tab-content" style="display:none;">[\s\S]*?</div>\s*<!-- Tab 6: So Sánh'

new_tab5_html = """<!-- Tab 5: Phân Bổ FamilyMart -->
      <div id="tabFmHubs" class="tab-content" style="display:none;">
        <!-- Header Banner -->
        <div style="background:linear-gradient(135deg, #f1f5f9 0%, #ccfbf1 100%); color:#0f172a; padding:18px 22px; border-radius:14px; margin-bottom:20px; box-shadow:var(--shadow-sm); border:1.5px solid var(--border-strong); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <h3 style="font-size:16px; font-weight:800; display:flex; align-items:center; gap:8px; margin:0; color:#0f172a;">
              🏪 PHÂN BỔ DOANH SỐ FAMILYMART (6 HUBS - TRỰC TIẾP NHÀ MÁY)
            </h3>
            <p style="font-size:13px; color:#475569; margin-top:4px;">
              Mô hình nhận hàng trực tiếp từ nhà máy giao về 6 Hubs toàn hệ thống 196 CH (Tương tự Bách Hóa Xanh)
            </p>
          </div>
          <div style="display:flex; gap:10px;">
            <button class="btn btn-excel" onclick="exportToExcelPerfect()" style="padding:8px 14px; font-size:12.5px;">
              📥 Tải File Excel (Đầy đủ 6 Sheet)
            </button>
          </div>
        </div>

        <!-- BẢNG 1: 6 HUBS FAMILYMART -->
        <div class="sheet-toolbar" style="margin-bottom:8px;">
          <div class="sheet-toolbar-left">
            <span style="font-size:14px; font-weight:800; color:#0f172a;">🏢 1. Chi Tiết 6 Hubs Xuất Hàng FamilyMart (Toàn Hệ Thống 196 CH):</span>
          </div>
          <div class="sheet-toolbar-right">
            <button class="btn-zalo" onclick="captureAndSendToZalo('tabFmHubs')" style="background:#0068FF; color:#fff; font-weight:700; padding:8px 15px; border-radius:12px; font-size:13px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 3px 10px rgba(0,104,255,0.3);">
              💬 Gửi Zalo
            </button>
            <button class="btn-capture" onclick="captureCurrentSheet('tabFmHubs')">
              📸 Copy Bảng 6 Hubs
            </button>
            <button class="btn-capture-outline" onclick="downloadCurrentSheetImage('tabFmHubs')">
              💾 Tải Ảnh
            </button>
          </div>
        </div>
        <div class="table-container" id="fmHubsTableContainer" style="margin-bottom:24px;">
          <table>
            <thead>
              <tr>
                <th class="text-center" style="width:50px;">STT</th>
                <th>Hub FamilyMart (Công ty TNHH CHTL Gia Đình Việt Nam)</th>
                <th class="text-right" style="color:#86EFAC; width:220px;">Doanh Số Thực Tế (VNĐ)</th>
                <th style="width:200px;">Ghi Chú</th>
              </tr>
            </thead>
            <tbody id="fmHubsTableBody"></tbody>
            <tfoot id="fmHubsTableFoot" style="background:#FFF2CC; font-weight:700;"></tfoot>
          </table>
        </div>

        <!-- BẢNG 2: PHÂN BỔ FAMILYMART THEO NHÂN VIÊN -->
        <div class="sheet-toolbar" style="margin-bottom:8px;">
          <div class="sheet-toolbar-left">
            <span style="font-size:14px; font-weight:800; color:#0f172a;">📦 2. Phân Bổ Doanh Số FamilyMart Theo Nhân Viên (36 Cửa Hàng):</span>
          </div>
          <div class="sheet-toolbar-right">
            <button class="btn-zalo" onclick="captureAndSendToZalo('tabFmDist')" style="background:#0068FF; color:#fff; font-weight:700; padding:8px 15px; border-radius:12px; font-size:13px; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 3px 10px rgba(0,104,255,0.3);">
              💬 Gửi Zalo
            </button>
            <button class="btn-capture" onclick="captureCurrentSheet('tabFmDist')">
              📸 Copy Bảng Phân Bổ
            </button>
            <button class="btn-capture-outline" onclick="downloadCurrentSheetImage('tabFmDist')">
              💾 Tải Ảnh
            </button>
          </div>
        </div>
        <div class="table-container" id="fmDistTableContainer">
          <table>
            <thead>
              <tr>
                <th class="text-center" style="background:#2E75B6; width:50px;">STT</th>
                <th style="background:#2E75B6;">Nhân Viên / Điểm Bán</th>
                <th class="text-center" style="background:#2E75B6;">Số Cửa Hàng Quản Lý</th>
                <th class="text-right" style="background:#2E75B6;">Đơn Giá/CH</th>
                <th class="text-right" style="background:#2E75B6;">Doanh Số FM Phân Bổ (VNĐ)</th>
                <th class="text-center" style="background:#2E75B6;">% Tỷ Trọng FM/Team</th>
              </tr>
            </thead>
            <tbody id="fmDistTableBody"></tbody>
            <tfoot id="fmDistTableFoot" style="background:#D9E1F2; font-weight:700;"></tfoot>
          </table>
        </div>
      </div>

      <!-- Tab 6: So Sánh"""

idx_content = re.sub(tab5_pattern, new_tab5_html, idx_content)
print("Replaced Tab 5 HTML structure in index.html")

# F. Add renderFmHubsTab function to index.html and call it:
idx_content = idx_content.replace('renderFmSkuTab(data);', 'renderFmHubsTab(data);\n      if (typeof renderFmSkuTab === "function") renderFmSkuTab(data);')

fm_hubs_tab_function = """    // =========================================================================
    // 5B. RENDER FAMILYMART 6 HUBS & DISTRIBUTION TAB
    // =========================================================================
    function renderFmHubsTab(data) {
      const tbodyHubs = document.getElementById('fmHubsTableBody');
      const tfootHubs = document.getElementById('fmHubsTableFoot');
      if (tbodyHubs && tfootHubs) {
        tbodyHubs.innerHTML = '';
        const hubs = (data && data.fm_hubs && data.fm_hubs.length > 0) ? data.fm_hubs : [
          { name: '125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 543750 },
          { name: '18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM', code: 'PNTU', amount: 141921000 },
          { name: '34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh', code: 'PNTU', amount: 483600 },
          { name: '97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 608100 },
          { name: 'Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh', code: 'PNTU', amount: 589017600 },
          { name: 'G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh', code: 'PNTU', amount: 633600 }
        ];

        let sumHubs = 0;
        hubs.forEach((h, idx) => {
          sumHubs += (h.amount || 0);
          tbodyHubs.innerHTML += `
            <tr>
              <td class="text-center">${idx + 1}</td>
              <td class="font-bold">${h.name}</td>
              <td class="text-right font-bold" style="color:#059669;">${formatNumber(h.amount)}</td>
              <td>Mã GS: ${h.code || 'PNTU'}</td>
            </tr>
          `;
        });

        const totStores = (data && data.total_stores_fm) ? data.total_stores_fm : 196;
        const unitPrice = (data && data.fm_per_store) ? data.fm_per_store : Math.round(sumHubs / totStores);

        tfootHubs.innerHTML = `
          <tr>
            <td colspan="2" class="text-center font-bold">TỔNG 6 HUBS FAMILYMART (HỆ THỐNG)</td>
            <td class="text-right font-bold" style="color:#059669;">${formatNumber(sumHubs)}</td>
            <td>Đơn giá: ${formatNumber(unitPrice)} VNĐ / CH (÷ ${totStores} CH toàn hệ thống)</td>
          </tr>
        `;

        const tbodyDist = document.getElementById('fmDistTableBody');
        const tfootDist = document.getElementById('fmDistTableFoot');
        if (tbodyDist && tfootDist) {
          tbodyDist.innerHTML = '';
          const dist = (data && data.fm_dist && data.fm_dist.length > 0) ? data.fm_dist : [
            { name: 'Nguyễn Đức Hoà', count: 24, amount: 24 * unitPrice, pct: 24 / 36 },
            { name: 'Nguyễn Thị Thanh Thủy', count: 7, amount: 7 * unitPrice, pct: 7 / 36 },
            { name: 'Não Thị Anh Đào', count: 3, amount: 3 * unitPrice, pct: 3 / 36 },
            { name: 'Kim Hoàng Khang', count: 1, amount: 1 * unitPrice, pct: 1 / 36 },
            { name: 'Chưa phân bổ nhân sự (Căn 03 Marina Swanbay)', count: 1, amount: 1 * unitPrice, pct: 1 / 36 }
          ];

          let totCount = 0, totAmt = 0;
          dist.forEach((d, idx) => {
            totCount += d.count;
            totAmt += d.amount;
            tbodyDist.innerHTML += `
              <tr>
                <td class="text-center">${idx + 1}</td>
                <td class="font-bold">${d.name}</td>
                <td class="text-center font-semibold">${d.count} Cửa hàng</td>
                <td class="text-right">${formatNumber(unitPrice)}</td>
                <td class="text-right font-bold" style="color:#059669;">${formatNumber(d.amount)}</td>
                <td class="text-center font-semibold">${(d.pct * 100).toFixed(1)}%</td>
              </tr>
            `;
          });

          tfootDist.innerHTML = `
            <tr style="background:#1F4E78;">
              <td colspan="2" class="text-center font-bold" style="color:#FFFFFF !important;">TỔNG CỘNG KHU VỰC (36 CỬA HÀNG)</td>
              <td class="text-center font-bold" style="color:#FFFFFF !important;">${totCount} Cửa hàng</td>
              <td class="text-right font-bold" style="color:#FFFFFF !important;">${formatNumber(unitPrice)}</td>
              <td class="text-right font-bold" style="color:#86EFAC !important;">${formatNumber(totAmt)}</td>
              <td class="text-center font-bold" style="color:#FDE047 !important;">100.0%</td>
            </tr>
          `;
        }
      }
    }

"""

if 'function renderFmHubsTab' not in idx_content:
    idx_content = idx_content.replace('function renderFmSkuTab(data) {', fm_hubs_tab_function + '    function renderFmSkuTab(data) {')
    print("Injected renderFmHubsTab function into index.html")

# G. In processedReportData assignment, attach fm_hubs and fm_dist:
old_processed_rep = """        stores: updatedStores,
        fm_sku_matrix: fmSkuMatrixData,
        total_ck_stores_system: totalCkStoresSystem,"""

new_processed_rep = """        stores: updatedStores,
        fm_sku_matrix: fmSkuMatrixData,
        fm_hubs: fmHubs,
        total_actual_fm_hubs: totalActualFmHubs,
        total_stores_fm: totalStoresFm,
        fm_per_store: fmPerStore,
        fm_dist: [
          { name: 'Nguyễn Đức Hoà', count: 24, amount: 24 * fmPerStore, pct: 24 / 36 },
          { name: 'Nguyễn Thị Thanh Thủy', count: 7, amount: 7 * fmPerStore, pct: 7 / 36 },
          { name: 'Não Thị Anh Đào', count: 3, amount: 3 * fmPerStore, pct: 3 / 36 },
          { name: 'Kim Hoàng Khang', count: 1, amount: 1 * fmPerStore, pct: 1 / 36 },
          { name: 'Chưa phân bổ nhân sự (Căn 03 Marina Swanbay)', count: 1, amount: 1 * fmPerStore, pct: 1 / 36 }
        ],
        total_ck_stores_system: totalCkStoresSystem,"""

if old_processed_rep in idx_content:
    idx_content = idx_content.replace(old_processed_rep, new_processed_rep)
    print("Attached fm_hubs & fm_dist to processedReportData in index.html")

# H. In captureCurrentSheet & captureAndSendToZalo:
idx_content = idx_content.replace(
    "} else if (sheetKey === 'tabBhxHubs') {",
    """} else if (sheetKey === 'tabBhxHubs') {
        containerId = 'bhxHubsTableContainer';
        baseName = 'Doanh_So_5_Hubs_BHX';
        subTitle = 'Doanh Số Thực Tế 5 Hubs Bách Hóa Xanh (XH4001)';
      } else if (sheetKey === 'tabFmDist') {
        containerId = 'fmDistTableContainer';
        baseName = 'Phan_Bo_FamilyMart_Team';
        subTitle = 'Bảng Phân Bổ Doanh Số 6 Hubs FamilyMart (36 Cửa Hàng)';
      } else if (sheetKey === 'tabFmHubs') {
        containerId = 'fmHubsTableContainer';
        baseName = 'Doanh_So_6_Hubs_FamilyMart';
        subTitle = 'Doanh Số Thực Tế 6 Hubs FamilyMart (Toàn Hệ Thống 196 CH)';"""
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_content)
print("Updated index.html successfully")

# 5. SYNC ASSETS TO ANDROID
android_www = 'android/app/src/main/assets/www'
for fn in ['index.html', 'view.html', 'master_data.js']:
    src = fn
    dst = os.path.join(android_www, fn)
    shutil.copy2(src, dst)
    print(f"Synced {src} -> {dst}")

# 6. BUMP version.json TO v1.3.1 (Code 32)
with open('version.json', 'r', encoding='utf-8') as f:
    v_data = json.load(f)

v_data['version_name'] = '1.3.1'
v_data['version_code'] = 32
v_data['release_date'] = '14/10/2026'
v_data['changelog'] = [
    "Cập nhật số lượng BHX hệ thống lên 240 CH (căn cứ FORM CHI TIÊU PG T10).",
    "Đổi tab 'Chi Tiết SKU FamilyMart' thành 'Phân Bổ FamilyMart' chuẩn 6 Hubs & phân bổ 36 CH.",
    "Bỏ cột Địa Chỉ bảng CVS, khắc phục triệt để lỗi nhảy lệch số tiền sang cột địa chỉ."
]

with open('version.json', 'w', encoding='utf-8') as f:
    json.dump(v_data, f, ensure_ascii=False, indent=2)

shutil.copy2('version.json', os.path.join(android_www, 'version.json'))
print("Bumped version.json to v1.3.1 (Code 32) and synced to assets")

print("=== ALL UPDATES COMPLETED SUCCESSFULLY ===")
