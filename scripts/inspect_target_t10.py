import sys, pyxlsb
sys.stdout.reconfigure(encoding='utf-8')

wb = pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb')

with wb.get_sheet('FORM CHI TIEU PG') as sheet:
    rows = list(sheet.rows())
    pg_summary = {}
    for r_idx in range(7, len(rows)):
        row = rows[r_idx]
        vals = [c.v for c in row]
        if len(vals) > 18:
            pg_code = vals[12]
            pg_name = vals[13]
            leader_code = vals[17]
            leader_name = vals[18]
            st_name = vals[5]
            store_code = vals[7]
            store_addr = vals[10]
            store_loc = vals[11]
            target = vals[19]
            status = vals[16]
            
            if leader_name and 'giang' in str(leader_name).lower():
                if pg_name not in pg_summary:
                    pg_summary[pg_name] = {
                        'code': pg_code,
                        'leader': leader_name,
                        'stores': [],
                        'chains': {}
                    }
                pg_summary[pg_name]['stores'].append({
                    'row': r_idx,
                    'st_name': st_name,
                    'store_code': store_code,
                    'store_addr': store_addr,
                    'store_loc': store_loc,
                    'target': target,
                    'status': status
                })
                pg_summary[pg_name]['chains'][st_name] = pg_summary[pg_name]['chains'].get(st_name, 0) + 1

    print('Total employees under Tran Thi Cam Giang:', len(pg_summary))
    total_all_target = 0
    total_bhx_stores = 0
    total_cvs_stores = 0
    for name, data in sorted(pg_summary.items()):
        stores = data['stores']
        total_tgt = sum(float(s['target']) for s in stores if s['target'] is not None)
        total_all_target += total_tgt
        bhx_count = data['chains'].get('BÁCH HOÁ XANH', 0)
        cvs_count = len(stores) - bhx_count
        total_bhx_stores += bhx_count
        total_cvs_stores += cvs_count
        code = data['code']
        chains_str = str(data['chains'])
        print(f"NV: {name} ({code}) | Tổng CH: {len(stores)} (BHX: {bhx_count}, CVS: {cvs_count}) | Target: {total_tgt:,.0f} đ")
        print(f"   Chains: {chains_str}")

    print(f"\n===> TOÀN TEAM: {len(pg_summary)} Nhân viên | Tổng Target: {total_all_target:,.0f} đ | Tổng BHX: {total_bhx_stores} CH | Tổng CVS: {total_cvs_stores} CH | Tổng CH: {total_bhx_stores + total_cvs_stores}")
