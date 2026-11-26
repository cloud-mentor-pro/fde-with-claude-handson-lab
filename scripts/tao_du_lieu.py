"""Dựng lại toàn bộ dữ liệu giả của Khách hàng mẫu trong du-lieu/ (trừ tài liệu của công ty mẹ, viết tay).

Khách hàng mẫu: Công ty TNHH Hoshimori Việt Nam (HMV), nhà máy linh kiện ô tô vốn Nhật ở Bình Dương cũ (nay thuộc
TP.HCM), công ty mẹ là Hoshimori Kogyo ở Nagoya. Mọi tên người, công ty, mã hàng đều là giả. Dữ liệu viết bằng tiếng
Việt và tiếng Anh, không có chữ Nhật, để người học không biết tiếng Nhật vẫn đọc được hết.

Dữ liệu cố tình bẩn như ở nhà máy thật: đơn hàng fax mờ và nghiêng, mỗi khách một mẫu PDF, file Excel kế hoạch có ô
gộp và ngày viết ba kiểu, hệ thống cũ lưu ngày dạng chữ và xuất CSV mã Windows-1258.

Chạy (cần Python 3.10+, requirements-du-lieu.txt và font DejaVu ở đường dẫn của Debian; máy dựng ảnh
aep-khoa-hoc-anh của Anthropic Exam Pro có sẵn):
    python scripts/tao_du_lieu.py
Cùng seed thì ra cùng dữ liệu, nên chạy lại không làm git thấy file đổi; riêng file Excel ghi giờ lưu, git vẫn báo đổi.
tests/test_du_lieu.py dựng lại vào thư mục tạm và so với bản trong repo, nên sửa dữ liệu thì sửa script rồi dựng lại,
đừng sửa tay file dữ liệu.
"""
from __future__ import annotations

import csv
import io
import json
import datetime as dt
import random
import sqlite3
import unicodedata
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

REPO = Path(__file__).resolve().parent.parent
SEED = 2026
FONT_VN = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_VN_DAM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Khách mua hàng của HMV (giả). `fax` là khách còn gửi đơn bằng fax; `mau` là kiểu mẫu đơn PDF của khách.
KHACH = [
    {"ma": "TPW", "ten": "Công ty TNHH Dây Điện Ô Tô Tân Phước", "fax": True, "mau": "bang"},
    {"ma": "LHP", "ten": "Công ty TNHH Linh Kiện Nhựa Long Hậu", "fax": True, "mau": "thu"},
    {"ma": "ICV", "ten": "Ichinose Electric Vietnam Co., Ltd.", "fax": False, "mau": "anh"},
    {"ma": "HLX", "ten": "Công ty CP Phụ Tùng Xe Máy Hồng Lạc", "fax": True, "mau": "bang"},
    {"ma": "HMK", "ten": "Hoshimori Kogyo Co., Ltd. (Nagoya)", "fax": False, "mau": "cong-ty-me"},
    {"ma": "MDT", "ten": "Công ty TNHH Cơ Điện Minh Đạt", "fax": False, "mau": "bang"},
]
# Hàng HMV làm: vỏ connector và kẹp dây ép nhựa, bó dây (wire harness) phụ.
HANG = [
    ("HM-CN-2041", "Vỏ connector 4 chân, PA66 đen", "cái", 1850),
    ("HM-CN-2062", "Vỏ connector 6 chân, PA66 xám", "cái", 2400),
    ("HM-CN-3120", "Vỏ connector 12 chân chống nước", "cái", 6900),
    ("HM-CL-0310", "Kẹp dây phi 10, PP trắng", "cái", 320),
    ("HM-CL-0516", "Kẹp dây phi 16 có tai bắt vít", "cái", 540),
    ("HM-GR-0808", "Gioăng cao su lỗ xuyên vách", "cái", 780),
    ("HM-WH-7712", "Bó dây đèn hậu xe tay ga", "bộ", 48500),
    ("HM-WH-7730", "Bó dây công tắc tay lái", "bộ", 61200),
]
# Công ty mẹ chỉ đặt bốn mã này, và đơn của công ty mẹ ghi tên hàng tiếng Anh theo danh mục ở Nagoya.
TEN_CONG_TY_ME = {
    "HM-CN-2041": "4-pole connector housing, black",
    "HM-CN-3120": "12-pole waterproof connector housing",
    "HM-CL-0516": "Clamp D16, bolt mount",
    "HM-WH-7712": "Wire harness, tail lamp",
}


