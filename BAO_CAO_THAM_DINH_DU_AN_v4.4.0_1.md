# BÁO CÁO THẨM ĐỊNH KỸ THUẬT & NGHIỆP VỤ
## DỰ ÁN: HỆ THỐNG BÁO CÁO DOANH SỐ CVS & BHX — TEAM CẨM GIANG
**Phiên bản thẩm định:** v4.4.0 (OTA Hybrid Edition)
**Ngày thẩm định:** 21/09/2026
**Phạm vi đối chiếu:** Tài liệu bàn giao (BAO_CAO_TU_DUY_LOGIC_DU_AN.txt) + mã nguồn thực tế (index.html ~9.113 dòng, master_data.js ~2.153 dòng)

---

## MỤC LỤC
1. Tóm tắt kết luận
2. Kiểm tra chéo số liệu (khớp / lệch)
3. Lỗi xác nhận trong mã nguồn (kèm số dòng)
4. Rủi ro kiến trúc & bảo mật
5. Trả lời 4 câu hỏi thẩm định trong tài liệu (Phần VI)
6. Điểm tích cực xác nhận được
7. Lộ trình hoàn thiện theo ưu tiên (P0/P1/P2)
8. Danh mục việc cần check lại với dự án (checklist)

---

## 1. TÓM TẮT KẾT LUẬN

| Hạng mục | Đánh giá |
|---|---|
| Kiến trúc tổng thể | ✅ Hợp lý cho bài toán (offline-first, serverless, chi phí ~0) |
| Dữ liệu danh mục | ✅ Cấu trúc sạch: 138 CH khớp chuẩn 70+34+27+5+2, không trùng mã nội bộ |
| Logic nghiệp vụ | ⚠️ Tốt ở tầng phân kênh & Dynamic SKU, nhưng có lỗi số học thật |
| Số học phân bổ | 🔴 Lỗi chia 72/70 GS25 — ảnh hưởng trực tiếp doanh thu báo cáo |
| Bảo mật chia sẻ | 🔴 Payload doanh thu gửi qua Bytebin (dịch vụ công cộng) + hash base64 không mã hóa |
| Đồng bộ dữ liệu | 🟠 Vẫn là đồng bộ thủ công 4 nơi (master_data.js / MasterData.gs / Excel / assets/www) |
| Hiệu năng mobile | 🟠 XLSX/XLSB parse trên main thread, KHÔNG có Web Worker (xác nhận 0 `new Worker`) |

---

## 2. KIỂM TRA CHÉO SỐ LIỆU

### 2.1. Các con số ĐÃ XÁC MINH KHỚP
- Thực đạt BHX + CVS: 3.551.927.443 + 359.247.028 = **3.911.174.471 ✓**
- % đạt: 3.911.174.471 / 10.826.339.729 = **36,1% ✓**
- Deficit Gap: 10.826.339.729 − 3.911.174.471 = **6.915.165.258 ✓**
- GS25 kho DC: 2.270.422 × 70 = **158.929.540 ✓** (nhưng mẫu số chia trong code là 72 → xem Lỗi 1)
- Circle K: 22 + 5 = **27 CH ✓**
- Tổng CVS: 70 + 34 + 27 + 5 + 2 = **138 CH ✓** (cấu trúc master_data.js khớp đúng)

### 2.2. Các con số BỊ LỆCH cần làm rõ
| Vị trí | Tài liệu | Mã nguồn | Chênh lệch |
|---|---|---|---|
| Target snapshot T9 (index.html:3620) | 10.826.339.729đ | 7.605.871.595đ / 178 CH BHX Team | Cần làm rõ: khác phạm vi (178 CH Team vs toàn hệ thống) hay sai số liệu |
| Số CH BHX hệ thống | 232–233 (không nhất quán trong chính tài liệu) | Code fallback dùng `232` (dòng 3485, 3915), ô nhập mặc định `233` (dòng 1750), nút khôi phục dùng `233` (dòng 3623) | 1 CH trên mẫu số ~4 tỷđ ≈ lệch ~17 triệu/CH |

---

## 3. LỖI XÁC NHẬN TRONG MÃ NGUỒN (THEO SỐ DÒNG)

