import json
import unicodedata
import re

ck_exact = {
    '373, Hồ Thị Hương': 6296004,
    'Số 22, Cách Mạng Tháng Tám': 6553904,
    'Số 78, Võ Thị Sáu': 3622608,
    '1347, Nguyễn Ái Quốc': 3458328,
    '144, Phan Trung': 6789156,
    '105, Lê Trọng Tấn': 8938196,
    'Số 174, Trần Văn Ơn': 5758788,
    'Số 508, Cách Mạng Tháng Tám': 5678088,
    'Ô 8, DC35': 3254928,
    '15, La Văn Cầu': 3865584,
    '1, Thùy Vân': 5186964,
    '1001, Bình Giã': 3576064,
    '103, Thùy Vân': 5358936,
    '117/21, Thùy Vân': 5662224,
    '126A1, Hoàng Hoa Thám': 5486064,
    '152, Hoàng Hoa Thám': 3636624,
    '18, Nguyễn Trường Tộ': 3875928,
    '186, Hoàng Hoa Thám': 4312176,
    '205, Nam Kỳ Khởi Nghĩa': 5825448,
    '26, Phan Văn Trị': 4448752,
    '273, Lê Hồng Phong': 7160064,
    '4, Lê Lợi': 3935928,
    '43, Thuỳ Vân': 3659184,
    '6, Quang Trung': 4770744,
    '78, Trần Hưng Đạo': 3526728,
    'Số 12 Khu Nhà DV 15 Tầng': 4133496,
    'Tầng 1, Chung Cư Kim Ngân': 5771376
}

# 1. Update index.html getInitialStores
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

m = re.search(r'function getInitialStores\(\)\s*\{\s*return\s*(\[.*?\]);', idx_content, re.DOTALL)
if m:
    stores = json.loads(m.group(1))
    found = 0
    for s in stores:
        if s.get('chain') == 'Circle K':
            addr_nfc = unicodedata.normalize('NFC', s.get('store_address', '')).lower()
            for k, v in ck_exact.items():
                k_nfc = unicodedata.normalize('NFC', k).lower()
                if k_nfc in addr_nfc:
                    s['actual'] = v
                    found += 1
                    break
    print('index.html getInitialStores matched:', found)
    new_stores_str = json.dumps(stores, ensure_ascii=False)
    idx_content = idx_content[:m.start(1)] + new_stores_str + idx_content[m.end(1):]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(idx_content)
    print('Updated index.html')

# 2. Update master_data.js
with open('master_data.js', 'r', encoding='utf-8') as f:
    md_content = f.read()

m2 = re.search(r'"stores":\s*(\[.*?\])(\s*,\s*"\w+"|\s*\})', md_content, re.DOTALL)
if m2:
    stores2 = json.loads(m2.group(1))
    found2 = 0
    for s in stores2:
        if s.get('chain') == 'Circle K':
            addr_nfc = unicodedata.normalize('NFC', s.get('store_address', '')).lower()
            for k, v in ck_exact.items():
                k_nfc = unicodedata.normalize('NFC', k).lower()
                if k_nfc in addr_nfc:
                    s['actual'] = v
                    found2 += 1
                    break
    print('master_data.js matched:', found2)
    new_stores2_str = json.dumps(stores2, ensure_ascii=False, indent=2)
    md_content = md_content[:m2.start(1)] + new_stores2_str + md_content[m2.end(1):]
    with open('master_data.js', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('Updated master_data.js')

with open('MasterData.gs', 'r', encoding='utf-8') as f:
    gs_content = f.read()
m3 = re.search(r'"stores":\s*(\[.*?\])(\s*,\s*"\w+"|\s*\})', gs_content, re.DOTALL)
if m3:
    gs_content = gs_content[:m3.start(1)] + new_stores2_str + gs_content[m3.end(1):]
    with open('MasterData.gs', 'w', encoding='utf-8') as f:
        f.write(gs_content)
    print('Updated MasterData.gs')
