"""Test cho hai script của Module 1: bo_ten.py (bỏ cột tên người khỏi sổ lỗi QC) và dem_loi.py (đếm lỗi để đối chiếu
con số Claude đưa ra). Chạy script bằng dòng lệnh như người học chạy.

    python -m unittest discover -s tests -v
"""
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
BAT_DAU = GOC / "module-1" / "bat-dau"
QC = GOC / "du-lieu" / "qc" / "loi_hang_ngay_2026-10.csv"
KHONG_TEN = "so_loi_qc_t10_khong_ten.csv"


# Không đặt PYTHONIOENCODING hay PYTHONUTF8: stdout là pipe như khi Claude Code chạy lệnh, nên trên Windows Python dùng
# bảng mã của máy (cp1258, cp932…) và script phải tự in UTF-8.
MOI_TRUONG = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}


def chay(script, *tham_so):
    """Chạy script (tên trong module-1/bat-dau hay đường dẫn) trong thư mục của nó, như người học chạy."""
    duong_dan = BAT_DAU / script
    return subprocess.run([sys.executable, str(duong_dan), *map(str, tham_so)], capture_output=True,
                          encoding="utf-8", cwd=duong_dan.parent, env=MOI_TRUONG)


def doc(duong_dan):
    with open(duong_dan, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


class BoTen(unittest.TestCase):
    def setUp(self):
        self.tam = Path(tempfile.mkdtemp())
        self.ra = self.tam / KHONG_TEN

    def tearDown(self):
        shutil.rmtree(self.tam)

    def test_bo_dung_cot_nguoi_ghi(self):
        kq = chay("bo_ten.py", QC, self.ra)
        self.assertEqual(kq.returncode, 0, kq.stderr)
        goc, moi = doc(QC), doc(self.ra)
        self.assertEqual(goc[0][-1], "nguoi_ghi")
        self.assertEqual(moi[0], goc[0][:-1])
        self.assertEqual(len(moi), len(goc))
        self.assertEqual([d for d in moi[1:]], [d[:-1] for d in goc[1:]])

    def test_bao_so_dong_va_ten_file(self):
        kq = chay("bo_ten.py", QC, self.ra)
        self.assertEqual(kq.stdout.strip(), f"Đã ghi 316 dòng, bỏ cột nguoi_ghi, vào {KHONG_TEN}")

    def test_khong_doi_file_goc(self):
        truoc = hashlib.sha256(QC.read_bytes()).hexdigest()
        chay("bo_ten.py", QC, self.ra)
        self.assertEqual(hashlib.sha256(QC.read_bytes()).hexdigest(), truoc)

    def test_mac_dinh_ghi_canh_script(self):
        # Người học chạy `python bo_ten.py` trong module-1/bat-dau, không tham số. Chép script sang thư mục tạm cho khỏi
        # ghi vào repo khi test.
        thu_muc = self.tam / "module-1" / "bat-dau"
        thu_muc.mkdir(parents=True)
        shutil.copy(BAT_DAU / "bo_ten.py", thu_muc)
        (self.tam / "du-lieu" / "qc").mkdir(parents=True)
        shutil.copy(QC, self.tam / "du-lieu" / "qc")
        kq = chay(thu_muc / "bo_ten.py")
        self.assertEqual(kq.returncode, 0, kq.stderr)
        self.assertTrue((thu_muc / KHONG_TEN).exists())

    def test_ban_hoan_chinh_khop_du_lieu_hien_tai(self):
        chay("bo_ten.py", QC, self.ra)
        self.assertEqual((GOC / "module-1" / "hoan-chinh" / KHONG_TEN).read_bytes(), self.ra.read_bytes())


class DemLoi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        kq = chay("dem_loi.py")
        if kq.returncode != 0:
            raise AssertionError(kq.stderr)
        cls.ra = kq.stdout
        cls.dong = [d.strip() for d in kq.stdout.splitlines()]

    def dong_dau(self, dau):
        thay = [d for d in self.dong if d.startswith(dau)]
        self.assertTrue(thay, f"không có dòng bắt đầu bằng {dau!r}:\n{self.ra}")
        return thay[0].split()

    def test_ti_le_loi_chung(self):
        self.assertIn("316 dòng, 2817 lỗi trên 246940 cái kiểm, tỉ lệ lỗi 1,14%", self.ra)

    def test_gop_cach_viet_cua_mot_loi(self):
        self.assertIn('ba via 904 (317 "ba via", 298 "bavia", 289 "Ba via")', " ".join(self.ra.split()))
        loai = [d.split("  ")[0] for d in self.dong if d and d[0].isalpha() and "  " in d]
        self.assertNotIn("bavia", loai)
        self.assertEqual(self.dong_dau("thiếu nhựa")[2], "590")

    def test_theo_cong_doan(self):
        self.assertEqual(self.dong_dau("máy ép")[2:4], ["2763", "lỗi"])
        self.assertEqual(self.dong_dau("chuyền bó dây")[3], "54")

    def test_nam_may_loi_cao_nhat(self):
        may = [d.split()[0] for d in self.dong if d[:1] in ("M", "B") and "%" in d and "(" in d]
        self.assertEqual(may, ["M02", "M22", "M03", "M20", "M19"])
        self.assertEqual(self.dong_dau("M02")[1:], ["1,49%", "(179/12000)"])

    def test_chay_duoc_tren_ban_khong_ten(self):
        kq = chay("dem_loi.py", GOC / "module-1" / "hoan-chinh" / KHONG_TEN)
        self.assertEqual(kq.returncode, 0, kq.stderr)
        self.assertEqual(kq.stdout.splitlines()[1:], self.ra.splitlines()[1:])


if __name__ == "__main__":
    unittest.main()