### 🔴 Lỗi 1 (CRITICAL) — Chia GS25 cho 72 nhưng master chỉ có 70 cửa hàng
- **Vị trí:** index.html dòng 3987: `const gs25PerStore = Math.round((totalGs25Dcs * 0.2046) / 72);`
- **Xác minh:** Đếm trong master_data.js: `MASTER_DATA` chứa đúng **70** cửa hàng `"chain": "GS25"`.
- **Tác động:** Doanh số mỗi CH GS25 bị pha loãng ~2,8%; tổng phân bổ không khớp khi kiểm tra chéo.
- **Cách sửa:** Thay `/72` bằng biến `GS25_STORE_COUNT` xuất từ master; đồng thời đưa toàn bộ magic number (20,46%, 3,62%, 5) vào config.
- **Trạng thái:** ☐ Chưa sửa

### 🔴 Lỗi 2 (CRITICAL) — Cửa hàng không mã (store_code rỗng) mang doanh số thật
- **Vị trí:** master_data.js dòng 1347 (GS25, `"store_code": ""`, `"actual": 873680`, địa chỉ TP.HCM — ngoài địa bàn) và dòng 537 (FM, `"store_code": ""`).
- **Nghi vấn:** CH rỗng mã có actual **873.680đ đúng bằng** CH "170 Đường 30/4, TP. Biên Hòa" ở ngay trên (dòng 1341) → nghi là bản ghi trùng lặp.
- **Tác động:** Nguy cơ **cộng trùng 873.680đ** vào tổng doanh thu; CH rỗng mã không đối soát được.
- **Cách sửa:** Kiểm tra và xóa/khôi phục mã cho 2 bản ghi này; thêm validate "store_code rỗng" khi build.
- **Trạng thái:** ☐ Chưa sửa

### 🔴 Lỗi 3 (CRITICAL) — Circle K: không có đơn mát → mất cả kho khô (0đ)
- **Vị trí:** index.html dòng 4174: `actual = foundAmt > 0 ? (tCk + Math.round(foundAmt)) : 0;`
- **Tác động:** CH có nhập kho khô nhưng không phát sinh đơn mát trong kỳ bị ghi 0 → mất doanh thu cá thể.
- **Điểm cần xác minh thêm:** `tCk = Math.round(ckKhoKhoAmt / totalCkStoresSystem)` — cần kiểm tra `ckStoresSo` là "CH có đơn" hay "toàn bộ 27 CH" vì 2 cách chia cho kết quả khác nhau.
- **Cách sửa:** Điều kiện nhận kho khô = "có phát sinh đơn hàng BẤT KỲ", không chỉ đơn mát.
- **Trạng thái:** ☐ Chưa sửa

### 🟠 Lỗi 4 (HIGH) — Chia sẻ báo cáo qua Bytebin (dịch vụ paste CÔNG CỘNG của bên thứ ba)
- **Vị trí:** index.html dòng 8385: `POST https://bytebin.lucko.me/post` → fallback Vercel `/api/report` → cuối cùng hash base64 `#d=...` (dòng 8407).
- **Tác động:** Payload chứa chỉ tiêu + doanh thu toàn team + danh sách 138 CH nằm trên máy chủ không kiểm soát, không expire, không xác thực. Hash base64 **không phải mã hóa** — ai có URL cũng đọc được và có thể sửa tay để giả mạo số liệu.
- **Cách sửa:** Bỏ bytebin; dùng GAS WebApp (đã có sẵn hạ tầng) làm short-link có token; thêm HMAC + expiry cho fallback hash.
- **Trạng thái:** ☐ Chưa sửa

### 🟠 Lỗi 5 (HIGH) — Parse XLSX/XLSB trên main thread, không có Web Worker
- **Vị trí:** index.html dòng 3164–3168, 3828–3838, 8925 (`FileReader` + `XLSX.read(data, {type:'array'})`). Toàn file **0 lần** xuất hiện `new Worker`.
- **Tác động:** File 10–15MB trên WebView máy yếu → ANR/OOM (khớp cảnh báo Câu hỏi 4 trong tài liệu — câu trả lời: CÓ, bắt buộc chuyển Web Worker).
- **Cách sửa:** Web Worker + truyền ArrayBuffer dạng Transferable (zero-copy); thêm progress bar và terminate khi user chọn file khác.
- **Trạng thái:** ☐ Chưa sửa

### 🟠 Lỗi 6 (HIGH) — Telegram Bot Token trong localStorage, gọi trực tiếp từ client
- **Vị trí:** index.html dòng 6288, 6379, 6403, 6451... (`localStorage.getItem('TELEGRAM_BOT_TOKEN')` + `fetch` thẳng `api.telegram.org`).
- **Tác động:** Ai đụng máy / bất kỳ script nào trong WebView đều đọc được token.
- **Cách sửa:** Chuyển gửi Telegram về backend GAS (giữ token phía server).
- **Trạng thái:** ☐ Chưa sửa

