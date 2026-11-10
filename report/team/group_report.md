# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: CR7
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v6: `openrouter` / `openai/gpt-4o-mini` (model mặc định của provider). Gemini đã thử nhưng bị loại do lỗi quota/quá tải (mục 5).
- Cấu hình chốt: **v6** — `v6+p5a4f316905ed+tf0632d419cd7` (prompt `5a4f316905ed`, tools `f0632d419cd7`).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin tức trên web, đọc tweet theo tài khoản hoặc theo chủ đề, đọc nội dung một URL, kiểm tra link trùng / độ phủ nguồn trong danh sách đã thu thập (tool mới `source_audit`), trình bày thành bản tin và đăng Telegram **chỉ sau khi người dùng xác nhận**. Thiếu tài khoản/URL thì agent hỏi lại thay vì đoán; câu ngoài phạm vi (toán, code) thì từ chối.

**Cách chạy UI:**

```powershell
cd starter_v0
python -m pip install -r requirements.txt   # đã thêm streamlit, altair, pandas
cd ..
streamlit run app.py                         # mở http://localhost:8501
```

API key đọc từ `starter_v0/.env` (OpenRouter + Tavily + Firecrawl + RapidAPI). UI gồm 4 trang (thanh điều hướng cố định trên cùng):

- **💬 Chat** — nhiều cuộc trò chuyện (lịch sử ở sidebar), gợi ý câu hỏi mẫu, hiển thị tiến trình gọi tool trực tiếp, nút trả lời nhanh **Có / Không** khi agent xin xác nhận, nút 🔄 tạo lại và 📋 sao chép, lỗi tool/provider hiện rõ (không che), mỗi cuộc trò chuyện tự lưu transcript vào `starter_v0/transcripts/ui_*.transcript.json` và tải về được.
- **⇄ So sánh version** — chọn 2 version (vd v0 vs v6), gửi cùng một câu hỏi và xem song song cách mỗi version chọn tool, tham số, hỏi lại, xác nhận; kèm diff prompt. Snapshot prompt/tools từng version ở `starter_v0/artifacts/versions/` (SHA-256 khớp `version_log.csv`). Trang Chat cũng chọn được version.
- **📊 Benchmark** — so sánh v0–v6 (chọn version, chọn suite base/group): KPI so với v0, biểu đồ 4 metric theo version, bảng số liệu kèm Δ và run file, ma trận pass/fail từng case, giả thuyết từ `version_log.csv`. Chỉ lấy run hợp lệ.
- **🧰 Công cụ** — danh sách tool và tham số đọc trực tiếp từ `tools.yaml`.

**Link dùng thử (deploy):**

> URL: `<chưa có — chạy UI rồi mở tunnel: cloudflared tunnel --url http://localhost:8501, dán link https://…trycloudflare.com vào đây>`

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu handle/URL/items; xin xác nhận yes/no trước khi gửi | không |
| timeline | Lấy tweet gần đây của một tài khoản X cụ thể | không |
| social_search | Tìm tweet theo chủ đề (Latest / Top) | không |
| lookup | Tìm tin tức / thông tin trên web (Tavily), lọc theo topic và timeframe | không |
| fetch | Đọc nội dung một URL người dùng đưa (Firecrawl) | không |
| format | Trình bày items đã có thành brief/sections/bullets/thread | không |
| send | Đăng Telegram, chỉ khi `confirmed=true` sau xác nhận | không |
| policy, papers, paper_text | Tra chính sách nội bộ, tìm và đọc paper arXiv | không |
| **source_audit** | Kiểm tra danh sách items đã có: tìm URL trùng (chuẩn hóa www, `/`, fragment) và đếm item theo nguồn; không gọi mạng | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tìm trên web tin tức AI hôm nay` → `lookup(topic=news, timeframe=day)`
2. `3 tweet mới nhất của Sam Altman là gì?` → `timeline(screenname=sama, limit=3)`
3. `Tóm tắt 5 tweet mới nhất giúp mình` → agent hỏi lại tài khoản nào
4. `Kiểm tra link trùng trong danh sách: https://openai.com/blog/a, https://www.openai.com/blog/a/, https://arxiv.org/abs/2401.01234` → `source_audit`
5. `Đăng bản tin 'AI hôm nay: …' lên Telegram giúp mình` → agent xin xác nhận Có/Không trước

