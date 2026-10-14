import sys, pyxlsb
sys.stdout.reconfigure(encoding='utf-8')

wb = pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb')

with wb.get_sheet('FORM CHI TIEU PG') as sheet:
    rows = list(sheet.rows())
    cg_rows = []
    for r_idx in range(7, len(rows)):
        vals = [c.v for c in rows[r_idx]]
        if len(vals) > 18:
            leader_name = vals[18]
            if leader_name and 'giang' in str(leader_name).lower():
                cg_rows.append((r_idx, vals))

print(f"Total rows for Team Cam Giang in FORM CHI TIEU PG: {len(cg_rows)}")

# Let's group by PG
emp_data = {}
for r_idx, v in cg_rows:
    pg_code = v[12]
    pg_name = v[13]
    chain = v[5]
    store_code = v[7]
    store_name_loc = v[11]
    store_addr = v[10]
    target = float(v[19]) if v[19] is not None else 0.0
    
    if pg_name not in emp_data:
        emp_data[pg_name] = {
            'code': pg_code,
            'bhx_stores': [],
            'cvs_stores': [],
            'bhx_target': 0.0,
            'cvs_target': 0.0,
            'total_target': 0.0
        }
    
    st_info = {
        'chain': chain,
        'store_code': store_code,
        'store_name': store_name_loc,
        'address': store_addr,
        'target': target
    }
    
    if chain == 'BÁCH HOÁ XANH':
        emp_data[pg_name]['bhx_stores'].append(st_info)
        emp_data[pg_name]['bhx_target'] += target
    else:
        emp_data[pg_name]['cvs_stores'].append(st_info)
        emp_data[pg_name]['cvs_target'] += target
    
    emp_data[pg_name]['total_target'] += target

print(f"\n--- CHI TIẾT 11 NHÂN VIÊN THÁNG 10/2026 ---")
grand_bhx_stores = 0
grand_cvs_stores = 0
grand_bhx_target = 0.0
grand_cvs_target = 0.0
grand_total_target = 0.0

for name in sorted(emp_data.keys()):
    d = emp_data[name]
    bhx_count = len(d['bhx_stores'])
    cvs_count = len(d['cvs_stores'])
    total_count = bhx_count + cvs_count
    grand_bhx_stores += bhx_count
    grand_cvs_stores += cvs_count
    grand_bhx_target += d['bhx_target']
    grand_cvs_target += d['cvs_target']
    grand_total_target += d['total_target']
    
    print(f"NV: {name:<22} | Mã: {d['code']} | BHX: {bhx_count:>2} CH ({d['bhx_target']:>13,.0f} đ) | CVS: {cvs_count:>2} CH ({d['cvs_target']:>11,.0f} đ) | Tổng CH: {total_count:>2} | Tổng Target: {d['total_target']:>14,.0f} đ (làm tròn: {round(d['total_target']):>14,})")

print("-" * 105)
print(f"TỔNG CỘNG ({len(emp_data)} NV)        | BHX: {grand_bhx_stores:>2} CH ({grand_bhx_target:>13,.0f} đ) | CVS: {grand_cvs_stores:>2} CH ({grand_cvs_target:>11,.0f} đ) | Tổng CH: {grand_bhx_stores + grand_cvs_stores:>2} | Tổng Target: {grand_total_target:>14,.0f} đ (làm tròn: {round(grand_total_target):>14,})")
