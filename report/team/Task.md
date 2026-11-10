# Kế hoạch công việc nhóm — 4 thành viên

Thời lượng dự kiến: **4 giờ**. Thay “Người 1–4” bằng tên thành viên khi phân công chính thức. Các mốc dưới đây tính từ lúc bắt đầu làm; nhiều việc chạy song song, nhưng các điểm bàn giao phải được giữ để tránh dùng cấu hình hoặc bằng chứng chưa hoàn chỉnh.

## 1. Phân công

| Thành viên | Phạm vi phụ trách | Sản phẩm/bằng chứng |
|---|---|---|
| **Người 1 — Setup, baseline và versioning** | Điền thông tin nhóm cùng Người 4; kiểm tra provider, chạy preflight và `pytest`; chạy baseline v0 trước khi sửa prompt/tools; phân loại lỗi; thực hiện v1–v3, mỗi version kiểm tra một giả thuyết; ghi hash, giả thuyết và metric vào version log. | `TEAM.md`; run v0–v3 hợp lệ; `artifacts/version_log.csv`; bảng B1/B2 trong báo cáo nhóm. |
| **Người 2 — Tool mới và unit test** | Chốt sớm tên, mô tả và args tool mới với Người 1 và Người 3; viết `tools/<tên>/tool.py`, `TOOL.md`; đăng ký hàm trong `tools/__init__.py`; viết ít nhất 3 unit test gồm happy path, input xấu và nhánh lỗi. | Tool mới đã đăng ký; `tests/test_tools_todo.py` có ít nhất 3 test không bị skip; bằng chứng B5a và báo cáo cá nhân. |
| **Người 3 — Eval nhóm** | Soạn đúng 10 case mới: 5 single-turn và 5 multi-turn; mỗi case có `expect` và `metadata.what_it_tests`; có ít nhất một case kiểm tra route tới tool mới; chạy group eval sau khi tool được tích hợp. | `data/eval_group.json`; run `--suite group`; bảng B3; báo cáo cá nhân. |
| **Người 4 — UI, live chat và báo cáo** | Dựng UI và hướng dẫn chạy; phối hợp Người 1 để dùng cấu hình agent v3; chạy chat tối thiểu 3 tình huống và lưu transcript; tổng hợp group report, hoàn thiện phần A trước buổi demo; kiểm tra checklist nộp bài và thông tin `TEAM.md`. | UI chạy được; transcript có đủ 3 tình huống; `report/team/group_report.md`; cập nhật `TEAM.md`; báo cáo cá nhân. |

**Quy ước sửa file để giảm xung đột:** Người 1 phụ trách `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`; Người 2 phụ trách code tool và unit test; Người 3 phụ trách `data/eval_group.json`; Người 4 phụ trách UI và `report/team/group_report.md`. Các thành viên cùng rà soát cuối nhưng báo trước khi sửa file do người khác phụ trách.

## 2. Lịch 4 giờ và các điểm bàn giao

