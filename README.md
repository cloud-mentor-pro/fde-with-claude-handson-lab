# FDE với Claude: repo mẫu

Code và dữ liệu mẫu cho khoá học miễn phí **FDE với Claude** trên Anthropic Exam Pro. Trong khoá, bạn đóng vai FDE
(Forward Deployed Engineer) của một công ty IT Việt Nam, được cử sang giúp một nhà máy đưa Claude vào công việc thật.

> Mọi công ty, người và số liệu trong repo này đều là giả, dựng ra để học.

## Khách hàng mẫu: Hoshimori Việt Nam

Công ty TNHH Hoshimori Việt Nam làm linh kiện ô tô và xe máy: ép nhựa vỏ connector, kẹp dây, và lắp bó dây điện
(wire harness). Nhà máy ở một khu công nghiệp thuộc Bình Dương cũ (nay là TP.HCM), công ty mẹ là Hoshimori Kogyo ở
Nagoya. Nhà máy đang vướng ở mấy chỗ quen thuộc: đơn hàng tới bằng fax và PDF rồi được gõ tay vào một hệ thống viết từ
năm 2011, kế hoạch sản xuất nằm trong Excel, sổ lỗi QC ghi mỗi người một kiểu, và mỗi tháng mất hai ngày soạn báo cáo
tiếng Nhật gửi công ty mẹ.

## Trong repo có gì

| Thư mục | Nội dung |
|---|---|
| `du-lieu/he-thong-cu/` | Cơ sở dữ liệu của hệ thống đơn hàng cũ (SQLite) và file CSV nó xuất ra (mã Windows-1258) |
| `du-lieu/don-hang-moi/` | Đơn hàng tuần 46 chưa nhập: bản fax và PDF gửi qua email, mỗi khách một mẫu |
| `du-lieu/ke-hoach-san-xuat/` | File Excel kế hoạch sản xuất tháng 10 |
| `du-lieu/qc/` | Sổ lỗi QC hằng ngày tháng 10 |
| `du-lieu/cong-ty-me/` | Bốn tài liệu tiếng Nhật của công ty mẹ, bản dịch tiếng Việt ở `ban-dich/` |
| `module-0/` … `module-9/` | Mỗi module một bản khởi đầu (`bat-dau/`) và một bản hoàn chỉnh (`hoan-chinh/`) |
| `scripts/tao_du_lieu.py` | Script dựng lại dữ liệu giả (người học không cần chạy) |

## Bắt đầu

Cần Python 3.10 trở lên và git.

```bash
git clone https://github.com/cloud-mentor-pro/fde-with-claude-handson-lab.git
cd fde-with-claude-handson-lab
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python xem_du_lieu.py
```

## Giấy phép

MIT, xem `LICENSE`.
