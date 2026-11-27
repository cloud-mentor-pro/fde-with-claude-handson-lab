"""Kiểm API key trong file .env ở gốc repo: đọc được không, Claude API có nhận không.

    python kiem_key.py        # chạy trong thư mục module-3/bat-dau

Script không in key ra màn hình. Nó chỉ hỏi Claude API danh sách model (GET /v1/models), không gửi prompt nào cho
model.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

FILE_ENV = Path(__file__).resolve().parent.parent.parent / ".env"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not FILE_ENV.exists():
        sys.exit("Chưa có file .env ở gốc repo. Chép .env.example thành .env rồi dán key vào.")
    # override=True: lấy key trong .env, kể cả khi máy đã đặt sẵn biến ANTHROPIC_API_KEY khác.
    load_dotenv(FILE_ENV, override=True)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        sys.exit("File .env chưa có giá trị cho ANTHROPIC_API_KEY. Dán key ngay sau dấu = rồi lưu file.")
    if not key.startswith("sk-ant-"):
        sys.exit("Giá trị ANTHROPIC_API_KEY không bắt đầu bằng sk-ant-, có thể bạn đã dán nhầm chuỗi khác.")
    print("Đã đọc ANTHROPIC_API_KEY từ .env (script không in key ra).")

    client = anthropic.Anthropic(api_key=key)
    try:
        trang = client.models.list(limit=20)
    except anthropic.AuthenticationError:
        sys.exit("Claude API từ chối key (lỗi 401): key sai, đã bị tắt, đã bị xoá hay đã hết hạn.")
    except anthropic.APIStatusError as loi:
        sys.exit(f"Claude API trả lỗi {loi.status_code}: {loi.message}")
    except anthropic.APIConnectionError:
        sys.exit("Không kết nối được tới api.anthropic.com. Kiểm mạng hay proxy của máy.")
    ten = [m.id for m in trang.data]
    print(f"Key dùng được. Claude API trả về {len(ten)} model, ba model đầu:")
    for t in ten[:3]:
        print(f"  {t}")


if __name__ == "__main__":
    main()
