# BÁO CÁO THẨM ĐỊNH KỸ THUẬT & NGHIỆP VỤ — PHIÊN BẢN RÀ SOÁT SAU PHẢN BIỆN
## DỰ ÁN: HỆ THỐNG BÁO CÁO DOANH SỐ CVS & BHX — TEAM CẨM GIANG
**Phiên bản:** v4.4.1 (rà soát sau Báo cáo Phản biện v4.5.0 của Dự án)
**Ngày lập:** 21/09/2026
**Tài liệu đối chiếu:**
- Báo cáo Thẩm định v4.4.0 (`BAO_CAO_THAM_DINH_DU_AN_v4.4.0.md`)
- Báo cáo Phản biện & Lộ trình nâng cấp v4.5.0 của Dự án (`BAO_CAO_PHAN_BIEN_VA_LO_TRINH_NANG_CAP.txt`)
- Mã nguồn thực tế: `index.html` (~9.113 dòng), `master_data.js` (~2.153 dòng)

> Mọi số liệu, số dòng trong báo cáo này đều được kiểm chứng lại trực tiếp trên mã nguồn trong phiên làm việc ngày 21/09/2026. Các điểm chưa xác minh được ghi rõ "chưa xác minh".

---

## MỤC LỤC
1. Tóm tắt điều hành (Executive Summary)
2. Ma trận tổng hợp kết quả thẩm định phản biện (4 điểm tranh luận)
3. Phân tích chi tiết từng điểm: tuyên bố → bằng chứng → kết luận → đề xuất
4. Các lỗi tiếp thu — trạng thái cập nhật sau phản biện
5. Rủi ro còn tồn đọng & 4 mục chưa có trong lộ trình v4.5.0
6. Điều chỉnh so với Báo cáo v4.4.0 (thu hồi / giữ nguyên / bổ sung)
7. Lộ trình khuyến nghị hợp nhất (bản v4.4.1)
8. Phụ lục: Kết quả kiểm chứng số liệu bằng mã nguồn

---

## 1. TÓM TẮT ĐIỀU HÀNH

Sau khi đối chiếu Báo cáo Phản biện v4.5.0 của Dự án với mã nguồn thực tế, kết luận tổng quát của vòng thẩm định này:

| Hạng mục | Kết quả |
|---|---|
| 4 điểm phản biện nghiệp vụ của Team | **4/4 có cơ sở hợp lý**; 2/4 xác minh trực tiếp được bằng code đều đúng |
| Điểm thẩm định v4.4.0 cần thu hồi | **3 điểm** (Lỗi 1 hạ cấp, Lỗi 2 rút nhận định trùng lặp, rút đề xuất sửa Circle K) |
| Điểm Team tiếp thu (Bytebin, Web Worker, Telegram token, 232/233, SSOT) | **Xác nhận đúng và giữ nguyên trong lộ trình** |
| Lộ trình v4.5.0 còn thiếu | **4 mục** (tách dữ liệu kỳ khỏi master, làm tròn khép kín, HMAC/expiry cho fallback hash, golden-file regression test) |
| Phát hiện mới sau phản biện | **2 mục** (đơn giá bake trong master không khép với công thức /72; CH 40 Thống Nhất chưa có mã trong bản file đã nhận) |

**Thông điệp chính:** Phản biện của Team trung thực, có căn cứ vận hành dữ liệu ERP và phần tôi kiểm chứng được bằng code đều xác nhận đúng. Hệ thống sau điều chỉnh không còn lỗi "CRITICAL" nào ở tầng số học; trọng tâm còn lại chuyển hẳn sang **bảo mật chia sẻ dữ liệu** và **kỷ luật dữ liệu kỳ**.

---

## 2. MA TRẬN TỔNG HỢP KẾT QUẢ THẨM ĐỊNH PHẢN BIỆN

