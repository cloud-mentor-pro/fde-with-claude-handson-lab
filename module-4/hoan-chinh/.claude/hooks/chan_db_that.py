"""Hook PreToolUse: không cho Claude Code ghi vào CSDL thật của hệ thống đơn hàng (du-lieu/he-thong-cu/donhang.db).

Claude Code gửi lời gọi tool dưới dạng JSON qua stdin. Thoát mã 2 là chặn, và chữ in ra stderr được gửi lại cho Claude
để nó biết vì sao bị chặn. Thoát mã 0 là để lời gọi đi tiếp qua bước hỏi quyền như thường.
"""
import json
import re
import sys

CSDL_THAT = re.compile(r"he-thong-cu[/\\]donhang\.db")
# Lệnh chạy công cụ: python, python3, py (Windows) rồi tới nhap_don.py. Lệnh chỉ đọc file như cat, git diff thì cho qua.
CHAY_CONG_CU = re.compile(r"\b(python[0-9.]*|py)(\.exe)?\s+(\S*[/\\])?nhap_don\.py\b")
LENH_GHI_SQL = re.compile(r"\b(insert|update|delete|drop|alter|replace|create)\b", re.IGNORECASE)


# Lý do in ra có dấu tiếng Việt; trên Windows stderr không mặc định UTF-8.
sys.stderr.reconfigure(encoding="utf-8")


def chan(ly_do: str) -> None:
    print(f"Bị hook chan_db_that chặn: {ly_do}. Hãy dùng một bản sao CSDL và truyền --db <bản sao>.", file=sys.stderr)
    sys.exit(2)


loi_goi = json.load(sys.stdin)
tool = loi_goi.get("tool_name", "")
dau_vao = loi_goi.get("tool_input", {})

if tool in ("Bash", "PowerShell"):
    lenh = dau_vao.get("command", "")
    if CHAY_CONG_CU.search(lenh):
        # Không có --db thì công cụ ghi vào CSDL thật ghi trong cau_hinh.ini.
        tim = re.search(r"--db\s+(\S+)", lenh)
        if tim is None:
            chan("nhap_don.py chạy không có --db sẽ ghi vào CSDL thật")
        if CSDL_THAT.search(tim.group(1)):
            chan("--db đang trỏ vào CSDL thật")
    if CSDL_THAT.search(lenh) and LENH_GHI_SQL.search(lenh):
        chan("lệnh có câu SQL ghi vào CSDL thật")

if tool in ("Edit", "Write", "MultiEdit"):
    if CSDL_THAT.search(dau_vao.get("file_path", "")):
        chan("không sửa trực tiếp file CSDL thật")

sys.exit(0)
