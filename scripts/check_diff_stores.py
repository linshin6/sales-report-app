import sys, pyxlsb, json, re
sys.stdout.reconfigure(encoding='utf-8')

wb = pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb')
xlsb_cvs = []
with wb.get_sheet('FORM CHI TIEU PG') as sheet:
    rows = list(sheet.rows())
    for r_idx in range(7, len(rows)):
        v = [c.v for c in rows[r_idx]]
        if len(v) > 18 and v[18] and 'giang' in str(v[18]).lower():
            if v[5] != 'BÁCH HOÁ XANH':
                xlsb_cvs.append({
                    'employee_name': v[13],
                    'chain': v[5],
                    'store_code': str(v[7]) if v[7] is not None else '',
                    'store_address': str(v[10]) if v[10] is not None else str(v[11]),
                    'store_name': str(v[11]) if v[11] is not None else ''
                })

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'function getInitialStores\(\)\s*\{.*?return\s*(\[.*?\]);', text, re.DOTALL)
init_stores = json.loads(m.group(1))

init_set = {(s['employee_name'], s['store_code']) for s in init_stores}

diff = [s for s in xlsb_cvs if (s['employee_name'], s['store_code']) not in init_set]
print(f"Stores in XLSB T10 not in getInitialStores ({len(diff)} stores):")
for s in diff:
    print(f"  {s['employee_name']} | {s['chain']} | {s['store_code']} | {s['store_address'][:50]}")
