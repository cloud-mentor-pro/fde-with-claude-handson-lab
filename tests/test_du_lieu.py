"""Test cho dữ liệu giả của Khách hàng mẫu: số liệu chốt ở ghi chú khoá học, luật "không chữ Nhật", và dữ liệu trong
repo đúng là thứ scripts/tao_du_lieu.py dựng ra (không ai sửa tay).

    python -m unittest discover -s tests -v

Số liệu ở đây là bảng "Số liệu chốt" của ghi chú khoá (Anthropic Exam Pro, docs/ghi-chu-soan-bai/khoa-fde.md §2). Đổi
dữ liệu thì sửa script, dựng lại, rồi sửa cả hai nơi cùng lúc.
"""
import collections
import csv
import importlib.util
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DU_LIEU = GOC / "du-lieu"
QC = DU_LIEU / "qc" / "loi_hang_ngay_2026-10.csv"

# Kana, kanji và dấu câu Nhật, như luật [chu-nhat] của quet.py bên repo khoá học.
CHU_NHAT = re.compile(r"[\u3001-\u303f\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]+")

LOI_EP = {"ba via", "Ba via", "bavia", "thiếu nhựa", "cong vênh", "sai màu", "trầy xước"}
LOI_DAY = {"bấm cos lệch", "đứt dây", "sai màu dây", "trầy xước"}