def ma_cp1258(text: str) -> bytes:
    """Mã hoá như phần mềm Windows đời cũ: Windows-1258 chỉ có sẵn â, ê, ô, ơ, ư, ă, đ; dấu thanh (sắc, huyền, hỏi, ngã,
    nặng) là ký tự dấu rời đi sau chữ cái. Codec cp1258 của Python không tự tách nên phải tách tay."""
    out = bytearray()
    for ch in text:
        try:
            out += ch.encode("cp1258")
            continue
        except UnicodeEncodeError:
            pass
        parts = unicodedata.normalize("NFD", ch)
        base = unicodedata.normalize("NFC", parts[:2])
        try:
            out += base.encode("cp1258") + parts[2:].encode("cp1258")
        except UnicodeEncodeError:
            out += parts[0].encode("cp1258") + parts[1:].encode("cp1258", errors="replace")
    return bytes(out)


def ngay_ngau_nhien(rng: random.Random, thang: int) -> dt.date:
    return dt.date(2026, thang, rng.randint(1, 28))


# ---------------------------------------------------------------------------------------------- hệ thống cũ
def he_thong_cu(rng: random.Random, du_lieu: Path) -> list[dict]:
    """SQLite giả lập hệ thống quản lý đơn hàng viết năm 2011 (bản gốc là Access): ngày lưu dạng chữ dd/mm/yyyy,
    trạng thái là số, vài dòng nhập tay sai kiểu. Trả về đơn hàng tháng 10 để dùng cho file xuất và kế hoạch."""
    thu_muc = du_lieu / "he-thong-cu"
    thu_muc.mkdir(parents=True, exist_ok=True)
    db = thu_muc / "donhang.db"
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE tblKhachHang (MaKH TEXT PRIMARY KEY, TenKH TEXT, DiaChi TEXT, SoFax TEXT, GhiChu TEXT);
        CREATE TABLE tblSanPham (MaSP TEXT PRIMARY KEY, TenSP TEXT, DVT TEXT, DonGia REAL);
        CREATE TABLE tblDonHang (SoDH TEXT PRIMARY KEY, MaKH TEXT, NgayDat TEXT, NgayGiao TEXT,
                                 TrangThai INTEGER, NguoiNhap TEXT, GhiChu TEXT);
        CREATE TABLE tblCTDH (SoDH TEXT, STT INTEGER, MaSP TEXT, SoLuong, DonGia REAL);
        """
    )
    for k in KHACH:
        con.execute(
            "INSERT INTO tblKhachHang VALUES (?,?,?,?,?)",
            (k["ma"], k["ten"], "Bình Dương" if k["ma"] != "HMK" else "Minato-ku, Nagoya, Japan",
             "0274 3" + str(rng.randint(100000, 999999)) if k["fax"] else "", ""),
        )
    # Khách trùng do nhập tay: cùng công ty, mã khác, tên thừa khoảng trắng.
    con.execute("INSERT INTO tblKhachHang VALUES ('TPW2','Cty TNHH Day Dien O To  Tan Phuoc ','Bình Dương','','nhập trùng?')")
    for ma, ten, dvt, gia in HANG:
        con.execute("INSERT INTO tblSanPham VALUES (?,?,?,?)", (ma, ten, dvt, gia))

    nguoi_nhap = ["diep.ln", "thao.nt", "thao.nt", "admin"]
    thang10 = []
    so = 0
    for thang in range(1, 11):
        for _ in range(rng.randint(140, 180)):
            so += 1
            khach = rng.choice(KHACH + [KHACH[0]])
            ma_kh = "TPW2" if khach["ma"] == "TPW" and rng.random() < 0.08 else khach["ma"]
            dat = ngay_ngau_nhien(rng, thang)
            giao = dat + dt.timedelta(days=rng.choice([7, 10, 14, 14, 21]))
            trang_thai = 2 if thang < 10 else rng.choice([0, 1, 1, 2])
            if rng.random() < 0.02:
                trang_thai = 9  # huỷ
            ngay_giao = "" if rng.random() < 0.03 else giao.strftime("%d/%m/%Y")
            ghi_chu = rng.choice(["", "", "", "", "giao gấp!!", "KH đổi số lượng qua đt", "xem fax lần 2", "chờ xác nhận giá"])
            so_dh = f"DH{dat:%y%m}-{so:04d}"
            con.execute(
                "INSERT INTO tblDonHang VALUES (?,?,?,?,?,?,?)",
                (so_dh, ma_kh, dat.strftime("%d/%m/%Y"), ngay_giao, trang_thai, rng.choice(nguoi_nhap), ghi_chu),
            )
            dong = []
            for stt, (ma_sp, ten, dvt, gia) in enumerate(rng.sample(HANG, rng.randint(1, 4)), start=1):
                sl = rng.choice([200, 500, 1000, 1200, 2000, 3000, 5000]) if dvt == "cái" else rng.choice([50, 100, 150, 300])
                # Vài dòng nhập số lượng dạng chữ có dấu chấm ngăn nghìn, như người nhập gõ từ fax.
                sl_luu = f"{sl:,}".replace(",", ".") if rng.random() < 0.04 else sl
                con.execute("INSERT INTO tblCTDH VALUES (?,?,?,?,?)", (so_dh, stt, ma_sp, sl_luu, gia))
                dong.append({"ma_sp": ma_sp, "ten": ten, "so_luong": sl, "don_gia": gia})
            if thang == 10:
                thang10.append({"so_dh": so_dh, "ma_kh": ma_kh, "dat": dat, "giao": giao, "trang_thai": trang_thai, "dong": dong, "ghi_chu": ghi_chu})
    con.commit()
    con.close()

    # File xuất CSV của hệ thống cũ: dấu chấm phẩy, mã Windows-1258, ngày dd/mm/yyyy.
    with open(thu_muc / "xuat_don_hang_2026-10.csv", "wb") as tep:
        f = io.StringIO(newline="")
        w = csv.writer(f, delimiter=";")
        w.writerow(["SoDH", "MaKH", "NgayDat", "NgayGiao", "MaSP", "SoLuong", "DonGia", "TrangThai", "GhiChu"])
        for dh in thang10:
            for d in dh["dong"]:
                w.writerow([dh["so_dh"], dh["ma_kh"], f"{dh['dat']:%d/%m/%Y}", f"{dh['giao']:%d/%m/%Y}", d["ma_sp"], d["so_luong"], d["don_gia"], dh["trang_thai"], dh["ghi_chu"]])
        tep.write(ma_cp1258(f.getvalue()))
    return thang10


# ---------------------------------------------------------------------------------------------- đơn hàng mới
def don_moi(rng: random.Random) -> list[dict]:
    """Đơn hàng mới tuần 46 (9–13/11/2026) chưa nhập vào hệ thống cũ: việc của Module 3 là đọc chúng ra JSON."""
    don = []
    for i, khach in enumerate([KHACH[0], KHACH[1], KHACH[3], KHACH[1], KHACH[2], KHACH[4], KHACH[5], KHACH[0], KHACH[2], KHACH[3]], start=1):
        dat = dt.date(2026, 11, 9 + (i - 1) // 2)
        dong = []
        hang = HANG if khach["ma"] != "HMK" else [h for h in HANG if h[0] in TEN_CONG_TY_ME]
        for ma_sp, ten, dvt, gia in rng.sample(hang, rng.randint(1, 3)):
            sl = rng.choice([500, 1000, 1500, 2000, 4000]) if dvt == "cái" else rng.choice([60, 120, 200])
            dong.append({"ma_sp": ma_sp, "ten": ten, "dvt": dvt, "so_luong": sl})
        don.append({"so": f"{khach['ma']}-2611-{i:02d}", "khach": khach, "dat": dat, "giao": dat + dt.timedelta(days=rng.choice([10, 14, 21])), "dong": dong})
    return don


def fax(d: dict, rng: random.Random, duong_dan: Path):
    """Đơn fax: vẽ như bản scan, nghiêng, lốm đốm, đen trắng; chữ viết tay ở cột số lượng."""
    w, h = 1240, 1754
    img = Image.new("L", (w, h), 255)
    ve = ImageDraw.Draw(img)
    to = ImageFont.truetype(FONT_VN_DAM, 40)
    vua = ImageFont.truetype(FONT_VN, 26)
    tay = ImageFont.truetype(FONT_VN, 30)
    gio = f"{rng.randint(7, 17):02d}:{rng.randint(0, 59):02d}"
    ve.text((80, 60), f"FAX: {rng.choice(['0274 3812 655', '0274 3779 120'])}   {d['dat']:%d/%m/%Y} {gio}   P.1/1", font=vua, fill=60)
    ve.text((80, 140), d["khach"]["ten"].upper(), font=to, fill=0)
    ve.text((80, 220), "ĐƠN ĐẶT HÀNG" if d["khach"]["mau"] != "thu" else "PHIẾU ĐẶT HÀNG", font=to, fill=0)
    if d["khach"]["mau"] == "thu":
        ve.text((560, 232), "(gửi P. Kinh doanh HMV, chị Diệp)", font=vua, fill=0)
    ve.text((80, 300), f"Số: {d['so']}        Ngày: {d['dat']:%d/%m/%Y}", font=vua, fill=0)
    ve.text((80, 345), "Kính gửi: Công ty TNHH Hoshimori Việt Nam", font=vua, fill=0)
    y = 430
    cot = [80, 180, 470, 900, 1060]
    ve.rectangle((70, y - 10, 1170, y + 50 * (len(d["dong"]) + 1) + 10), outline=0, width=2)
    for x, nhan in zip(cot, ["STT", "Mã hàng", "Tên hàng", "Số lượng", "ĐVT"]):
        ve.text((x, y), nhan, font=vua, fill=0)
    for i, dong in enumerate(d["dong"], start=1):
        yy = y + 50 * i
        ve.line((70, yy - 8, 1170, yy - 8), fill=80, width=1)
        ve.text((cot[0], yy), str(i), font=vua, fill=0)
        ve.text((cot[1], yy), dong["ma_sp"], font=vua, fill=0)
        ve.text((cot[2], yy), dong["ten"][:24], font=vua, fill=0)
        # Số lượng viết tay: lệch dòng, nét đậm nhạt.
        ve.text((cot[3] + rng.randint(-10, 10), yy + rng.randint(-6, 6)), f"{dong['so_luong']:,}".replace(",", "."), font=tay, fill=rng.randint(0, 70))
        ve.text((cot[4], yy), dong["dvt"], font=vua, fill=0)
    yy = y + 50 * (len(d["dong"]) + 1) + 60
    ve.text((80, yy), f"Ngày giao yêu cầu: {d['giao']:%d/%m}", font=vua, fill=0)
    ve.text((80, yy + 50), rng.choice(["Giao tại kho KH, trước 10h sáng.", "Giao 2 đợt, gọi trước khi giao.", "Hàng gấp, xác nhận giúp trong ngày."]), font=tay, fill=30)
    ve.text((820, yy + 140), "Người đặt hàng", font=vua, fill=0)
    ve.text((830, yy + 200), rng.choice(["(ký) Trinh", "(ký) Phúc", "(ký) Lan"]), font=tay, fill=20)
    img = img.rotate(rng.uniform(-1.6, 1.6), fillcolor=255, resample=Image.BICUBIC)
    # Bản fax: chấm bẩn, một vệt dọc của đầu quét, nét chữ nhoè rồi cắt về đen trắng.
    ve = ImageDraw.Draw(img)
    for _ in range(2500):
        x, y = rng.randrange(w), rng.randrange(h)
        ve.point((x, y), fill=0)
    x = rng.randint(200, 1000)
    ve.line((x, 0, x, h), fill=110, width=2)
    img = img.filter(ImageFilter.GaussianBlur(1.1)).point(lambda p: 0 if p < 170 else 255).convert("1")
    ngay_tao = dt.datetime.combine(d["dat"], dt.time(8))
    img.save(duong_dan, "PDF", resolution=150, creationDate=ngay_tao.timetuple(), modDate=ngay_tao.timetuple())


# Mẫu đơn email theo `mau` của khách: tiêu đề, dòng đầu đơn, nhãn cột, đơn vị, ghi chú cuối, chỗ bắt đầu bảng.
MAU_EMAIL = {
    "cong-ty-me": {
        "tieu_de": "ORDER SHEET",
        "dau": lambda d: [
            f"Order No.: {d['so']}", f"Order date: {d['dat']:%Y/%m/%d}", "To: Hoshimori Vietnam Co., Ltd.",
            "From: Hoshimori Kogyo Co., Ltd., International Sales Dept. (Nagoya)", f"Due date: {d['giao']:%Y/%m/%d}",
            "Payment terms: closing at month end, payment at the end of the following month",
        ],
        "cot": ["Item code", "Item name", "Quantity", "Unit"],
        "don_vi": {"cái": "pcs", "bộ": "set"},
        "ghi_chu": "Notes: Enclose the inspection report in each carton.",
        "bang_y": 240,
    },
    "anh": {
        "tieu_de": "PURCHASE ORDER",
        "dau": lambda d: [
            f"PO No.: {d['so']}", f"Date: {d['dat']:%b %d, %Y}", "To: Hoshimori Vietnam Co., Ltd.",
            f"Delivery: {d['giao']:%Y-%m-%d} (DDP our warehouse)",
        ],
        "cot": ["Part No.", "Description", "Qty", "Unit"],
        "don_vi": {"cái": "pcs", "bộ": "set"},
        "ghi_chu": "Remarks: Please attach CoC with each lot.",
        "bang_y": 210,
    },
    "bang": {
        "tieu_de": "ĐƠN ĐẶT HÀNG",
        "dau": lambda d: [
            f"Số đơn: {d['so']}", f"Ngày đặt: {d['dat']:%d-%m-%Y}", "Bên bán: Công ty TNHH Hoshimori Việt Nam",
            f"Thời hạn giao: {d['giao']:%d-%m-%Y}",
        ],
        "cot": ["Mã hàng", "Tên hàng", "Số lượng", "ĐVT"],
        "don_vi": {},
        "ghi_chu": "Ghi chú: giao kèm phiếu kiểm tra chất lượng.",
        "bang_y": 210,
    },
}


def pdf_email(d: dict, duong_dan: Path):
    """Đơn gửi qua email: PDF có chữ thật, mỗi khách một mẫu (MAU_EMAIL). ICV gửi PO tiếng Anh; công ty mẹ gửi order
    sheet tiếng Anh theo mẫu của Nagoya (ngày yyyy/mm/dd, điều khoản thanh toán); khách khác gửi đơn tiếng Việt."""
    mau = MAU_EMAIL[d["khach"]["mau"]]
    c = canvas.Canvas(str(duong_dan), pagesize=A4, invariant=1)
    w, h = A4
    c.setFont("VN-Dam", 16)
    c.drawString(50, h - 70, mau["tieu_de"])
    c.setFont("VN", 10)
    for i, text in enumerate(mau["dau"](d)):
        c.drawString(50, h - 110 - 16 * i, text)
    y = h - mau["bang_y"]
    for x, n in zip([50, 160, 420, 500], mau["cot"]):
        c.drawString(x, y, n)
    c.line(50, y - 4, 545, y - 4)
    for dong in d["dong"]:
        y -= 18
        ten = TEN_CONG_TY_ME.get(dong["ma_sp"], dong["ten"]) if d["khach"]["ma"] == "HMK" else dong["ten"]
        c.drawString(50, y, dong["ma_sp"])
        c.drawString(160, y, ten[:38])
        c.drawRightString(470, y, f"{dong['so_luong']:,}")
        c.drawString(500, y, mau["don_vi"].get(dong["dvt"], dong["dvt"]))
    c.line(50, y - 6, 545, y - 6)
    c.drawString(50, y - 30, mau["ghi_chu"])
    c.showPage()
    c.save()


# Đơn Module 3 đọc chưa chắc (số lượng viết tay bị vệt dọc của đầu fax đè lên): JSON đánh dấu để người so lại với bản fax.
DON_CAN_NGUOI_XEM = {"TPW-2611-08": "Số lượng viết tay ở dòng 1 bị vệt dọc đè lên, đọc chưa chắc"}


def json_don(d: dict, nguon: str) -> dict:
    """Đơn đã đọc thành JSON, đúng dạng script đọc đơn của Module 3 xuất ra. Module 4 nhập các file này vào hệ thống cũ."""
    return {
        "so_don_khach": d["so"],
        "ma_khach": d["khach"]["ma"],
        "nguon": nguon,
        "ngay_dat": d["dat"].isoformat(),
        "ngay_giao": d["giao"].isoformat(),
        "dong": [{"ma_hang": dong["ma_sp"], "so_luong": dong["so_luong"], "don_vi": dong["dvt"]} for dong in d["dong"]],
        "can_nguoi_xem": d["so"] in DON_CAN_NGUOI_XEM,
        "ly_do": DON_CAN_NGUOI_XEM.get(d["so"], ""),
    }


def don_hang(rng: random.Random, du_lieu: Path):
    thu_muc = du_lieu / "don-hang-moi"
    (thu_muc / "fax").mkdir(parents=True, exist_ok=True)
    (thu_muc / "email").mkdir(parents=True, exist_ok=True)
    # JSON mẫu của Module 3 (đọc đơn bằng Claude API), để làm Module 4 mà chưa cần API key.
    ket_qua = du_lieu.parent / "module-3" / "hoan-chinh" / "ket-qua"
    ket_qua.mkdir(parents=True, exist_ok=True)
    for d in don_moi(rng):
        if d["khach"]["fax"]:
            nguon = f"fax/fax_{d['dat']:%Y%m%d}_{d['so']}.pdf"
            fax(d, rng, thu_muc / nguon)
        else:
            nguon = f"email/{d['so']}.pdf"
            pdf_email(d, thu_muc / nguon)
        with open(ket_qua / f"{d['so']}.json", "w", encoding="utf-8", newline="") as tep:
            json.dump(json_don(d, nguon), tep, ensure_ascii=False, indent=2)
            tep.write("\n")


# ---------------------------------------------------------------------------------------------- kế hoạch sản xuất
def ke_hoach(rng: random.Random, thang10: list[dict], du_lieu: Path):
    """File Excel kế hoạch sản xuất tháng 10 của phòng sản xuất: ô gộp, ngày viết ba kiểu, dòng tổng giữa bảng,
    một cột bị ẩn, ghi chú chen vào ô số."""
    thu_muc = du_lieu / "ke-hoach-san-xuat"
    thu_muc.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "KH T10"
    ws.merge_cells("A1:H1")
    ws["A1"] = "KẾ HOẠCH SẢN XUẤT THÁNG 10/2026 - XƯỞNG ÉP NHỰA & BÓ DÂY (bản cập nhật 28/10, chị Hà duyệt)"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")
    dau = ["STT", "Số ĐH", "Khách", "Mã hàng", "SL đặt", "Máy / Chuyền", "Ngày SX", "Ngày giao", "Ghi chú"]
    ws.append([])
    ws.append(dau)
    for o in ws[3]:
        o.font = Font(bold=True)
        o.fill = PatternFill("solid", fgColor="FFF2CC")
    may = [f"Máy ép {n:02d}" for n in range(1, 25)] + ["Chuyền BD-1", "Chuyền BD-2", "Chuyền BD-3"]
    stt = 0
    for tuan in range(1, 5):
        for dh in [x for x in thang10 if (x["dat"].day - 1) // 7 + 1 == tuan]:
            for d in dh["dong"]:
                stt += 1
                sx = dh["giao"] - dt.timedelta(days=rng.randint(2, 6))
                kieu = rng.random()
                ngay_sx = sx if kieu < 0.6 else (sx.strftime("%d/%m") if kieu < 0.85 else sx.strftime("%d-%b"))
                so_luong = d["so_luong"] if rng.random() > 0.05 else f"{d['so_luong']} (KH báo tăng?)"
                tram = rng.choice(may[-3:]) if d["ma_sp"].startswith("HM-WH") else rng.choice(may[:24])
                ws.append([stt, dh["so_dh"], dh["ma_kh"], d["ma_sp"], so_luong, tram, ngay_sx, dh["giao"], dh["ghi_chu"]])
        ws.append(["", "", "", f"TỔNG TUẦN {tuan}", f"=SUM(E4:E{ws.max_row})", "", "", "", ""])
        ws.cell(ws.max_row, 4).font = Font(bold=True)
    for o in ws["G"] + ws["H"]:
        if isinstance(o.value, (dt.date, dt.datetime)):
            o.number_format = "dd/mm/yyyy"
    ws.column_dimensions["F"].hidden = True
    for cot, rong in zip("ABCDEFGHI", [5, 14, 7, 13, 18, 13, 11, 11, 26]):
        ws.column_dimensions[cot].width = rong
    wb.properties.created = dt.datetime(2026, 10, 28, 8, 30)
    wb.properties.modified = dt.datetime(2026, 10, 28, 8, 30)
    wb.save(thu_muc / "KeHoachSX_T10-2026_v3_final.xlsx")


# ---------------------------------------------------------------------------------------------- QC
# Sổ lỗi ban đầu rút loại lỗi từ một danh sách chung, nên máy ép có cả lỗi dây và chuyền bó dây có cả lỗi ép. Hai bảng
# dưới đổi loại lỗi sai công đoạn sang một lỗi của đúng công đoạn. Vẫn rút đúng một lần `rng.choice(LOI)` mỗi dòng như
# bản đầu, nên số dòng, số kiểm, số lỗi từng dòng và mọi dữ liệu dựng sau sổ lỗi (đơn tuần 46, JSON) không đổi.
LOI = ["ba via", "Ba via", "bavia", "thiếu nhựa", "cong vênh", "sai màu", "đứt dây", "bấm cos lệch", "trầy xước"]
DOI_LOI_MAY_EP = {"đứt dây": "thiếu nhựa", "bấm cos lệch": "cong vênh"}
DOI_LOI_BO_DAY = {"ba via": "bấm cos lệch", "bavia": "bấm cos lệch", "Ba via": "đứt dây", "thiếu nhựa": "đứt dây",
                  "cong vênh": "sai màu dây", "sai màu": "sai màu dây"}


def qc(rng: random.Random, du_lieu: Path):
    """Sổ lỗi QC hằng ngày tháng 10, tổ trưởng ca gõ tay: loại lỗi viết không thống nhất, ghi chú viết tắt. Máy ép chỉ
    có lỗi ép (ba via viết ba kiểu, thiếu nhựa, cong vênh, sai màu, trầy xước), chuyền bó dây chỉ có lỗi dây (bấm cos
    lệch, đứt dây, sai màu dây, trầy xước)."""
    thu_muc = du_lieu / "qc"
    thu_muc.mkdir(parents=True, exist_ok=True)
    ghi_chu = ["", "", "", "đã báo bảo trì", "khuôn mòn, chờ thay", "NVL ẩm, sấy lại 4h", "ca 2 thiếu người",
               "KH TPW khiếu nại lô 10/10"]
    with open(thu_muc / "loi_hang_ngay_2026-10.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ngay", "ca", "may_chuyen", "ma_hang", "sl_kiem", "sl_loi", "loai_loi", "ghi_chu", "nguoi_ghi"])
        for ngay in range(1, 32):
            for ca in (1, 2):
                for _ in range(rng.randint(3, 7)):
                    ma = rng.choice(HANG)[0]
                    kiem = rng.choice([500, 800, 1000, 1200, 2000]) if not ma.startswith("HM-WH") else rng.choice([60, 80, 120])
                    sl_loi = max(0, int(rng.gauss(kiem * 0.012, kiem * 0.006)))
                    bo_day = ma.startswith("HM-WH")
                    tram = f"BD-{rng.randint(1, 3)}" if bo_day else f"M{rng.randint(1, 24):02d}"
                    loai = ""
                    if sl_loi:
                        loai = rng.choice(LOI)
                        loai = (DOI_LOI_BO_DAY if bo_day else DOI_LOI_MAY_EP).get(loai, loai)
                    ghi = rng.choice(ghi_chu)  # rút ghi chú trước người ghi, đúng thứ tự của bản đầu
                    nguoi_ghi = rng.choice(["Tú", "Hưng", "Nga", "tu.pv"])
                    w.writerow([f"{ngay:02d}/10/2026", ca, tram, ma, kiem, sl_loi, loai, ghi, nguoi_ghi])


def dung(repo: Path = REPO) -> None:
    """Dựng mọi file dữ liệu vào `repo` (thư mục gốc của repo mẫu, hay thư mục tạm khi test)."""
    du_lieu = repo / "du-lieu"
    rng = random.Random(SEED)
    pdfmetrics.registerFont(TTFont("VN", FONT_VN))
    pdfmetrics.registerFont(TTFont("VN-Dam", FONT_VN_DAM))
    thang10 = he_thong_cu(rng, du_lieu)
    ke_hoach(rng, thang10, du_lieu)
    qc(rng, du_lieu)
    don_hang(rng, du_lieu)


def main():
    dung()
    print(f"Đã dựng dữ liệu giả trong {REPO / 'du-lieu'}")


if __name__ == "__main__":
    main()
