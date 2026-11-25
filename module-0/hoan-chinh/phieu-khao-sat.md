# Phiếu ghi chép buổi khảo sát đầu tiên

Khách: Công ty TNHH Hoshimori Việt Nam (HMV)
Ngày: thứ hai của tuần đầu
Người ghi: FDE của công ty bạn

Một cách ghi cho buổi khảo sát ở bài "Gặp khách hàng mẫu". Phiếu của bạn không cần giống từng chữ; so xem bạn có bỏ sót
người, nguồn dữ liệu hay việc phải xin duyệt nào không.

## 1. Ai là ai

| Người | Việc ở nhà máy | Vai trong dự án | Điều họ lo |
|---|---|---|---|
| Ông Yamada Kenichi | Tổng giám đốc, sang từ công ty mẹ năm 2023 | Người ký cuối ở phía HMV | Có kết quả để báo cáo về Nagoya; lộ dữ liệu |
| Chị Trần Thu Hà | Phó giám đốc sản xuất | Người mời công ty mình tới; có thể làm champion | Họp dài, mua phần mềm rồi để đó |
| Anh Nguyễn Minh Quân | Một mình lo IT | Người cấp quyền truy cập hệ thống và dữ liệu | AI làm hỏng dữ liệu; không có thời gian viết lại hệ thống cũ |
| Chị Lê Ngọc Diệp | Trưởng nhóm kinh doanh, nhận đơn | Người hưởng lợi trực tiếp nếu đọc đơn tự động | Ngày nào cũng gọi khách hỏi lại đơn fax mờ |
| Em Nguyễn Thị Thảo | Nhập đơn vào hệ thống cũ | Người dùng hằng ngày | Sợ bị AI thay việc |
| Anh Phạm Văn Tú | Trưởng QC | Người dùng nếu làm phần sổ lỗi | Lỗi nào lặp lại ở máy nào |
| Chị Võ Hoàng Yến | Thư ký giám đốc, phiên dịch tiếng Nhật | Người kiểm bản nháp báo cáo tháng | Mất khoảng hai ngày mỗi tháng cho báo cáo |
| Ông Satō Makoto (công ty mẹ) | Trưởng phòng Hệ thống thông tin | Người duyệt mọi dịch vụ AI mới (ringi) | Dữ liệu đi đâu |
| Chị Suzuki Misaki (công ty mẹ) | Phòng Kinh doanh quốc tế | Người nhận báo cáo tháng | Báo cáo đúng mẫu, đúng hạn |

## 2. Dữ liệu

| Nguồn | Nằm ở đâu | Bao nhiêu | Bẩn chỗ nào | Có thông tin cá nhân không |
|---|---|---|---|---|
| Hệ thống đơn hàng cũ (2011) | `du-lieu/he-thong-cu/donhang.db` | 1625 đơn (01–10/2026) | 40 đơn thiếu ngày giao, 161 dòng số lượng là chữ, khách `TPW` nhập trùng thành `TPW2` | Có: tài khoản người nhập (`thao.nt`, `diep.ln`) |
| File CSV hệ thống cũ xuất ra | `du-lieu/he-thong-cu/xuat_don_hang_2026-10.csv` | Đơn tháng 10 | Dấu chấm phẩy, mã Windows-1258, mở bằng UTF-8 ra chữ lỗi | Không thấy |
| Đơn hàng mới tuần 46 | `du-lieu/don-hang-moi/` | 6 fax, 4 email PDF | Fax mờ, nghiêng; mỗi khách một mẫu đơn; đơn của công ty mẹ bằng tiếng Nhật | Có: tên người đặt hàng trên đơn |
| Kế hoạch sản xuất tháng 10 | `du-lieu/ke-hoach-san-xuat/` | 1 file Excel | Ô gộp, ngày viết ba kiểu, cột bị ẩn | Chưa xem kỹ |
| Sổ lỗi QC tháng 10 | `du-lieu/qc/` | 316 dòng | Lỗi "ba via" viết ba kiểu; tỉ lệ lỗi 1,14% so với mục tiêu 1,0% | Có: tên người ghi sổ |
| Tài liệu công ty mẹ | `du-lieu/cong-ty-me/` | 4 tài liệu tiếng Nhật, có bản dịch | Không bẩn, nhưng quyết định được dùng AI tới đâu | Không |

## 3. Chỗ vướng

| Việc | Ai làm | Mất bao lâu | Sai thì hậu quả gì |
|---|---|---|---|
| Gõ đơn fax và PDF vào hệ thống cũ | Em Thảo, chị Diệp | Chưa đo, hỏi chị Diệp số đơn mỗi ngày và thời gian mỗi đơn | Sai số lượng thì giao nhầm hàng |
| Hỏi "đơn nào sắp trễ?" | Anh Quân chạy truy vấn | Chưa đo | Biết trễ quá muộn |
| Soạn báo cáo tháng tiếng Nhật | Chị Yến | Khoảng hai ngày mỗi tháng | Báo cáo sai số liệu gửi công ty mẹ |
| Tổng hợp sổ lỗi QC | Chưa ai làm | Không làm | Không thấy lỗi lặp lại ở máy nào |

## 4. Câu cần hỏi thêm

- Ba khách còn gửi fax (`TPW`, `LHP`, `HLX`) có gửi được PDF qua email không?
- Mỗi ngày có bao nhiêu đơn, nhập mỗi đơn mất bao lâu? (cần số này để đo trước và sau pilot)
- `TPW` và `TPW2` có phải cùng một khách không? Ai sửa được?
- Ai ở nhà máy được xem dữ liệu nào?

## 5. Việc phải xin duyệt trước khi làm

- Dùng Claude cho dữ liệu thật của nhà máy: công ty mẹ chưa duyệt dịch vụ AI nào, phải qua ringi gửi ông Satō
  (mục 2 của hướng dẫn dùng AI tạo sinh, bản 1.2).
- Thông tin cá nhân trên đơn và trong sổ QC: mục 3 của cùng hướng dẫn.
- Tới lúc đó chỉ làm thử trên dữ liệu giả hay dữ liệu đã bỏ tên người.
