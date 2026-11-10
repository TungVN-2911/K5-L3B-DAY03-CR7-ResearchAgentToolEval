"""Giao diện Streamlit cho Research Agent — chạy: streamlit run app.py (từ thư mục gốc repo)."""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
AGENT_ROOT = ROOT / "starter_v0"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from chat import now_iso  # noqa: E402  # pyright: ignore[reportMissingImports]
from env_loader import load_lab_env  # noqa: E402  # pyright: ignore[reportMissingImports]
from providers import make_provider  # noqa: E402  # pyright: ignore[reportMissingImports]
from tools import load_tool_declarations, to_openai_tools  # noqa: E402  # pyright: ignore[reportMissingImports]
import ui_core  # noqa: E402  # pyright: ignore[reportMissingImports]

load_lab_env(AGENT_ROOT)

PROMPT_PATH = AGENT_ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = AGENT_ROOT / "artifacts" / "tools.yaml"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY", "openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY", "ollama": None,
}
SAMPLES = [
    ("📰", "Tin AI hôm nay", "Tìm trên web tin tức AI hôm nay"),
    ("🐦", "Tweet theo tài khoản", "3 tweet mới nhất của Sam Altman là gì?"),
    ("🔥", "Tweet nổi bật", "Tìm các tweet nổi bật nhất về tool calling"),
    ("❓", "Thiếu thông tin", "Tóm tắt 5 tweet mới nhất giúp mình"),
    ("🔗", "Kiểm tra link trùng", "Kiểm tra link trùng trong danh sách: https://openai.com/blog/a, https://www.openai.com/blog/a/, https://arxiv.org/abs/2401.01234"),
    ("📣", "Đăng Telegram", "Đăng bản tin 'AI hôm nay: OpenAI ra mắt model mới' lên Telegram giúp mình"),
]
TOOL_ICONS = {
    "clarify": "❓", "timeline": "🐦", "social_search": "🔎", "lookup": "🌐", "fetch": "📄",
    "format": "📝", "send": "📣", "policy": "📚", "papers": "🎓", "paper_text": "📑", "source_audit": "🧮",
}

