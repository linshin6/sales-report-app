import sys, os, re, json, shutil
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("BẮT ĐẦU CẬP NHẬT 11 NHÂN VIÊN (VÕ THỊ HẰNG) VÀ TARGET THÁNG 10/2026")
print("=================================================================")

T10_EMPLOYEES = [
    { "name": "Bùi Thị Sen", "bhx_stores": 21, "target": 1224747376 },
    { "name": "Chắng Lý Quỳnh", "bhx_stores": 27, "target": 1553803206 },
    { "name": "Kim Hoàng Khang", "bhx_stores": 24, "target": 1439209643 },
    { "name": "Lê Thị Thùy Châu", "bhx_stores": 22, "target": 1347067397 },
    { "name": "Lê Trần Bá Kiện", "bhx_stores": 26, "target": 1490030916 },
    { "name": "Não Thị Anh Đào", "bhx_stores": 11, "target": 735943613 },
    { "name": "Nguyễn Đức Hoà", "bhx_stores": 0, "target": 300816749 },
    { "name": "Nguyễn Thanh Nhàn", "bhx_stores": 24, "target": 1427158977 },
    { "name": "Nguyễn Thị Thanh Thủy", "bhx_stores": 6, "target": 543282274 },
    { "name": "Phạm Thị Kim Nhung", "bhx_stores": 20, "target": 1230123482 },
    { "name": "Võ Thị Hằng", "bhx_stores": 18, "target": 1007529600 }
]

TOTAL_TARGET = sum(e['target'] for e in T10_EMPLOYEES) # 12,299,713,232
TOTAL_BHX_TEAM = sum(e['bhx_stores'] for e in T10_EMPLOYEES) # 199
print(f"Tổng Target: {TOTAL_TARGET:,.0f} đ | Tổng CH BHX Team: {TOTAL_BHX_TEAM} | Số NV: {len(T10_EMPLOYEES)}")

# -------------------------------------------------------------
# 1. CẬP NHẬT index.html
# -------------------------------------------------------------
print("\n--- 1. Cập nhật index.html ---")
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Replace DEFAULT_MASTER in index.html
emp_js_block = "[\n"
for e in T10_EMPLOYEES:
    emp_js_block += f"        {{ name: '{e['name']}', bhx_stores: {e['bhx_stores']}, target: {e['target']} }},\n"
emp_js_block = emp_js_block.rstrip(',\n') + "\n      ]"

# Replace month: 9 -> month: 10, total_stores_bhx_team: 199, employees: [...]
dm_pattern = r'const DEFAULT_MASTER\s*=\s*\{.*?\bemployees:\s*\[.*?\],\s*bhx_hubs:'
def dm_repl(match):
    s = match.group(0)
    s = re.sub(r'month:\s*\d+', 'month: 10', s)
    s = re.sub(r'total_stores_bhx_team:\s*\d+', f'total_stores_bhx_team: {TOTAL_BHX_TEAM}', s)
    s = re.sub(r'employees:\s*\[.*?\]', f'employees: {emp_js_block}', s, flags=re.DOTALL)
    return s

new_idx_content = re.sub(dm_pattern, dm_repl, idx_content, flags=re.DOTALL)
if new_idx_content != idx_content:
    print("✓ Đã cập nhật DEFAULT_MASTER trong index.html sang Tháng 10, 11 NV, 199 BHX.")
    idx_content = new_idx_content
else:
    print("! Không khớp regex DEFAULT_MASTER, thử thay thế chi tiết.")

