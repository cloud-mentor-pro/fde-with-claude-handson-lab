"""Chép sổ lỗi QC tháng 10 sang một file mới không có cột tên người (`nguoi_ghi`), để đưa cho Claude thử mà không
gửi thông tin cá nhân. Các cột khác giữ nguyên từng chữ.

    python bo_ten.py                     # đọc ../../du-lieu/qc/loi_hang_ngay_2026-10.csv, ghi file cạnh script
    python bo_ten.py <file vào> <file ra>

Chỉ dùng thư viện có sẵn của Python.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

THU_MUC = Path(__file__).resolve().parent
VAO = THU_MUC.parent.parent / "du-lieu" / "qc" / "loi_hang_ngay_2026-10.csv"
RA = THU_MUC / "so_loi_qc_t10_khong_ten.csv"
COT_TEN = "nguoi_ghi"


def bo_cot_ten(vao: Path, ra: Path) -> int:
    """Ghi `vao` sang `ra` mà bỏ cột tên người; trả về số dòng dữ liệu (không tính dòng tiêu đề)."""
    with open(vao, encoding="utf-8", newline="") as f:
        dong = list(csv.reader(f))
    vi_tri = dong[0].index(COT_TEN)
    with open(ra, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for d in dong:
            w.writerow(d[:vi_tri] + d[vi_tri + 1:])
    return len(dong) - 1


def main(tham_so: list[str]) -> None:
    vao = Path(tham_so[0]) if tham_so else VAO
    ra = Path(tham_so[1]) if len(tham_so) > 1 else RA
    so_dong = bo_cot_ten(vao, ra)
    print(f"Đã ghi {so_dong} dòng, bỏ cột {COT_TEN}, vào {ra.name}")


if __name__ == "__main__":
    # In UTF-8 cả khi stdout là pipe (Claude Code chạy lệnh), vì bảng mã mặc định của Windows không có đủ chữ Việt.
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
