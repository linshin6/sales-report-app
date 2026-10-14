import json
import re
import sys
import pyxlsb

sys.stdout.reconfigure(encoding='utf-8')

# 1. Read Target T10 36 FM stores
t10_fm = []
with pyxlsb.open_workbook('HNTrinh Form Target PG_T10 2026 NDTRINH (1).xlsb') as wb:
    with wb.get_sheet('FORM CHI TIEU PG') as sheet:
        for r in sheet.rows():
            vals = [c.v for c in r]
            if len(vals) > 8 and vals[4] and str(vals[4]).startswith('FM'):
                t10_fm.append({
                    'code': str(vals[6]) if vals[6] else '',
                    'store_code': str(vals[7]) if vals[7] else '',
                    'addr': str(vals[10]) if len(vals) > 10 and vals[10] else '',
                    'location': str(vals[11]) if len(vals) > 11 and vals[11] else 'ST00_CVS_FM',
                    'ma_pg': str(vals[12]) if len(vals) > 12 and vals[12] else '',
                    'ten_pg': str(vals[13]) if len(vals) > 13 and vals[13] else '',
                    'vtcv': str(vals[14]) if len(vals) > 14 and vals[14] else 'SR',
                    'target': float(vals[19]) if len(vals) > 19 and vals[19] is not None else 0.0,
                    'actual': 3740855,
                    'actual_sales': 3740855
                })

print('Found Target T10 FM stores:', len(t10_fm))
for idx, s in enumerate(t10_fm):
    print(f"{idx+1}. {s['store_code']} | PG: {s['ten_pg']} | Addr: {s['addr']}")
