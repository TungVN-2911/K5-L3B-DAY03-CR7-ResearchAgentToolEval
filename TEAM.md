# Team

## Thông tin nhóm

- Tên nhóm: CR7
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-CR7-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/TungVN-2911/K5-L3B-DAY03-CR7-ResearchAgentToolEval — nhánh `main` — commit chốt: `HEAD` (commit cập nhật thông tin nhóm này)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đỗ Hồng Vỹ | 2A202604107 | 26ai.vydh@vinuni.edu.vn | Do-Hong-Vy | Người 1 — Setup, baseline, versioning v0–v6 |
|   2 | Vũ Ngọc Tùng | 2A202604106 | vungoctung098@gmail.com | ToiLaTung | Người 2 — Tool mới `source_audit` + unit test |
|   3 | Nguyễn Trọng Khiêm | 2A202604109 | khiem14205@gmail.com | KhiemNTK | Người 3 — Eval nhóm (10 case) |
|   4 | Nguyễn Việt Hoàng | 2A202604104 | 26ai.hoangnv10@vinuni.edu.vn | viethoang127 | Người 4 — UI, live chat, báo cáo nhóm |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

## DoHongVy-2A202604107

### Phần việc phụ trách

- Setup provider (thử Gemini, chuyển sang OpenRouter), preflight, `pytest`; baseline v0; phân loại lỗi; versioning v1–v6; `version_log.csv`; bảng B1/B2.

### Đóng góp cụ thể

- `artifacts/system_prompt.md` (v1, v2, v4, v5, v6), `artifacts/tools.yaml` (v3); base eval 0.70 → 1.00; chạy lại group eval với cấu hình đã commit.

### Bằng chứng

- `starter_v0/runs/v0…v6_B_base_openrouter_*.json`, `starter_v0/artifacts/version_log.csv`, [báo cáo cá nhân](report/team/2A202604107_DoHongVy.md), commit `8c2834f`.

## VuNgocTung-2A202604106

### Phần việc phụ trách

- Tool mới `source_audit`: code, `TOOL.md`, đăng ký registry, unit test.

### Đóng góp cụ thể

- `starter_v0/tools/source_audit/`, 3 test `test_source_audit_*` trong `tests/test_tools_todo.py`.

### Bằng chứng

- Commit `12eb631`, [báo cáo cá nhân](report/team/2A202604106_VuNgocTung.md).

## NguyenTrongKhiem-2A202604109

### Phần việc phụ trách

- 10 case eval nhóm, tích hợp declaration `source_audit`, chạy group eval, bảng B3.

### Đóng góp cụ thể

- `starter_v0/data/eval_group.json`, `starter_v0/tests/test_group_eval.py`, declaration `source_audit` trong `tools.yaml`.

### Bằng chứng

- Commit `581ead2`, `1403e00`, run `v3-source-audit_B_group_openrouter_20261110T182420071920.json`, [báo cáo cá nhân](report/team/2A202604109_NguyenTrongKhiem.md).

## NguyenVietHoang-2A202604104

### Phần việc phụ trách

- Xây dựng UI Streamlit và hướng dẫn chạy.
- Tích hợp UI với agent, cấu hình prompt/tool và provider của nhóm.
- Chạy chat trực tiếp, lưu transcript và tổng hợp báo cáo nhóm.

### Đóng góp cụ thể

- Xây dựng giao diện trong `app.py` với các trang Chat, So sánh version, Benchmark và Công cụ.
- Tách logic vòng lặp agent, sự kiện gọi tool, transcript và dữ liệu benchmark dùng chung vào `starter_v0/ui_core.py`.
- Bổ sung lựa chọn provider/version, hiển thị tiến trình gọi tool và lỗi, phản hồi nhanh Có/Không khi agent xin xác nhận, lưu và tải transcript.
- Bổ sung hướng dẫn chạy trong `starter_v0/README.md` và dependency Streamlit trong `starter_v0/requirements.txt`.
- Chạy chat qua UI cho tình huống thiếu thông tin rồi bổ sung và yêu cầu gửi Telegram; transcript ghi nhận luồng hỏi lại/xác nhận. Lần gửi chưa thành công do thiếu `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`, lỗi được hiển thị trên UI.
- Tổng hợp phần giới thiệu agent và bằng chứng UI/live chat trong `report/team/group_report.md`.

### Bằng chứng

- `app.py`, `starter_v0/ui_core.py`, `starter_v0/README.md`, `starter_v0/requirements.txt`, `starter_v0/tests/test_ui_core.py` (12 test theo báo cáo nhóm), transcript `starter_v0/transcripts/ui_v6_openrouter_20261110T192858267079.transcript.json`.
- Commit `257c2f9`; [báo cáo cá nhân](report/team/2A202604104_NguyenVietHoang.md).
