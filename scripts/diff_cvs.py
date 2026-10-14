import sys, pyxlsb, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Read XLSB stores
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
                    'store_name': str(v[11]) if v[11] is not None else '',
                    'target': float(v[19]) if v[19] is not None else 0.0
                })

print("XLSB CVS stores:", len(xlsb_cvs))

# Read master_data.js stores
with open('master_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('"stores": [')
end_pos = text.find('],', pos)
js_stores = json.loads(text[pos+10:end_pos+1])
print("master_data.js stores:", len(js_stores))

# Compare by (employee_name, store_code or address)
js_codes = {s.get('store_code') for s in js_stores if s.get('store_code')}
xlsb_codes = {s.get('store_code') for s in xlsb_cvs if s.get('store_code')}

print(f"XLSB codes: {len(xlsb_codes)}, JS codes: {len(js_codes)}")
in_xlsb_not_js = [s for s in xlsb_cvs if s.get('store_code') and s.get('store_code') not in js_codes]
print("In XLSB but not in JS:", len(in_xlsb_not_js))
for s in in_xlsb_not_js:
    print("  +", s['employee_name'], s['chain'], s['store_code'], s['store_address'][:50])

in_js_not_xlsb = [s for s in js_stores if s.get('store_code') and s.get('store_code') not in xlsb_codes]
print("In JS but not in XLSB:", len(in_js_not_xlsb))
for s in in_js_not_xlsb:
    print("  -", s['employee_name'], s['chain'], s['store_code'], s['store_address'][:50])