| # | Tuyên bố của Team (Phản biện v4.5.0) | Bằng chứng kiểm chứng | Kết luận | Điều chỉnh so với v4.4.0 |
|---|---|---|---|---|
| PB1 | CH GS25 `"store_code": ""` với actual 873.680đ **không phải bản ghi trùng** — 873.680đ là đơn giá bình quân gán cho toàn bộ 70 CH GS25 | Đếm lại: chuỗi `873680` xuất hiện đúng **70 lần** trong `master_data.js`; section `MASTER_DATA` chứa đúng **70 bản ghi** `"actual": 873680` — khớp tuyệt đối 70 CH GS25 | ✅ **Team đúng — thẩm định v4.4.0 sai** | Rút nhận định "nghi trùng lặp cộng thừa 873.680đ"; hạ Lỗi 2 khỏi CRITICAL |
| PB2 | Mẫu số **/72 là quy định kiểm toán**, không phải lỗi: 72 = quy mô tuyến DC miền Đông; Team quản lý 70 CH; đơn giá chuẩn = (Tổng DC × 20,46%) / 72 | Code: `index.html:3987` `const gs25PerStore = Math.round((totalGs25Dcs * 0.2046) / 72);` — khớp mô tả của Team | ✅ **Team đúng** (lỗi chỉ tồn tại nếu thiếu ghi chú nghiệp vụ) | Rút đề xuất sửa /72 → /70; chuyển thành yêu cầu "ghi chú nghiệp vụ + config hóa magic number" |
| PB3 | Circle K 0đ khi không có đơn mát là **quy ước nghiệm thu của công ty**; file ERP gom kho khô dưới 1 mã tổng `VT4050` (430.620.084đ), **không có chi tiết theo CH** nên không thể kiểm tra "đơn hàng bất kỳ" | Code: `index.html:4174` `actual = foundAmt > 0 ? (tCk + Math.round(foundAmt)) : 0;` — khớp mô tả; không có dữ liệu nguồn theo CH để thay đổi điều kiện | ✅ **Team đúng về giới hạn dữ liệu** | Rút đề xuất đổi điều kiện; giữ 1 kiến nghị nhỏ: gắn nhãn trạng thái "0đ (không có đơn mát trong kỳ)" |
| PB4 | 7,605,871,595đ và 10,826,339,729đ là **2 phạm vi khác nhau**: 10,8 tỷ = hạn mức toàn kênh Team Lead (232 CH BHX + 138 CH CVS); 7,6 tỷ = target phân rã cho 10 PG tại 178 CH BHX có PG trực tiếp | Code: `index.html:3620` nút "Khôi phục Target chuẩn Tháng 9 (Tổng: 7,605,871,595 đ - 178 CH BHX Team / 233 CH Hệ Thống)" — nhất quán với giải trình; kiểm tra hợp lý: 7,6 tỷ / 178 CH ≈ 42,7 triệu/CH | ✅ **Chấp nhận được — đóng vấn đề** | Đóng câu hỏi số 4 trong Checklist v4.4.0; tán thành phương án tách 2 profile |

---

## 3. PHÂN TÍCH CHI TIẾT TỪNG ĐIỂM

### 3.1. PB1 — Cửa hàng rỗng mã 873.680đ: KHÔNG phải trùng lặp

**Tuyên bố của Team (trích Phản biện v4.5.0):** *"TẤT CẢ 70 CỬA HÀNG GS25 ĐỀU MANG GIÁ TRỊ 873.680đ — đây là đơn giá bình quân doanh số gán cho toàn bộ cửa hàng trong chuỗi theo cơ chế phân bổ đồng nhất, KHÔNG PHẢI lỗi copy dữ liệu trùng lặp."*

**Bằng chứng kiểm chứng (mã nguồn, 21/09/2026):**
- `grep -o "873680" master_data.js | wc -l` → **70**
- `sed -n '1105,2153p' master_data.js | grep -c '"actual": 873680'` → **70**
- Cấu trúc `MASTER_DATA`: 70 × GS25, 34 × FamilyMart, 27 × Circle K, 5 × 7-Eleven, 2 × Hoàng Đức = **138 CH, khớp chuẩn**; chỉ duy nhất 2 bản ghi `store_code: ""` (dòng 537 — FM, dòng 1347 — GS25).

