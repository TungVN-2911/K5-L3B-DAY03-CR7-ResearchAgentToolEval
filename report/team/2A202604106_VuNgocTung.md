# Báo cáo cá nhân — VuNgocTung-2A202604106

## 1. Thông tin thành viên

- Họ tên: Vũ Ngọc Tùng
- MSSV: 2A202604106
- Email: Chưa cung cấp

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
- Kết quả tự kiểm tra:
  - `python -m pytest tests/test_tools_todo.py -k source_audit -q`: **3 passed**.
  - `python -m pytest tests/test_tool_contract.py -q`: **55 passed**.
  - `git diff --check`: không phát hiện lỗi whitespace.
- Công cụ AI đã dùng: trợ lý AI trong VS Code để hỗ trợ triển khai và kiểm tra. Tôi tự xác nhận kết quả bằng cách chạy unit test và contract test nêu trên.

## 5. Tự đánh giá

Tool chạy cục bộ, không cần API key, không gọi mạng và không tạo side effect. Các test bao phủ kết quả thường, input sai và nhánh lỗi. Phần khai báo model-facing trong `starter_v0/artifacts/tools.yaml`, eval case kiểm tra model route tới tool mới và run eval tích hợp chưa thực hiện trong phạm vi công việc này; cần thành viên phụ trách các phần đó phối hợp hoàn tất trước khi dùng tool làm bằng chứng tích hợp.
