"""In tóm tắt dữ liệu của Khách hàng mẫu (Hoshimori Việt Nam): có những nguồn nào, bao nhiêu, bẩn chỗ nào.

    python xem_du_lieu.py
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from rich.console import Console
from rich.table import Table

DU_LIEU = Path(__file__).resolve().parent / "du-lieu"


def don_he_thong_cu() -> tuple[int, int, int]:
    """Số đơn trong hệ thống cũ, số đơn thiếu ngày giao, số dòng lưu số lượng dạng chữ."""
    con = sqlite3.connect(DU_LIEU / "he-thong-cu" / "donhang.db")
    tong = con.execute("SELECT COUNT(*) FROM tblDonHang").fetchone()[0]
    thieu_ngay = con.execute("SELECT COUNT(*) FROM tblDonHang WHERE NgayGiao = ''").fetchone()[0]
    so_chu = con.execute("SELECT COUNT(*) FROM tblCTDH WHERE typeof(SoLuong) = 'text'").fetchone()[0]
    con.close()
    return tong, thieu_ngay, so_chu


def loi_qc() -> tuple[int, float, int]:
    """Số dòng sổ lỗi QC, tỉ lệ lỗi chung (%), số cách viết khác nhau của lỗi "ba via"."""
    with open(DU_LIEU / "qc" / "loi_hang_ngay_2026-10.csv", encoding="utf-8") as f:
        dong = list(csv.DictReader(f))
    kiem = sum(int(d["sl_kiem"]) for d in dong)
    loi = sum(int(d["sl_loi"]) for d in dong)
    cach_viet = len({d["loai_loi"] for d in dong if d["loai_loi"].lower().replace(" ", "") == "bavia"})
    return len(dong), loi / kiem * 100, cach_viet


def dem(thu_muc: Path, mau: str) -> int:
    return len(list(thu_muc.glob(mau)))


def main():
    tong, thieu_ngay, so_chu = don_he_thong_cu()
    so_dong_qc, ti_le, cach_viet = loi_qc()
    fax = dem(DU_LIEU / "don-hang-moi" / "fax", "*.pdf")
    email = dem(DU_LIEU / "don-hang-moi" / "email", "*.pdf")
    tai_lieu_cong_ty_me = dem(DU_LIEU / "cong-ty-me", "*.md")

    bang = Table(title="Dữ liệu của Hoshimori Việt Nam (giả lập)", title_justify="left")
    bang.add_column("Nguồn", style="bold")
    bang.add_column("Bao nhiêu", justify="right")
    bang.add_column("Bẩn chỗ nào", style="yellow")
    bang.add_row("Hệ thống đơn hàng cũ (2011)", f"{tong} đơn", f"{thieu_ngay} đơn thiếu ngày giao, {so_chu} dòng số lượng là chữ")
    bang.add_row("Đơn hàng mới tuần 46", f"{fax} fax, {email} email", "fax mờ và nghiêng, mỗi khách một mẫu đơn")
    bang.add_row("Kế hoạch sản xuất T10", "1 file Excel", "ô gộp, ngày viết ba kiểu, cột bị ẩn")
    bang.add_row("Sổ lỗi QC T10", f"{so_dong_qc} dòng", f"lỗi {ti_le:.2f}%".replace(".", ",") + f', "ba via" viết {cach_viet} kiểu')
    bang.add_row("Tài liệu công ty mẹ", f"{tai_lieu_cong_ty_me} tài liệu", "tiếng Anh, quy định dùng AI và mẫu báo cáo")
    Console().print(bang)


if __name__ == "__main__":
    main()
