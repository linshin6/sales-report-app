---
name: skill-creator
description: Hướng dẫn tiêu chuẩn và quy trình tạo mới một Agent Skill theo đặc tả kỹ thuật Agent Skills (agentskills/agentskills). Sử dụng khi người dùng hoặc agent cần đóng gói quy trình, thư viện hàm, hoặc tri thức chuyên biệt thành kỹ năng tái sử dụng.
---

# Agent Skills Specification (Đặc tả Chuẩn Kỹ Năng Agent)

Tài liệu đặc tả và hướng dẫn triển khai dựa trên tiêu chuẩn mở **Agent Skills** ([github.com/agentskills/agentskills](https://github.com/agentskills/agentskills) & [agentskills.io](https://agentskills.io)).

---

## 1. Cấu trúc thư mục của một Skill

Mỗi Skill là một thư mục độc lập nằm trong:
- Cấp dự án: `.agents/skills/<skill-name>/`
- Cấp toàn cục: `~/.gemini/config/skills/<skill-name>/`

```
<skill-name>/
├── SKILL.md                 # (BẮT BUỘC) Hợp đồng chính: metadata frontmatter + hướng dẫn chi tiết
├── scripts/                 # (Tùy chọn) Mã thực thi (Python, JS, PowerShell, Bash) cho các tác vụ cần độ chính xác cao
├── references/              # (Tùy chọn) Tài liệu tra cứu chuyên sâu, API docs, bảng ánh xạ
└── assets/                  # (Tùy chọn) Mẫu dữ liệu, template, file ví dụ
```

---

## 2. Định dạng chuẩn của file `SKILL.md`

File `SKILL.md` bắt buộc phải có phần mở đầu bằng **YAML frontmatter** (giữa 2 dấu `---`), gồm ít nhất 2 trường:

```yaml
---
name: kebab-case-skill-name
description: Tóm tắt 1-2 câu nêu rõ Skill này làm gì và KHI NÀO agent nên kích hoạt nó.
---
```

### Nguyên tắc Progressive Disclosure (Nạp lũy tiến):
- **Quét tổng thể**: Agent chỉ đọc `name` và `description` trong YAML frontmatter để nhận diện khi nào cần kích hoạt skill (giúp tối ưu token ngữ cảnh).
- **Thực thi chuyên sâu**: Chỉ khi nhận thấy tác vụ khớp với `description`, agent mới nạp toàn bộ nội dung `SKILL.md` và truy xuất tài nguyên trong `references/` hoặc thực thi lệnh trong `scripts/`.

---

## 3. Quy trình tạo một Skill mới

Khi tạo Skill mới cho dự án:

1. **Đặt tên thư mục**: Dạng kebab-case phản ánh đúng nghiệp vụ (ví dụ: `api-validator`, `db-migrator`, `report-generator`).
2. **Soạn thảo `SKILL.md`**:
   - `name`: Trùng với tên thư mục.
   - `description`: Viết rõ ràng từ khóa nghiệp vụ và tình huống áp dụng.
   - Nội dung bên dưới:
     - **Vai trò & Mục tiêu**: Skill này giải quyết vấn đề gì?
     - **Quy trình từng bước**: Các bước agent cần thực hiện.
     - **Quy tắc & Ràng buộc**: Điều được phép và không được phép làm.
     - **Cách kiểm tra kết quả**: Tiêu chí đánh giá hoàn thành.
3. **Đóng gói Script hỗ trợ (`scripts/`)**:
   - Các tác vụ lặp đi lặp lại hoặc đòi hỏi tính toán chính xác 100% (ví dụ: Regex phức tạp, chuyển đổi file Excel, hash mật khẩu...) nên được viết thành script độc lập.
   - Agent chỉ cần gọi script này qua `run_command` thay vì tự viết code nháp.
4. **Tài liệu tham khảo (`references/`)**:
   - Chứa thông số API, cheat-sheet cú pháp, quy chuẩn đặt tên database... Tách biệt khỏi `SKILL.md` để tránh tràn ngữ cảnh.

---

## 4. Bảng kiểm tra chất lượng Skill (Checklist)

Trước khi nghiệm thu một Skill:
- [ ] Thư mục skill nằm đúng vị trí (`.agents/skills/` hoặc `~/.gemini/config/skills/`).
- [ ] File `SKILL.md` có YAML frontmatter hợp lệ với `name` và `description`.
- [ ] Mô tả `description` nêu rõ điều kiện kích hoạt.
- [ ] Các script trong `scripts/` có hướng dẫn cách chạy cụ thể.
- [ ] Không chứa thông tin nhạy cảm (API keys, credentials hardcode).
