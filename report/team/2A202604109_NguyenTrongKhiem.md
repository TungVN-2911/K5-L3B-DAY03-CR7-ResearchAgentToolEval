# Báo cáo cá nhân — Nguyễn Trọng Khiêm (2A202604109)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trọng Khiêm
- MSSV: 2A202604109
- Email: khiem14205@gmail.com
- Vai trò trong nhóm: **Người 3 — Eval nhóm**

## 2. Phần việc phụ trách

Theo phân công trong [Task.md](Task.md), tôi phụ trách:

1. Viết 10 case eval mới gồm 5 single-turn và 5 multi-turn, có `expect` và `metadata.what_it_tests`.
2. Bổ sung case kiểm tra agent chọn đúng tool mới của nhóm là `source_audit`.
3. Kiểm tra cấu trúc case, chạy group eval sau khi tool được tích hợp và đối chiếu kết quả trong run JSON.
4. Điền bảng B3 trong [group_report.md](group_report.md) và ghi lại bằng chứng đóng góp cá nhân.

File phụ trách chính: `starter_v0/data/eval_group.json`.

## 3. Đóng góp cụ thể

### 3.1. Xây dựng bộ eval nhóm

- Soạn 10 case trong `starter_v0/data/eval_group.json`, tập trung vào lựa chọn tool, tham số, hỏi lại khi thiếu dữ liệu và xác nhận trước khi gửi.
- Thiết kế các case G01, G06, G10 cho tool `source_audit` do Người 2 triển khai: kiểm tra link trùng, thay thế danh sách nguồn và xử lý danh sách rỗng.

| Case | Loại   | Kiểm tra                                                    |
| ---- | ------ | ----------------------------------------------------------- |
| G01  | Single | Route tới `source_audit`, giữ link trùng và thống kê nguồn. |
| G02  | Single | Tìm web news theo năm, đúng query và số lượng 2.            |
| G03  | Single | Hỏi lại khi chưa có items để kiểm tra nguồn.                |
| G04  | Single | Xin xác nhận yes/no dù đã có nguyên văn bản nháp gửi.       |
| G05  | Single | Format items đã có thành thread, không tìm thêm dữ liệu.    |
| G06  | Multi  | Audit danh sách thay thế ở lượt cuối, bỏ danh sách cũ.      |
| G07  | Multi  | Đổi đồng thời timeframe và số lượng, giữ chủ đề.            |
| G08  | Multi  | Đổi Latest sang Top và số lượng, giữ từ khóa.               |
| G09  | Multi  | Dừng mọi tool khi người dùng hủy yêu cầu gửi.               |
| G10  | Multi  | Xử lý `items=[]` được cung cấp rõ sau lượt hỏi lại.         |

Các case multi-turn kiểm tra việc giữ hoặc thay đổi thông tin theo lượt cuối của hội thoại.

### 3.2. Tích hợp và kiểm tra

- Bổ sung declaration `source_audit(items)` vào `starter_v0/artifacts/tools.yaml` để model có thể gọi tool đã được Người 2 đăng ký trong code.
- Thêm `starter_v0/tests/test_group_eval.py` để kiểm tra đủ 10 case, tỷ lệ 5/5, ID duy nhất, các trường bắt buộc và tên tool/tham số hợp lệ; kiểm tra không trùng nguyên input với bộ base/extension.
- Kết quả `python -m pytest -q -p no:cacheprovider`: **71 passed, 14 skipped**. Các test skip thuộc phần challenge của tool có sẵn.
- Bộ nạp eval chấp nhận đủ 10 case. Cập nhật dòng run group trong `version_log.csv` và kết quả từng case ở bảng B3.

### 3.3. Kết quả group eval

Provider/model: `openrouter` / `openai/gpt-4o-mini`. Lệnh chạy từ `starter_v0/` sau khi kích hoạt virtual environment:

```powershell
python run_eval.py --provider openrouter --version v3-source-audit --suite group --eval-cases data/eval_group.json
```

- Run: [v3-source-audit_B_group_openrouter_20261110T182420071920.json](../../starter_v0/runs/v3-source-audit_B_group_openrouter_20261110T182420071920.json).
- Kết quả: **10/10 case PASS**; `measured_cases=total_cases=10`, `provider_error_cases=0`.
- Các metric `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` đều đạt **1.0** theo các trường đã khai báo trong `expect`.
- G01/G06 chỉ chấm tự động tên tool, G05 chấm tên tool và template do bộ chấm chưa hỗ trợ danh sách nhiều object. Đã đối chiếu thêm input/output của G01/G05/G06/G10 bằng assert: **4/4 đạt**.
- G08 chọn đúng `social_search` và tham số nhưng API trả **HTTP 403**, chưa lấy được tweet. Vì vậy, PASS ở case này chỉ xác nhận routing/args.
- G04 hỏi xác nhận trước khi gửi; G09 không gọi tool sau khi người dùng hủy.

Nhận xét: Bộ eval kiểm tra được tool mới và việc xử lý ngữ cảnh nhiều lượt. Kết quả group được báo cáo riêng với base v0–v3 vì hai bộ case khác nhau.

## 4. Bằng chứng

- File/commit/PR:
  - [Bộ eval nhóm](../../starter_v0/data/eval_group.json) — 10 case, gồm 5 single-turn và 5 multi-turn.
  - [Test cấu trúc dataset](../../starter_v0/tests/test_group_eval.py).
  - [Declaration tool](../../starter_v0/artifacts/tools.yaml) và [version log](../../starter_v0/artifacts/version_log.csv), dòng `v3-source-audit`.
  - [Run group](../../starter_v0/runs/v3-source-audit_B_group_openrouter_20261110T182420071920.json) — 10 case được đo, không lỗi provider.
  - [Bảng B3 trong báo cáo nhóm](group_report.md#b3-team-eval-cases).
  - Commit: chưa tạo.

### AI/công cụ đã dùng và cách kiểm tra

- Công cụ AI: **Codex trong VS Code**, hỗ trợ soạn case, tích hợp declaration, phân tích kết quả.
- Cách kiểm tra kết quả: đối chiếu `expect` với tool contract, đọc `summary` và tool calls trong run JSON; kiểm tra riêng input/output ở các case có danh sách items.

## 5. Tự đánh giá

Tôi đánh giá phần việc của mình đã đáp ứng các yêu cầu kỹ thuật chính của của task: bộ eval có đủ 10 case gồm 5 single-turn và 5 multi-turn, có case kiểm tra tool mới và có run group làm bằng chứng. Kết quả 10/10 PASS phản ánh việc chọn tool và các tham số được kiểm tra. Phần soạn case, tích hợp và kiểm tra có sử dụng Codex hỗ trợ như đã nêu ở mục 4.

Hạn chế là bộ case còn nhỏ và một số đầu vào cần đối chiếu thêm ngoài bộ chấm tự động. G08 vẫn gặp lỗi HTTP 403 nên chưa thể kết luận toàn bộ luồng lấy dữ liệu hoạt động thành công. Phần cần cải thiện tiếp là kiểm tra nguyên nhân lỗi API, mở rộng các tình huống biên và đánh giá cả dữ liệu tool trả về thay vì chỉ dựa vào điểm PASS.