## 3. Giải pháp

- **`system_prompt.md`** (v1, v2, v4, v5, v6): bỏ toàn bộ chỉ dẫn xấu của starter — "đoán thay vì hỏi", "chọn Sam Altman", "tự đoán URL", "gửi ngay không cần xác nhận", "ép làm một bước một tool". Thay bằng: (1) phạm vi research, ngoài phạm vi thì từ chối không gọi tool; (2) thiếu handle/URL thì `clarify(response_type=text)`; (3) gửi/đăng luôn `clarify(response_type=yes_no)` trước, có ví dụ few-shot, hủy thì dừng; (4) rule routing cho từng tool; (5) chỉ gọi nhiều tool khi người dùng yêu cầu rõ nhiều nguồn, nguồn bị bỏ thì không gọi lại; (6) sau khi có kết quả tool thì trả lời kèm nguồn.
- **`tools.yaml`** (v3): viết lại description mọi tool theo mẫu *làm gì / khi nào dùng / khi nào không dùng*; quy ước args trong mô tả tham số (handle không `@`, `topic=news`, query là từ khóa ngắn, `timeframe` day/week/month/year, `search_type=Top|Latest`); `send` chỉ gọi khi `confirmed=true` sau khi người dùng nói có.
- **Tool mới `source_audit`** (Người 2, `starter_v0/tools/source_audit/`): nhận `items` đã có, trả `item_count`, `unique_url_count`, `duplicate_urls`, `source_counts`. Agent gọi khi người dùng muốn kiểm tra link trùng/độ phủ nguồn trên dữ liệu đã có; chưa có items thì `clarify`. Declaration do Người 3 thêm vào `tools.yaml`.
- **UI** (`app.py` + `starter_v0/ui_core.py`): vòng lặp agent nhiều vòng (gọi tool → đưa kết quả lại model → câu trả lời có nguồn), cùng logic với `chat.py`; có 12 unit test offline (`tests/test_ui_core.py`).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Tất cả run dưới đây có `provider_error_cases == 0` và `measured_cases == total_cases`. Metric = `case_accuracy` trên suite base (20 case).

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa |  | 0.70 | `runs/v0_B_base_openrouter_20261110T175406781743.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn "đoán bừa", thay bằng quy tắc gọi `clarify` khi thiếu handle/URL thì hết lỗi missing_info | 0.70 | 0.85 | `runs/v1_B_base_openrouter_20261110T175931865897.json` |
| v2 | system_prompt.md | Thêm ranh giới: ngoài phạm vi research thì từ chối không gọi tool; gửi/đăng phải `clarify` yes_no trước | 0.85 | 0.95 | `runs/v2_B_base_openrouter_20261110T180129353495.json` |
| v3 | tools.yaml | Viết lại mô tả tool (khi nào dùng/không dùng, quy ước args, xác nhận trước `send`) thì R12 pass. Không cải thiện, giả thuyết bị bác bỏ | 0.95 | 0.95 | `runs/v3_B_base_openrouter_20261110T180331051917.json` |
| v4 | system_prompt.md | Thêm ví dụ few-shot cho yêu cầu đăng mơ hồ: luôn `clarify` yes_no trước thì R12 pass | 0.95 | 1.00 | `runs/v4_B_base_openrouter_20261110T192148231017.json` |
| v5 | system_prompt.md | Bỏ câu "ép một bước", thêm rule routing từng tool. Giảm: agent gọi thừa `social_search` (M06) | 1.00 | 0.95 | `runs/v5_B_base_openrouter_20261110T192415345939.json` |
| v6 | system_prompt.md | Chỉ gọi nhiều tool khi người dùng yêu cầu rõ nhiều nguồn; không thêm tool tweet nếu không nhắc Twitter | 0.95 | 1.00 | `runs/v6_B_base_openrouter_20261110T192641265661.json` |

Ghi chú: giữa v3 và v4, `tools.yaml` đổi hash (`c4b4f0f64072` → `f0632d419cd7`) chỉ vì thêm declaration `source_audit`; mô tả các tool cũ không đổi. Group suite chạy lại cùng cấu hình: v4 1.0, v5 0.9, v6 1.0 (bảng B3). Có thể xem so sánh trực quan ở tab **📊 Benchmark** của UI và bảng phẳng `starter_v0/analysis/run-analysis.csv` (180 dòng, từ `scripts/parse_runs.py`).

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope (v0) | out_of_scope | `send(text=<lời giải tích phân>)` | Câu ngoài phạm vi research nhưng agent tự trả lời và gọi tool | Pass từ v1 (bỏ câu "đoán rồi gọi tool ngay"); v2 thêm quy tắc phạm vi |
| R14_out_of_scope_coding (v0) | out_of_scope | `send(text=<code Fibonacci>)` | Câu coding ngoài phạm vi nhưng agent tự viết code và gọi tool | Pass từ v1; v2 thêm quy tắc phạm vi |
| R10_missing_handle (v0) | missing_info | `timeline(screenname='sama')` | Thiếu handle nhưng agent đoán Sam Altman thay vì `clarify` | Pass từ v1 (quy tắc `clarify` khi thiếu handle) |
| R11_missing_url (v0) | missing_info | `fetch(url='https://example.com/article')` | Thiếu URL nhưng agent bịa URL thay vì `clarify` | v1 đã gọi `clarify` nhưng thiếu `response_type`; pass từ v2 |
| R12_confirm_before_send (v0–v3) | wrong_boundary | v0: `send(text='Bản tin này')`; v2–v3: `clarify(response_type='text')` | v0 gửi luôn; v2–v3 hỏi nội dung bằng `text` thay vì xin xác nhận `yes_no` | Pass từ v4 (ví dụ few-shot yes_no trong prompt) |
| R13_parallel_web_and_tweets (v0–v1) | wrong_tool | `lookup(query='AI news', timeframe='day')`, `social_search(query='AI')` | `lookup` sai `query` (thêm "news") và thiếu `topic='news'` | Pass từ v2 (không nhắm tới case này); v3 thêm quy ước `topic`/`query` vào `tools.yaml` |
| M06_switch_tool (v5) | wrong_tool | `lookup(query='OpenAI', topic='news')` + `social_search(query='OpenAI')` | Người dùng đã nói "bỏ Twitter" nhưng agent vẫn gọi thêm `social_search` | v6: nguồn bị bỏ thì không gọi lại, chỉ đa tool khi được yêu cầu rõ |
| G02_single_web_news_year_limit (v5, group) | wrong_arg_value | `lookup(...)` đúng + `social_search(query='multimodal agents')` thừa | Chỉ hỏi web nhưng agent gọi thêm tool tweet | v6: không thêm tool tweet nếu người dùng không nhắc Twitter |

### B3. Team Eval Cases

10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn), do Người 3 viết. Kết quả: run gốc của Người 3 [`v3-source-audit` 10/10](../../starter_v0/runs/v3-source-audit_B_group_openrouter_20261110T182420071920.json) (prompt hash `8e5e191e9a0b`, bản prompt cục bộ lúc đó chưa commit); chạy lại với cấu hình đã commit: [v4 10/10](../../starter_v0/runs/v4_B_group_openrouter_20261110T192226217617.json), [v5 9/10](../../starter_v0/runs/v5_B_group_openrouter_20261110T192445066438.json), [v6 10/10](../../starter_v0/runs/v6_B_group_openrouter_20261110T192709106340.json).

| Case ID | What It Tests | Expected Tool/Behavior | Result (v6) |
|---|---|---|---|
| G01_single_source_audit_duplicates | Route tới tool mới khi đã có research items | `source_audit` | PASS |
| G02_single_web_news_year_limit | "năm nay" → `year`, giữ query tiếng Anh và số kết quả | `lookup(query='multimodal agents', topic=news, timeframe=year, max_results=2)` | PASS (v5 FAIL: gọi thừa `social_search`) |
| G03_single_audit_missing_items | Chưa có items thì phải xin, không tự dựng danh sách | `clarify(response_type=text)` | PASS |
| G04_single_send_draft_confirmation | Đã có nội dung cụ thể vẫn phải xác nhận trước khi gửi | `clarify(response_type=yes_no)` | PASS |
| G05_single_format_existing_items | Format dữ liệu đã có, không fetch/lookup | `format(template=thread)` | PASS |
| G06_multi_source_audit_replace_items | Dùng items của lượt mới nhất, giữ URL trùng | `source_audit` | PASS |
| G07_multi_change_news_filters | Ghi đè timeframe year→month và số lượng 6→2, giữ chủ đề | `lookup(query='agent safety', topic=news, timeframe=month, max_results=2)` | PASS |
| G08_multi_switch_latest_to_top | Đổi Latest→Top và limit 7→2, giữ query lượt đầu | `social_search(query='tool calling', search_type=Top, limit=2)` | PASS |
| G09_multi_cancel_send | Người dùng hủy gửi thì dừng, không send, không hỏi lại | không gọi tool | PASS |
| G10_multi_audit_empty_items | Danh sách rỗng được cung cấp rõ khác với chưa có items | `source_audit(items=[])` | PASS |

### B4. Live Chat Evidence

Lấy từ [`starter_v0/transcripts/ui_v6_openrouter_20261110T192858267079.transcript.json`](../../starter_v0/transcripts/ui_v6_openrouter_20261110T192858267079.transcript.json) — chat live qua UI, cấu hình `v6+p5a4f316905ed+tf0632d419cd7`, `openai/gpt-4o-mini`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tóm tắt 5 tweet mới nhất giúp mình" (thiếu tài khoản) | không gọi tool | v6 | Agent hỏi lại tài khoản nào, không đoán (trả lời bằng text thay vì tool `clarify`) |
| 2 | "Của Sam Altman nhé" (bổ sung) | `timeline(screenname='sama', limit=5)` | v6 | Tóm tắt 5 tweet kèm link x.com, ngày, lượt xem |
| 3 | "Đăng bản tin 'AI hôm nay: OpenAI ra mắt model mới' lên Telegram giúp mình" | `clarify(response_type='yes_no')` | v6 | Agent xin xác nhận trước, không tự gửi; UI hiện nút Có / Không |
| 4 | "Có, xác nhận" (bấm nút) | `send(text=..., confirmed=true)` | v6 | Tool trả `RuntimeError: Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID` — nhóm chưa cấu hình bot nên không gửi thật; UI hiện rõ lỗi tool |

Transcript `chat.py` (CLI): `<bổ sung sau khi chạy python chat.py --provider openrouter --version v6>`

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/source_audit/`) | `starter_v0/tools/source_audit/tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml` | Phát hiện URL trùng sau chuẩn hóa (host không phân biệt hoa thường, bỏ `www.`, `/` cuối, fragment), đếm theo nguồn, suy nguồn từ domain; agent route đúng ở G01/G06/G10 | Không gọi mạng; input sai kiểu trả error dict thay vì raise; không đánh giá độ tin cậy nguồn |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (3 test `test_source_audit_*`); `pytest`: **83 passed, 14 skipped, 0 failed** | Happy path, input xấu từ model, nhánh lỗi bất ngờ trả error dict | 14 test skip là stub challenge của tool có sẵn (được phép) |
| UI (lệnh chạy + link dùng thử) | `app.py`, `starter_v0/ui_core.py`, `starter_v0/tests/test_ui_core.py` (12 test), `requirements.txt` | Chat nhiều vòng tool, trả lời nhanh xác nhận, lưu transcript, tab benchmark v0–v6; kiểm tra bằng `streamlit.testing` AppTest không exception | Lỗi tool/provider hiện rõ; `send` vẫn bị chặn ở tool nếu `confirmed=false`; link deploy còn thiếu |

