# Module 4, bản sửa chờ soát

Công cụ nhập đơn sau bài viết test: lỗi `4.000` đã sửa, có test. File `ban-sua-nhap-json.patch` là một bản sửa thêm cờ
`--json` (nhập đơn Module 3 đọc ra) đang chờ soát trước khi giao cho anh Quân. Bản sửa này khoá học chuẩn bị sẵn, có cài
vài chỗ cần soi, để ai làm bài cũng soát cùng một diff.

- Áp bản sửa: `git apply ban-sua-nhap-json.patch`, rồi đọc bằng `git --no-pager diff`.
- Bỏ bản sửa, về lại như cũ: `git restore .` (bản sửa do lệnh git áp vào, nên `/rewind` của Claude Code không hoàn tác được).
- Test: `python -m unittest discover -s tests`.
