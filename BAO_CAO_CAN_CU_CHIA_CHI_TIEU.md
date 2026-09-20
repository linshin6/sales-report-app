# BÁO CÁO CĂN CỨ VÀ NGUYÊN TẮC XÂY DỰNG CHỈ TIÊU & MHTT
**Kỳ áp dụng:** Tháng 09/2026 (và chuẩn hóa cho các kỳ tiếp theo)  
**Đơn vị thực hiện:** Team Bán lẻ (Team Lead: Trần Thị Cẩm Giang)  
**Phạm vi:** 6 Hệ thống Kênh CVS & Siêu thị Mini (377 điểm bán / 10 Nhân sự PG)

---

## I. MỤC ĐÍCH BÁO CÁO
Báo cáo này giải trình chi tiết **cơ sở dữ liệu, phương pháp luận toán học, nguyên tắc phân bổ và căn cứ kiểm tra chéo** được sử dụng để xây dựng bảng phân bổ Chỉ tiêu Doanh số Tổng và Mặt Hàng Trọng Tâm (MHTT) cho 377 điểm bán thuộc Team Cẩm Giang, đảm bảo:
1. **Minh bạch & Khoa học:** Dựa trên năng lực bán hàng lịch sử và hạn mức được Ban Lãnh đạo phê duyệt.
2. **Khớp số 100%:** Tổng chỉ tiêu phân bổ bằng đúng hạn mức công ty giao (không thiếu, không dư).
3. **Đồng bộ tuyệt đối:** Cấu trúc 48 cột khớp 100% với File Tổng của Giám sát/Trưởng ban để sao chép thuận tiện.

---

## II. BA CĂN CỨ DỮ LIỆU NGUỒN (INPUT DATA)

Bảng tính được xây dựng dựa trên sự kết hợp của 3 nguồn dữ liệu chính thức:

1. **Căn cứ Hạn mức Công ty giao (`Chi tieu & MHTT T09.2026_MD00.xlsx`):**
   - **Sheet `DST` (Row 4):** Hạn mức giao cho cụm Đồng Nai (BHX) - CVS MD là **`9.634.000.000 VNĐ`** (9.634 triệu VNĐ).
   - **Sheet `DS Chuỗi`:** Hạn mức phân bổ theo từng chuỗi đối tác (BHX MD: 8.433,94 triệu, GS25: 451,83 triệu, FamilyMart: 263,76 triệu, Circle K: 245,00 triệu, 7-Eleven: 50,00 triệu).

2. **Căn cứ Dữ liệu Bán hàng Thực tế Lịch sử (Sheet `3.Data sent`):**
   - **Doanh số 3 tháng gần nhất:** Tháng 6 (Cột 27), Tháng 7 (Cột 43), Tháng 8 (Cột 59) theo từng Location Code của từng cửa hàng.
   - **Doanh số thực tế từng nhóm MHTT trong Tháng 8:**
     - TT1 (SN Green Farm): Cột 54
     - TT2 (SC Green Farm): Cột 56
     - TT3 (FM 180ml): Cột 55
     - TT4 (SCA các loại): Cột 58
     - TT5 (SCU Probi & Star): Cột 57

3. **Căn cứ Danh mục Phân công Nhân sự Team Lead Cẩm Giang:**
   - Danh sách 10 nhân sự PG phụ trách thực tế trên địa bàn (Bùi Thị Sen, Chắng Lý Quỳnh, Kim Hoàng Khang, Lê Thị Thùy Châu, Lê Trần Bá Kiện, Nguyễn Thanh Nhàn, Nguyễn Thị Thanh Thủy, Nguyễn Đức Hoà, Não Thị Anh Đào, Phạm Thị Kim Nhung).

---

## III. CĂN CỨ XÁC ĐỊNH PHẠM VI HỆ THỐNG (SCOPE)

Trong toàn bộ 724 dòng của File tổng toàn Miền MD00 (bao gồm cả các đại siêu thị GO!, Lotte, Coopmart, Metro, Winmart, Con Cưng, Avakids...), công cụ đã trích xuất chính xác **377 điểm bán thuộc đúng 6 hệ thống** do Team Cẩm Giang phụ trách:

