import urllib.request, json
from collections import defaultdict

req = urllib.request.Request('https://bcgiang.vercel.app/api/report?id=latest', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    rep = data.get('data', {})

stores = rep.get('stores', [])
print('Total stores count in rep[stores]:', len(stores))

chain_sums = defaultdict(float)
chain_counts = defaultdict(int)
for s in stores:
    ch = s.get('chain', 'Unknown')
    act = s.get('actual', 0)
    chain_sums[ch] += act
    chain_counts[ch] += 1

print('\n--- Sums from rep[stores] ---')
for ch, val in chain_sums.items():
    print(f'{ch} ({chain_counts[ch]} CH): {val:,.0f}')

# Employee table sums
emps = rep.get('employees', [])
print('\n--- Sums from rep[employees] ---')
print('GS25:', f"{sum(e.get('gs25_actual',0) for e in emps):,.0f}")
print('FM:', f"{sum(e.get('fm_actual',0) for e in emps):,.0f}")
print('CK:', f"{sum(e.get('ck_actual',0) for e in emps):,.0f}")
print('SE:', f"{sum(e.get('se_actual',0) for e in emps):,.0f}")
print('HD:', f"{sum(e.get('hd_actual',0) for e in emps):,.0f}")

# FM SKU Matrix sums
fm_matrix = rep.get('fm_sku_matrix', {})
fm_matrix_stores = fm_matrix.get('stores', [])
print('\n--- FM SKU Matrix ---')
print('FM Matrix stores count:', len(fm_matrix_stores))
print('FM Matrix total_actual:', f"{fm_matrix.get('total_actual', 0):,.0f}")
print('FM Matrix sum of stores actual:', f"{sum(s.get('actual', 0) for s in fm_matrix_stores):,.0f}")
