import urllib.request, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://raw.githubusercontent.com/linshin6/sales-report-app/live-data/latest_report.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

stores = data.get('stores', [])
print(f"Total stores: {len(stores)}")

chains = {}
for s in stores:
    c = s.get('chain', 'unknown')
    val = s.get('actual') or s.get('actual_sales') or 0
    chains[c] = chains.get(c, 0) + val
print("Chains sum:", {k: f"{v:,} đ" for k, v in chains.items()})

emps = data.get('employees', [])
print("Employees sum:")
for e in emps:
    print(f"  {e['name']}: GS25={e.get('gs25_actual',0):,}, FM={e.get('fm_actual',0):,}, BHX={e.get('bhx_actual',0):,}, Tot={e.get('total_actual',0):,}")