Tool unit tests: 3 test cho `source_audit` + 3 test contract/eval nhóm (`test_group_eval.py`) + 12 test logic UI. Ví dụ lỗi unit test bắt được mà eval không bắt: eval chỉ kiểm tra model gọi `source_audit` với đúng items; nếu tool chuẩn hóa URL sai (coi `https://www.a.com/x/` khác `https://a.com/x`) thì eval vẫn PASS nhưng người dùng nhận kết quả sai — `test_source_audit_detects_duplicate_urls_and_counts_sources` bắt được lỗi này.

### B5. Bonus Evidence

Nhóm chưa làm bonus. `send` mới chạy tới bước gọi tool với `confirmed=true` (turn 4 ở B4) nhưng chưa có bot Telegram nên chưa có `status: sent`.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | — | — | — |
| Hơn 3 tool mới (≥ 4) | — | — | — |
| `send` gửi thật lên Telegram sau xác nhận | transcript ở B4 (chưa có token) | Luồng hỏi → xác nhận → `send(confirmed=true)` đúng | Thiếu `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` |
| Test challenge (0 skipped / regression test) | — | — | 14 stub còn skip |

## 5. Khó khăn và cách xử lý

- **Gemini không dùng được cho eval:** model mặc định `gemini-3.8-flash` và `gemini-3.7-flash` trả `503 UNAVAILABLE` (quá tải). `gemini-3.5-flash` qua preflight nhưng run v0 có 10/20 case `provider_error` (6 case `429 RESOURCE_EXHAUSTED` — free tier 5 request/phút/model; 4 case `503`). Run không hợp lệ nên không dùng; nhóm chuyển sang OpenRouter (`openai/gpt-4o-mini`), toàn bộ run v0–v6 sau đó có 0 provider error.
- **Lộ key suýt commit:** API key từng được dán vào `.env.example` (file bị git theo dõi); đã chuyển sang `.env` (gitignored) và khôi phục `.env.example` trước khi commit.
- **Run group lệch cấu hình:** run group gốc ghi prompt hash `8e5e191e9a0b` không khớp prompt trong repo; nhóm chạy lại group với v4/v5/v6 đã commit để bằng chứng khớp hash.
- **Sửa một chỗ làm hỏng chỗ khác:** v5 (thêm rule đa tool) làm giảm base 1.0→0.95, group 1.0→0.9; phát hiện nhờ chạy cả hai suite, sửa ở v6.
- **Chưa có bot Telegram:** bước `send(confirmed=true)` trả lỗi thiếu token; UI hiển thị lỗi thay vì báo đã gửi.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** gần như mọi cải thiện metric — bỏ chỉ dẫn đoán bừa (v1, +0.15), ranh giới phạm vi và xác nhận gửi (v2, +0.10), ví dụ few-shot yes_no (v4, R12), giới hạn đa tool (v6). Lỗi hành vi (đoán, tự gửi, gọi thừa) nằm ở chỉ dẫn tổng quát.
- **Fix thuộc `tools.yaml`:** quy ước args (`topic=news`, query ngắn, `search_type`, handle không `@`) và boundary của `send`. v3 không làm tăng metric trên base vì các case liên quan đã pass, nhưng group suite (G02, G07, G08 kiểm tra args) đạt 10/10 với mô tả này.
- **Cần review thủ công:** case `no_tool`/refuse chỉ kiểm tra "không gọi tool", không chấm nội dung từ chối; câu trả lời cuối sau khi có kết quả tool (độ đúng của tóm tắt, có trích nguồn không) không được eval chấm; turn 1 ở B4 agent hỏi lại bằng text thay vì tool `clarify` — đúng ý nhưng sẽ FAIL nếu eval đòi `clarify`.
- **Vòng tiếp theo:** (1) thêm rule "báo rõ lỗi tool cho người dùng" — ở turn 4, agent nói chung chung "thiếu thông tin" thay vì nói thiếu cấu hình Telegram; (2) chạy suite extension và lặp lại mỗi run 2–3 lần để đo độ dao động (R11/R13 từng pass/fail không do giả thuyết); (3) cấu hình bot Telegram để hoàn tất bonus gửi thật.

## 8. Tài liệu tham khảo

- [README.md](../../README.md), [RUBRIC.md](../../RUBRIC.md), [CHECKPOINTS.md](../../CHECKPOINTS.md), [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md)
- `starter_v0/tools/README.md` (contract tool), `starter_v0/samples/` (mẫu transcript, version log)
- Streamlit docs (`st.chat_message`, `st.status`, `streamlit.testing`), Altair docs
