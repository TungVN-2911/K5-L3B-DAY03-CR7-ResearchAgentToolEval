from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
AGENT_ROOT = ROOT / "starter_v0"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from agent import ResearchAgent  # pyright: ignore[reportMissingImports]
from env_loader import load_lab_env  # pyright: ignore[reportMissingImports]
from providers import make_provider  # pyright: ignore[reportMissingImports]
from tools import load_tool_declarations, to_openai_tools  # pyright: ignore[reportMissingImports]


load_lab_env(AGENT_ROOT)

st.set_page_config(page_title="AI Agent Group Demo", page_icon="🤖")
st.title("🤖 AI Research & Task Agent")
st.caption("Gửi yêu cầu nghiên cứu; agent sẽ chọn và chạy các công cụ phù hợp.")

with st.sidebar:
    st.header("Cấu hình agent")
    provider_name = st.selectbox(
        "AI provider",
        options=["openrouter", "openai", "anthropic", "gemini", "ollama"],
        format_func=lambda value: value.title(),
    )
    provider = make_provider(provider_name)
    model = st.text_input(
        "Model (để trống dùng mặc định)",
        placeholder=getattr(provider, "default_model", ""),
    ).strip()
    st.caption("API key và cấu hình được đọc từ starter_v0/.env.")
    if st.button("Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["content"])
        else:
            st.markdown(message["content"])

        tool_results = message.get("tool_results")
        if tool_results:
            with st.expander("Kết quả công cụ"):
                st.code(
                    json.dumps(tool_results, ensure_ascii=False, indent=2, default=str),
                    language="json",
                )

        if st.button("Xóa", key=f"delete_{index}", help="Xóa tin nhắn này"):
            st.session_state.messages.pop(index)
            st.rerun()

if prompt := st.chat_input("Nhập yêu cầu của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        system_prompt = (AGENT_ROOT / "artifacts" / "system_prompt.md").read_text(
            encoding="utf-8"
        )
        declarations = load_tool_declarations(
            AGENT_ROOT / "artifacts" / "tools.yaml"
        )
        agent = ResearchAgent(
            provider,
            system_prompt=system_prompt,
            tools=to_openai_tools(declarations),
            model=model or None,
        )
        conversation = [
            {"role": item["role"], "content": item["content"]}
            for item in st.session_state.messages
            if item["role"] in {"user", "assistant"}
        ]

        with st.spinner("Agent đang xử lý yêu cầu..."):
            result = agent.run(conversation)

        response = (result.text or "").strip()
        if not response:
            clarification = next(
                (
                    item.get("result", {}).get("question")
                    for item in result.tool_results
                    if isinstance(item.get("result"), dict)
                    and item["result"].get("awaiting_user")
                ),
                None,
            )
            response = clarification or (
                "Agent đã gọi công cụ. Xem kết quả chi tiết bên dưới."
                if result.tool_calls
                else "Agent chưa trả về nội dung."
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "tool_results": result.tool_results,
            }
        )
    except Exception as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Lỗi khi gọi agent: {type(exc).__name__}: {exc}",
                "error": True,
            }
        )

    st.rerun()