def nap_tao_du_lieu():
    spec = importlib.util.spec_from_file_location("tao_du_lieu", GOC / "scripts" / "tao_du_lieu.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dong_qc(duong_dan=QC):
    with open(duong_dan, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def la_chuyen_bo_day(dong):
    return dong["may_chuyen"].startswith("BD-")


class HeThongCu(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(DU_LIEU / "he-thong-cu" / "donhang.db")

    def tearDown(self):
        self.con.close()

    def mot(self, sql):
        return self.con.execute(sql).fetchone()[0]

    def test_so_don_thieu_ngay_giao_va_so_luong_dang_chu(self):
        self.assertEqual(self.mot("SELECT COUNT(*) FROM tblDonHang"), 1625)
        self.assertEqual(self.mot("SELECT COUNT(*) FROM tblDonHang WHERE NgayGiao = ''"), 40)
        self.assertEqual(self.mot("SELECT COUNT(*) FROM tblCTDH WHERE typeof(SoLuong) = 'text'"), 161)

    def test_khach_nhap_trung_hai_ma(self):
        ma = {r[0] for r in self.con.execute("SELECT MaKH FROM tblKhachHang")}
        self.assertEqual(ma, {"TPW", "TPW2", "LHP", "ICV", "HLX", "HMK", "MDT"})

    def test_csdl_khong_co_chu_nhat(self):
        for bang in ("tblKhachHang", "tblSanPham", "tblDonHang", "tblCTDH"):
            for dong in self.con.execute(f"SELECT * FROM {bang}"):
                for o in dong:
                    self.assertIsNone(CHU_NHAT.search(str(o)), f"{bang}: {dong}")


class DonHangMoi(unittest.TestCase):
    def test_sau_fax_bon_email_muoi_json(self):
        self.assertEqual(len(list((DU_LIEU / "don-hang-moi" / "fax").glob("*.pdf"))), 6)
        self.assertEqual(len(list((DU_LIEU / "don-hang-moi" / "email").glob("*.pdf"))), 4)
        ket_qua = sorted((GOC / "module-3" / "hoan-chinh" / "ket-qua").glob("*.json"))
        self.assertEqual(len(ket_qua), 10)
        can_xem = [p.stem for p in ket_qua if json.loads(p.read_text(encoding="utf-8"))["can_nguoi_xem"]]
        self.assertEqual(can_xem, ["TPW-2611-08"])

    def test_don_cua_cong_ty_me_viet_bang_tieng_anh(self):
        pdf = (DU_LIEU / "don-hang-moi" / "email" / "HMK-2611-06.pdf").read_bytes()
        # Bản cũ vẽ chữ Nhật bằng font CID HeiseiKakuGo; bản tiếng Anh dùng font Latinh nhúng sẵn.
        self.assertNotIn(b"HeiseiKakuGo", pdf)
        self.assertNotIn(b"UniJIS", pdf)


class SoLoiQC(unittest.TestCase):
    def setUp(self):
        self.dong = dong_qc()

    def tong(self, dong):
        return sum(int(d["sl_kiem"]) for d in dong), sum(int(d["sl_loi"]) for d in dong)

    def test_so_dong_so_kiem_so_loi(self):
        self.assertEqual(len(self.dong), 316)
        self.assertEqual(self.tong(self.dong), (246940, 2817))
        self.assertEqual(self.tong([d for d in self.dong if not la_chuyen_bo_day(d)]), (239400, 2763))
        self.assertEqual(self.tong([d for d in self.dong if la_chuyen_bo_day(d)]), (7540, 54))

    def test_loi_khop_cong_doan(self):
        for d in self.dong:
            if not d["loai_loi"]:
                self.assertEqual(d["sl_loi"], "0", d)
                continue
            cho_phep = LOI_DAY if la_chuyen_bo_day(d) else LOI_EP
            self.assertIn(d["loai_loi"], cho_phep, d)

    def test_so_loi_theo_tung_cach_viet(self):
        dem = collections.Counter()
        for d in self.dong:
            dem[d["loai_loi"]] += int(d["sl_loi"])
        del dem[""]
        self.assertEqual(dict(dem), {
            "ba via": 317, "bavia": 298, "Ba via": 289, "thiếu nhựa": 590, "cong vênh": 565, "sai màu": 393,
            "trầy xước": 315, "bấm cos lệch": 22, "đứt dây": 14, "sai màu dây": 14,
        })

    def test_may_loi_cao_nhat(self):
        theo_may = collections.defaultdict(lambda: [0, 0])
        for d in self.dong:
            theo_may[d["may_chuyen"]][0] += int(d["sl_loi"])
            theo_may[d["may_chuyen"]][1] += int(d["sl_kiem"])
        dau = sorted(theo_may, key=lambda m: (-theo_may[m][0] / theo_may[m][1], m))[:5]
        self.assertEqual(dau, ["M02", "M22", "M03", "M20", "M19"])
        self.assertEqual(theo_may["M02"], [179, 12000])

    def test_nguoi_ghi_la_cot_duy_nhat_co_ten(self):
        self.assertEqual({d["nguoi_ghi"] for d in self.dong}, {"Tú", "tu.pv", "Hưng", "Nga"})


class TaiLieuCongTyMe(unittest.TestCase):
    def test_bon_tai_lieu_tieng_anh_ten_chu_latinh(self):
        thu_muc = DU_LIEU / "cong-ty-me"
        ten = sorted(p.name for p in thu_muc.iterdir())
        self.assertEqual(ten, [
            "01_generative-ai-guidelines.md", "02_monthly-report-template.md", "03_ringi-request-template.md",
            "04_information-security-rules-excerpt.md",
        ])

    def test_cac_muc_bai_hoc_trich_toi(self):
        thu_muc = DU_LIEU / "cong-ty-me"
        ai = (thu_muc / "01_generative-ai-guidelines.md").read_text(encoding="utf-8")
        self.assertIn("Version 1.2", ai)
        self.assertIn("## 4.", ai)
        self.assertIn("record who reviewed", ai)
        an_toan = (thu_muc / "04_information-security-rules-excerpt.md").read_text(encoding="utf-8")
        self.assertIn("## Article 18", an_toan)


class KhongChuNhat(unittest.TestCase):
    def test_khong_file_van_ban_nao_co_chu_nhat(self):
        thay = []
        for p in GOC.rglob("*"):
            if not p.is_file() or {".git", ".venv", "__pycache__"} & set(p.relative_to(GOC).parts):
                continue
            if CHU_NHAT.search(str(p.relative_to(GOC))):
                thay.append(f"tên file: {p.relative_to(GOC)}")
                continue
            try:
                chu = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue
            for i, dong in enumerate(chu.splitlines(), 1):
                if CHU_NHAT.search(dong):
                    thay.append(f"{p.relative_to(GOC)}:{i}")
        self.assertEqual(thay, [])


class XemDuLieu(unittest.TestCase):
    def test_tom_tat_khop_so_lieu(self):
        ra = subprocess.run([sys.executable, str(GOC / "xem_du_lieu.py")], capture_output=True, encoding="utf-8",
                            env={**os.environ, "COLUMNS": "200", "PYTHONIOENCODING": "utf-8"}, check=True).stdout
        for cum in ("1625 đơn", "40 đơn thiếu ngày giao", "161 dòng", "6 fax, 4 email", "316 dòng", "1,14%",
                    "4 tài liệu", "tiếng Anh"):
            self.assertIn(cum, ra)
        self.assertNotIn("tiếng Nhật", ra)


class DungLai(unittest.TestCase):
    """Dựng lại dữ liệu vào thư mục tạm rồi so với bản trong repo. Cần font DejaVu của Debian, nên chỉ chạy trong máy
    dựng ảnh aep-khoa-hoc-anh hay máy có font ở đúng đường dẫn."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.tao = nap_tao_du_lieu()
        except ModuleNotFoundError as loi:
            raise unittest.SkipTest(f"thiếu thư viện của requirements-du-lieu.txt: {loi.name}")
        thieu = [f for f in (cls.tao.FONT_VN, cls.tao.FONT_VN_DAM) if not Path(f).exists()]
        if thieu:
            raise unittest.SkipTest(f"thiếu font {', '.join(thieu)}")
        cls.tam = tempfile.TemporaryDirectory()
        cls.moi = Path(cls.tam.name)
        cls.tao.dung(cls.moi)

    @classmethod
    def tearDownClass(cls):
        cls.tam.cleanup()

    def test_file_giong_het_ban_trong_repo(self):
        # File Excel ghi giờ lưu nên không so từng byte.
        tep = [p.relative_to(self.moi) for p in self.moi.rglob("*") if p.is_file() and p.suffix != ".xlsx"]
        self.assertGreater(len(tep), 20)
        for duong_dan in tep:
            if duong_dan.suffix == ".db":
                continue
            with self.subTest(str(duong_dan)):
                self.assertEqual((self.moi / duong_dan).read_bytes(), (GOC / duong_dan).read_bytes())

    def test_csdl_giong_het_ban_trong_repo(self):
        def do(duong_dan):
            con = sqlite3.connect(duong_dan)
            ra = list(con.iterdump())
            con.close()
            return ra

        self.assertEqual(do(self.moi / "du-lieu" / "he-thong-cu" / "donhang.db"),
                         do(GOC / "du-lieu" / "he-thong-cu" / "donhang.db"))


if __name__ == "__main__":
    unittest.main()
