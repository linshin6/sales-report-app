import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://raw.githubusercontent.com/linshin6/sales-report-app/live-data/latest_report.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

# Read existing master_data.js up to const MASTER_DATA = {
with open('master_data.js', 'r', encoding='utf-8') as f:
    orig_code = f.read()

# FM_CATEGORIES is the first part
fm_categories_part = orig_code.split('const DEFAULT_FM_STORES = [')[0]

# Prepare updated DEFAULT_FM_STORES
fm_matrix = data.get('fm_sku_matrix', {})
fm_stores = fm_matrix.get('stores', [])
if not fm_stores:
    # fallback to stores with chain == 'FamilyMart'
    fm_stores = [s for s in data.get('stores', []) if s.get('chain') == 'FamilyMart']

fm_stores_json = json.dumps(fm_stores, ensure_ascii=False, indent=2)

# Prepare updated stores
stores = data.get('stores', [])
clean_stores = []
for s in stores:
    clean_stores.append({
        "employee_name": s.get("employee_name", ""),
        "chain": s.get("chain", ""),
        "store_code": s.get("store_code", ""),
        "store_address": s.get("store_address") or s.get("address", ""),
        "actual": s.get("actual") or s.get("actual_sales") or 0
    })
stores_json = json.dumps(clean_stores, ensure_ascii=False, indent=2)

# Prepare employees
employees = data.get('employees', [])
clean_employees = []
for e in employees:
    clean_employees.append({
        "name": e.get("name", ""),
        "bhx_stores": e.get("bhx_stores", 0),
        "target": e.get("target", 0)
    })
employees_json = json.dumps(clean_employees, ensure_ascii=False, indent=4)

# Build new master_data.js
new_code = fm_categories_part.strip() + "\n\nconst DEFAULT_FM_STORES = " + fm_stores_json + ";\n\n"
new_code += """const MASTER_DATA = {
  "team_lead": "Trần Thị Cẩm Giang",
  "total_stores_bhx": 233,
  "total_stores_bhx_team": 179,
  "employees": """ + employees_json + """,
  "stores": """ + stores_json + """,
  "bhx_hubs": [
    "Ấp 4, Xã Châu Pha, Thành phố Hồ Chí Minh, Việt Nam",
    "G243 Bùi Văn Hòa, Khu Phố 7, Phường Long Bình, Tỉnh Đồng Nai, Việt Nam",
    "Hub - Ấp 4, Xã Châu Pha, Thành phố Hồ Chí Minh, Việt Nam",
    "Hub - G243 Bùi Văn Hòa, Khu Phố 7, Phường Long Bình, Tỉnh Đồng Nai, Việt Nam",
    "Hub - Đường Phan Huy Chú, tổ 6, khu phố 1, Phường Phú Bình, Thành phố Long Khánh, Tỉnh Đồng Nai"
  ],
  "gs25_dcs": [
    "Lô H.04, Đường số 1, Khu Công Nghiệp Long Hậu, Xã Long Hậu, Huyện Cần Giuộc, Tỉnh Long An",
    "Lô IIIB2, Trung tâm thương mại Bình Điền, đường Nguyễn Văn Linh, Khu phố 06, Phường 07, Quận 08, Thành Phố Hồ Chí Minh"
  ],
  "se_dcs": [
    "BW Tân Phú Trung - Lô D2, Khu công nghiệp Tân Phú Trung, xã Tân Phú Trung, huyện Củ Chi, Thành phố Hồ Chí Minh",
    "Lô II-3 Nhóm CN II,Đường số 11,KCN Tân Bình,P.Tây Thạnh,Q.Tân Phú,Tp.HCM"
  ],
  "fm_categories": FM_CATEGORIES,
  "fm_stores": DEFAULT_FM_STORES,
  "wmp_stores": []
};

if (typeof module !== "undefined") module.exports = MASTER_DATA;
if (typeof window !== "undefined") {
  window.MASTER_DATA = MASTER_DATA;
  window.DEFAULT_MASTER = MASTER_DATA;
}
"""

with open('master_data.js', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("master_data.js updated successfully! Total stores:", len(clean_stores))
