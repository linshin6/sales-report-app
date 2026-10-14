import sys, pyxlsb, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Read CVS stores from XLSB
wb = pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb')
xlsb_cvs = []
with wb.get_sheet('FORM CHI TIEU PG') as sheet:
    rows = list(sheet.rows())
    for r_idx in range(7, len(rows)):
        vals = [c.v for c in rows[r_idx]]
        if len(vals) > 18:
            leader_name = vals[18]
            if leader_name and 'giang' in str(leader_name).lower():
                chain = vals[5]
                if chain != 'BÁCH HOÁ XANH':
                    xlsb_cvs.append({
                        'employee_name': vals[13],
                        'chain': chain,
                        'store_code': str(vals[7]) if vals[7] is not None else '',
                        'store_address': str(vals[10]) if vals[10] is not None else str(vals[11]),
                        'store_name': str(vals[11]) if vals[11] is not None else '',
                        'target': float(vals[19]) if vals[19] is not None else 0.0
                    })

print(f"XLSB CVS stores count: {len(xlsb_cvs)}")

# Read index.html getInitialStores
with open('index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

m = re.search(r'function getInitialStores\(\)\s*\{.*?return\s*(\[.*?\]);', html_text, re.DOTALL)
if m:
    init_stores = json.loads(m.group(1))
    print(f"index.html initial stores count: {len(init_stores)}")
    # Check if Vo Thi Hang is in init_stores
    vth_stores = [s for s in init_stores if s.get('employee_name') == 'Võ Thị Hằng']
    print(f"Vo Thi Hang in index.html getInitialStores: {len(vth_stores)} stores")
    for s in vth_stores:
        print("  ", s)

# Check master_data.js
with open('master_data.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

m_js = re.search(r'"stores":\s*(\[.*?\]),\s*"total_actual_bhx_hubs"', js_text, re.DOTALL)
if m_js:
    js_stores = json.loads(m_js.group(1))
    print(f"\nmaster_data.js stores count: {len(js_stores)}")
    vth_js = [s for s in js_stores if s.get('employee_name') == 'Võ Thị Hằng']
    print(f"Vo Thi Hang in master_data.js stores: {len(vth_js)} stores")
    for s in vth_js:
        print("  ", s)
else:
    print("Could not match stores in master_data.js with that regex, searching differently...")
    m_js2 = re.search(r'"stores":\s*(\[\s*\{.*?\}\s*\])\s*,\s*"fm_stores"', js_text, re.DOTALL)
    if not m_js2:
        # let's find "stores": [ up to ],\n  "
        pos = js_text.find('"stores": [')
        if pos != -1:
            end_pos = js_text.find('],', pos)
            stores_str = js_text[pos+10:end_pos+1]
            try:
                js_stores = json.loads(stores_str)
                print(f"master_data.js parsed stores count: {len(js_stores)}")
                vth_js = [s for s in js_stores if s.get('employee_name') == 'Võ Thị Hằng']
                print(f"Vo Thi Hang in master_data.js: {len(vth_js)} stores")
                for s in vth_js:
                    print("  ", s)
            except Exception as e:
                print("JSON error:", e)