# Replace UI strings
replacements_index = [
    ("Cho phép <strong>nạp file Target</strong> hoặc <strong>sửa chỉ tiêu 10 nhân viên</strong>.",
     "Cho phép <strong>nạp file Target</strong> hoặc <strong>sửa chỉ tiêu 11 nhân viên</strong>."),
    ("✏️ Sửa Nhanh Bảng Chỉ Tiêu (10 NV)", "✏️ Sửa Nhanh Bảng Chỉ Tiêu (11 NV)"),
    ("Tổng Chỉ Tiêu: 10,826,339,729 ₫ | 10 Nhân Viên | 178 CH BHX phụ trách",
     f"Tổng Chỉ Tiêu: {TOTAL_TARGET:,.0f} ₫ | 11 Nhân Viên | {TOTAL_BHX_TEAM} CH BHX phụ trách".replace(',', '.')),
    ("Tổng Chỉ Tiêu: 10,826,339,729 ₫ | 10 Nhân Viên | 197 CH BHX phụ trách",
     f"Tổng Chỉ Tiêu: {TOTAL_TARGET:,.0f} ₫ | 11 Nhân Viên | {TOTAL_BHX_TEAM} CH BHX phụ trách".replace(',', '.')),
    ("👥 Tiến Độ 10 Nhân Viên", "👥 Tiến Độ 11 Nhân Viên"),
    ("<!-- Tab 1: Tiến độ 10 Nhân Viên -->", "<!-- Tab 1: Tiến độ 11 Nhân Viên -->"),
    ("Tất cả nhân viên (10 NV)", "Tất cả nhân viên (11 NV)"),
    (">10 Nhân viên<", ">11 Nhân viên<"),
    ("Tất cả 10 nhân viên", "Tất cả 11 nhân viên"),
    ("✏️ Cập Nhật Chỉ Tiêu & Số Cửa Hàng BHX (10 Nhân Viên)", "✏️ Cập Nhật Chỉ Tiêu & Số Cửa Hàng BHX (11 Nhân Viên)"),
    ("cho toàn bộ 10 nhân viên không?", "cho toàn bộ 11 nhân viên không?"),
    ("// 3. Tab 1: Tiến độ 10 Nhân Viên", "// 3. Tab 1: Tiến độ 11 Nhân Viên"),
    ("Bảng Tiến Độ 10 Nhân Viên Toàn Team (BHX + CVS)", "Bảng Tiến Độ 11 Nhân Viên Toàn Team (BHX + CVS)"),
    ("Bảng Phân Bổ Doanh Số 5 Hubs Bách Hóa Xanh (10 NV)", "Bảng Phân Bổ Doanh Số 5 Hubs Bách Hóa Xanh (11 NV)"),
    ("(10 Nhân Viên)", "(11 Nhân Viên)"),
    ("1/4. Bảng Tiến Độ 10 Nhân Viên Toàn Team (BHX + CVS)", "1/4. Bảng Tiến Độ 11 Nhân Viên Toàn Team (BHX + CVS)"),
    ("3/4. Bảng Phân Bổ Doanh Số 5 Hubs Bách Hóa Xanh (10 NV)", "3/4. Bảng Phân Bổ Doanh Số 5 Hubs Bách Hóa Xanh (11 NV)"),
    ("Toàn bộ 10 nhân sự đã được áp dụng target chuẩn!", "Toàn bộ 11 nhân sự đã được áp dụng target chuẩn!")
]

for old, new in replacements_index:
    idx_content = idx_content.replace(old, new)

# Update cache check around line 9012
idx_content = re.sub(r'parsed\.month !== \d+', 'parsed.month !== 10', idx_content)
idx_content = re.sub(r'parsed\.employees\.length < \d+', 'parsed.employees.length < 11', idx_content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_content)
print("✓ index.html đã được ghi đè thành công.")

# -------------------------------------------------------------
# 2. CẬP NHẬT view.html
# -------------------------------------------------------------
print("\n--- 2. Cập nhật view.html ---")
with open('view.html', 'r', encoding='utf-8') as f:
    view_content = f.read()

replacements_view = [
    ('<span class="header-badge" id="headerTeamSize">👥 10 Nhân viên</span>',
     '<span class="header-badge" id="headerTeamSize">👥 11 Nhân viên</span>'),
    ('<div class="kpi-value" style="color:#2563EB;" id="kpiStores">10 NV</div>',
     '<div class="kpi-value" style="color:#2563EB;" id="kpiStores">11 NV</div>'),
    ('<button class="tab-btn active" onclick="switchTab(\'tabTeam\')">📊 1. Tiến Độ 10 Nhân Viên</button>',
     '<button class="tab-btn active" onclick="switchTab(\'tabTeam\')">📊 1. Tiến Độ 11 Nhân Viên</button>'),
    ('Bảng Tiến Độ 10 Nhân Viên Toàn Team (BHX + CVS)',
     'Bảng Tiến Độ 11 Nhân Viên Toàn Team (BHX + CVS)'),
    ('<!-- TAB 1: TIẾN ĐỘ 10 NHÂN VIÊN -->', '<!-- TAB 1: TIẾN ĐỘ 11 NHÂN VIÊN -->'),
    ('<!-- BẢNG 2: PHÂN BỔ BHX THEO NHÂN VIÊN (10 NV) -->', '<!-- BẢNG 2: PHÂN BỔ BHX THEO NHÂN VIÊN (11 NV) -->'),
    ('Tất cả 10 nhân viên', 'Tất cả 11 nhân viên'),
    ('Target 10 Nhân viên', 'Target 11 Nhân viên'),
    ('10 NV • ${(data.stores && data.stores.length)', '11 NV • ${(data.stores && data.stores.length)'),
    ('Bảng Tiến Độ 10 Nhân Viên Toàn Team', 'Bảng Tiến Độ 11 Nhân Viên Toàn Team'),
    ('CHO 10 NHÂN VIÊN TỪ FORM CHI TIÊU', 'CHO 11 NHÂN VIÊN TỪ FORM CHI TIÊU'),
    ('(10 Nhân Viên)', '(11 Nhân Viên)')
]

for old, new in replacements_view:
    view_content = view_content.replace(old, new)

with open('view.html', 'w', encoding='utf-8') as f:
    f.write(view_content)
print("✓ view.html đã được cập nhật thành công.")