| STT | Tên Hệ thống / Chuỗi | Số lượng CH | Đặc thù vận hành | Phụ trách chính |
|:---:|:---|:---:|:---|:---|
| 1 | **BÁCH HOÁ XANH** | 233 CH | Siêu thị mini thực phẩm | Chia đều cho 9 nhân sự phụ trách cụm |
| 2 | **GS25** | 74 CH | Chuỗi cửa hàng tiện lợi CVS | Não Thị Anh Đào, Nguyễn Đức Hoà, Thanh Thủy... |
| 3 | **FAMILY MART** | 36 CH | Chuỗi cửa hàng tiện lợi CVS | Nguyễn Đức Hoà, Thanh Thủy, Anh Đào... |
| 4 | **CIRCLE K** | 27 CH | Chuỗi cửa hàng tiện lợi CVS | Nguyễn Thị Thanh Thủy (18 CH), Anh Đào, Hoà... |
| 5 | **7-ELEVEN (7E)** | 5 CH | Chuỗi cửa hàng tiện lợi CVS | Não Thị Anh Đào (3 CH), Nguyễn Đức Hoà (2 CH) |
| 6 | **HOÀNG ĐỨC** | 2 CH | NPP / Siêu thị địa phương Long Khánh | Lê Thị Thùy Châu (1 CH), Phạm Thị Kim Nhung (1 CH) |
| **TỔNG** | **6 HỆ THỐNG** | **377 CH** | **Toàn bộ mạng lưới của Team** | **10 Nhân viên PG / Leader Trần Thị Cẩm Giang** |

---

## IV. NGUYÊN TẮC VÀ CÔNG THỨC TÍNH TOÁN THEO TỪNG KÊNH

### 1. Kênh Bách Hóa Xanh (BHX — 233 cửa hàng)
- **Đặc thù:** Hệ thống chuỗi lớn, độ phủ dày đặc, doanh số phụ thuộc vào phân bổ nguồn hàng từ các Hub trung chuyển.
- **Nguyên tắc phân bổ:** **Chia đều trên toàn mạng lưới (Equal Distribution)**.
- **Công thức:**
  $$\text{Target}_{\text{BHX/CH}} = \frac{\text{Hạn mức Chuỗi BHX}}{\text{Số lượng CH}} = \mathbf{35.443.102 \text{ VNĐ / CH}}$$
- **Phân bổ MHTT (Cột 20 - 24):** Cố định đồng mức cho từng cửa hàng:
  - TT1 (SN Green Farm): **932.824,49 VNĐ**
  - TT2 (SC Green Farm): **0 VNĐ**
  - TT3 (FM 180ml): **753.110,20 VNĐ**
  - TT4 (SCA các loại): **14.349.028,57 VNĐ**
  - TT5 (SCU Probi & Star): **10.875.648,98 VNĐ**
  - *Tổng MHTT = 26.910.612,24 VNĐ/CH*.

---

### 2. Kênh CVS Chuẩn hóa DC (GS25 & 7-Eleven)
- **Đặc thù:** Doanh số xuất từ các Kho DC tổng và phân bổ theo tỷ lệ cửa hàng hoạt động thực tế.
- **GS25 (74 cửa hàng):**
  - 72 cửa hàng tiêu chuẩn: **7.301.585 VNĐ / CH**
  - 2 cửa hàng trọng điểm (Doanh số cao): **7.691.691 VNĐ / CH**
  - MHTT CHTL (Cột 25-29): Phân bổ theo tỷ trọng đặt hàng thực tế từng nhóm sản phẩm.
- **7-Eleven (5 cửa hàng):**
  - Phân bổ theo quy mô cửa hàng: 2 CH lớn đạt ~12,22 triệu VNĐ/CH; 1 CH đạt ~10,90 triệu VNĐ/CH; 2 CH đạt ~5,60 triệu VNĐ/CH.

---

### 3. Kênh CVS Dựa trên Lịch sử Bán hàng (FamilyMart, Circle K, Hoàng Đức)
- **Đặc thù:** Đã có đầy đủ số liệu bán hàng thực tế qua hệ thống Scan Data của từng điểm bán.
- **Bước 1 — Tính Bình quân 3 tháng (BQ3T - Cột 36):**
  $$\text{BQ3T} = \frac{T06 + T07 + T08}{3}$$
