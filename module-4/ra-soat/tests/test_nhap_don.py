"""Test cho công cụ nhập đơn: chạy đúng như em Thảo chạy (dòng lệnh), trên một bản sao của CSDL thật.

    python -m unittest discover -s tests -v
"""
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

THU_MUC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONG_CU = os.path.join(THU_MUC, "nhap_don.py")
CSDL_GOC = os.path.join(THU_MUC, "..", "..", "du-lieu", "he-thong-cu", "donhang.db")


class NhapDon(unittest.TestCase):
    def setUp(self):
        self.tam = tempfile.mkdtemp()
        self.db = os.path.join(self.tam, "donhang.db")
        shutil.copy(CSDL_GOC, self.db)

    def tearDown(self):
        shutil.rmtree(self.tam)

    def chay(self, *tham_so):
        return subprocess.run([sys.executable, CONG_CU, *tham_so, "--db", self.db], capture_output=True, text=True)

    def phieu(self, *dong):
        """Phiếu nhập CSV như P. Kinh doanh lưu từ Excel: dấu chấm phẩy, mã Windows-1258."""
        duong_dan = os.path.join(self.tam, "phieu.csv")
        with open(duong_dan, "w", encoding="cp1258", newline="") as f:
            f.write("SoDonKhach;MaKH;NgayDat;NgayGiao;MaSP;SoLuong;GhiChu\r\n")
            for d in dong:
                f.write(";".join(d) + "\r\n")
        return duong_dan

    def so_luong(self, so_don_khach):
        con = sqlite3.connect(self.db)
        dong = con.execute(
            "SELECT c.MaSP, c.SoLuong FROM tblCTDH c JOIN tblDonHang d ON c.SoDH = d.SoDH WHERE d.GhiChu LIKE ? ORDER BY c.STT",
            ("%[phieu " + so_don_khach + "]%",),
        ).fetchall()
        con.close()
        return dong

    def test_nhap_phieu_mau(self):
        kq = self.chay(os.path.join(THU_MUC, "phieu_nhap_mau.csv"))
        self.assertEqual(kq.returncode, 0, kq.stdout + kq.stderr)
        self.assertIn("Da nhap 2/2 don.", kq.stdout)
        self.assertEqual(self.so_luong("ICV-2611-05"), [("HM-WH-7712", 120), ("HM-CN-3120", 1000)])

    def test_so_luong_co_dau_cham_ngan_nghin(self):
        # Lỗi cũ: "4.000" bị đọc thành 4 cái.
        self.chay(os.path.join(THU_MUC, "phieu_nhap_mau.csv"))
        self.assertEqual(self.so_luong("LHP-2611-02"), [("HM-CN-2062", 4000), ("HM-WH-7712", 60)])

    def test_so_luong_co_dau_phay_ngan_nghin(self):
        phieu = self.phieu(["T-1", "TPW", "16/11/2026", "30/11/2026", "HM-CN-2041", "1,500", ""])
        self.chay(phieu)
        self.assertEqual(self.so_luong("T-1"), [("HM-CN-2041", 1500)])

    def test_ma_khach_khong_co_thi_bo_qua_don(self):
        phieu = self.phieu(["T-2", "XYZ", "16/11/2026", "30/11/2026", "HM-CN-2041", "500", ""])
        kq = self.chay(phieu)
        self.assertIn("Da nhap 0/1 don.", kq.stdout)
        self.assertIn("khong co ma khach XYZ", kq.stdout)

    def test_don_khong_con_dong_hop_le_thi_khong_ghi(self):
        phieu = self.phieu(["T-3", "TPW", "16/11/2026", "30/11/2026", "HM-XX-0000", "500", ""])
        kq = self.chay(phieu)
        self.assertIn("Da nhap 0/1 don.", kq.stdout)
        con = sqlite3.connect(self.db)
        so = con.execute("SELECT COUNT(*) FROM tblDonHang WHERE GhiChu LIKE '%[phieu T-3]%'").fetchone()[0]
        con.close()
        self.assertEqual(so, 0)

    def test_khong_co_csdl(self):
        kq = subprocess.run([sys.executable, CONG_CU, "phieu.csv", "--db", os.path.join(self.tam, "khong-co.db")], capture_output=True, text=True)
        self.assertEqual(kq.returncode, 1)


if __name__ == "__main__":
    unittest.main()
