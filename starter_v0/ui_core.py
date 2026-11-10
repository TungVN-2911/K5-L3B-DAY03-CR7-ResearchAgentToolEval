"""Logic dùng chung cho UI Streamlit (app.py): vòng lặp agent, transcript, benchmark.

Không import streamlit ở đây để có thể unit test offline (tests/test_ui_core.py).
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from chat import (
    assistant_tool_message,
    execute_tool_call,
    now_iso,
    safe_slug,
    tool_results_message,
    trim_history,
    write_transcript,
)
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"

METRICS = [
    ("case_accuracy", "Case accuracy"),
    ("tool_routing_accuracy", "Tool routing"),
    ("argument_accuracy", "Arguments"),
    ("multiturn_accuracy", "Multi-turn"),
]

EventCallback = Callable[[str, dict[str, Any]], None]


# --------------------------------------------------------------------------- agent turn


@dataclass
class TurnResult:
    status: str  # answered | waiting_for_user | max_tool_rounds | provider_error
    assistant_text: str
    rounds: list[dict[str, Any]] = field(default_factory=list)
    tool_events: list[dict[str, Any]] = field(default_factory=list)
    pending: dict[str, Any] | None = None  # clarify payload when waiting_for_user
    error: str | None = None


def run_turn(
    *,
    provider: Any,
    system_prompt: str,
    tools: list[dict[str, Any]],
    history: list[dict[str, str]],
    user_text: str,
    model: str | None = None,
    history_window: int = 5,
    max_tool_rounds: int = 4,
    on_event: EventCallback | None = None,
) -> TurnResult:
    """Một lượt chat: gọi model, chạy tool, đưa kết quả lại cho model đến khi có câu trả lời.

    Cùng logic với chat.run_model_tool_loop nhưng có callback để UI hiện tiến trình,
    và trả về payload của clarify để UI dựng nút trả lời nhanh.
    """
    emit = on_event or (lambda kind, data: None)
    working = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, history_window),
        {"role": "user", "content": user_text},
    ]
    rounds: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    try:
        for round_index in range(1, max_tool_rounds + 1):
            emit("thinking", {"round": round_index})
            response = provider.complete(working, tools, model=model, temperature=0.0)
            calls = response.tool_calls
            record: dict[str, Any] = {
                "round": round_index,
                "assistant_text": response.text,
                "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
                "tool_results": [],
            }
            if not calls:
                rounds.append(record)
                text = (response.text or "").strip() or "Mình chưa có câu trả lời cho yêu cầu này."
                return TurnResult("answered", text, rounds, events)

            working.append(assistant_tool_message(response.text, calls))
            done_events: list[dict[str, Any]] = []
            for call in calls:
                emit("tool_call", {"name": call.name, "args": call.args})
                event = execute_tool_call(call)
                record["tool_results"].append(event)
                events.append(event)
                emit("tool_result", event)
                result = event.get("result")
                if isinstance(result, dict) and result.get("awaiting_user"):
                    rounds.append(record)
                    question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                    pending = {
                        "question": question,
                        "response_type": result.get("response_type") or "text",
                        "options": list(result.get("options") or []),
                    }
                    return TurnResult("waiting_for_user", question, rounds, events, pending=pending)
                done_events.append(event)
            rounds.append(record)
            working.append(tool_results_message(done_events))
    except Exception as exc:  # lỗi provider: báo rõ cho người dùng, không che
        return TurnResult(
            "provider_error",
            "Không gọi được model. Bạn thử lại sau ít giây nhé.",
            rounds,
            events,
            error=f"{type(exc).__name__}: {exc}",
        )

    return TurnResult(
        "max_tool_rounds",
        f"Agent đã dừng sau {max_tool_rounds} vòng gọi tool mà chưa có câu trả lời cuối. Xem chi tiết công cụ bên dưới.",
        rounds,
        events,
    )


def tool_error(event: dict[str, Any]) -> str | None:
    """Trả về thông điệp lỗi nếu tool lỗi (để UI hiện rõ, không che lỗi)."""
    result = event.get("result")
    if isinstance(result, dict):
        if result.get("error"):
            return str(result.get("message") or result.get("error"))
        if result.get("status") in {"error", "failed"}:
            return str(result.get("message") or result.get("status"))
    return None


def quick_replies(pending: dict[str, Any] | None) -> list[str]:
    """Các nút trả lời nhanh cho câu hỏi clarify."""
    if not pending:
        return []
    kind = pending.get("response_type")
    if kind == "yes_no":
        return ["Có, xác nhận", "Không, hủy"]
    if kind == "choice":
        return [str(o) for o in pending.get("options") or []][:6]
    return []


def find_empty_conversation(conversations: dict[str, dict[str, Any]], prefer: str | None = None) -> str | None:
    """ID một cuộc trò chuyện chưa có tin nhắn (ưu tiên `prefer`), để tái sử dụng thay vì tạo thêm cuộc rỗng."""
    if prefer in conversations and not conversations[prefer].get("messages"):
        return prefer
    return next((cid for cid, conv in conversations.items() if not conv.get("messages")), None)


def conversation_title(text: str, limit: int = 42) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------- transcript


def new_transcript(*, version: str, provider_name: str, model: str | None,
                   history_window: int, max_tool_rounds: int,
                   system_prompt_path: Path = ARTIFACTS_DIR / "system_prompt.md",
                   tools_path: Path = ARTIFACTS_DIR / "tools.yaml",
                   transcripts_dir: Path = TRANSCRIPTS_DIR) -> tuple[Path, dict[str, Any]]:
    artifact = build_artifact_version(version, system_prompt_path, tools_path)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), stamp])
    transcript = {
        "transcript_id": transcript_id,
        "source": "streamlit_ui",
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcripts_dir / f"{transcript_id}.transcript.json", transcript


def record_turn(path: Path, transcript: dict[str, Any], user_text: str, result: TurnResult,
                started_at: str) -> dict[str, Any]:
    turn = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": started_at,
        "user": user_text,
        "status": result.status,
        "assistant_text": result.assistant_text,
        "rounds": result.rounds,
        "tool_events": result.tool_events,
        "ended_at": now_iso(),
    }
    if result.error:
        turn["error"] = result.error
    transcript["turns"].append(turn)
    write_transcript(path, transcript)
    return turn


# --------------------------------------------------------------------------- version snapshots

VERSIONS_DIR = ARTIFACTS_DIR / "versions"


@dataclass
class AgentVersion:
    version: str
    prompt_path: Path
    tools_path: Path
    artifact_version: str
    hash_matches_log: bool | None  # None = version không có trong version_log
    hypothesis: str = ""
    changed_artifact: str = ""
    base_accuracy: float | None = None


def list_versions(versions_dir: Path = VERSIONS_DIR, log_path: Path = ARTIFACTS_DIR / "version_log.csv",
                  runs_dir: Path = RUNS_DIR) -> list[AgentVersion]:
    """Các snapshot vN/ (system_prompt.md + tools.yaml), kèm kiểm tra hash với version_log và điểm base."""
    log = {row.get("version"): row for row in read_version_log(log_path)}
    scores = {v: run["summary"].get("case_accuracy") for v, run in load_runs(runs_dir, "base").items()}
    found: list[AgentVersion] = []
    if not versions_dir.is_dir():
        return found
    for folder in versions_dir.iterdir():
        prompt, tools = folder / "system_prompt.md", folder / "tools.yaml"
        if not (folder.is_dir() and prompt.is_file() and tools.is_file()):
            continue
        art = build_artifact_version(folder.name, prompt, tools)
        row = log.get(folder.name)
        matches = None if row is None else (
            art.prompt_hash.startswith(row.get("prompt_hash", "")) and art.tools_hash.startswith(row.get("tools_hash", ""))
        )
        found.append(AgentVersion(
            version=folder.name, prompt_path=prompt, tools_path=tools, artifact_version=art.artifact_version,
            hash_matches_log=matches, hypothesis=(row or {}).get("hypothesis", ""),
            changed_artifact=(row or {}).get("changed_artifact", ""), base_accuracy=scores.get(folder.name),
        ))
    return sorted(found, key=lambda v: version_sort_key(v.version))


def prompt_diff(old_path: Path, new_path: Path) -> str:
    """Unified diff giữa hai prompt (để hiển thị version khác nhau chỗ nào)."""
    import difflib

    old = old_path.read_text(encoding="utf-8").splitlines()
    new = new_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(difflib.unified_diff(old, new, fromfile=old_path.parent.name, tofile=new_path.parent.name,
                                          lineterm="", n=1))


# --------------------------------------------------------------------------- versions & benchmark


def latest_version_label(log_path: Path = ARTIFACTS_DIR / "version_log.csv", default: str = "ui") -> str:
    """Nhãn version mới nhất trong version_log (vd 'v6'), bỏ qua các dòng nhánh như 'v3-source-audit'."""
    try:
        with log_path.open(encoding="utf-8") as fh:
            versions = [row.get("version", "") for row in csv.DictReader(fh)]
    except OSError:
        return default
    plain = [v for v in versions if re.fullmatch(r"v\d+", v or "")]
    return max(plain, key=lambda v: int(v[1:])) if plain else default


def read_version_log(log_path: Path = ARTIFACTS_DIR / "version_log.csv") -> list[dict[str, str]]:
    try:
        with log_path.open(encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except OSError:
        return []


def version_sort_key(version: str) -> tuple[int, str]:
    match = re.match(r"v(\d+)(.*)", version)
    return (int(match.group(1)), match.group(2)) if match else (10**6, version)


def is_valid_run(summary: dict[str, Any]) -> bool:
    return (
        summary.get("provider_error_cases") == 0
        and summary.get("total_cases", 0) > 0
        and summary.get("measured_cases") == summary.get("total_cases")
    )


def load_runs(runs_dir: Path = RUNS_DIR, suite: str = "base") -> dict[str, dict[str, Any]]:
    """Run hợp lệ mới nhất cho mỗi version của một suite: {version: run_json + '_file'}."""
    best: dict[str, dict[str, Any]] = {}
    for path in sorted(runs_dir.glob("*.json")):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if run.get("suite") != suite or not is_valid_run(run.get("summary", {})):
            continue
        version = str(run.get("version"))
        run["_file"] = f"runs/{path.name}"
        current = best.get(version)
        if current is None or str(run.get("generated_at", "")) >= str(current.get("generated_at", "")):
            best[version] = run
    return dict(sorted(best.items(), key=lambda kv: version_sort_key(kv[0])))


def metric_rows(runs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous: float | None = None
    for version, run in runs.items():
        s = run["summary"]
        acc = s.get("case_accuracy")
        rows.append({
            "version": version,
            "passed": f"{s.get('passed_cases')}/{s.get('total_cases')}",
            **{key: s.get(key) for key, _ in METRICS},
            "delta": None if previous is None or acc is None else round(acc - previous, 4),
            "model": run.get("model"),
            "artifact_version": run.get("artifact_version"),
            "run_file": run["_file"],
        })
        previous = acc
    return rows


def case_matrix(runs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Một dòng cho mỗi (case, version): passed + failure_type, để vẽ ma trận pass/fail."""
    cells: list[dict[str, Any]] = []
    for version, run in runs.items():
        for item in run.get("results", []):
            res = item.get("result", {})
            cells.append({
                "case": item.get("id"),
                "version": version,
                "passed": bool(res.get("passed")),
                "failure_type": "" if res.get("passed") else (res.get("failure_type") or ""),
                "failures": "; ".join(res.get("failures") or []),
            })
    return cells
