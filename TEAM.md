# Team

## Thông tin nhóm

- Tên nhóm: CR7
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-CR7-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/TungVN-2911/K5-L3B-DAY03-CR7-ResearchAgentToolEval — nhánh `main` — commit chốt: `<điền sau commit cuối>`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đỗ Hồng Vỹ | 2A202604107 | 26ai.vydh@vinuni.edu.vn | `<điền>` | Người 1 — Setup, baseline, versioning v0–v6 |
|   2 | Vũ Ngọc Tùng | 2A202604106 | `<tự điền>` | ToiLaTung | Người 2 — Tool mới `source_audit` + unit test |
|   3 | Nguyễn Trọng Khiêm | 2A202604109 | `<tự điền>` | KhiemNTK | Người 3 — Eval nhóm (10 case) |
|   4 | `<tự điền>` | `<tự điền>` | `<tự điền>` | viethoang127 | Người 4 — UI, live chat, báo cáo nhóm |

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

## `<HoTen-MSSV Người 4>`

### Phần việc phụ trách

- UI Streamlit, live chat/transcript, tổng hợp group report.

### Đóng góp cụ thể

- `app.py` bản đầu + hướng dẫn chạy trong `starter_v0/README.md`, thêm `streamlit` vào `requirements.txt`.

### Bằng chứng

- Commit `257c2f9`, báo cáo cá nhân `<chưa có — report/team/MSSV_HoTen.md>`.