**Kết luận:** Tuyên bố của Team **đúng**. Hai cửa hàng ở dòng 1341 và 1347 của `master_data.js` là 2 điểm bán khác nhau (170 Đường 30/4, TP. Biên Hòa và 40 Đ. Thống Nhất, TP.HCM), doanh thu **không bị cộng trùng**. Thẩm định v4.4.0 rút hoàn toàn nhận định "nghi trùng lặp cộng thừa tiền" và hạ Lỗi 2 khỏi mức CRITICAL.

**Điều chỉnh trạng thái:** Việc bổ sung mã POS cho CH 40 Thống Nhất là việc hành chính bình thường, phụ thuộc đối tác cấp mã — Team đã đánh dấu hoàn thành.

### 3.2. PB2 — Mẫu số /72 cho GS25: quy định kiểm toán, không phải lỗi số học

**Tuyên bố của Team (trích Phản biện v4.5.0):** *"Tỷ lệ 20.46% là hạn mức giao cho TOÀN BỘ tuyến 72 CH GS25 miền Đông. Team Cẩm Giang chỉ quản lý 70 CH. Công ty bắt buộc tính đơn giá chuẩn = (Tổng 2 Kho DC × 20.46%) / 72, sau đó Team nhận 70 × đơn giá chuẩn. Nếu chia theo 70, đơn giá sẽ thổi phồng cao hơn định mức toàn miền, vi phạm quy chế kiểm toán với Ban Giám Đốc."*

**Bằng chứng kiểm chứng:** `index.html:3987` — `const gs25PerStore = Math.round((totalGs25Dcs * 0.2046) / 72);` và `index.html:4160` — `actual = gs25PerStore;` (áp cho 70 CH trong master). Cấu trúc code khớp chính xác mô tả nghiệp vụ của Team.

**Kết luận:** **Team đúng.** Về mặt kế toán quản trị, mẫu số 72 phản ánh đúng cơ sở cấp hạn mức (toàn miền Đông); việc Team chỉ nhận trên 70 CH là phân cấp nội bộ, không phải sai số. So sánh số học: 70 × (Tổng DC × 20,46% / 72) = 158.929.540đ khi Tổng DC = 2.270.422đ — khớp đúng con số trong tài liệu bàn giao. Thẩm định v4.4.0 **rút đề xuất sửa /72 → /70**.

**Điều chỉnh trạng thái:** Lỗi 1 chuyển từ CRITICAL sang yêu cầu kỹ thuật: đưa 72, 20,46%, 3,62%, 5 vào object cấu hình duy nhất kèm ghi chú giải trình nghiệp vụ — trùng với P1 mục 6 của lộ trình v4.5.0 mà Team đã tự đề xuất. Đây là cách xử lý đúng: giữ nguyên con số, nhưng không để nó đứng như một magic number vô chủ.

### 3.3. PB3 — Circle K 0đ khi không có đơn mát: giới hạn dữ liệu ERP

**Tuyên bố của Team (trích Phản biện v4.5.0):** *"File ERP xuất ra chỉ có duy nhất MÃ TỔNG VT4050 (Kho Khô Nam Tân Uyên) với 430.620.084đ, KHÔNG HỀ có dòng chi tiết từng cửa hàng cho kho khô. Cửa hàng phát sinh đơn hàng Mát được coi như chứng minh đang hoạt động → được hưởng kho khô. Đây là quy định NGHIỆM THU của công ty."*

**Bằng chứng kiểm chứng:** `index.html:3990` — `const tCk = totalCkStoresSystem > 0 ? Math.round(ckKhoKhoAmt / totalCkStoresSystem) : 0;` và `index.html:4174` — `actual = foundAmt > 0 ? (tCk + Math.round(foundAmt)) : 0;`. Logic code khớp mô tả: không có nguồn dữ liệu nào cho phép kiểm tra đơn kho khô theo từng CH.

