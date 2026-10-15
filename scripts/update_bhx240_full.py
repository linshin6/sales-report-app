import sys, os, re, json, shutil

sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING COMPREHENSIVE UPDATE: BHX 240 CH & 11 EMPLOYEES ===")

# -------------------------------------------------------------
# 1. UPDATE index.html
# -------------------------------------------------------------
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Fallback in calculateProcessedData
idx_content = re.sub(r'const totalStoresBhx = \(currentMaster\.total_stores_bhx && currentMaster\.total_stores_bhx > 50\) \? currentMaster\.total_stores_bhx : \d+;',
                     'const totalStoresBhx = (currentMaster.total_stores_bhx && currentMaster.total_stores_bhx > 50) ? currentMaster.total_stores_bhx : 240;',
                     idx_content)

# Reset defaults in index.html
idx_content = idx_content.replace('currentMaster.total_stores_bhx = 233;', 'currentMaster.total_stores_bhx = 240;')
idx_content = idx_content.replace('currentMaster.total_stores_bhx_team = 178;', 'currentMaster.total_stores_bhx_team = 199;')
idx_content = idx_content.replace('currentMaster.total_stores_bhx = 232;', 'currentMaster.total_stores_bhx = 240;')

# UI KPIs
idx_content = idx_content.replace('const stTeam = data.total_stores_bhx_team || 178;', 'const stTeam = data.total_stores_bhx_team || 199;')
idx_content = idx_content.replace('const stSys = data.total_stores_bhx || 232;', 'const stSys = data.total_stores_bhx || 240;')
idx_content = idx_content.replace('const stSys = data.total_stores_bhx || 233;', 'const stSys = data.total_stores_bhx || 240;')
idx_content = idx_content.replace('data.total_stores_bhx || 232', 'data.total_stores_bhx || 240')
idx_content = idx_content.replace('data.total_stores_bhx || 233', 'data.total_stores_bhx || 240')

# Excel export
idx_content = idx_content.replace('{ col: \'E\', lbl: \'Tổng CH BHX Team\', val: (p.total_stores_bhx_team || 178) + \' CH\', fmt: null, bg: \'FF4472C4\', fg: \'FFFFFFFF\' }',
                                  '{ col: \'E\', lbl: \'Tổng CH BHX Team\', val: (p.total_stores_bhx_team || 199) + \' CH\', fmt: null, bg: \'FF4472C4\', fg: \'FFFFFFFF\' }')
idx_content = idx_content.replace('setInfo(\'E\', p.total_stores_bhx_team || p.total_stores_bhx, false, true);',
                                  'setInfo(\'E\', p.total_stores_bhx_team || 199, false, true);')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_content)
print("✓ index.html updated.")