| Thời gian | Người 1 | Người 2 | Người 3 | Người 4 |
|---|---|---|---|---|
| **0:00–0:20** | Kiểm tra cấu hình provider, preflight, `pytest`; xác nhận provider dùng chung. | Đọc contract tool; thống nhất tên và args với Người 1, Người 3. | Lập danh sách 10 tình huống eval; dành một case cho tool mới sau khi nhận tên/args. | Điền thông tin nhóm cùng Người 1; đọc mẫu báo cáo, dựng khung UI và phần A. |
| **0:20–0:55** | Chạy v0 khi prompt và `tools.yaml` còn nguyên; lưu run, ghi metric và lỗi. | Viết tool, `TOOL.md`, đăng ký hàm và unit test theo giao diện đã chốt. | Viết các case độc lập với tool mới; kiểm tra đủ 5 single-turn và 5 multi-turn. | Dựng UI và lệnh chạy; chuẩn bị 3 kịch bản live chat. |
| **0:55–2:10** | Phân loại lỗi v0; chạy v1, v2, v3 theo từng giả thuyết; ghi kết quả và hash. | Hoàn thiện tool và test; chạy test, bàn giao tên/args cùng trạng thái code cho Người 1 và Người 3. | Hoàn thiện JSON eval; chờ giao diện tool để viết case route chính xác; soạn phần B3. | Tiếp tục UI; điền phần A, tool list và câu hỏi mẫu dựa trên cấu hình đã thống nhất. |
| **2:10–2:40** | Sau khi v3 đã chạy, tích hợp declaration của tool mới vào `tools.yaml`; chạy contract test và bàn giao cấu hình cho Người 3, Người 4. | Sửa lỗi test/integration theo phản hồi; xác nhận tool trả kết quả lỗi theo contract. | Hoàn tất case route tool mới sau khi nhận args; chạy group eval khi tool và declaration đã tích hợp. | Kết nối UI với agent/config đã bàn giao; kiểm thử nhanh luồng chat. |
| **2:40–3:25** | Rà soát tính hợp lệ run v0–v3; điền B1/B2 từ run JSON. | Chạy lại unit test và chuẩn bị bằng chứng B5a. | Kiểm tra run group đủ 10 case, điền B3. | Chạy 3 tình huống live chat, lưu transcript; điền B4 và hoàn thiện phần A trước demo. |
| **3:25–4:00** | Hỗ trợ sửa lỗi kiểm tra cuối; xác nhận version log và run khớp nhau. | Chạy `pytest`, ghi đóng góp/bằng chứng cá nhân, commit phần code. | Kiểm tra cấu trúc eval và kết quả group run; ghi đóng góp cá nhân, commit. | Rà soát báo cáo, UI, transcript, `TEAM.md` và checklist nộp; ghi đóng góp cá nhân, commit. Cả nhóm xác nhận không có secret trong thay đổi. |

## 3. Phụ thuộc và cách xử lý khi phải chờ

1. **Tên/args tool mới (Người 2 → Người 1, Người 3):** cần chốt trong 20 phút đầu. Người 3 có thể viết các case không phụ thuộc tool mới trước; chỉ hoàn thiện case route sau khi nhận args chính xác.
2. **Baseline v0 (Người 1 → tối ưu prompt):** phải lưu v0 trước khi sửa prompt hoặc declaration, nếu không sẽ mất mốc so sánh. Trong lúc Người 1 chạy eval, Người 2–4 làm việc riêng như lịch.
3. **Tool code (Người 2 → Người 1, Người 3):** Người 1 chỉ thêm declaration vào `tools.yaml` sau khi tên/args ổn định; Người 3 chỉ chạy case route sau khi tool được đăng ký và contract test xanh.
4. **Cấu hình v3 và tool tích hợp (Người 1 → Người 3, Người 4):** group eval cuối và kiểm thử UI/transcript phải dùng cấu hình đã bàn giao. Trong lúc chờ, Người 3 hoàn thiện các case khác và Người 4 dựng UI/phần A.
5. Nếu một lần chạy provider bị lỗi, không ghi nhận đó là kết quả hợp lệ. Lưu bằng chứng lỗi, thử lại nếu còn thời gian và ghi rõ khó khăn trong group report.

## 4. Tiêu chí hoàn thành

- Có run v0, v1, v2, v3; mỗi run dùng làm bằng chứng có `provider_error_cases == 0` và `measured_cases == total_cases`.
- Mỗi version có giả thuyết riêng; version log có hash và metric trước/sau.
- Tool mới đã đăng ký đúng, có `TOOL.md` và ít nhất 3 unit test; `pytest` không có test thất bại.
- Eval nhóm có đúng 10 case (5 single-turn, 5 multi-turn), có case route tới tool mới và có run group.
- UI có hướng dẫn chạy; transcript có yêu cầu thường, lượt cần hỏi/bổ sung thông tin và yêu cầu gửi/đăng.
- Group report trỏ tới run, transcript và file bằng chứng thật; mỗi thành viên có báo cáo cá nhân theo tên `report/team/MSSV_HoTen.md` và có commit kỹ thuật.
- Không commit `.env`, API key, token hoặc dữ liệu cá nhân.

**Ưu tiên:** hoàn thành các deliverable bắt buộc và bằng chứng hợp lệ trước; chỉ làm bonus khi các mục trên đã ổn định.
