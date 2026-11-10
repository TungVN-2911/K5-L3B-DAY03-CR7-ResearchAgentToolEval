# Báo cáo cá nhân — VuNgocTung-2A202604106

## 1. Thông tin thành viên

- Họ tên: Vũ Ngọc Tùng
- MSSV: 2A202604106
- Email: vungoctung098@gmail.com

## 2. Phần việc phụ trách

- Phát triển một tool mới phục vụ kiểm tra các nguồn đã được research agent thu thập.
- Viết tài liệu cho tool, đăng ký implementation trong registry và viết unit test cho các hành vi chính.

## 3. Đóng góp cụ thể

- Tạo tool `source_audit` trong `starter_v0/tools/source_audit/`.
- Implement việc chuẩn hóa URL HTTP/HTTPS để nhận diện link trùng; bỏ qua fragment và chuẩn hóa host không phân biệt hoa thường, `www.` và dấu `/` cuối đường dẫn.
- Trả về tổng số item, số URL duy nhất, danh sách URL trùng kèm chỉ số item và số item theo từng nguồn. Nếu không có `source`, tool suy ra nguồn từ domain của URL.
- Kiểm tra kiểu dữ liệu đầu vào; trả error dictionary theo quy ước tool thay vì để lỗi đầu vào hoặc lỗi thực thi làm văng exception ra ngoài.
- Viết `TOOL.md` mô tả mục đích, giới hạn và trường dữ liệu của tool.
- Đăng ký implementation trong `starter_v0/tools/__init__.py`.
- Thêm ba test trong `starter_v0/tests/test_tools_todo.py`: kết quả thường và URL trùng, input item không hợp lệ, và lỗi thực thi trả về error dictionary.

## 4. Bằng chứng

- Implementation: `starter_v0/tools/source_audit/tool.py`
- Tài liệu: `starter_v0/tools/source_audit/TOOL.md`
- Registry: `starter_v0/tools/__init__.py`
- Unit test: `starter_v0/tests/test_tools_todo.py`
- Commit kỹ thuật: `12eb631` (`feat: implement source_audit tool with unit tests and documentation`).
- Tích hợp sau bàn giao: declaration trong `starter_v0/artifacts/tools.yaml`, eval route trong `starter_v0/data/eval_group.json` và run group do thành viên phụ trách tích hợp; xem [báo cáo nhóm, B3](group_report.md#b3-team-eval-cases) và run `starter_v0/runs/v6_B_group_openrouter_20261110T192709106340.json`.
- Kết quả tự kiểm tra:
  - `python -m pytest tests/test_tools_todo.py -k source_audit -q`: **3 passed**.
  - `python -m pytest tests/test_tool_contract.py -q`: **55 passed**.
  - Toàn suite `python -m pytest -q` (chạy lại ngày 2026-11-10): **86 passed, 14 skipped, 0 failed**; 14 skipped là các TODO test của tool có sẵn.
  - `git diff --check`: không phát hiện lỗi whitespace.
- Công cụ AI đã dùng: trợ lý AI trong VS Code để hỗ trợ triển khai và kiểm tra. Tôi tự xác nhận kết quả bằng cách chạy unit test, contract test và toàn suite nêu trên.

## 5. Tự đánh giá

Tool chạy cục bộ, không cần API key, không gọi mạng và không tạo side effect. Các test bao phủ kết quả thường, input sai và nhánh lỗi. Phần declaration model-facing, eval route và run tích hợp được thành viên phụ trách tương ứng hoàn tất sau khi bàn giao; run group v6 đạt 10/10 về các tiêu chí được scorer đo, còn phần kiểm tra output items của tool được đối chiếu thủ công như ghi trong báo cáo nhóm.
