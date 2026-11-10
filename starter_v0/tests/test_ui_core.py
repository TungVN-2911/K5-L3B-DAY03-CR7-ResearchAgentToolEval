"""Unit test cho logic UI (ui_core.py) — offline, dùng provider giả."""
from __future__ import annotations

import json
from pathlib import Path

from providers.base import ModelResponse, ToolCall
import ui_core


class ScriptedProvider:
    """Trả lần lượt các response đã soạn; ghi lại messages mỗi lần gọi."""

    def __init__(self, responses: list[ModelResponse | Exception]) -> None:
        self.responses = list(responses)
        self.seen: list[list[dict[str, str]]] = []

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        self.seen.append(list(messages))
        nxt = self.responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


def _run(provider, user_text="xin chào", history=None, **kw):
    return ui_core.run_turn(provider=provider, system_prompt="SYS", tools=[], history=history or [],
                            user_text=user_text, **kw)


def test_direct_answer_without_tools() -> None:
    result = _run(ScriptedProvider([ModelResponse(text="Chào bạn!")]))
    assert result.status == "answered"
    assert result.assistant_text == "Chào bạn!"
    assert result.tool_events == []


def test_tool_then_final_answer_feeds_results_back_to_model() -> None:
    items = [{"title": "A", "url": "https://a.com/x"}, {"title": "B", "url": "https://a.com/x/"}]
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("source_audit", {"items": items})]),
        ModelResponse(text="Có 1 URL bị trùng."),
    ])
    events: list[str] = []
    result = _run(provider, on_event=lambda kind, data: events.append(kind))

    assert result.status == "answered"
    assert result.assistant_text == "Có 1 URL bị trùng."
    assert result.tool_events[0]["tool"] == "source_audit"
    assert "TOOL_RESULTS_JSON" in provider.seen[1][-1]["content"]  # kết quả tool được gửi lại model
    assert events == ["thinking", "tool_call", "tool_result", "thinking"]


def test_clarify_yes_no_pauses_and_offers_quick_replies() -> None:
    provider = ScriptedProvider([ModelResponse(tool_calls=[ToolCall(
        "clarify", {"question": "Xác nhận đăng lên Telegram?", "response_type": "yes_no"})])])
    result = _run(provider, user_text="Đăng bản tin này lên Telegram")

    assert result.status == "waiting_for_user"
    assert result.assistant_text == "Xác nhận đăng lên Telegram?"
    assert result.pending["response_type"] == "yes_no"
    assert ui_core.quick_replies(result.pending) == ["Có, xác nhận", "Không, hủy"]
    assert len(provider.seen) == 1  # không gọi model tiếp khi đang chờ người dùng


def test_quick_replies_for_choice_and_text() -> None:
    assert ui_core.quick_replies({"response_type": "choice", "options": ["sama", "elonmusk"]}) == ["sama", "elonmusk"]
    assert ui_core.quick_replies({"response_type": "text"}) == []
    assert ui_core.quick_replies(None) == []


def test_send_without_confirmation_never_reaches_network() -> None:
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("send", {"text": "hi"})]),
        ModelResponse(text="Cần bạn xác nhận trước khi gửi."),
    ])
    result = _run(provider)
    assert result.tool_events[0]["result"]["status"] == "needs_confirmation"


def test_provider_error_is_reported_not_raised() -> None:
    result = _run(ScriptedProvider([RuntimeError("503 UNAVAILABLE")]))
    assert result.status == "provider_error"
    assert "503" in result.error


def test_tool_errors_are_surfaced() -> None:
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("made_up_tool", {})]),
        ModelResponse(text="Xin lỗi, công cụ lỗi."),
    ])
    result = _run(provider)
    assert ui_core.tool_error(result.tool_events[0]) is not None
    assert ui_core.tool_error({"result": {"items": []}}) is None


def test_max_tool_rounds_stops_loop() -> None:
    call = ModelResponse(tool_calls=[ToolCall("source_audit", {"items": []})])
    result = _run(ScriptedProvider([call, call]), max_tool_rounds=2)
    assert result.status == "max_tool_rounds"
    assert len(result.rounds) == 2


def test_history_window_trims_old_turns() -> None:
    history = []
    for i in range(10):
        history += [{"role": "user", "content": f"u{i}"}, {"role": "assistant", "content": f"a{i}"}]
    provider = ScriptedProvider([ModelResponse(text="ok")])
    _run(provider, history=history, history_window=2, user_text="mới")
    sent = provider.seen[0]
    assert sent[0]["role"] == "system"
    assert [m["content"] for m in sent[1:]] == ["u8", "a8", "u9", "a9", "mới"]


