"""Đếm lỗi trong sổ lỗi QC bằng code, để đối chiếu với con số Claude đưa ra: tỉ lệ lỗi chung, số lỗi theo loại (gộp
các cách viết của cùng một lỗi), theo công đoạn, và năm máy hay chuyền có tỉ lệ lỗi cao nhất.

    python dem_loi.py                    # đọc ../../du-lieu/qc/loi_hang_ngay_2026-10.csv
    python dem_loi.py <file sổ lỗi>      # ví dụ file đã bỏ tên người của bo_ten.py

Hai cách viết là một lỗi khi giống nhau sau khi bỏ khoảng trắng và không kể hoa thường ("ba via", "Ba via", "bavia").
Mỗi lỗi lấy cách viết hay gặp nhất làm tên. Chỉ dùng thư viện có sẵn của Python.
"""
from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path

VAO = Path(__file__).resolve().parent.parent.parent / "du-lieu" / "qc" / "loi_hang_ngay_2026-10.csv"


def phan_tram(loi: int, kiem: int) -> str:
    return f"{loi / kiem * 100:.2f}%".replace(".", ",")


def khoa(loai_loi: str) -> str:
    return "".join(loai_loi.lower().split())


def main(tham_so: list[str]) -> None:
    vao = Path(tham_so[0]) if tham_so else VAO
    with open(vao, encoding="utf-8", newline="") as f:
        dong = list(csv.DictReader(f))
    kiem = sum(int(d["sl_kiem"]) for d in dong)
    loi = sum(int(d["sl_loi"]) for d in dong)

    cach_viet: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for d in dong:
        if d["loai_loi"]:
            cach_viet[khoa(d["loai_loi"])][d["loai_loi"]] += int(d["sl_loi"])
    theo_loai = sorted(cach_viet.values(), key=lambda c: (-sum(c.values()), c.most_common(1)[0][0]))

    cong_doan = {"máy ép": [0, 0], "chuyền bó dây": [0, 0]}
    theo_may: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    for d in dong:
        o = cong_doan["chuyền bó dây" if d["may_chuyen"].startswith("BD-") else "máy ép"]
        o[0] += int(d["sl_loi"])
        o[1] += int(d["sl_kiem"])
        theo_may[d["may_chuyen"]][0] += int(d["sl_loi"])
        theo_may[d["may_chuyen"]][1] += int(d["sl_kiem"])
    may_dau = sorted(theo_may, key=lambda m: (-theo_may[m][0] / theo_may[m][1], m))[:5]

    print(f"Sổ lỗi: {vao.name}")
    print(f"{len(dong)} dòng, {loi} lỗi trên {kiem} cái kiểm, tỉ lệ lỗi {phan_tram(loi, kiem)}")
    print()
    print("Lỗi theo loại (gộp cách viết):")
    for c in theo_loai:
        ten = c.most_common(1)[0][0]
        chi_tiet = ""
        if len(c) > 1:
            chi_tiet = "  (" + ", ".join(f'{so} "{viet}"' for viet, so in c.most_common()) + ")"
        print(f"  {ten:<14}{sum(c.values()):>5}{chi_tiet}")
    print()
    print("Theo công đoạn:")
    for ten, (so_loi, so_kiem) in cong_doan.items():
        print(f"  {ten:<14}{so_loi:>5} lỗi trên {so_kiem:>6} cái kiểm  {phan_tram(so_loi, so_kiem)}")
    print()
    print("Năm máy, chuyền có tỉ lệ lỗi cao nhất:")
    for m in may_dau:
        so_loi, so_kiem = theo_may[m]
        print(f"  {m:<5}{phan_tram(so_loi, so_kiem):>6}  ({so_loi}/{so_kiem})")


if __name__ == "__main__":
    # In UTF-8 cả khi stdout là pipe (Claude Code chạy lệnh), vì bảng mã mặc định của Windows không có đủ chữ Việt.
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
