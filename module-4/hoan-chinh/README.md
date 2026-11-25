# Module 4, bản hoàn chỉnh

Công cụ nhập đơn sau bốn bài của Module 4:

- `CLAUDE.md`: điều Claude Code cần biết về dự án của khách (bài "Đọc hiểu code cũ").
- `tests/`: test viết trước khi sửa, chạy bằng `python -m unittest discover -s tests -v` (bài "Viết test trước khi sửa").
- `nhap_don.py`: đã sửa lỗi số lượng có dấu chấm ngăn nghìn (`4.000` bị đọc thành 4), thêm `--json` để nhập đơn Module 3
  đọc ra từ `module-3/hoan-chinh/ket-qua/` (bài "Thêm chức năng nhập JSON").
- `.claude/settings.json` và `.claude/hooks/chan_db_that.py`: hook chặn Claude Code ghi vào CSDL thật.

Code Claude Code viết cho bạn sẽ khác bản này từng chữ. So xem bản của bạn có đủ những việc trên không, và test của bạn
có bắt được lỗi `4.000` không.
