# Module 1: AI làm được gì, không làm được gì

Hai script nhỏ để thử Claude trên sổ lỗi QC tháng 10 của Hoshimori Việt Nam, chỉ dùng thư viện có sẵn của Python:

- `bo_ten.py`: chép sổ lỗi sang file mới không có cột tên người (`nguoi_ghi`), để đưa cho Claude mà không gửi thông tin
  cá nhân.
- `dem_loi.py`: đếm lỗi bằng code (tỉ lệ lỗi chung, lỗi theo loại sau khi gộp các cách viết, theo công đoạn, năm máy lỗi
  cao nhất), để đối chiếu với con số Claude đưa ra.

- `bat-dau/`: hai script, chạy trong thư mục này.
- `hoan-chinh/`: file sổ lỗi đã bỏ tên người, đúng như `bo_ten.py` ghi ra, để so với file của bạn.