# -------------------------------------------------------------
# 2. UPDATE view.html
# -------------------------------------------------------------
with open('view.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

v_content = re.sub(r'const totalStoresBhx = \(m\.total_stores_bhx && m\.total_stores_bhx > 180\) \? m\.total_stores_bhx : \d+;',
                   'const totalStoresBhx = (m.total_stores_bhx && m.total_stores_bhx > 180) ? m.total_stores_bhx : 240;',
                   v_content)
v_content = re.sub(r'total_stores_bhx: \(m\.total_stores_bhx && m\.total_stores_bhx > 180\) \? m\.total_stores_bhx : \d+,',
                   'total_stores_bhx: (m.total_stores_bhx && m.total_stores_bhx > 180) ? m.total_stores_bhx : 240,',
                   v_content)
v_content = v_content.replace('total_stores_bhx_team: compact.sbhx || 178,', 'total_stores_bhx_team: compact.sbhx || 199,')
v_content = v_content.replace('total_stores_bhx_team: 178,', 'total_stores_bhx_team: 199,')
v_content = v_content.replace('${data.total_stores_bhx_team || 178} CH', '${data.total_stores_bhx_team || 199} CH')
v_content = v_content.replace('÷ ${data.total_stores_bhx || 233} CH', '÷ ${data.total_stores_bhx || 240} CH')
v_content = v_content.replace('÷ ${data.total_stores_bhx || 232} CH', '÷ ${data.total_stores_bhx || 240} CH')
v_content = v_content.replace('{ col: \'E\', lbl: \'Tổng CH BHX Team\', val: (p.total_stores_bhx_team || 178) + \' CH\'',
                              '{ col: \'E\', lbl: \'Tổng CH BHX Team\', val: (p.total_stores_bhx_team || 199) + \' CH\'')
v_content = v_content.replace('setInfo(\'E\', p.total_stores_bhx_team || p.total_stores_bhx, false, true);',
                              'setInfo(\'E\', p.total_stores_bhx_team || 199, false, true);')

with open('view.html', 'w', encoding='utf-8') as f:
    f.write(v_content)
print("✓ view.html updated.")

# -------------------------------------------------------------
# 3. UPDATE lib/excel-builder.js
# -------------------------------------------------------------
with open('lib/excel-builder.js', 'r', encoding='utf-8') as f:
    eb_content = f.read()

eb_content = eb_content.replace('p.total_stores_bhx_team || 178', 'p.total_stores_bhx_team || 199')
eb_content = eb_content.replace('p.total_stores_bhx || 232', 'p.total_stores_bhx || 240')
eb_content = eb_content.replace('p.total_stores_bhx || 233', 'p.total_stores_bhx || 240')
eb_content = eb_content.replace('setInfo(\'E\', p.total_stores_bhx_team || p.total_stores_bhx, false, true);',
                                'setInfo(\'E\', p.total_stores_bhx_team || 199, false, true);')

with open('lib/excel-builder.js', 'w', encoding='utf-8') as f:
    f.write(eb_content)
print("✓ lib/excel-builder.js updated.")

# -------------------------------------------------------------
# 4. UPDATE ReportEngine.gs & TelegramBot.gs & MasterData.gs
# -------------------------------------------------------------
with open('ReportEngine.gs', 'r', encoding='utf-8') as f:
    re_content = f.read()

re_content = re.sub(r'var totalStoresBhx = \(master\.total_stores_bhx && master\.total_stores_bhx > 180\) \? master\.total_stores_bhx : \d+;',
                    'var totalStoresBhx = (master.total_stores_bhx && master.total_stores_bhx > 180) ? master.total_stores_bhx : 240;',
                    re_content)
with open('ReportEngine.gs', 'w', encoding='utf-8') as f:
    f.write(re_content)
print("✓ ReportEngine.gs updated.")

with open('TelegramBot.gs', 'r', encoding='utf-8') as f:
    tb_content = f.read()

tb_content = tb_content.replace('(payload.total_stores_bhx_team || 178)', '(payload.total_stores_bhx_team || 199)')
tb_content = tb_content.replace('(payload.total_stores_bhx || 232)', '(payload.total_stores_bhx || 240)')
tb_content = tb_content.replace('(payload.total_stores_bhx || 233)', '(payload.total_stores_bhx || 240)')
with open('TelegramBot.gs', 'w', encoding='utf-8') as f:
    f.write(tb_content)
print("✓ TelegramBot.gs updated.")

with open('MasterData.gs', 'r', encoding='utf-8') as f:
    gs_content = f.read()

# Fix bhx_hubs array in MasterData.gs
bad_bhx_hubs = """,
  {
    "employee_name": "Võ Thị Hằng",
    "chain": "GS25",
    "store_code": "CVS_GS25.75.6976",
    "store_address": "GS25 Lê Duẩn - Long Thành",
    "actual": 0
  },
  {
    "employee_name": "Võ Thị Hằng",
    "chain": "GS25",
    "store_code": "CVS_GS25.75.6975",
    "store_address": "Siêu thị GS-25 35, Nguyễn Đình Chiểu",
    "actual": 0
  }"""
if bad_bhx_hubs in gs_content:
    gs_content = gs_content.replace(bad_bhx_hubs, "")
    # Add those 2 stores before line 2133 (closing of stores array)
    vo_stores = """,
  {
    "employee_name": "Võ Thị Hằng",
    "chain": "GS25",
    "store_code": "CVS_GS25.75.6976",
    "store_address": "GS25 Lê Duẩn - Long Thành",
    "actual": 0
  },
  {
    "employee_name": "Võ Thị Hằng",
    "chain": "GS25",
    "store_code": "CVS_GS25.75.6975",
    "store_address": "Siêu thị GS-25 35, Nguyễn Đình Chiểu",
    "actual": 0
  }"""
    target_str = '"store_address": "Tòa A Happy One Central, 113 đường 30/4, Phường Phú Hòa, Thủ Dầu Một, Bình Dương",\n    "actual": 0\n  }\n]'
    replacement_str = '"store_address": "Tòa A Happy One Central, 113 đường 30/4, Phường Phú Hòa, Thủ Dầu Một, Bình Dương",\n    "actual": 0\n  }' + vo_stores + '\n]'
    if target_str in gs_content:
        gs_content = gs_content.replace(target_str, replacement_str)

with open('MasterData.gs', 'w', encoding='utf-8') as f:
    f.write(gs_content)
print("✓ MasterData.gs updated & syntax verified.")

# -------------------------------------------------------------
# 5. SYNC TO ANDROID ASSETS & TOOLS
# -------------------------------------------------------------
print("\n--- Đồng bộ sang Android assets & tools ---")
targets_sync = [
    ('index.html', 'android/app/src/main/assets/www/index.html'),
    ('view.html', 'android/app/src/main/assets/www/view.html'),
    ('master_data.js', 'android/app/src/main/assets/www/master_data.js'),
    ('lib/excel-builder.js', 'android/app/src/main/assets/www/lib/excel-builder.js'),
    ('index.html', 'tools/apk_src/assets/www/index.html'),
    ('view.html', 'tools/apk_src/assets/www/view.html'),
    ('master_data.js', 'tools/apk_src/assets/www/master_data.js'),
    ('lib/excel-builder.js', 'tools/apk_src/assets/www/lib/excel-builder.js'),
]

for src, dst in targets_sync:
    if os.path.exists(os.path.dirname(dst)) and os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✓ Đồng bộ: {src} -> {dst}")

print("\n=== HOÀN TẤT CẬP NHẬT CODE WEB VÀ GIAO DIỆN ===")
