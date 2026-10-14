# -*- coding: utf-8 -*-
import json
import shutil
import os

print("=== FIXING CVS STORE DISPLAY NAME ===")

# 1. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

old_idx_block = """        const displayName = (s.store_name && s.store_name !== 'undefined') ? s.store_name : (s.chain + (s.store_code ? (' - ' + s.store_code) : ''));

        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center" style="color:#64748B; font-weight:700;">${idx + 1}</td>
            <td class="text-center">${getChainBadgeLocal(s.chain)}</td>
            <td>${empCell}</td>
            <td><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600; color:#0F172A; max-width:380px; overflow:hidden; text-overflow:ellipsis;">${displayName}</td>
            <td class="text-right font-bold" style="color:#0F766E;">${formatNumber(s.actual)}</td>
          </tr>
        `;"""

new_idx_block = """        const storeDisplayName = (s.store_address || s.address || s.store_name || (s.chain + (s.store_code ? (' - ' + s.store_code) : ''))).trim();

        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center" style="color:#64748B; font-weight:700;">${idx + 1}</td>
            <td class="text-center">${getChainBadgeLocal(s.chain)}</td>
            <td>${empCell}</td>
            <td><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600; color:#0F172A; max-width:450px; overflow:hidden; text-overflow:ellipsis;" title="${storeDisplayName}">${storeDisplayName}</td>
            <td class="text-right font-bold" style="color:#0F766E;">${formatNumber(s.actual)}</td>
          </tr>
        `;"""

assert old_idx_block in idx_content, "old_idx_block not found in index.html"
idx_content = idx_content.replace(old_idx_block, new_idx_block)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_content)
print("Updated index.html: CVS store name restored to full descriptive name")

# 2. Update view.html
with open('view.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

old_v_block = """        const displayName = (s.store_name && s.store_name !== 'undefined')
          ? s.store_name
          : (s.chain + (s.store_code ? (' - ' + s.store_code.replace(/^CVS_[^.]+\.\d+\./, '')) : ''));
        const displayAddr = s.store_address || s.address || '';

        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center font-bold" style="color:#64748B;">${idx + 1}</td>
            <td class="text-center">${getCvsChainBadge(s.chain)}</td>
            <td>${empCell}</td>
            <td class="font-bold" style="color:#1E293B;"><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600;">${displayName}</td>
            <td class="text-right font-bold" style="color:#0F766E; font-size:13px;">${formatMoney(val)}</td>
          </tr>
        `;"""

new_v_block = """        const storeDisplayName = (s.store_address || s.address || s.store_name || (s.chain + (s.store_code ? (' - ' + s.store_code) : ''))).trim();

        tbody.innerHTML += `
          <tr ${isFirstOfEmp ? 'style="border-top:2px solid #0F766E; background:#FAFDFD;"' : ''}>
            <td class="text-center font-bold" style="color:#64748B;">${idx + 1}</td>
            <td class="text-center">${getCvsChainBadge(s.chain)}</td>
            <td>${empCell}</td>
            <td class="font-bold" style="color:#1E293B;"><code>${s.store_code || '-'}</code></td>
            <td style="font-weight:600; color:#0F172A; max-width:450px; overflow:hidden; text-overflow:ellipsis;" title="${storeDisplayName}">${storeDisplayName}</td>
            <td class="text-right font-bold" style="color:#0F766E; font-size:13px;">${formatMoney(val)}</td>
          </tr>
        `;"""

assert old_v_block in v_content, "old_v_block not found in view.html"
v_content = v_content.replace(old_v_block, new_v_block)

with open('view.html', 'w', encoding='utf-8') as f:
    f.write(v_content)
print("Updated view.html: CVS store name restored to full descriptive name")

# 3. Update version.json to v1.3.2 (Code 33)
with open('version.json', 'r', encoding='utf-8') as f:
    v_data = json.load(f)

v_data['latestVersionCode'] = 33
v_data['latestVersionName'] = "1.3.2"
v_data['version_code'] = 33
v_data['version_name'] = "1.3.2"
v_data['release_date'] = "14/10/2026"
v_data['releaseNotes'] = "✨ [BẢN CẬP NHẬT v1.3.2 - GIỮ NGUYÊN TÊN CỬA HÀNG CVS & CHUẨN CỘT BẢNG]\n• Giữ nguyên vẹn tên cửa hàng chi tiết (Số nhà, Tên đường, Điểm bán) ở cột 'TÊN CỬA HÀNG'.\n• Bỏ cột 'Địa Chỉ' thừa, đảm bảo toàn bộ số tiền Doanh Số nằm đúng cột chuẩn 100%."
v_data['changelog'] = [
    "Khôi phục tên cửa hàng chi tiết ở cột 'TÊN CỬA HÀNG' bảng CVS.",
    "Bỏ cột Địa Chỉ thừa, doanh số hiển thị chuẩn xác ở cột cuối cùng.",
    "Cập nhật BHX 240 CH và tab Phân Bổ FamilyMart chuẩn mô hình Bách Hóa Xanh."
]

with open('version.json', 'w', encoding='utf-8') as f:
    json.dump(v_data, f, ensure_ascii=False, indent=2)

# 4. Sync assets to android
android_www = 'android/app/src/main/assets/www'
for fn in ['index.html', 'view.html', 'master_data.js', 'version.json']:
    shutil.copy2(fn, os.path.join(android_www, fn))
    print(f"Synced {fn} -> {android_www}")

print("=== COMPLETED SCRIPT ===")
