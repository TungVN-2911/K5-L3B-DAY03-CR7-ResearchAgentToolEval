# Source code

Toàn bộ source code của lab nằm trong folder này. Chạy mọi lệnh từ `starter_v0/`.

- File bắt đầu chạy: `run_eval.py` (chạy eval), `chat.py` (chat live), `scripts/preflight_provider.py` (kiểm tra provider).
- Cách chạy: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`; `python chat.py --provider openrouter --version v3`; `pytest`.
- Input: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, bộ case `data/*.json`, API key trong `.env` (mẫu ở `.env.example`).
- Output: `runs/*.json` (kết quả eval), `transcripts/*.transcript.json` (chat live), `analysis/*.csv` (nếu chạy `scripts/parse_runs.py`).
- File học viên được sửa: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tools/` (thêm tool mới và đăng ký trong `tools/__init__.py`), `tests/test_tools_todo.py`, code UI và `requirements.txt`. Không sửa nội dung case trong `data/eval_base.json`.

## Chạy giao diện Streamlit

Cài dependencies từ `starter_v0/` bằng `python -m pip install -r requirements.txt`, cấu hình API key trong `starter_v0/.env`, sau đó chạy từ thư mục gốc dự án:

```powershell
streamlit run app.py
```

Trong giao diện, chọn provider; để trống model để dùng model mặc định. Agent dùng prompt và khai báo tool trong `starter_v0/artifacts/`.

Thanh điều hướng trên cùng có 3 trang:

- **Chat** (`/`): nhiều cuộc trò chuyện (lịch sử ở sidebar), thẻ câu hỏi mẫu, tiến trình gọi tool hiện trực tiếp, nút trả lời nhanh *Có / Không* khi agent xin xác nhận, *Tạo lại* và *Sao chép*. Lỗi tool/provider hiển thị rõ. Mỗi cuộc trò chuyện tự lưu `starter_v0/transcripts/ui_*.transcript.json` (tải về ở sidebar).
- **Benchmark** (`/benchmark`): so sánh các version (mặc định v0–v3, chọn thêm v4–v6), suite base/group: KPI so với v0, biểu đồ 4 metric, bảng số liệu + Δ + run file, ma trận pass/fail từng case, giả thuyết từ `version_log.csv`. Chỉ dùng run hợp lệ.
- **Công cụ** (`/tools`): tool và tham số đọc từ `artifacts/tools.yaml`.

Cấu hình (provider, model, nhãn version, số lượt nhớ, số vòng tool) nằm trong mục *Cấu hình agent* ở sidebar. Logic UI ở `ui_core.py`, test offline: `pytest tests/test_ui_core.py`.

Chi tiết từng bước xem [README.md](../README.md) ở root; cấu hình API key xem [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md).
