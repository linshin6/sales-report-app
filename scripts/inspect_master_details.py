import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('master_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m_fm = re.search(r'const DEFAULT_FM_STORES\s*=\s*(\[.*?\]);', text, re.DOTALL)
if m_fm:
    fm_list = json.loads(m_fm.group(1))
    print('DEFAULT_FM_STORES count:', len(fm_list))
    emp_map = {}
    for st in fm_list:
        pg = st.get('ten_pg', 'None')
        emp_map[pg] = emp_map.get(pg, 0) + 1
    print('FM by ten_pg in DEFAULT_FM_STORES:', emp_map)

m_stores = re.search(r'"stores":\s*(\[.*?\]),\s*"bhx_hubs"', text, re.DOTALL)
if m_stores:
    stores = json.loads(m_stores.group(1))
    print('MASTER_DATA.stores count:', len(stores))
    chain_map = {}
    emp_map = {}
    for st in stores:
        c = st.get('chain', 'None')
        e = st.get('employee_name', 'None')
        chain_map[c] = chain_map.get(c, 0) + 1
        if e not in emp_map: emp_map[e] = {}
        emp_map[e][c] = emp_map[e].get(c, 0) + 1
    print('Stores by chain:', chain_map)
    print('Stores by employee and chain:')
    for e, chs in emp_map.items():
        print(f'  {e}: {chs} (Total: {sum(chs.values())})')
