import json
import re
import sys
import pyxlsb

sys.stdout.reconfigure(encoding='utf-8')

print("Starting FamilyMart Hubs Architecture Update...")

# 1. Load the 36 FM stores from Target T10
t10_fm_stores = []
with pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb') as wb:
    with wb.get_sheet('FORM CHI TIEU PG') as sheet:
        for r in sheet.rows():
            vals = [c.v for c in r]
            if len(vals) > 8 and vals[4] and str(vals[4]).startswith('FM'):
                pg = str(vals[13]).strip() if len(vals) > 13 and vals[13] else ''
                t10_fm_stores.append({
                    'code': str(vals[6]).strip() if vals[6] else '',
                    'store_code': str(vals[7]).strip() if vals[7] else '',
                    'addr': str(vals[10]).strip() if len(vals) > 10 and vals[10] else '',
                    'location': str(vals[11]).strip() if len(vals) > 11 and vals[11] else 'ST00_CVS_FM',
                    'ma_pg': str(vals[12]).strip() if len(vals) > 12 and vals[12] else '',
                    'ten_pg': pg if pg != 'None' else '',
                    'vtcv': str(vals[14]).strip() if len(vals) > 14 and vals[14] else 'SR',
                    'target': float(vals[19]) if len(vals) > 19 and vals[19] is not None else 0.0,
                    'actual': 3740855,
                    'actual_sales': 3740855
                })

print(f"Loaded {len(t10_fm_stores)} stores from Target T10.")

# 2. FamilyMart 6 Hubs Data
fm_hubs_data = [
    {"name": "125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh", "code": "PNTU", "amount": 543750},
    {"name": "18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM", "code": "PNTU", "amount": 141921000},
    {"name": "34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh", "code": "PNTU", "amount": 483600},
    {"name": "97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh", "code": "PNTU", "amount": 608100},
    {"name": "Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh", "code": "PNTU", "amount": 589017600},
    {"name": "G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh", "code": "PNTU", "amount": 633600}
]
total_fm_hubs_amount = sum(h["amount"] for h in fm_hubs_data)
per_store_fm = round(total_fm_hubs_amount / 196) # 3740855

# ==============================================================================
# A. UPDATE MASTER_DATA.JS
# ==============================================================================
print("Updating master_data.js...")
with open('master_data.js', 'r', encoding='utf-8') as f:
    mjs = f.read()

# Replace DEFAULT_FM_STORES
fm_stores_json = json.dumps(t10_fm_stores, ensure_ascii=False, indent=2)
mjs = re.sub(
    r'const DEFAULT_FM_STORES\s*=\s*\[.*?\];\s*const MASTER_DATA',
    f'const DEFAULT_FM_STORES = {fm_stores_json};\n\nconst MASTER_DATA',
    mjs,
    flags=re.DOTALL
)

# Convert 36 stores to cvs_stores format for MASTER_DATA.stores
cvs_fm_stores = []
for s in t10_fm_stores:
    cvs_fm_stores.append({
        "employee_name": s["ten_pg"] if s["ten_pg"] else "Chưa phân bổ",
        "chain": "FamilyMart",
        "store_code": s["store_code"],
        "store_address": s["addr"],
        "actual": per_store_fm
    })

# Replace FamilyMart stores in MASTER_DATA.stores
m_stores = re.search(r'"stores":\s*(\[.*?\]),\s*"bhx_hubs"', mjs, re.DOTALL)
if m_stores:
    all_stores = json.loads(m_stores.group(1))
    # Filter out old FamilyMart stores
    non_fm_stores = [st for st in all_stores if st.get('chain') != 'FamilyMart']
    # Add new 36 FM stores
    new_stores = non_fm_stores + cvs_fm_stores
    new_stores_json = json.dumps(new_stores, ensure_ascii=False, indent=2)
    mjs = mjs[:m_stores.start(1)] + new_stores_json + mjs[m_stores.end(1):]

# Add fm_hubs and config in MASTER_DATA
fm_hubs_json = json.dumps(fm_hubs_data, ensure_ascii=False, indent=2)
mjs = re.sub(
    r'"bhx_hubs":\s*\[',
    f'"total_stores_fm": 196,\n  "total_stores_fm_team": 36,\n  "fm_hubs": {fm_hubs_json},\n  "bhx_hubs": [',
    mjs,
    count=1
)

with open('master_data.js', 'w', encoding='utf-8') as f:
    f.write(mjs)

print("master_data.js updated successfully!")
