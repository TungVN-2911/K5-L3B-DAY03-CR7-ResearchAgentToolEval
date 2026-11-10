# Snapshot prompt/tools theo version

Mỗi thư mục `vN/` chứa đúng `system_prompt.md` + `tools.yaml` đã dùng để chạy eval version đó. SHA-256 của từng file khớp `prompt_hash` / `tools_hash` trong `../version_log.csv` và trong run JSON (UI kiểm tra lại khi tải, hiện ✅ nếu khớp).

| Version | prompt | tools | Nguồn |
|---|---|---|---|
| v0 | `eb1c8179815b` | `e69bc53ed884` | starter gốc (commit `c50c8e1`, xuống dòng CRLF như lúc chạy) |
| v1 | `087b01792027` | `e69bc53ed884` | prompt v1 |
| v2 | `3007e5e8931b` | `e69bc53ed884` | commit `8c2834f` |
| v3 | `3007e5e8931b` | `c4b4f0f64072` | commit `8c2834f` |
| v4 | `d4acd5bb4523` | `f0632d419cd7` | + few-shot xác nhận yes_no; tools có `source_audit` |
| v5 | `0980414118c3` | `f0632d419cd7` | + rule routing, bỏ "ép một bước" |
| v6 | `5a4f316905ed` | `f0632d419cd7` | cấu hình chốt (= `../system_prompt.md`, `../tools.yaml`) |

`.gitattributes` đặt các file này là `-text` để git không đổi CRLF/LF làm lệch hash. Dùng trong UI: chọn version ở trang **Chat**, hoặc so sánh 2 version ở trang **So sánh**.
