import sys, re
sys.stdout.reconfigure(encoding='utf-8')
with open('master_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'stores:\s*\[(.*?)\]\s*,?\s*fm_categories', text, re.DOTALL)
if not m:
    m = re.search(r'stores:\s*\[(.*?)\]\s*\}', text, re.DOTALL)

if m:
    stores_str = m.group(1)
    stores = re.findall(r'\{[^{}]*\}', stores_str)
    print('Total stores in MASTER_DATA:', len(stores))
    
    emp_chain = {}
    for s in stores:
        chain_m = re.search(r'chain:\s*["\']([^"\']+)["\']', s)
        emp_m = re.search(r'employee_name:\s*["\']([^"\']+)["\']', s)
        c = chain_m.group(1) if chain_m else '?'
        e = emp_m.group(1) if emp_m else '?'
        if e not in emp_chain: emp_chain[e] = {}
        emp_chain[e][c] = emp_chain[e].get(c, 0) + 1
    for e, cc in emp_chain.items():
        print(f'{e}: {cc}')
