# AGENTS.md - CONTEXT & INSTRUCTIONS FOR AI AGENTS

This workspace contains the CVS & BHX Sales Reporting Application for **Team Cẩm Giang**.

## Critical Project Brain Reference
For complete business logic, store distribution, SKU discovery engine, and historical discrepancy explanations, refer to:
- [PROJECT_BRAIN.md](file:///d:/v/BC-CVS-main/gas_app/PROJECT_BRAIN.md)
- [GEMINI.md](file:///d:/v/BC-CVS-main/gas_app/GEMINI.md)

## Key Technical & Business Truths
- Total CVS stores: **138** across 6 representatives.
- Representative **Nguyễn Đức Hòa** does NOT manage WinMart+ (4 stores removed; WMP count = 0).
- Team CVS Target: 10,826,339,729 đ. Team Total Attainment: 3,911,174,471 đ (36.1%).
- FamilyMart Hubs Model (Direct Factory Billing): 6 Hubs (733,207,650 đ) chia đều cho 196 CH hệ thống = 3,740,855 đ/CH. Team quản lý 36 CH (Nguyễn Đức Hoà: 24, Nguyễn Thị Thanh Thủy: 7, Não Thị Anh Đào: 3, Kim Hoàng Khang: 1, Chưa phân bổ: 1) = 134,670,793 đ. Bỏ sheet 46 SKU, hiển thị giống mô hình Bách Hóa Xanh.
- Sync constraint: Any edits to `index.html`, `view.html`, `master_data.js` must be copied to `android/app/src/main/assets/www/`.
- Release APKs: Built via `build_apk.bat` -> `BaoCaoDoanhSo_TeamCamGiang.apk` and `BaoCaoThucDat.apk`.
- Auto Git Push: Always commit & push to `origin main` after APK builds or web/native code updates so users get instant OTA updates via `bcgiang.vercel.app`.
- Circle K formula (sheet SO): Tự động nhận diện chuỗi Circle K (VT*, Vòng Tròn Đỏ), tách Kho Khô Nam Tân Uyên (Lô G1-9... = 762,467,544 đ) chia đều cho số CH có đơn thực tế (274 CH = 275 dòng trừ 1 DC Khô) = 2,782,728 đ/CH + Hàng Mát của từng CH. Cửa hàng không đơn = 0 đ.
