# Module 4, bản khởi đầu

Công cụ nhập đơn hàng viết năm 2016 của Hoshimori Việt Nam, đúng như anh Quân đưa cho bạn: không có test, không có tài
liệu, người viết đã nghỉ.

- `nhap_don.py`: nhập phiếu đơn hàng (CSV) vào CSDL của hệ thống đơn hàng cũ.
- `cau_hinh.ini`: đường dẫn CSDL (mặc định là CSDL thật trong `du-lieu/he-thong-cu/`) và tài khoản người nhập.
- `phieu_nhap_mau.csv`: một phiếu mẫu hai đơn, mã Windows-1258.

Đừng chạy `nhap_don.py` khi chưa có `--db` trỏ vào một bản sao: không có `--db`, công cụ ghi thẳng vào CSDL thật.
