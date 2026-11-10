# Báo cáo cá nhân — Nguyễn Việt Hoàng (2A202604104)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Việt Hoàng
- MSSV: 2A202604104
- Email: 26ai.hoangnv10@vinuni.edu.vn
- Vai trò trong nhóm: Người 4 — UI, live chat và báo cáo nhóm

## 2. Phần việc phụ trách

Theo phân công trong [Task.md](Task.md), tôi phụ trách:

- Xây dựng giao diện Streamlit và hướng dẫn chạy.
- Tích hợp UI với agent, cấu hình prompt/tool và provider của nhóm.
- Chạy các tình huống chat trực tiếp, lưu transcript làm bằng chứng.
- Tổng hợp báo cáo nhóm, kiểm tra `TEAM.md` và checklist nộp bài.

## 3. Đóng góp cụ thể

- Xây dựng giao diện trong `app.py` với các trang Chat, So sánh version, Benchmark và Công cụ.
- Tách logic vòng lặp agent, sự kiện gọi tool, transcript và dữ liệu benchmark dùng chung vào `starter_v0/ui_core.py`; phần logic này không phụ thuộc Streamlit để có thể kiểm thử offline.
- Tích hợp lựa chọn provider/version, hiển thị tiến trình gọi tool và lỗi, hỗ trợ phản hồi nhanh Có/Không khi agent xin xác nhận, lưu và tải transcript chat.
- Bổ sung hướng dẫn cài dependency và chạy UI trong `starter_v0/README.md`; thêm dependency Streamlit vào `starter_v0/requirements.txt`.
- Chạy chat trên cấu hình v6 qua UI: thử tình huống thiếu tài khoản rồi cung cấp bổ sung, và tình huống xin xác nhận trước khi gửi Telegram. Transcript cho thấy agent hỏi lại/xin xác nhận; lần gọi `send` chưa gửi được vì môi trường thiếu `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`, lỗi được hiển thị thay vì báo gửi thành công.
- Tổng hợp phần giới thiệu agent và các bằng chứng UI/live chat trong `report/team/group_report.md`.

## 4. Bằng chứng

- File/commit:
  - UI: `app.py`
  - Logic UI: `starter_v0/ui_core.py`
  - Hướng dẫn chạy: `starter_v0/README.md`
  - Dependency: `starter_v0/requirements.txt`
  - Test logic UI: `starter_v0/tests/test_ui_core.py` (12 test theo báo cáo nhóm)
  - Transcript live chat: `starter_v0/transcripts/ui_v6_openrouter_20261110T192858267079.transcript.json`
  - Báo cáo nhóm, mục A và B4–B5a: `report/team/group_report.md`
  - Commit được ghi nhận trong `TEAM.md`: `257c2f9`
- AI/công cụ đã dùng: GitHub Copilot trong VS Code hỗ trợ xây dựng giao diện và tích hợp.
- Cách tự kiểm tra: đối chiếu UI với luồng chat của agent, kiểm tra transcript thực tế và test logic UI. Báo cáo nhóm ghi nhận 12 test UI chạy qua `streamlit.testing` AppTest không có exception.

## 5. Tự đánh giá

Tôi đã tạo được giao diện và tích hợp thành công với agent; các luồng chat, xin xác nhận và lưu transcript có bằng chứng trong repository. Điểm cần hoàn thiện là cấu hình Telegram để kiểm chứng gửi thật: lần thử hiện tại dừng ở lỗi thiếu thông tin xác thực, nhưng UI đã thể hiện lỗi rõ ràng và không báo thành công sai.
