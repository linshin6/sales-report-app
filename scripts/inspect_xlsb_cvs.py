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
                    'store_name': str(v[11]) if v[11] is not None else '',
                    'target': float(v[19]) if v[19] is not None else 0.0
                })

print("Total XLSB CVS:", len(xlsb_cvs))
by_emp = {}
for s in xlsb_cvs:
    by_emp[s['employee_name']] = by_emp.get(s['employee_name'], 0) + 1

for e, c in sorted(by_emp.items()):
    print(f"  {e}: {c} stores")