st.set_page_config(page_title="CR7 Research Agent", page_icon="🔬", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(
    """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 7rem; max-width: 1100px;}
[data-testid="stChatMessage"] {border-radius: 14px; padding: .55rem .9rem;}
.sample-hint {opacity: .7; font-size: .95rem; margin: -.3rem 0 1rem;}
.card-title {font-weight: 600; font-size: 1rem; margin-bottom: .15rem;}
.card-text {opacity: .7; font-size: .88rem; line-height: 1.35; min-height: 2.6em;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;}
.pill {display:inline-block; padding:.1rem .55rem; border-radius:999px; font-size:.78rem;
       border:1px solid rgba(128,128,128,.35); margin-right:.3rem; opacity:.85}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- versions & state

VERSIONS = ui_core.list_versions()
VERSION_MAP = {v.version: v for v in VERSIONS}
VERSION_NAMES = [v.version for v in VERSIONS] or ["current"]
LATEST = VERSION_NAMES[-1]


def version_label(name: str) -> str:
    v = VERSION_MAP.get(name)
    if not v:
        return name
    score = "" if v.base_accuracy is None else f" · base {v.base_accuracy:.0%}"
    return f"{name}{score}"


def version_paths(name: str) -> tuple[Path, Path]:
    v = VERSION_MAP.get(name)
    return (v.prompt_path, v.tools_path) if v else (PROMPT_PATH, TOOLS_PATH)


def make_conversation(version: str, title: str = "Cuộc trò chuyện mới") -> dict:
    return {
        "title": title, "messages": [], "pending": None, "version": version,
        "transcript_path": None, "transcript": None,
        "created": datetime.now().strftime("%H:%M · %d/%m/%Y"),
    }


def _new_conversation(version: str | None = None) -> str:
    """Mở cuộc trò chuyện mới; nếu đã có một cuộc còn trống thì dùng lại, không tạo thêm cuộc rỗng."""
    version = version or st.session_state.get("chat_version", LATEST)
    convs = st.session_state.conversations
    cid = ui_core.find_empty_conversation(convs, prefer=st.session_state.get("active"))
    if cid is None:
        cid = uuid.uuid4().hex[:8]
        convs[cid] = make_conversation(version)
    else:
        convs[cid].update(version=version, transcript=None, transcript_path=None, pending=None,
                          created=datetime.now().strftime("%H:%M · %d/%m/%Y"))
        convs[cid] = convs.pop(cid)  # đưa lên đầu danh sách (mới nhất)
    st.session_state.active = cid
    return cid


if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    _new_conversation(LATEST)
for key, default in {"queued": None, "compare_queued": None}.items():
    st.session_state.setdefault(key, default)
if "compare" not in st.session_state:
    st.session_state.compare = {"A": make_conversation(VERSION_NAMES[0], "So sánh A"),
                                "B": make_conversation(LATEST, "So sánh B")}


def active_conv() -> dict:
    return st.session_state.conversations[st.session_state.active]


# --------------------------------------------------------------------------- sidebar


with st.sidebar:
    st.markdown("## 🔬 CR7 Research Agent")
    _is_empty = not active_conv()["messages"]
    if st.button("➕ Cuộc trò chuyện mới", width="stretch", type="primary", disabled=_is_empty,
                 help="Bạn đang ở một cuộc trò chuyện trống" if _is_empty else None):
        _new_conversation(LATEST)
        st.rerun()

    st.caption("Lịch sử")
    _history = [(cid, item) for cid, item in st.session_state.conversations.items() if item["messages"]]
    if not _history:
        st.caption("Chưa có cuộc trò chuyện nào.")
    for cid, item in reversed(_history):
        label = ("▸ " if cid == st.session_state.active else "") + f"[{item['version']}] {item['title']}"
        if st.button(label, key=f"conv_{cid}", width="stretch"):
            st.session_state.active = cid
            st.rerun()

    st.divider()
    with st.expander("⚙️ Cấu hình agent", expanded=False):
        provider_name = st.selectbox("Provider", PROVIDERS, index=0, format_func=str.title)
        provider = make_provider(provider_name)
        default_model = getattr(provider, "default_model", "") or ""
        model = st.text_input("Model", placeholder=default_model, help="Để trống để dùng model mặc định.").strip() or None
        history_window = st.slider("Số cặp hội thoại nhớ", 1, 10, 5)
        max_rounds = st.slider("Số vòng gọi tool tối đa", 1, 6, 4)

    key_env = PROVIDER_KEYS.get(provider_name)
    key_ok = key_env is None or bool(os.getenv(key_env))
    tg_ok = bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))
    st.markdown(
        f"{'🟢' if key_ok else '🔴'} API key {provider_name}  \n"
        f"{'🟢' if tg_ok else '⚪'} Telegram {'đã cấu hình' if tg_ok else 'chưa cấu hình'}  \n"
        f"<span class='pill'>{model or default_model}</span>",
        unsafe_allow_html=True,
    )
    _conv = active_conv()
    if _conv["transcript_path"] and Path(_conv["transcript_path"]).exists():
        st.download_button("⬇️ Tải transcript JSON", Path(_conv["transcript_path"]).read_bytes(),
                           file_name=Path(_conv["transcript_path"]).name, mime="application/json",
                           width="stretch")
        st.caption(f"Đã lưu: `starter_v0/transcripts/{Path(_conv['transcript_path']).name}`")


# --------------------------------------------------------------------------- chat helpers


def render_tool_events(events: list[dict], key: str = "") -> None:
    if not events:
        return
    errors = [e for e in events if ui_core.tool_error(e)]
    names = ", ".join(dict.fromkeys(e.get("tool", "?") for e in events))
    label = f"🔧 {len(events)} công cụ: {names}" + (f" · ⚠️ {len(errors)} lỗi" if errors else "")
    with st.expander(label, expanded=bool(errors)):
        for event in events:
            name = event.get("tool", "?")
            st.markdown(f"**{TOOL_ICONS.get(name, '🔧')} `{name}`**")
            st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
            err = ui_core.tool_error(event)
            if err:
                st.error(f"Lỗi công cụ: {err}")
            result = event.get("result")
            if isinstance(result, dict) and isinstance(result.get("items"), list) and result["items"]:
                for item in result["items"][:8]:
                    title = item.get("title") or item.get("text") or item.get("url") or "(không tiêu đề)"
                    url = item.get("url")
                    st.markdown(f"- [{title}]({url})" if url else f"- {str(title)[:200]}")
            with st.popover("Xem JSON kết quả"):
                st.json(result, expanded=False)


def render_message(msg: dict) -> None:
    avatar = "🧑" if msg["role"] == "user" else "🔬"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("status") == "provider_error":
            st.warning(msg["content"])
            st.caption(msg.get("error", ""))
        elif msg.get("status") == "waiting_for_user":
            st.info(f"**Agent hỏi lại:** {msg['content']}")
        else:
            st.markdown(msg["content"])
        if msg["role"] == "assistant" and not msg.get("tool_events") and msg.get("status") == "answered":
            st.caption("Không gọi công cụ")
        render_tool_events(msg.get("tool_events") or [])


def history_for_model(messages: list[dict]) -> list[dict[str, str]]:
    return [{"role": m["role"], "content": m["content"]} for m in messages
            if m["role"] in {"user", "assistant"} and m.get("status") != "provider_error"]


def agent_reply(conv: dict) -> None:
    """Chạy agent (đúng version của cuộc trò chuyện) cho tin nhắn user cuối, hiện tiến trình, lưu transcript."""
    prompt_path, tools_path = version_paths(conv["version"])
    if conv["transcript"] is None:
        path, transcript = ui_core.new_transcript(
            version=conv["version"], provider_name=provider_name, model=model or default_model,
            history_window=history_window, max_tool_rounds=max_rounds,
            system_prompt_path=prompt_path, tools_path=tools_path)
        conv["transcript_path"], conv["transcript"] = str(path), transcript
    conv["pending"] = None

    with st.chat_message("assistant", avatar="🔬"):
        status = st.status(f"{conv['version']} đang suy nghĩ…", expanded=False)

        def on_event(kind: str, data: dict) -> None:
            if kind == "tool_call":
                status.update(label=f"{TOOL_ICONS.get(data['name'], '🔧')} Đang chạy `{data['name']}`…")
                status.write(f"`{data['name']}` {json.dumps(data['args'], ensure_ascii=False)}")
            elif kind == "tool_result" and ui_core.tool_error(data):
                status.write(f"⚠️ `{data.get('tool')}` lỗi: {ui_core.tool_error(data)}")
            elif kind == "thinking" and data["round"] > 1:
                status.update(label="Đang tổng hợp câu trả lời…")

        started = now_iso()
        result = ui_core.run_turn(
            provider=provider,
            system_prompt=prompt_path.read_text(encoding="utf-8"),
            tools=to_openai_tools(load_tool_declarations(tools_path)),
            history=history_for_model(conv["messages"][:-1]),
            user_text=conv["messages"][-1]["content"],
            model=model,
            history_window=history_window,
            max_tool_rounds=max_rounds,
            on_event=on_event,
        )
        failed = result.status == "provider_error"
        status.update(label="Lỗi provider" if failed else "Xong", state="error" if failed else "complete")

    ui_core.record_turn(Path(conv["transcript_path"]), conv["transcript"], conv["messages"][-1]["content"],
                        result, started)
    conv["messages"].append({
        "role": "assistant", "content": result.assistant_text, "status": result.status,
        "tool_events": result.tool_events, "error": result.error,
    })
    conv["pending"] = result.pending


def add_user_message(conv: dict, text: str) -> None:
    conv["messages"].append({"role": "user", "content": text})
    if conv["title"] in {"Cuộc trò chuyện mới"}:
        conv["title"] = ui_core.conversation_title(text)


def handle_user_message(text: str, *, regenerate: bool = False) -> None:
    conv = active_conv()
    if not regenerate:
        add_user_message(conv, text)
        render_message(conv["messages"][-1])
    agent_reply(conv)
    st.rerun()


def sample_cards(state_key: str, prefix: str) -> None:
    cols = st.columns(3, gap="medium")
    for i, (icon, title, prompt_text) in enumerate(SAMPLES):
        with cols[i % 3].container(border=True):
            st.markdown(f"<div class='card-title'>{icon} {title}</div>"
                        f"<div class='card-text'>{prompt_text}</div>", unsafe_allow_html=True)
            if st.button("Hỏi thử →", key=f"{prefix}_{i}", help=prompt_text, width="stretch"):
                st.session_state[state_key] = prompt_text
                st.rerun()


def version_badge(name: str) -> str:
    v = VERSION_MAP.get(name)
    if not v:
        return f"`{name}`"
    check = "✅ hash khớp version_log" if v.hash_matches_log else "⚠️ hash không khớp version_log"
    return f"`{v.artifact_version}` · {check}"


# --------------------------------------------------------------------------- pages
# Mỗi trang là một hàm; st.navigation(position="top") đặt thanh điều hướng cố định trên header
# (không cuộn theo nội dung), mỗi trang có URL riêng: /, /compare, /benchmark, /tools.


def _on_chat_version_change() -> None:
    conv = active_conv()
    chosen = st.session_state.chat_version
    if conv["messages"]:
        _new_conversation(chosen)  # giữ nguyên cuộc cũ, mở cuộc mới với version vừa chọn
    else:
        conv["version"] = chosen
        conv["transcript"] = conv["transcript_path"] = None


def page_chat() -> None:
    conv = active_conv()
    st.session_state.chat_version = conv["version"]
    head, pick = st.columns([3, 1], vertical_alignment="bottom")
    with pick:
        st.selectbox("Phiên bản agent", VERSION_NAMES, key="chat_version", format_func=version_label,
                     on_change=_on_chat_version_change,
                     help="Đổi version khi đang chat sẽ mở cuộc trò chuyện mới với version đó.")
    with head:
        if conv["messages"]:
            asked = sum(1 for m in conv["messages"] if m["role"] == "user")
            st.markdown(f"### {conv['title']}")
            st.caption(f"{conv.get('created', '')} · {asked} câu hỏi · {version_badge(conv['version'])}")
        else:
            st.markdown("## Xin chào 👋 Mình có thể giúp bạn nghiên cứu gì hôm nay?")
    if not conv["messages"]:
        st.markdown("<div class='sample-hint'>Tìm tin web, đọc tweet theo tài khoản hoặc chủ đề, đọc URL, "
                    "kiểm tra link trùng và đăng Telegram (luôn hỏi xác nhận trước). Chọn một gợi ý để thử, "
                    "hoặc mở trang <b>So sánh</b> để xem các version trả lời khác nhau thế nào:</div>",
                    unsafe_allow_html=True)
        sample_cards("queued", "sample")

    for msg in conv["messages"]:
        render_message(msg)

    # Hành động sau câu trả lời cuối: trả lời nhanh cho clarify, tạo lại, sao chép
    last = conv["messages"][-1] if conv["messages"] else None
    if last and last["role"] == "assistant":
        replies = ui_core.quick_replies(conv["pending"])
        with st.container(horizontal=True, gap="small"):
            for i, reply in enumerate(replies):
                if st.button(reply, key=f"qr_{i}", type="primary" if i == 0 else "secondary"):
                    st.session_state.queued = reply
                    st.rerun()
            if st.button("🔄 Tạo lại", help="Chạy lại câu hỏi cuối", type="tertiary"):
                conv["messages"].pop()
                st.session_state.queued = ("__regenerate__", conv["messages"][-1]["content"])
                st.rerun()
            with st.popover("📋 Sao chép", type="tertiary"):
                st.code(last["content"], language=None, wrap_lines=True)

    placeholder = "Trả lời câu hỏi của agent…" if conv["pending"] else f"Hỏi agent {conv['version']} về tin tức, tweet, URL…"
    typed = st.chat_input(placeholder)
    queued, st.session_state.queued = st.session_state.queued, None
    if typed:
        handle_user_message(typed)
    elif isinstance(queued, tuple):
        handle_user_message(queued[1], regenerate=True)
    elif queued:
        handle_user_message(queued)


def _reset_compare_side(side: str) -> None:
    st.session_state.compare[side] = make_conversation(st.session_state[f"cmp_{side}"], f"So sánh {side}")


def page_compare() -> None:
    cmp = st.session_state.compare
    st.markdown("### So sánh hai version")
    st.caption("Gửi cùng một câu hỏi cho hai version để thấy khác biệt về cách chọn tool, tham số, hỏi lại và xác nhận. "
               "Mỗi bên có lịch sử riêng; nút trả lời nhanh ở mỗi cột chỉ gửi cho bên đó.")

    for side in ("A", "B"):
        st.session_state.setdefault(f"cmp_{side}", cmp[side]["version"])
    with st.container(horizontal=True, gap="small", vertical_alignment="bottom"):
        st.selectbox("Version A", VERSION_NAMES, key="cmp_A", format_func=version_label,
                     on_change=_reset_compare_side, args=("A",))
        st.selectbox("Version B", VERSION_NAMES, key="cmp_B", format_func=version_label,
                     on_change=_reset_compare_side, args=("B",))
        if st.button("🧹 Làm mới", help="Xóa hội thoại so sánh của cả hai bên"):
            _reset_compare_side("A")
            _reset_compare_side("B")
            st.rerun()

    va, vb = VERSION_MAP.get(cmp["A"]["version"]), VERSION_MAP.get(cmp["B"]["version"])
    if va and vb:
        with st.expander(f"📝 Prompt {va.version} → {vb.version} khác nhau chỗ nào?"):
            diff = ui_core.prompt_diff(va.prompt_path, vb.prompt_path)
            st.code(diff or "Hai prompt giống hệt nhau.", language="diff", wrap_lines=True)
            if va.tools_path.read_bytes() != vb.tools_path.read_bytes():
                st.caption(f"`tools.yaml` cũng khác nhau ({va.artifact_version} → {vb.artifact_version}).")
            else:
                st.caption("`tools.yaml` giống nhau.")

    if not cmp["A"]["messages"] and not cmp["B"]["messages"]:
        st.markdown("<div class='sample-hint'>Gợi ý để thấy khác biệt rõ: <b>Thiếu thông tin</b>, "
                    "<b>Đăng Telegram</b> (so v0 với v6), hoặc một câu ngoài phạm vi như "
                    "<i>“Viết giúp mình hàm Python tính Fibonacci”</i>.</div>", unsafe_allow_html=True)
        sample_cards("compare_queued", "cmp_sample")

    cols = st.columns(2, gap="large")
    for col, side in zip(cols, ("A", "B")):
        conv = cmp[side]
        with col:
            v = VERSION_MAP.get(conv["version"])
            st.markdown(f"#### {side} · {conv['version']}")
            if v:
                st.caption(f"**{v.changed_artifact or '—'}** · {v.hypothesis or ''}")
            for msg in conv["messages"]:
                render_message(msg)
            replies = ui_core.quick_replies(conv["pending"])
            if replies:
                with st.container(horizontal=True, gap="small"):
                    for i, reply in enumerate(replies):
                        if st.button(reply, key=f"cmp_qr_{side}_{i}", type="primary" if i == 0 else "secondary"):
                            st.session_state.compare_queued = ((side,), reply)
                            st.rerun()

    typed = st.chat_input("Gửi cùng câu hỏi cho cả hai version…")
    queued, st.session_state.compare_queued = st.session_state.compare_queued, None
    if typed:
        queued = (("A", "B"), typed)
    elif isinstance(queued, str):
        queued = (("A", "B"), queued)
    if queued:
        sides, text = queued
        for side in sides:
            add_user_message(cmp[side], text)
        live = st.columns(2, gap="large")
        for side in sides:
            with live[0 if side == "A" else 1]:
                render_message(cmp[side]["messages"][-1])
                agent_reply(cmp[side])
        st.rerun()


def page_benchmark() -> None:
    import altair as alt
    import pandas as pd

    suite = st.radio("Bộ eval", ["base", "group"], horizontal=True,
                     format_func=lambda s: "Base (20 case)" if s == "base" else "Group (10 case nhóm)")
    runs = ui_core.load_runs(ui_core.RUNS_DIR, suite)
    if not runs:
        st.info("Chưa có run hợp lệ cho bộ này trong `starter_v0/runs/`.")
    else:
        all_versions = list(runs)
        default = [v for v in all_versions if v in {"v0", "v1", "v2", "v3"}] or all_versions
        chosen = st.multiselect("Version so sánh", all_versions, default=default)
        runs = {v: runs[v] for v in all_versions if v in chosen}
        if runs:
            rows = ui_core.metric_rows(runs)
            first, last_row = rows[0], rows[-1]
            kpis = st.columns(len(ui_core.METRICS))
            for col, (key, label) in zip(kpis, ui_core.METRICS):
                value, base = last_row.get(key), first.get(key)
                col.metric(f"{label} · {last_row['version']}", "—" if value is None else f"{value:.0%}",
                           None if value is None or base is None or len(rows) == 1
                           else f"{(value - base) * 100:+.0f} điểm so với {first['version']}")

            long = pd.DataFrame([
                {"version": r["version"], "metric": label, "value": r[key]}
                for r in rows for key, label in ui_core.METRICS if r[key] is not None
            ])
            order = list(runs)
            bars = (
                alt.Chart(long)
                .mark_bar(color="#2a78d6", cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=26)
                .encode(
                    x=alt.X("version:N", sort=order, title=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("value:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", grid=True,
                            gridOpacity=0.25), title=None),
                    tooltip=[alt.Tooltip("version:N"), alt.Tooltip("metric:N"),
                             alt.Tooltip("value:Q", format=".0%")],
                )
            )
            labels = bars.mark_text(dy=-8, fontSize=11).encode(text=alt.Text("value:Q", format=".0%"),
                                                               color=alt.value("#888"))
            st.markdown("#### Thông số theo version")
            st.altair_chart(
                alt.layer(bars, labels, data=long).properties(width=210, height=190)
                .facet(column=alt.Column("metric:N", title=None, sort=[l for _, l in ui_core.METRICS]))
                .configure_view(stroke=None),
                width="content",
            )

            st.markdown("#### Bảng số liệu")
            table = pd.DataFrame(rows)[["version", "passed", "case_accuracy", "tool_routing_accuracy",
                                        "argument_accuracy", "multiturn_accuracy", "delta", "artifact_version",
                                        "run_file"]]
            st.dataframe(
                table, hide_index=True, width="stretch",
                column_config={
                    "case_accuracy": st.column_config.NumberColumn("Case acc.", format="percent"),
                    "tool_routing_accuracy": st.column_config.NumberColumn("Routing", format="percent"),
                    "argument_accuracy": st.column_config.NumberColumn("Args", format="percent"),
                    "multiturn_accuracy": st.column_config.NumberColumn("Multi-turn", format="percent"),
                    "delta": st.column_config.NumberColumn("Δ case acc.", format="%+.2f"),
                    "passed": "Pass", "artifact_version": "Artifact", "run_file": "Run file",
                },
            )

            st.markdown("#### Pass / fail từng case")
            cells = pd.DataFrame(ui_core.case_matrix(runs))
            cells["kết quả"] = cells["passed"].map({True: "Pass", False: "Fail"})
            cells["ký hiệu"] = cells["passed"].map({True: "✓", False: "✗"})
            base_chart = alt.Chart(cells).encode(
                x=alt.X("version:N", sort=order, title=None, axis=alt.Axis(orient="top", labelAngle=0)),
                y=alt.Y("case:N", title=None, sort=sorted(cells["case"].unique()),
                        axis=alt.Axis(labelOverlap=False, labelLimit=260, labelFontSize=11)),
            )
            heat = base_chart.mark_rect(cornerRadius=3, stroke="white", strokeWidth=2).encode(
                color=alt.Color("kết quả:N", scale=alt.Scale(domain=["Pass", "Fail"], range=["#0ca30c", "#d03b3b"]),
                                legend=alt.Legend(orient="bottom", title=None)),
                tooltip=["case", "version", "kết quả", "failure_type", "failures"],
            )
            marks = base_chart.mark_text(color="white", fontSize=13, fontWeight="bold").encode(text="ký hiệu:N")
            st.altair_chart((heat + marks).properties(height=26 * cells["case"].nunique() + 40),
                            width="stretch")

            fails = cells[~cells["passed"]]
            if not fails.empty:
                with st.expander(f"Chi tiết {len(fails)} lượt fail"):
                    st.dataframe(fails[["version", "case", "failure_type", "failures"]], hide_index=True,
                                 width="stretch")

            log = [r for r in ui_core.read_version_log() if r.get("version") in runs]
            if log:
                st.markdown("#### Giả thuyết từng version (version_log.csv)")
                st.dataframe(pd.DataFrame(log)[["version", "changed_artifact", "hypothesis", "metric_before",
                                                "metric_after"]], hide_index=True, width="stretch")

def page_tools() -> None:
    st.markdown("#### Công cụ agent đang dùng")
    st.caption("Đọc trực tiếp từ `starter_v0/artifacts/tools.yaml`.")
    for decl in load_tool_declarations(TOOLS_PATH):
        name = decl["name"]
        params = decl.get("parameters", {}).get("properties", {})
        required = set(decl.get("parameters", {}).get("required", []))
        tag = " · 🆕 tool nhóm" if name == "source_audit" else ""
        with st.expander(f"{TOOL_ICONS.get(name, '🔧')} `{name}`{tag}"):
            st.write(decl.get("description", ""))
            st.dataframe(
                [{"tham số": p + (" *" if p in required else ""), "kiểu": spec.get("type", ""),
                  "mô tả": spec.get("description", "") + (f" (enum: {', '.join(map(str, spec['enum']))})"
                                                         if spec.get("enum") else "")}
                 for p, spec in params.items()],
                hide_index=True, width="stretch",
            )


nav = st.navigation(
    [
        st.Page(page_chat, title="Chat", icon=":material/forum:", url_path="chat", default=True),
        st.Page(page_compare, title="So sánh version", icon=":material/compare_arrows:", url_path="compare"),
        st.Page(page_benchmark, title="Benchmark", icon=":material/monitoring:", url_path="benchmark"),
        st.Page(page_tools, title="Công cụ", icon=":material/construction:", url_path="tools"),
    ],
    position="top",
)
nav.run()