### 🟡 Lỗi 7 (MEDIUM) — Snapshot target tháng 9 hardcode trong code + lệch số với tài liệu
- **Vị trí:** index.html dòng 3620–3629 (7.605.871.595đ / 178 CH / 233 CH).
- **Tác động:** Sang tháng 10 phải sửa code tay; con số lệch với tài liệu (10.826.339.729đ).
- **Cách sửa:** Chuyển snapshot theo tháng vào config/master hoặc load từ GAS; làm rõ 2 nguồn số liệu.
- **Trạng thái:** ☐ Chưa sửa

### 🟡 Lỗi 8 (MEDIUM) — master_data.js trộn cấu trúc và dữ liệu kỳ
- **Vị trí:** master_data.js: 173 trường `"actual"` với số tiền cụ thể bake sẵn trong file danh mục.
- **Tác động:** Mỗi tháng phải regenerate cả master → tăng rủi ro lệch theo đúng Quy tắc Triple-Sync mà tài liệu đang lo (Phần V).
- **Cách sửa:** Tách `master_data.js` (danh mục) và `period_data.json` (số liệu kỳ).
- **Trạng thái:** ☐ Chưa sửa

### 🟡 Lỗi 9 (MEDIUM) — Số học làm tròn không khép kín
- **Vị trí:** index.html dòng 3987–3990 (`Math.round` mọi phép chia); ví dụ kho khô 430.620.084 / 230 = 1.872.261 (dư ~0,23đ × 230 CH ≈ 54đ không gán).
- **Cách sửa:** Gán phần dư chia cho 1 CH "seed"; quy toàn bộ tiền về số nguyên VND ngay khi đọc cell.
- **Trạng thái:** ☐ Chưa sửa

### 🟢 Lỗi 10 (LOW) — % Timegone thiếu quy ước mốc tính (off-by-one)
- Đầu tháng/cuối tháng lệch ~3% pacing nếu không rõ "đã chạy" tính có bao gồm hôm nay. Cần chuẩn hóa 1 công thức duy nhất.
- **Trạng thái:** ☐ Chưa sửa

### 🟢 Lỗi 11 (LOW) — Không có audit trail
- Báo cáo sống dưới dạng link/ảnh Zalo, không có snapshot lịch sử → không đối soát "tháng trước tính bao nhiêu". GAS đã có hạ tầng, chỉ cần lưu 1 hàng JSON/snapshot vào Google Sheet mỗi lần xuất.
- **Trạng thái:** ☐ Chưa sửa

---

## 4. RỦI RO KIẾN TRÚC & BẢO MẬT (TỔNG HỢP)

1. **Đồng bộ thủ công 4 nơi** (master_data.js / MasterData.gs / Excel Config / assets/www) — vẫn chưa có Single Source of Truth. Khuyến nghị: 1 file `master_config.json` + script pre-build sinh tự động cả 3 định dạng + CI guard fail build nếu file sinh ra không khớp.
2. **OTA không verify checksum** — `version.json` nên thêm `apkSha256`; AppUpdateManager tính hash sau khi tải trước khi cài. Nâng Target SDK và test lại luồng cài đặt trên Android 14/15.
3. **Keystore/secrets trong repo** — `push_to_github.bat` dùng `git add .`; cần `.gitignore` chặt (keystore, *.jks, local.properties, token).
4. **html2canvas scale:2 trên bảng dài** — nguy cơ vượt giới hạn texture WebView (~4096px) ra ảnh trắng/cropped; giảm scale 1.5 hoặc chụp theo khối.

---

## 5. TRẢ LỜI 4 CÂU HỎI THẨM ĐỊNH (PHẦN VI CỦA TÀI LIỆU)

**Câu 1 — Phân bổ kho DC GS25 & 7E (tỷ lệ cố định rồi chia đều):**
Chấp nhận được trong giới hạn dữ liệu, nhưng (a) phải sửa lỗi chia 72/70 trước — nó làm sai chính tỷ lệ nền; (b) nâng cấp tiếp: thêm trọng số quy mô cửa hàng (diện tích/SKU count) thay vì chia đều.

**Câu 2 — Kho khô Circle K "chia đều có điều kiện":**
An toàn hơn phân bổ theo tỷ trọng hàng mát (không phạt CH bán mát tốt), nhưng đang có lỗ hổng 0đ cho CH không có đơn mát (Lỗi 3). Chuẩn hơn: chia theo tỷ trọng TỔNG đơn hàng (mát + khô), điều kiện = có đơn bất kỳ.