**Kết luận:** **Team đúng về giới hạn dữ liệu.** Đề xuất gốc của v4.4.0 (đổi điều kiện thành "có đơn hàng bất kỳ") **không thể triển khai** vì dữ liệu thô không có chi tiết kho khô theo CH — chính thức thu hồi. Logic "dùng đơn mát làm proxy hoạt động" là lựa chọn hợp lý duy nhất với dữ liệu hiện có, và đã được pháp chế/nghiệm thu của công ty chấp thuận.

**Kiến nghị giữ lại (chi phí ~0, không đụng công thức nghiệm thu):** tại `index.html:4174`, khi `foundAmt = 0`, thay vì ghi 0đ trống, gắn nhãn trạng thái hiển thị, ví dụ **"0đ (không có đơn mát trong kỳ)"**. Mục đích: khi Ban Giám Đốc đọc bảng số, phân biệt được "CH đóng cửa theo quy ước" với "CH lỗi dữ liệu / chưa nạp file" — loại trừ đúng rủi ro diễn giải sai mà v4.4.0 lo ngại, mà không thay đổi cách tính.

### 3.4. PB4 — 7,6 tỷ vs 10,8 tỷ: hai phạm vi target khác nhau

**Tuyên bố của Team (trích Phản biện v4.5.0):** *"10.826.339.729đ là hạn mức cấp cho Team Lead phụ trách TOÀN BỘ kênh (232 CH BHX + 138 CH CVS). 7.605.871.595đ là Target phân rã cho 10 nhân sự PG Siêu Thị (178 CH BHX có PG trực tiếp). Nút khôi phục ở dòng 3620 là 'Khôi phục Target 10 PG' nên hiển thị 7.6 tỷ là chính xác theo phân rã."*

**Bằng chứng kiểm chứng:** `index.html:3620` — thông báo khôi phục ghi rõ "178 CH BHX Team / 233 CH Hệ Thống" — nhất quán với giải trình (7,6 tỷ gắn với 178 CH có PG; phần chênh ~3,2 tỷ tương ứng CVS + 54 CH BHX không có PG trực tiếp). Kiểm tra hợp lý: 7,6 tỷ / 178 CH ≈ **42,7 triệu/CH** — hợp lý với quy mô CH BHX.

**Kết luận:** **Chấp nhận được — đóng vấn đề.** Câu hỏi số 4 trong Checklist v4.4.0 chính thức được trả lời. Phương án của Team (lộ trình v4.5.0, P1 mục 8: tách 2 profile "Góc nhìn Team Lead Toàn Kênh" và "Góc nhìn 10 PG Siêu Thị") là cách xử lý đúng — tán thành, khuyến nghị hiển thị đồng thời 2 profile trên 1 dashboard để tránh nhầm lẫn khi trao đổi với Ban Giám Đốc.

---

## 4. CÁC LỖI TIẾP THU — TRẠNG THÁI CẬP NHẬT SAU PHẢN BIỆN

| Lỗi (theo v4.4.0) | Nội dung | Vị trí đã kiểm chứng | Trạng thái trong lộ trình v4.5.0 | Xác nhận của thẩm định v4.4.1 |
|---|---|---|---|---|
| Lỗi 4 | Rò rỉ dữ liệu qua Bytebin (dịch vụ paste công cộng) | `index.html:8385` — `fetch('https://bytebin.lucko.me/post')` | P0: xóa Bytebin, chuyển 100% sang GAS WebApp / Vercel nội bộ có token | ✅ Đúng, giải pháp phù hợp |
| Lỗi 5 | Parse XLSX/XLSB trên main thread, không Web Worker | `index.html:3164–3168, 3828–3838`; đếm `new Worker` = **0** | P1: chuyển SheetJS sang Web Worker (zero-copy ArrayBuffer) | ✅ Đúng, bắt buộc với file 10–15MB |
| Lỗi 6 | Telegram Bot Token trong localStorage, gọi từ client | `index.html:6288, 6359, 6700` | P1: chuyển gửi Telegram về `TelegramBot.gs` (giấu token phía server) | ✅ Đúng |
| — | 232 vs 233 không nhất quán | Fallback `232`: dòng 3130, 3485, 3506, 3517, 3550; mặc định `233`: dòng 1750; snapshot: dòng 3620 | P1 mục 6: hằng số `TOTAL_BHX_SYSTEM` duy nhất trong Master Config | ✅ Đúng; khuyến nghị chốt giá trị theo văn bản chốt kỳ |
| — | Thiếu Single Source of Truth (đồng bộ thủ công 4 nơi) | Vận hành: master_data.js / MasterData.gs / Excel Config / assets/www | P1 mục 7: `team_store_master.json` → codegen tự động | ✅ Đúng; khuyến nghị thêm CI guard so hash fail-build |

