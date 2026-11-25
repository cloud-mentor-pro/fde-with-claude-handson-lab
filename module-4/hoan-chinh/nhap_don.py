# -*- coding: utf-8 -*-
# Cong cu nhap don hang tu phieu nhap (CSV) vao he thong don hang
# Viet: Long - P.IT - 03/2016
# Sua 12/2016 (Long): them kiem tra ma khach
# Sua 07/2020 (Quan): chay duoc tren Python 3
# Sua 11/2026 (FDE): so luong co dau cham/phay ngan nghin (4.000) bi doc thanh 4; them --json (don Module 3 doc ra)
#
# Cach dung:  python nhap_don.py <phieu_nhap.csv> [--db <duong dan db>]
#             python nhap_don.py --json <thu muc JSON> [--db <duong dan db>]
# Phieu nhap: file Excel cua P.Kinh doanh, luu ra CSV (dau ; , ma Windows)
import sys, os, csv, glob, json, re, sqlite3, configparser
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
cfg.read(os.path.join(THU_MUC, "cau_hinh.ini"), encoding="utf-8")

DB = os.path.join(THU_MUC, cfg.get("csdl", "duong_dan"))
NGUOI_NHAP = cfg.get("chung", "nguoi_nhap")
MA_FILE = "cp1258"

con = None
loi = []


def ket_noi():
    global con
    con = sqlite3.connect(DB)


def so_luong(s):
    # so luong la so nguyen; nguoi nhap hay go dau cham hoac phay ngan nghin (4.000, 1,500) -> bo di
    s = str(s).strip()
    if not re.fullmatch(r"\d+|\d{1,3}([.,]\d{3})+", s):
        raise ValueError("so luong khong hop le: %r" % s)
    return int(re.sub(r"[.,]", "", s))


def ngay(s):
    # ngay dd/mm/yyyy, de trong thi tra ve rong
    s = s.strip()
    if s == "":
        return ""
    d = datetime.strptime(s, "%d/%m/%Y")
    return d.strftime("%d/%m/%Y")


def so_don_moi(ngay_dat):
    # so don: DH + yymm + so thu tu 4 chu so (chay tiep tu so lon nhat)
    d = datetime.strptime(ngay_dat, "%d/%m/%Y")
    r = con.execute("SELECT SoDH FROM tblDonHang").fetchall()
    n = 0
    for (sdh,) in r:
        try:
            k = int(sdh.split("-")[1])
            if k > n:
                n = k
        except:
            pass
    return "DH%s-%04d" % (d.strftime("%y%m"), n + 1)


def doc_phieu(duong_dan):
    don = {}
    thu_tu = []
    f = open(duong_dan, encoding=MA_FILE, newline="")
    for dong in csv.DictReader(f, delimiter=";"):
        k = dong["SoDonKhach"].strip()
        if k not in don:
            don[k] = {"MaKH": dong["MaKH"].strip(), "NgayDat": dong["NgayDat"], "NgayGiao": dong["NgayGiao"], "GhiChu": dong.get("GhiChu", ""), "dong": []}
            thu_tu.append(k)
        don[k]["dong"].append((dong["MaSP"].strip(), dong["SoLuong"]))
    f.close()
    return [(k, don[k]) for k in thu_tu]


def doc_json(thu_muc):
    # Don Module 3 doc ra: moi file mot don. Don can_nguoi_xem thi giu lai, khong nhap.
    ds, giu_lai = [], []
    for duong_dan in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        with open(duong_dan, encoding="utf-8") as f:
            j = json.load(f)
        if j.get("can_nguoi_xem"):
            giu_lai.append("%s: %s" % (j["so_don_khach"], j.get("ly_do", "")))
            continue
        d = {
            "MaKH": j["ma_khach"],
            "NgayDat": datetime.strptime(j["ngay_dat"], "%Y-%m-%d").strftime("%d/%m/%Y"),
            "NgayGiao": datetime.strptime(j["ngay_giao"], "%Y-%m-%d").strftime("%d/%m/%Y") if j.get("ngay_giao") else "",
            "GhiChu": "",
            "dong": [(x["ma_hang"], str(x["so_luong"])) for x in j["dong"]],
        }
        ds.append((j["so_don_khach"], d))
    return ds, giu_lai


def nhap_mot_don(so_khach, d):
    kh = con.execute("SELECT MaKH FROM tblKhachHang WHERE MaKH=?", (d["MaKH"],)).fetchone()
    if kh is None:
        loi.append("%s: khong co ma khach %s" % (so_khach, d["MaKH"]))
        return False
    dat = ngay(d["NgayDat"])
    sdh = so_don_moi(dat)
    ghi_chu = (d["GhiChu"] + " ").strip() + " [phieu " + so_khach + "]"
    con.execute("INSERT INTO tblDonHang VALUES (?,?,?,?,?,?,?)", (sdh, d["MaKH"], dat, ngay(d["NgayGiao"]), 0, NGUOI_NHAP, ghi_chu.strip()))
    stt = 0
    for ma_sp, sl in d["dong"]:
        sp = con.execute("SELECT DonGia FROM tblSanPham WHERE MaSP=?", (ma_sp,)).fetchone()
        if sp is None:
            loi.append("%s: khong co ma hang %s" % (so_khach, ma_sp))
            continue
        try:
            sl = so_luong(sl)
        except ValueError as e:
            loi.append("%s: %s" % (so_khach, e))
            continue
        stt = stt + 1
        con.execute("INSERT INTO tblCTDH VALUES (?,?,?,?,?)", (sdh, stt, ma_sp, sl, sp[0]))
    con.commit()
    print("  %s -> %s (%d dong)" % (so_khach, sdh, stt))
    return True


def main(args):
    global DB
    if "--db" in args:
        i = args.index("--db")
        DB = args[i + 1]
        args = args[:i] + args[i + 2:]
    thu_muc_json = None
    if "--json" in args:
        i = args.index("--json")
        thu_muc_json = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) < 1 and thu_muc_json is None:
        print("Cach dung: python nhap_don.py <phieu_nhap.csv> [--db <duong dan db>]")
        print("           python nhap_don.py --json <thu muc JSON> [--db <duong dan db>]")
        return 1
    if not os.path.exists(DB):
        print("Khong thay CSDL: " + DB)
        return 1
    ket_noi()
    print("Nhap vao: " + DB)
    giu_lai = []
    if thu_muc_json is not None:
        ds, giu_lai = doc_json(thu_muc_json)
    else:
        ds = doc_phieu(args[0])
    ok = 0
    for so_khach, d in ds:
        if nhap_mot_don(so_khach, d):
            ok += 1
    print("Da nhap %d/%d don." % (ok, len(ds)))
    for l in loi:
        print("LOI: " + l)
    for g in giu_lai:
        print("CAN NGUOI XEM, CHUA NHAP: " + g)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
