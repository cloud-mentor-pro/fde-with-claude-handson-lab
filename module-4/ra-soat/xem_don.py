# Xem nhanh mot don trong CSDL theo so don cua khach (anh Quan viet de kiem phieu nhap)
# Cach dung: python xem_don.py <duong dan db> <so don khach>
import os, sys, sqlite3

if len(sys.argv) != 3:
    print("Cach dung: python xem_don.py <duong dan db> <so don khach>")
    sys.exit(1)
if not os.path.exists(sys.argv[1]):
    print("Khong thay CSDL: " + sys.argv[1])
    sys.exit(1)
con = sqlite3.connect(sys.argv[1])
dong = con.execute(
    "SELECT d.SoDH, d.MaKH, d.NgayGiao, c.STT, c.MaSP, c.SoLuong FROM tblDonHang d JOIN tblCTDH c ON c.SoDH = d.SoDH "
    "WHERE instr(d.GhiChu, ?) > 0 ORDER BY d.SoDH, c.STT",
    ("[phieu " + sys.argv[2] + "]",),
).fetchall()
if not dong:
    print("Khong thay don " + sys.argv[2])
for so_dh, ma_kh, giao, stt, ma_sp, sl in dong:
    print("%s  %s  giao %s  dong %d  %s  so luong %s" % (so_dh, ma_kh, giao, stt, ma_sp, sl))