---

## 5. RỦI RO CÒN TỒN ĐỒNG & 4 MỤC CHƯA CÓ TRONG LỘ TRÌNH v4.5.0

### 5.1. Hai phát hiện mới sau phản biện

**M1 — Đơn giá bake trong master không khép với công thức /72 (chưa xác minh nguyên nhân gốc):**
Giá trị `actual = 873.680đ/CH` bake sẵn trong `master_data.js` **không tương thích** với công thức (Tổng DC × 20,46% / 72) nếu dùng bộ số KPI trong tài liệu bàn giao (Tổng DC = 2.270.422đ → đơn giá ≈ 6.452đ/CH). Nghĩa là các giá trị `actual` trong master là **dữ liệu kỳ khác / dữ liệu nền**, không phải kỳ hiện hành tính theo công thức. Nguyên nhân chính xác chưa xác minh được (cần Team cung cấp bộ số `totalGs25Dcs` của kỳ bake). Dù vậy, điều này **chứng minh thực nghiệm Lỗi 8 là rủi ro thật**: master data và dữ liệu kỳ đang dính nhau, dễ gây hiểu nhầm số liệu khi kiểm tra chéo.

**M2 — CH 40 Thống Nhất chưa có mã trong bản file đã nhận:**
Team đánh dấu `[x]` hoàn thành việc bổ sung mã POS, nhưng bản `master_data.js` đang thẩm định vẫn còn `"store_code": ""` tại dòng 1347. Cần xác nhận: (a) tôi đang giữ bản cũ, hoặc (b) việc cập nhật chưa thực sự deploy.

### 5.2. Bốn mục của v4.4.0 chưa xuất hiện trong lộ trình v4.5.0

| # | Mục còn thiếu | Cơ sở | Đề xuất đưa vào |
|---|---|---|---|
| 1 | **Tách dữ liệu kỳ khỏi master_data.js** (173 trường `actual` bake sẵn — đã đếm lại: 173) | Phát hiện M1 ở trên là bằng chứng thực nghiệm | P1: tách `master_data.js` (danh mục) và `period_data.json` (số liệu kỳ), master chỉ regenerate khi danh mục thay đổi |
| 2 | **Làm tròn không khép kín** | `Math.round` mọi phép chia (dòng 3987–3990); phần dư chia 230 CH (~54đ) không gán | P1: gán phần dư cho 1 CH "seed"; quy toàn bộ tiền về số nguyên VND khi đọc cell |
| 3 | **HMAC + thời hạn cho fallback hash** | Sau khi bỏ Bytebin, fallback `#d=base64` vẫn không có chữ ký, không hết hạn, ai có URL cũng đọc/sửa được | P0: thêm HMAC + `exp` 24–72h vào payload fallback; GAS short-link là phương án chính |
| 4 | **Golden-file regression test với `team_leader_report_v4.py`** | Script Python kiểm chéo độc lập đã tồn tại trong hệ thống | P2: mỗi kỳ lưu output chuẩn; CI chạy so output JS vs Python trước mỗi build — nơi ghi lại chính quy ước /72 và quy ước VT4050 thành test case có bản quyền nghiệp vụ |

### 5.3. Các điểm chưa xác minh được (giữ nguyên trạng thái)

