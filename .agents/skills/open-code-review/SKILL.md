---
name: open-code-review
description: Tự động review code bằng công cụ Alibaba Open Code Review (`ocr`), kết hợp tập luật kiểm tra của dự án Team Cẩm Giang (Web JS/HTML, Android Java OTA, Python scripts, Business Rules 138 CH CVS). Hỗ trợ review git diff, scan toàn bộ file hoặc delegation mode.
---

# Open Code Review - Team Cẩm Giang Skill

Kỹ năng này hướng dẫn tích hợp và sử dụng công cụ **Alibaba Open Code Review (`ocr`)** trong dự án Báo cáo Doanh số Team Cẩm Giang.

## 1. Tổng quan & Triết lý kiến trúc
`OpenCodeReview` kết hợp giữa **Deterministic Engineering** (bộ luật cứng, lọc file chính xác, gom nhóm sub-agent) và **LLM Agent** để tạo ra các nhận xét review chính xác ở từng dòng code (`line-level precision`), tránh hiện tượng ảo giác và tiết kiệm token.

- **CLI Package**: `@alibaba-group/open-code-review` (v1.12.5+)
- **Quy tắc dự án**: `.opencodereview/rule.json`
- **Chế độ Delegation**: Cho phép AI host agent (như Antigravity/Gemini) tự thực hiện review theo spec và rules của OCR mà không cần nạp thêm LLM API key riêng cho OCR.

## 2. Các lệnh thông dụng

### A. Kiểm tra nhanh (Preview & Rules)
```powershell
# Xem danh sách file có thay đổi cần review
ocr delegate preview

# Kiểm tra quy tắc review áp dụng cho 1 file cụ thể
ocr rules check android/app/src/main/java/com/salesreport/app/AppUpdateManager.java
ocr rules check index.html
```

### B. Chạy Code Review với LLM (Khi đã cấu hình API Key)
```powershell
# Review toàn bộ thay đổi chưa commit trong workspace
ocr review --audience agent -b "Cập nhật ứng dụng Báo cáo Doanh số Team Cẩm Giang"

# Review một commit cụ thể
ocr review --commit <commit-hash>

# Review toàn bộ mã nguồn một thư mục (không cần git diff)
ocr scan --path android/app/src/main/java
```

### C. Xem kết quả trực quan trên Web (Session Viewer)
```powershell
ocr viewer
```

## 3. Quy tắc kiểm tra trọng tâm trong dự án này (.opencodereview/rule.json)
1. **Giao diện Web (`**/*.{js,html}`)**:
   - Chống tấn công XSS khi chèn dữ liệu động.
   - Luôn đảm bảo đồng bộ `index.html`, `view.html`, `master_data.js` vào `android/app/src/main/assets/www/`.
   - Đảm bảo responsive trên mobile.
2. **Ứng dụng Android Java (`**/android/**/*.java`)**:
   - Tránh NullPointerException (NPE) và an toàn đa luồng.
   - PendingIntent trên Android 12+ (API 31+) phải khai báo `FLAG_IMMUTABLE` hoặc `FLAG_UPDATE_CURRENT`.
   - PackageInstaller và BroadcastReceiver xử lý đúng `STATUS_PENDING_USER_ACTION`, không crash UI thread.
3. **Python Scripts (`**/*.py`)**:
   - File I/O trên Windows luôn dùng `encoding='utf-8'`.
   - Tuân thủ nghiệp vụ chuẩn: 138 CH CVS, nhân sự Hòa không có WinMart+, công thức Circle K tính kho khô chia 230 CH có đơn.