def test_transcript_written_with_artifact_hashes(tmp_path: Path) -> None:
    path, transcript = ui_core.new_transcript(version="v9", provider_name="fake", model="m",
                                              history_window=5, max_tool_rounds=4, transcripts_dir=tmp_path)
    result = ui_core.TurnResult("answered", "ok")
    ui_core.record_turn(path, transcript, "hello", result, started_at="t0")

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["source"] == "streamlit_ui"
    assert saved["prompt_hash"] and saved["tools_hash"]
    assert saved["turns"][0]["user"] == "hello" and saved["turns"][0]["status"] == "answered"


def _write_run(dir_: Path, name: str, version: str, acc: float, errors: int = 0, generated="2026-01-01") -> None:
    run = {
        "version": version, "suite": "base", "model": "m", "artifact_version": version,
        "generated_at": generated,
        "summary": {"total_cases": 2, "measured_cases": 2 - errors, "provider_error_cases": errors,
                    "passed_cases": int(acc * 2), "case_accuracy": acc, "tool_routing_accuracy": acc,
                    "argument_accuracy": acc, "multiturn_accuracy": None},
        "results": [{"id": "R01", "result": {"passed": acc >= 0.5, "failure_type": "wrong_tool", "failures": []}}],
    }
    (dir_ / name).write_text(json.dumps(run), encoding="utf-8")


def test_benchmark_keeps_latest_valid_run_per_version(tmp_path: Path) -> None:
    _write_run(tmp_path, "v10_a.json", "v10", 1.0)
    _write_run(tmp_path, "v2_a.json", "v2", 0.5, generated="2026-01-01")
    _write_run(tmp_path, "v2_b.json", "v2", 1.0, generated="2026-01-02")
    _write_run(tmp_path, "v2_bad.json", "v2", 0.0, errors=1, generated="2026-01-03")  # không hợp lệ

    runs = ui_core.load_runs(tmp_path, "base")
    assert list(runs) == ["v2", "v10"]  # sắp xếp theo số, không theo chữ
    assert runs["v2"]["_file"] == "runs/v2_b.json"

    rows = ui_core.metric_rows(runs)
    assert rows[0]["delta"] is None and rows[1]["delta"] == 0.0
    assert {c["version"] for c in ui_core.case_matrix(runs)} == {"v2", "v10"}


def test_latest_version_label_ignores_branch_rows(tmp_path: Path) -> None:
    log = tmp_path / "log.csv"
    log.write_text("version,author\nv0,a\nv3,a\nv3-source-audit,b\nv12,a\n", encoding="utf-8")
    assert ui_core.latest_version_label(log) == "v12"
    assert ui_core.latest_version_label(tmp_path / "missing.csv") == "ui"


def test_version_snapshots_match_version_log() -> None:
    versions = ui_core.list_versions()
    names = [v.version for v in versions]
    assert names[:7] == ["v0", "v1", "v2", "v3", "v4", "v5", "v6"]
    # mỗi snapshot phải đúng byte với hash đã ghi khi chạy eval
    assert all(v.hash_matches_log for v in versions if v.version in {"v0", "v1", "v2", "v3", "v4", "v5", "v6"})
    assert versions[-1].base_accuracy == 1.0


def test_prompt_diff_shows_changed_lines() -> None:
    v0 = ui_core.VERSIONS_DIR / "v0" / "system_prompt.md"
    v1 = ui_core.VERSIONS_DIR / "v1" / "system_prompt.md"
    diff = ui_core.prompt_diff(v0, v1)
    assert "-If a request mentions a tweet" in diff or "Sam Altman" in diff
    assert "+Never guess information" in diff


def test_find_empty_conversation_reuses_instead_of_creating() -> None:
    convs = {"a": {"messages": [{"role": "user", "content": "hi"}]}, "b": {"messages": []}, "c": {"messages": []}}
    assert ui_core.find_empty_conversation(convs, prefer="c") == "c"   # ưu tiên cuộc đang mở nếu trống
    assert ui_core.find_empty_conversation(convs, prefer="a") == "b"   # cuộc đang mở có tin nhắn → lấy cuộc trống khác
    assert ui_core.find_empty_conversation({"a": convs["a"]}, prefer="a") is None