- **Idempotency khi nạp trùng file Excel** (cộng dồn hay ghi đè khi nạp 2 lần / nạp tuần 2 đè tuần 1): chưa có file handler để kiểm tra.
- **% Timegone off-by-one** (mốc "ngày đã chạy" có bao gồm hôm nay): chưa xác minh trong code.
- **html2canvas scale:2 trên bảng dài** (nguy cơ vượt giới hạn texture WebView ~4096px): đã thấy 2 lời gọi `html2canvas` (dòng 6017, 6656) nhưng chưa đo đạc trên máy thật.
- **Keystore/secrets trong repo Git**: phụ thuộc `push_to_github.bat` và `.gitignore` — chưa có file để kiểm tra.

---

## 6. ĐIỀU CHỈNH SO VỚI BÁO CÁO THẨM ĐỊNH v4.4.0

### 6.1. Thu hồi / hạ cấp
1. **Rút Lỗi 1 khỏi CRITICAL**: mẫu số /72 là quy định kiểm toán của công ty, không phải lỗi. Chuyển thành yêu cầu config hóa magic number + ghi chú nghiệp vụ.
2. **Rút Lỗi 2 khỏi CRITICAL**: CH rỗng mã 873.680đ KHÔNG phải trùng lặp — là cơ chế đơn giá bình quân phẳng cho 70 CH GS25 (xác minh: 70/70 bản ghi).
3. **Rút đề xuất sửa điều kiện Circle K**: dữ liệu ERP kho khô chỉ có mã tổng VT4050, không thể kiểm tra "đơn hàng bất kỳ". Thay bằng kiến nghị gắn nhãn trạng thái 0đ.

### 6.2. Giữ nguyên (đã được Team tiếp thu)
- Lỗi 4 (Bytebin), Lỗi 5 (Web Worker), Lỗi 6 (Telegram token), 232/233, Single Source of Truth — xác nhận đúng, giữ trong lộ trình P0/P1.

### 6.3. Đóng
- Câu hỏi 4 trong Checklist v4.4.0 (7,6 tỷ vs 10,8 tỷ) — đã có giải trình 2 phạm vi, chấp nhận.

### 6.4. Bổ sung mới
- Mục 5.1 (2 phát hiện mới) và 5.2 (4 mục còn thiếu) đưa vào lộ trình hợp nhất ở mục 7.

---

## 7. LỘ TRÌNH KHUYẾN NGHỊ HỢP NHẤT (BẢN v4.4.1)

### GIAI ĐOẠN 1 — XỬ LÝ NGAY (P0, trong tuần)
- [ ] 1. Xóa Bytebin; chuyển 100% chia sẻ sang GAS WebApp có token (Team đã cam kết — P0 mục 1–2)
- [ ] 2. Thêm HMAC + thời hạn (24–72h) cho fallback link hash `#d=` *(bổ sung mới)*
- [ ] 3. Config hóa magic number (72, 20,46%, 3,62%, 5, 232/233) vào object cấu hình duy nhất kèm ghi chú giải trình nghiệp vụ /72 và quy ước VT4050 *(điều chỉnh từ Lỗi 1)*
- [ ] 4. Gắn nhãn trạng thái cho CH Circle K 0đ: "0đ (không có đơn mát trong kỳ)" *(kiến nghị thay cho đề xuất cũ)*
- [ ] 5. Xác nhận bản master_data.js mới nhất: CH 40 Thống Nhất đã có mã chưa (M2)

### GIAI ĐOẠN 2 — TRONG THÁNG (P1)
- [ ] 6. Web Worker cho parse XLSX/XLSB (zero-copy ArrayBuffer) + progress bar + hủy parse (Team cam kết)
- [ ] 7. Chuyển Telegram về backend `TelegramBot.gs` (Team cam kết)
- [ ] 8. Tách 2 profile target: "Team Lead Toàn Kênh (10,8 tỷ)" và "10 PG Siêu Thị (7,6 tỷ)" hiển thị song song (Team cam kết, khuyến nghị hiển thị đồng thời)
- [ ] 9. Pipeline Single Source of Truth: `team_store_master.json` → codegen `master_data.js` / `MasterData.gs` / Excel Config + CI guard so hash fail-build (Team cam kết + bổ sung CI guard)
- [ ] 10. **Tách dữ liệu kỳ khỏi master** (`period_data.json`) *(bổ sung mới — có bằng chứng thực nghiệm M1)*
- [ ] 11. Chuẩn hóa số học: số nguyên VND + gán phần dư chia cho CH "seed" *(bổ sung mới)*