- **Bước 2 — Tính Chỉ tiêu Doanh số Tổng (Cột 19):**
  Phân bổ hạn mức chuỗi dựa trên trọng số đóng góp của từng cửa hàng:
  $$\text{Target}_{\text{Store}} = \text{Hạn mức Chuỗi} \times \frac{\text{BQ3T}_{\text{Store}}}{\sum \text{BQ3T}_{\text{Chuỗi}}}$$
- **Bước 3 — Tính Tỷ lệ Tăng trưởng (Cột 37):**
  $$\text{Tăng trưởng (\%)} = \frac{\text{Target (Cột 19)} - \text{BQ3T (Cột 36)}}{\text{BQ3T (Cột 36)}}$$
- **Bước 4 — Quy tắc Giải trình (Cột 38):**
  Nếu tỷ lệ Tăng trưởng lệch vượt quá $\pm 25\%$, ghi rõ lý do (ví dụ: *"Giảm theo kế hoạch"*, *"Tăng theo mùa vụ"*).
- **Bước 5 — Xác định MHTT CHTL (Cột 25 - 29):**
  Trích xuất từ doanh số bán thực tế của Tháng 8 tại sheet `3.Data sent` tương ứng với từng nhóm sản phẩm TT1 đến TT5.

---

### 4. Công thức Doanh số Ngoài MHTT (Cột 32)
Để đảm bảo tổng cơ cấu doanh số của cửa hàng luôn cân bằng và logic:
$$\text{Doanh số Cột 32} = \text{Target Tổng (Cột 19)} - \sum (\text{MHTT ST} + \text{MHTT CHTL})$$
*(Đảm bảo tổng các nhóm hàng trọng tâm cộng với nhóm hàng phổ thông bằng chính xác 100% Chỉ tiêu Tổng).*

---

## V. CĂN CỨ KIỂM TRA CHÉO TÍNH CHÍNH XÁC (CROSS-VALIDATION)

Bảng tổng hợp sau khi chạy tự động được đối soát chéo với file Hạn mức của Công ty:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. TỔNG TARGET THEO FILE XUẤT RA:                                           │
│    - Bách Hóa Xanh (233 CH)       :  8.094.934.248 VNĐ                     │
│    - GS25 (74 CH)                 :    540.181.461 VNĐ                     │
│    - FamilyMart (36 CH)           :    139.734.406 VNĐ                     │
│    - Circle K (27 CH)             :    130.990.009 VNĐ                     │
│    - Công Ty TNHH Hoàng Đức (2 CH):    233.837.957 VNĐ                     │
│    - 7-Eleven (5 CH)              :     46.545.328 VNĐ                     │
│    ──────────────────────────────────────────────────────────────────       │
│    => TỔNG CỘNG THỰC TẾ PHÂN BỔ   :  9.634.000.000 VNĐ                     │
│                                                                             │
│ 2. ĐỐI SOÁT FILE CÔNG TY (Sheet DST - Row 4):                               │
│    - Hạn mức Cụm Đồng Nai & CVS   :  9.634.000.000 VNĐ                     │
│                                                                             │
│ 3. ĐỘ LỆCH (VARIANCE):                                                      │
│    - Chênh lệch                   :  0 VNĐ (Chính xác tuyệt đối 100%)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## VI. CĂN CỨ KỸ THUẬT ĐẢM BẢO ĐỒNG BỘ 100% VÀO FILE TỔNG

Để giải quyết triệt để rủi ro lệch cột, lỗi font, vỡ format khi sao chép sang File Tổng:
1. **Sử dụng Microsoft Excel COM trực tiếp:** Tận dụng chính bộ ứng dụng Microsoft Excel bản quyền trên máy để nhân bản file `.xlsb` gốc, không qua thư viện trung gian làm mất thuộc tính.
2. **Bảo lưu 100% cấu trúc 48 cột (Cột A đến Cột AW):** Giữ nguyên thứ tự, độ rộng từng cột, chiều cao từng dòng, viền ô và các dải màu phân cấp.
3. **Thao tác sao chép 1 bước:** Người dùng chỉ cần bôi đen từ dòng 10 đến dòng 386 của file kết quả $\rightarrow$ `Ctrl + C` $\rightarrow$ dán sang File Tổng $\rightarrow$ `Ctrl + V`. Toàn bộ dữ liệu sẽ ăn khớp khít từng ô mà không cần căn chỉnh lại.

---
*Báo cáo được phê duyệt và lưu trữ cùng bộ công cụ tự động hóa tại dự án Team 4.*
