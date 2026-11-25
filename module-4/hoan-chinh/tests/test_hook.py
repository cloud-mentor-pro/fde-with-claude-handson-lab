"""Test cho hook chan_db_that: gửi lời gọi tool giả như Claude Code gửi, xem hook chặn hay cho qua."""
import json
import os
import subprocess
import sys
import unittest

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "hooks", "chan_db_that.py")


def chay_hook(tool, **dau_vao):
    kq = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": tool, "tool_input": dau_vao}), capture_output=True, text=True)
    return kq.returncode


class Hook(unittest.TestCase):
    def test_chan_nhap_don_khong_co_db(self):
        self.assertEqual(chay_hook("Bash", command="python nhap_don.py phieu_nhap_mau.csv"), 2)

    def test_chan_db_tro_vao_csdl_that(self):
        self.assertEqual(chay_hook("Bash", command="python nhap_don.py x.csv --db ../../du-lieu/he-thong-cu/donhang.db"), 2)

    def test_cho_qua_khi_db_la_ban_sao(self):
        self.assertEqual(chay_hook("Bash", command="python nhap_don.py x.csv --db thu.db"), 0)

    def test_chan_sql_ghi_vao_csdl_that(self):
        self.assertEqual(chay_hook("Bash", command='sqlite3 ../../du-lieu/he-thong-cu/donhang.db "DELETE FROM tblDonHang"'), 2)

    def test_cho_doc_csdl_that(self):
        self.assertEqual(chay_hook("Bash", command='sqlite3 ../../du-lieu/he-thong-cu/donhang.db "SELECT COUNT(*) FROM tblDonHang"'), 0)

    def test_cho_chep_csdl_that_ra_ban_sao(self):
        self.assertEqual(chay_hook("Bash", command="cp ../../du-lieu/he-thong-cu/donhang.db thu.db"), 0)

    def test_chan_python3_va_py(self):
        self.assertEqual(chay_hook("Bash", command="python3 ./nhap_don.py phieu_nhap_mau.csv"), 2)
        self.assertEqual(chay_hook("Bash", command="py nhap_don.py --json ket-qua"), 2)

    def test_chan_lenh_powershell(self):
        self.assertEqual(chay_hook("PowerShell", command="python nhap_don.py phieu_nhap_mau.csv"), 2)

    def test_cho_doc_file_nhap_don(self):
        self.assertEqual(chay_hook("Bash", command="cat nhap_don.py"), 0)
        self.assertEqual(chay_hook("Bash", command="git --no-pager diff nhap_don.py"), 0)

    def test_chan_sua_file_csdl_that(self):
        self.assertEqual(chay_hook("Write", file_path="/x/du-lieu/he-thong-cu/donhang.db", content=""), 2)


if __name__ == "__main__":
    unittest.main()