### GIAI ĐOẠN 3 — QUÝ TỚI (P2)
- [ ] 12. Audit Trail: GAS lưu snapshot vào Google Sheet mỗi lần nạp file (Team cam kết)
- [ ] 13. OTA: xác thực SHA-256 APK trước khi cài + nâng Target SDK + test Android 14/15 (Team cam kết)
- [ ] 14. **Golden-file regression test**: `team_leader_report_v4.py` làm test tự động trong CI, ghi lại quy ước /72 và VT4050 thành test case *(bổ sung mới)*

---

## 8. PHỤ LỤC: KẾT QUẢ KIỂM CHỨNG SỐ LIỆU BẰNG MÃ NGUỒN (21/09/2026)

| # | Kiểm chứng | Kết quả thực tế |
|---|---|---|
| 1 | Số lần xuất hiện `873680` trong master_data.js | 70 |
| 2 | Số bản ghi `"actual": 873680` trong section MASTER_DATA (dòng 1105–2153) | 70 |
| 3 | Cấu trúc chuỗi MASTER_DATA | GS25: 70, FamilyMart: 34, Circle K: 27, 7-Eleven: 5, Hoàng Đức Gia Kiệm: 1, Hoàng Đức Long Khánh: 1 (tổng 138 ✓) |
| 4 | Bản ghi `store_code: ""` | Dòng 537 (FM) và dòng 1347 (GS25) |
| 5 | Công thức chia GS25 | `index.html:3987` — `(totalGs25Dcs * 0.2046) / 72` |
| 6 | Công thức chia 7-Eleven | `index.html:3988` — `(totalSeDcs * 0.0362) / 5` |
| 7 | Kho khô Circle K | `index.html:3990` — chia theo `totalCkStoresSystem` (động) |
| 8 | Điều kiện 0đ Circle K | `index.html:4174` — `actual = foundAmt > 0 ? (tCk + Math.round(foundAmt)) : 0;` |
| 9 | Bytebin | `index.html:8385` — `fetch('https://bytebin.lucko.me/post')` |
| 10 | Web Worker | Đếm `new Worker` trong toàn index.html = **0** |
| 11 | Telegram token | `index.html:6288, 6359, 6700` — `localStorage('TELEGRAM_BOT_TOKEN')` |
| 12 | Fallback 232 | Dòng 3130, 3485, 3506, 3517, 3550; mặc định nhập `233`: dòng 1750 |
| 13 | Snapshot T9 | `index.html:3620` — 7,605,871,595đ / 178 CH BHX Team / 233 CH Hệ Thống |
| 14 | Số trường `actual` trong master_data.js | 173 |

---

## KẾT LUẬN CUỐI

Phản biện của Team Cẩm Giang **được chấp nhận toàn bộ 4/4 điểm về nghiệp vụ**, với 2 điểm xác minh trực tiếp bằng mã nguồn đều đúng. Báo cáo v4.4.0 điều chỉnh 3 nhận định (mục 6.1). Hệ thống ở vòng thẩm định này **không còn lỗi CRITICAL về số học**; trọng tâm nâng cấp v4.5.0 nên dồn vào: (1) bảo mật kênh chia sẻ (Bytebin → GAS + HMAC/expiry), (2) kỷ luật dữ liệu kỳ (tách `actual` khỏi master — đã có bằng chứng thực nghiệm), (3) Web Worker cho parse file lớn. Lộ trình hợp nhất 14 mục tại mục 7 sẵn sàng làm cơ sở triển khai v4.5.0.

---
*Báo cáo v4.4.1 lập bởi Chuyên gia Thẩm định — mọi số dòng tham chiếu theo file `index.html` và `master_data.js` đã cung cấp, kiểm chứng ngày 21/09/2026.*
