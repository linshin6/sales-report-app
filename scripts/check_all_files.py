import sys, re, json, glob
sys.stdout.reconfigure(encoding='utf-8')

print("=== CHECKING MASTER_DATA.JS ===")
with open('master_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract employees
emp_match = re.search(r'"employees":\s*(\[[^\]]+\])', text)
if emp_match:
    try:
        employees = json.loads(emp_match.group(1))
        print(f"master_data.js has {len(employees)} employees:")
        for e in employees:
            print(f"  - {e['name']}: {e.get('bhx_stores')} BHX, Target: {e.get('target'):,}")
    except Exception as ex:
        print("Error parsing employees:", ex)

# Check stores in master_data.js
stores_match = re.search(r'"stores":\s*(\[.*?\]),\s*"total_actual_bhx_hubs"', text, re.DOTALL)
if stores_match:
    try:
        stores = json.loads(stores_match.group(1))
        print(f"\nmaster_data.js has {len(stores)} CVS stores:")
        emp_stores = {}
        for s in stores:
            emp = s.get('employee_name')
            emp_stores[emp] = emp_stores.get(emp, 0) + 1
        for emp, cnt in emp_stores.items():
            print(f"  - {emp}: {cnt} stores")
    except Exception as ex:
        print("Error parsing stores:", ex)

print("\n=== CHECKING MASTERDATA.GS ===")
with open('MasterData.gs', 'r', encoding='utf-8') as f:
    gs_text = f.read()
print("Võ Thị Hằng in MasterData.gs:", "Võ Thị Hằng" in gs_text)
emp_gs = re.findall(r'name:\s*[\'"]([^\'"]+)[\'"]', gs_text)
print("Employees in MasterData.gs:", len(emp_gs), emp_gs)

print("\n=== CHECKING INDEX.HTML ===")
with open('index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

# Check DEFAULT_MASTER in index.html
dm_match = re.search(r'const DEFAULT_MASTER\s*=\s*(\{.*?\n\s*\};)', html_text, re.DOTALL)
if dm_match:
    print("Found DEFAULT_MASTER in index.html")
    for line in dm_match.group(1).splitlines():
        if 'name:' in line or 'total_stores' in line or 'bhx_stores' in line:
            print("  ", line.strip())

# Check getInitialStores or CVS stores in index.html
init_stores_match = re.search(r'function getInitialStores\(\)\s*\{.*?return\s*(\[.*?\]);', html_text, re.DOTALL)
if init_stores_match:
    try:
        init_stores = json.loads(init_stores_match.group(1))
        print(f"\nindex.html getInitialStores has {len(init_stores)} stores:")
        emp_stores = {}
        for s in init_stores:
            emp = s.get('employee_name')
            emp_stores[emp] = emp_stores.get(emp, 0) + 1
        for emp, cnt in emp_stores.items():
            print(f"  - {emp}: {cnt} stores")
    except Exception as ex:
        print("Error parsing getInitialStores:", ex)

print("\n=== CHECKING VIEW.HTML ===")
with open('view.html', 'r', encoding='utf-8') as f:
    view_text = f.read()
print("10 Nhân viên occurrences in view.html:", view_text.count("10 Nhân viên") + view_text.count("10 nhân viên") + view_text.count("10 Nhân Viên"))
print("11 Nhân viên occurrences in view.html:", view_text.count("11 Nhân viên") + view_text.count("11 nhân viên") + view_text.count("11 Nhân Viên"))
print("Võ Thị Hằng in view.html:", "Võ Thị Hằng" in view_text)
