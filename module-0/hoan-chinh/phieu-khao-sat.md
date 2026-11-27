# Phiếu ghi chép buổi khảo sát đầu tiên

Khách: Công ty TNHH Hoshimori Việt Nam (HMV)
Ngày: ngày đầu khảo sát
Người ghi: FDE của công ty bạn

Một cách ghi cho buổi khảo sát ở bài "Gặp khách hàng mẫu". Phiếu của bạn không cần giống từng chữ; so xem bạn có bỏ sót
người, nguồn dữ liệu, mốc đo hay việc phải xin duyệt nào không.

## 1. Ai là ai

| Người | Việc ở nhà máy | Vai trò trong dự án | Điều họ lo |
|---|---|---|---|
| Chị Trần Thu Hà | Phó giám đốc sản xuất; phòng chị soạn báo cáo tháng gửi công ty mẹ | Mời công ty mình tới, bảo trợ pilot | Mua phần mềm rồi để đó |
| Anh Nguyễn Minh Quân | Một mình lo IT, giữ hệ thống cũ và công cụ nhập đơn | Cấp quyền truy cập hệ thống và dữ liệu | AI làm hỏng dữ liệu; không có thời gian viết lại hệ thống cũ |
| Chị Lê Ngọc Diệp | Trưởng nhóm kinh doanh, nhận đơn fax và email | Champion nếu làm pilot đọc đơn | Ngày nào cũng gọi khách hỏi lại đơn fax mờ |
| Em Nguyễn Thị Thảo | Nhập đơn vào hệ thống cũ (tài khoản `thao.nt`) | Người dùng hằng ngày | Sợ bị AI thay việc |
| Ông Satō Makoto (công ty mẹ ở Nagoya) | Trưởng phòng Hệ thống thông tin | Người duyệt mọi dịch vụ AI mới (ringi) | Dữ liệu đi đâu |

## 2. Dữ liệu

| Nguồn | Nằm ở đâu | Bao nhiêu | Bẩn chỗ nào | Có thông tin cá nhân không |
|---|---|---|---|---|
| Hệ thống đơn hàng cũ (2011) | `du-lieu/he-thong-cu/donhang.db` | 1625 đơn (01–10/2026) | 40 đơn thiếu ngày giao, 161 dòng số lượng là chữ, khách `TPW` nhập trùng thành `TPW2` | Có: tài khoản người nhập (`thao.nt`, `diep.ln`) |
| File CSV hệ thống cũ xuất ra | `du-lieu/he-thong-cu/xuat_don_hang_2026-10.csv` | Đơn tháng 10 | Dấu chấm phẩy, mã Windows-1258, mở bằng UTF-8 ra chữ lỗi | Không thấy |
| Đơn hàng mới tuần 46 | `du-lieu/don-hang-moi/` | 6 fax, 4 email PDF | Fax mờ, nghiêng; mỗi khách một mẫu đơn; đơn của công ty mẹ bằng tiếng Anh | Có: tên người đặt hàng trên đơn |
| Kế hoạch sản xuất tháng 10 | `du-lieu/ke-hoach-san-xuat/` | 1 file Excel | Ô gộp, ngày viết ba kiểu, cột bị ẩn | Chưa xem kỹ |
| Sổ lỗi QC tháng 10 | `du-lieu/qc/` | 316 dòng | Lỗi "ba via" viết ba kiểu; tỉ lệ lỗi 1,14% so với mục tiêu 1,0% | Có: tên người ghi sổ (cột `nguoi_ghi`) |
| Tài liệu công ty mẹ | `du-lieu/cong-ty-me/` | 4 tài liệu tiếng Anh | Không bẩn, nhưng quyết định được dùng AI tới đâu | Không |

## 3. Chỗ vướng

| Việc | Ai làm | Mất bao lâu | Sai thì hậu quả gì |
|---|---|---|---|
| Gõ đơn fax và PDF vào hệ thống cũ | Em Thảo, chị Diệp | Xem mốc đo ở mục 4 | Sai số lượng thì giao nhầm hàng |
| Gọi khách hỏi lại đơn fax mờ | Chị Diệp | Xem mốc đo ở mục 4 | Nhập theo chỗ đoán thì giao nhầm |
| Soạn báo cáo tháng gửi công ty mẹ | Vài người ở phòng chị Hà | Chưa đo | Báo cáo sai số liệu gửi công ty mẹ |
| Tổng hợp sổ lỗi QC | Chưa ai làm | Không làm | Không thấy lỗi lặp lại ở máy nào |

## 4. Mốc đo trước khi làm

| Mốc đo | Hiện nay | Đo hay ước | Đo thế nào | Ai cho số, ngày |
|---|---|---|---|---|
| Phút nhập một đơn | Email PDF 4 phút, fax 7 phút (trung bình) | Đo | Ngồi cạnh em Thảo một buổi sáng, bấm giờ từ lúc mở đơn tới lúc lưu xong, 12 đơn (5 email, 7 fax) | Em Thảo, ngày đầu khảo sát |
| Cuộc gọi xác nhận đơn fax mỗi tuần | Khoảng 10 cuộc | Ước | Chị Diệp nhớ lại, chưa có sổ ghi. Đã nhờ chị ghi mỗi cuộc gọi (ngày, khách, số đơn, hỏi gì) trong hai tuần trước pilot | Chị Diệp, ngày đầu khảo sát |
| Đơn giao nhầm mỗi tháng | 3 đơn trong tháng 10/2026 | Đo | Đếm phiếu khách báo giao nhầm mà phòng kinh doanh lưu; chưa tách nhầm do nhập đơn với nhầm do kho | Chị Diệp, ngày đầu khảo sát |

## 5. Câu cần hỏi thêm

- Ba khách còn gửi fax (`TPW`, `LHP`, `HLX`) có gửi được PDF qua email không?
- Ba đơn giao nhầm tháng 10: đơn nào nhầm do nhập, đơn nào do kho? (hỏi chị Diệp)
- `TPW` và `TPW2` có phải cùng một khách không? Ai sửa được?
- Ai ở nhà máy được xem dữ liệu nào?

## 6. Việc phải xin duyệt trước khi làm

- Dùng Claude cho dữ liệu thật của nhà máy: công ty mẹ chưa duyệt dịch vụ AI nào, phải qua ringi gửi ông Satō
  (mục 2 của hướng dẫn dùng AI tạo sinh, bản 1.2).
- Thông tin cá nhân trên đơn và trong sổ QC: mục 3 của cùng hướng dẫn.
- Tới lúc đó chỉ làm thử trên dữ liệu giả hay dữ liệu đã bỏ tên người.