**Câu 3 — Single Source of Truth:**
Đúng định hướng: `master_config.json` → pre-build script sinh master_data.js + MasterData.gs + Sheet Config (openpyxl) → script so hash, fail build nếu file không khớp. Biến Quy tắc Triple-Sync từ "kỷ luật con người" thành "bất biến máy móc".

**Câu 4 — OOM khi giải mã XLSB trong WebView:**
**CÓ, rủi ro thật** — đã xác nhận trong code: 0 Web Worker, parse trực tiếp main thread. Bắt buộc chuyển Web Worker; bổ sung cảnh báo file >25MB; lưu ý điểm tử vong thứ 2 là html2canvas scale:2 trên bảng dài.

---

## 6. ĐIỂM TÍCH CỰC XÁC NHẬN ĐƯỢC

1. Dữ liệu danh mục 138 CH khớp chuẩn, không trùng mã nội bộ trong MASTER_DATA, đủ 7 kênh kể cả WMP giữ chỗ 0đ.
2. Cơ chế chia sẻ đa tầng có suy nghĩ (Vercel → bytebin → hash offline) — ý tưởng đúng, chỉ sai lựa chọn bytebin.
3. Dynamic SKU Auto-Discovery chống mất doanh thu khi có mã hàng mới — thiết kế đúng.
4. Offline-first thật sự: xlsx/exceljs/html2canvas bundle cục bộ, không phụ thuộc CDN runtime.
5. Format tiền `vi-VN` + `Math.round` nhất quán ở các phép gán actual.

---

## 7. LỘ TRÌNH HOÀN THIỆN THEO ƯU TIÊN

### P0 — Làm ngay (tuần này, chi phí thấp)
- [ ] Sửa `/72` → `/70` hoặc biến cấu hình (Lỗi 1)
- [ ] Xử lý 2 cửa hàng `store_code: ""` (Lỗi 2)
- [ ] Bỏ bytebin, đổi sang GAS short-link có token + HMAC/expiry cho hash (Lỗi 4)
- [ ] Sửa điều kiện Circle K 0đ (Lỗi 3)
- [ ] `.gitignore` keystore/secrets

### P1 — Trong tháng
- [ ] Web Worker cho parse XLSX/XLSB (Lỗi 5)
- [ ] Telegram token về backend GAS (Lỗi 6)
- [ ] Tách snapshot target tháng khỏi code + làm rõ lệch 7,6 tỷ vs 10,8 tỷ (Lỗi 7)
- [ ] Dựng Single Source of Truth + pre-build codegen + CI guard
- [ ] Số học tiền về số nguyên + gán phần dư chia (Lỗi 9)

### P2 — Quý tới
- [ ] Audit trail: GAS lưu snapshot mỗi báo cáo vào Google Sheet (Lỗi 11)
- [ ] Đưa `team_leader_report_v4.py` thành golden-file regression test trong CI
- [ ] OTA thêm SHA-256 verify + nâng Target SDK + test Android 14/15
- [ ] Tách `actual` khỏi master_data.js (Lỗi 8)

---

## 8. CHECKLIST CHECK LẠI VỚI DỰ ÁN

| # | Câu hỏi cần xác minh với team | Liên quan |
|---|---|---|
| 1 | CH GS25 `"store_code": ""` (actual 873.680đ, ĐC TP.HCM) là bản ghi thật hay trùng của CH 170 Đường 30/4 Biên Hòa? | Lỗi 2 |
| 2 | Tại sao mẫu số chia kho DC GS25 là 72 trong khi master chỉ có 70 CH? 2 CH còn lại gán cho ai? | Lỗi 1 |
| 3 | `ckStoresSo` trong tính `tCk` là "CH có đơn" hay "toàn bộ 27 CH"? | Lỗi 3 |
| 4 | Snapshot T9 7.605.871.595đ/178 CH khác tài liệu 10.826.339.729đ — khác phạm vi hay sai số liệu? | Lỗi 7 |
| 5 | 232 hay 233 là số CH BHX hệ thống chuẩn? | Lỗi 9 mục 2.2 |
| 6 | Khi nạp 2 lần cùng file Excel (hoặc file tuần 2 đè tuần 1), dữ liệu cộng dồn hay ghi đè? Cần kiểm tra handler drag & drop. | Idempotency |

---
*Báo cáo lập bằng thẩm định trực tiếp mã nguồn; mọi số dòng tham chiếu theo file index.html và master_data.js đã cung cấp.*
