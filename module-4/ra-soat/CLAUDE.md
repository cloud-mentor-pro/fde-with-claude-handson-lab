# Công cụ nhập đơn hàng của Hoshimori Việt Nam

Công cụ dòng lệnh viết năm 2016 (anh Long, đã nghỉ), anh Quân sửa cho chạy Python 3 năm 2020. Em Thảo bên Kinh doanh
dùng hằng ngày để nhập phiếu đơn hàng (CSV xuất từ Excel) vào CSDL của hệ thống đơn hàng viết năm 2011.

## Chạy

- `python nhap_don.py <phieu.csv> --db <bản sao CSDL>`: nhập phiếu CSV (dấu `;`, mã Windows-1258).
- `python nhap_don.py --json <thư mục> --db <bản sao CSDL>`: nhập đơn Module 3 đọc ra (mỗi file một đơn, UTF-8). Đơn có
  `"can_nguoi_xem": true` thì không nhập, chỉ in ra để người so lại với bản fax.
- Test: `python -m unittest discover -s tests -v`. Test chép CSDL thật ra thư mục tạm rồi chạy công cụ trên bản sao.

## Không được làm

- Không chạy công cụ vào CSDL thật `../../du-lieu/he-thong-cu/donhang.db` (đường dẫn mặc định trong `cau_hinh.ini`).
  Luôn truyền `--db` trỏ vào một bản sao.
- Không đổi cấu trúc bảng (`tblDonHang`, `tblCTDH`…): hệ thống cũ trên Access còn đọc trực tiếp các bảng này.
- Không đổi cách lưu dữ liệu: ngày là chữ `dd/mm/yyyy`, trạng thái là số (0 mới, 1 đang làm, 2 đã giao, 9 huỷ), số đơn
  dạng `DH<yymm>-<4 số>`.
- Không đổi định dạng phiếu CSV: P. Kinh doanh vẫn lưu từ cùng một file Excel.

## Biết trước

- Số lượng trên phiếu hay có dấu chấm hoặc phẩy ngăn nghìn (`4.000`, `1,500`), vì người nhập gõ theo bản fax.
- Khách `TPW` có mã trùng `TPW2` trong CSDL (nhập trùng từ trước). Chưa ai được giao gộp, đừng tự gộp.
- Code cũ viết chữ không dấu trong chú thích và thông báo; giữ kiểu đó cho thống nhất, vì terminal ở máy em Thảo không
  hiện được tiếng Việt có dấu.