# -------------------------------------------------------------
# 3. CẬP NHẬT master_data.js
# -------------------------------------------------------------
print("\n--- 3. Cập nhật master_data.js ---")
with open('master_data.js', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Replace employees in master_data.js
emp_json_str = json.dumps(T10_EMPLOYEES, ensure_ascii=False, indent=4)
md_content = re.sub(r'"employees":\s*\[.*?\]\s*,\s*"stores":', f'"employees": {emp_json_str},\n  "stores":', md_content, flags=re.DOTALL)
md_content = re.sub(r'"total_stores_bhx_team":\s*\d+', f'"total_stores_bhx_team": {TOTAL_BHX_TEAM}', md_content)

with open('master_data.js', 'w', encoding='utf-8') as f:
    f.write(md_content)
print("✓ master_data.js đã được cập nhật thành công.")

# -------------------------------------------------------------
# 4. CẬP NHẬT MasterData.gs
# -------------------------------------------------------------
print("\n--- 4. Cập nhật MasterData.gs ---")
with open('MasterData.gs', 'r', encoding='utf-8') as f:
    gs_content = f.read()

gs_content = re.sub(r'"employees":\s*\[.*?\]\s*,\s*"stores":', f'"employees": {emp_json_str},\n  "stores":', gs_content, flags=re.DOTALL)
gs_content = re.sub(r'"total_stores_bhx_team":\s*\d+', f'"total_stores_bhx_team": {TOTAL_BHX_TEAM}', gs_content)

with open('MasterData.gs', 'w', encoding='utf-8') as f:
    f.write(gs_content)
print("✓ MasterData.gs đã được cập nhật thành công.")

# -------------------------------------------------------------
# 5. CẬP NHẬT api/webhook.js & render.html & TelegramBot.gs
# -------------------------------------------------------------
print("\n--- 5. Cập nhật api/webhook.js, render.html, TelegramBot.gs ---")
with open('api/webhook.js', 'r', encoding='utf-8') as f:
    wh_content = f.read()
wh_content = wh_content.replace('10 Nhân Viên', '11 Nhân Viên')
wh_content = wh_content.replace('10 Nhân viên', '11 Nhân viên')
wh_content = wh_content.replace('10 NV', '11 NV')
with open('api/webhook.js', 'w', encoding='utf-8') as f:
    f.write(wh_content)

with open('render.html', 'r', encoding='utf-8') as f:
    rd_content = f.read()
rd_content = rd_content.replace('10 Nhân viên', '11 Nhân viên')
rd_content = rd_content.replace('10 Nhân Viên', '11 Nhân Viên')
rd_content = rd_content.replace('10 NV', '11 NV')
with open('render.html', 'w', encoding='utf-8') as f:
    f.write(rd_content)

with open('TelegramBot.gs', 'r', encoding='utf-8') as f:
    tb_content = f.read()
tb_content = tb_content.replace('Top 10 nhân viên', 'Top 11 nhân viên')
with open('TelegramBot.gs', 'w', encoding='utf-8') as f:
    f.write(tb_content)
print("✓ api/webhook.js, render.html, TelegramBot.gs đã được cập nhật.")

# -------------------------------------------------------------
# 6. CẬP NHẬT Team_CamGiang_Report.xlsx với Target T10
# -------------------------------------------------------------
print("\n--- 6. Cập nhật Team_CamGiang_Report.xlsx ---")
wb = openpyxl.load_workbook('Team_CamGiang_Report.xlsx')

# Update Config
ws_cfg = wb['Config']
ws_cfg['B5'] = "10/2026"
ws_cfg['B10'] = 11

# Update Tiến độ Team
ws_td = wb['Tiến độ Team']
t10_map = {e['name']: e for e in T10_EMPLOYEES}

for r in range(7, 18):
    emp_name = ws_td.cell(r, 3).value
    if emp_name in t10_map:
        ws_td.cell(r, 4).value = t10_map[emp_name]['target']

# Update Dashboard ranking targets
ws_db = wb['Dashboard']
for r in range(13, 24):
    emp_name = ws_db.cell(r, 3).value
    if emp_name in t10_map:
        ws_db.cell(r, 4).value = t10_map[emp_name]['target']

# Update summary row 7 in Dashboard
ws_db.cell(7, 1).value = TOTAL_TARGET

wb.save('Team_CamGiang_Report.xlsx')
print("✓ Team_CamGiang_Report.xlsx đã cập nhật Target T10 cho 11 NV.")

# -------------------------------------------------------------
# 7. ĐỒNG BỘ SANG android/... VÀ tools/apk_src/...
# -------------------------------------------------------------
print("\n--- 7. Đồng bộ sang Android assets & tools ---")
targets_sync = [
    ('index.html', 'android/app/src/main/assets/www/index.html'),
    ('view.html', 'android/app/src/main/assets/www/view.html'),
    ('master_data.js', 'android/app/src/main/assets/www/master_data.js'),
    ('index.html', 'tools/apk_src/assets/www/index.html'),
    ('view.html', 'tools/apk_src/assets/www/view.html'),
    ('master_data.js', 'tools/apk_src/assets/www/master_data.js'),
]

for src, dst in targets_sync:
    if os.path.exists(os.path.dirname(dst)):
        shutil.copy2(src, dst)
        print(f"✓ Đồng bộ: {src} -> {dst}")

print("\n=================================================================")
print("HOÀN TẤT ĐỒNG BỘ 11 NHÂN VIÊN VÀ TARGET THÁNG 10!")
print("=================================================================")
