import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://bcgiang.vercel.app/api/report?id=latest'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

print('ok:', data.get('ok'), 'source:', data.get('source'))
d = data.get('data')
print('d type:', type(d))
if isinstance(d, dict):
    print('d keys:', list(d.keys()))
    payload = d.get('payload') if 'payload' in d else d
    print('payload keys:', list(payload.keys()))

    emps = payload.get('employees', [])
    print('Num employees:', len(emps))
    tot_gs25 = 0
    tot_fm = 0
    tot_all = 0
    for e in emps:
        tot_gs25 += e.get('gs25_actual', 0)
        tot_fm += e.get('fm_actual', 0)
        tot_all += e.get('total_actual', 0)
        print(e.get('name'), 'GS25:', e.get('gs25_actual', 0), 'FM:', e.get('fm_actual', 0), 'Total:', e.get('total_actual', 0))

    print('--- EMPLOYEES TOTAL ---')
    print('GS25:', tot_gs25)
    print('FM:', tot_fm)
    print('Total:', tot_all)

    stores = payload.get('stores', [])
    print('Num stores:', len(stores))
    by_chain = {}
    for s in stores:
        c = s.get('chain', 'unknown')
        val = s.get('actual') or s.get('actual_sales') or 0
        by_chain[c] = by_chain.get(c, 0) + val
    print('Stores by chain:', by_chain)
