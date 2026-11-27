# Module 3, bản khởi đầu

Chạy các script trong thư mục này, trong venv của repo đã cài `pip install -r ../requirements.txt`. API key đặt trong
file `.env` ở gốc repo (chép từ `.env.example`); `.env` đã có trong `.gitignore`.

- `kiem_key.py`: đọc key trong `.env` rồi hỏi Claude API danh sách model, để biết key dùng được. Không in key ra, không
  gửi prompt nào cho model.
