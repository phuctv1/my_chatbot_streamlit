"""
⚡ Codex AI Chatbot - Titanium Super-App Edition 4.0 (Ultimate)
Built with Python, Streamlit, and OpenAI Python SDK.
Featuring:
- 4 Operating Modes: Standard Chat, Model Arena Duel, Autonomous ReAct Agent, AI Council Consensus
- RAG Knowledge Base: Persistent vector retrieval with semantic search & source citations
- Interactive Python Code Runner with Matplotlib Plot Visualizer
- Claude-Style Live Artifacts (HTML/CSS/JS Sandbox & SVG Canvas)
- Interactive Mermaid.js Flowchart & Sequence Diagram Visualizer
- Git-Style Code Diff & Version Comparison Tool
- Real-Time Web Search & Instant Link/URL Content Reader
- Chain-of-Thought (<think>) Reasoning Process Accordion
- Multimodal Vision (PNG, JPG, WEBP) & Document Parser (PDF, DOCX, XLSX, CSV)
- Smart Context Compactor (saves 70%+ token cost)
- Web Speech Voice Input (Speech-to-Text) & Audio Read Aloud (TTS)
- Full-Text Session Search, Forking, Pinned Bookmarks & Multi-Format Export
"""

import os
import sys
import io
import time
import json
import base64
from datetime import datetime
import streamlit as st
from openai import OpenAI

from config import load_config, save_config, POPULAR_MODELS, CONFIG_FILE
from modules.personas import PERSONAS, get_persona
from modules.document_parser import parse_uploaded_file, format_file_context_for_prompt
from modules.ai_service import (
    test_api_connection, estimate_token_count, prepare_messages_payload,
    extract_thought_process, enhance_user_prompt
)
from modules.chat_manager import (
    list_sessions, load_session, save_session,
    create_new_session, delete_session, rename_session,
    duplicate_session, auto_title_session, pin_message, unpin_message
)
from modules.prompt_library import get_all_categories, get_prompts_by_category
from modules.code_runner import extract_python_code_blocks, execute_python_code
from modules.web_search import search_web, fetch_url_content, detect_urls, format_search_results_for_prompt
from modules.artifacts_preview import extract_artifacts
from modules.context_compactor import compact_conversation_history
from modules.arena_mode import run_parallel_arena_inference
from modules.knowledge_base import (
    add_document_to_kb, query_kb, format_kb_context_for_prompt,
    list_kb_documents, delete_kb_document, clear_kb
)
from modules.react_agent import run_react_agent_loop
from modules.ai_council import run_ai_council
from modules.diagram_renderer import extract_mermaid_blocks, generate_mermaid_html
from modules.code_diff import generate_diff_html

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Codex AI Titanium 4.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- TITANIUM CSS STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1160px;
    }

    /* Glassmorphic App Header */
    .titanium-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 0.9rem 1.4rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.35);
    }
    .titanium-title {
        font-size: 1.65rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    /* Glowing Badges */
    .glow-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.35);
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
    }
    .badge-persona {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
        margin-left: 6px;
    }
    .badge-mode {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        background: rgba(245, 158, 11, 0.18);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.25);
        margin-left: 6px;
    }

    /* Agent Thought Container */
    .thought-container {
        background: rgba(17, 24, 39, 0.7);
        border-left: 3px solid #a855f7;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-size: 0.88rem;
        color: #cbd5e1;
    }

    /* Agent Step Card */
    .agent-step-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }

    /* Stats Footer */
    .stats-footer {
        font-size: 0.76rem;
        color: #64748b;
        margin-top: 8px;
        display: flex;
        gap: 12px;
        align-items: center;
        border-top: 1px dashed rgba(100, 116, 139, 0.2);
        padding-top: 6px;
    }

    /* Attachment Chip */
    .attachment-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 10px;
        font-size: 0.83rem;
        margin-bottom: 8px;
        color: #93c5fd;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE & INITIALIZATION -----------------
config = load_config()

# Operating Mode: "chat", "arena", "agent", "council"
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "chat"

# Active Session ID
if "current_session_id" not in st.session_state:
    all_sess = list_sessions()
    if all_sess:
        st.session_state.current_session_id = all_sess[0]["id"]
    else:
        new_s = create_new_session(
            title="Cuộc trò chuyện mới",
            model=config.get("model", "claude-opus-5-5"),
            persona="general"
        )
        st.session_state.current_session_id = new_s["id"]

current_session = load_session(st.session_state.current_session_id)
if not current_session:
    current_session = create_new_session(
        title="Cuộc trò chuyện mới",
        model=config.get("model", "claude-opus-5-5"),
        persona="general"
    )
    st.session_state.current_session_id = current_session["id"]

# Core parameters
if "api_key" not in st.session_state:
    st.session_state.api_key = config.get("api_key", "")
if "base_url" not in st.session_state:
    st.session_state.base_url = config.get("base_url", "https://codex.fosta.app/v1")
if "model" not in st.session_state:
    st.session_state.model = current_session.get("model") or config.get("model", "claude-opus-5-5")
if "persona_key" not in st.session_state:
    st.session_state.persona_key = current_session.get("persona", "general")
if "temperature" not in st.session_state:
    st.session_state.temperature = float(config.get("temperature", 0.5))
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = int(config.get("max_tokens", 4096))
if "user_memory" not in st.session_state:
    st.session_state.user_memory = config.get("user_memory", "")

# Toggles & Buffers
if "web_search_enabled" not in st.session_state:
    st.session_state.web_search_enabled = False
if "use_kb_search" not in st.session_state:
    st.session_state.use_kb_search = False
if "arena_model_a" not in st.session_state:
    st.session_state.arena_model_a = "claude-opus-5-5"
if "arena_model_b" not in st.session_state:
    st.session_state.arena_model_b = "gpt-6.1-sol"
if "arena_votes" not in st.session_state:
    st.session_state.arena_votes = {"model_a": 0, "model_b": 0, "tie": 0}
if "last_arena_results" not in st.session_state:
    st.session_state.last_arena_results = None
if "pending_file" not in st.session_state:
    st.session_state.pending_file = None
if "quick_prompt_to_send" not in st.session_state:
    st.session_state.quick_prompt_to_send = None
if "session_search_query" not in st.session_state:
    st.session_state.session_search_query = ""
if "code_exec_results" not in st.session_state:
    st.session_state.code_exec_results = {}
if "last_council_results" not in st.session_state:
    st.session_state.last_council_results = None
if "agent_run_data" not in st.session_state:
    st.session_state.agent_run_data = None


# ----------------- SIDEBAR UI -----------------
with st.sidebar:
    st.markdown("## ⚡ **Codex AI Titanium**")
    st.caption("Autonomous Agent & Multi-Model Super-App")
    st.markdown("---")

    # Mode Selector
    st.markdown("##### 🧭 Chế độ Hoạt động:")
    mode_options = {
        "chat": "💬 Chat Chuẩn (Standard)",
        "arena": "⚔️ Model Arena (So sánh 2 Model)",
        "agent": "🤖 Autonomous Agent (Tác tử ReAct)",
        "council": "👥 Hội đồng AI (Consensus 3 Model)"
    }
    selected_mode = st.radio(
        "Chọn chế độ:",
        options=list(mode_options.keys()),
        format_func=lambda k: mode_options[k],
        index=list(mode_options.keys()).index(st.session_state.app_mode),
        label_visibility="collapsed"
    )
    st.session_state.app_mode = selected_mode
    st.markdown("---")

    # Sidebar Tabs
    tab_chats, tab_config, tab_kb, tab_persona, tab_library, tab_pins = st.tabs([
        "💬 Lịch sử", "⚙️ Cài đặt", "📚 Kho Tri Thức", "🎭 Chuyên gia", "📚 Prompt", "📌 Đã ghim"
    ])

    # ---- TAB 1: SESSIONS & SEARCH ----
    with tab_chats:
        if st.button("＋ Tạo đoạn chat mới", type="primary", use_container_width=True):
            new_s = create_new_session(
                title="Cuộc trò chuyện mới",
                model=st.session_state.model,
                persona=st.session_state.persona_key
            )
            st.session_state.current_session_id = new_s["id"]
            st.session_state.pending_file = None
            st.session_state.last_arena_results = None
            st.session_state.last_council_results = None
            st.session_state.agent_run_data = None
            st.rerun()

        search_kw = st.text_input("🔍 Tìm kiếm hội thoại:", value=st.session_state.session_search_query, placeholder="Gõ từ khóa...")
        st.session_state.session_search_query = search_kw

        filtered_sessions = list_sessions(search_kw)
        if not filtered_sessions:
            st.info("Không tìm thấy đoạn chat nào.")
        else:
            for s in filtered_sessions:
                s_id = s["id"]
                s_title = s["title"]
                is_active = (s_id == st.session_state.current_session_id)

                col_btn, col_dup, col_del = st.columns([5, 1, 1])
                with col_btn:
                    icon = "🔥" if is_active else "💬"
                    if st.button(f"{icon} {s_title}", key=f"sess_btn_{s_id}", use_container_width=True):
                        st.session_state.current_session_id = s_id
                        st.session_state.pending_file = None
                        st.rerun()
                with col_dup:
                    if st.button("📋", key=f"dup_{s_id}", help="Nhân bản (Fork) đoạn chat này"):
                        cloned = duplicate_session(s_id)
                        if cloned:
                            st.session_state.current_session_id = cloned["id"]
                            st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{s_id}", help="Xóa đoạn chat này"):
                        delete_session(s_id)
                        remaining = list_sessions()
                        st.session_state.current_session_id = remaining[0]["id"] if remaining else create_new_session(model=st.session_state.model)["id"]
                        st.rerun()

        st.markdown("---")
        with st.expander("✏️ Đổi tên phiên chat hiện tại"):
            new_title_val = st.text_input("Tên mới:", value=current_session.get("title", ""))
            if st.button("Cập nhật tên", use_container_width=True):
                rename_session(st.session_state.current_session_id, new_title_val)
                st.success("Đã cập nhật!")
                st.rerun()

    # ---- TAB 2: CONFIGURATION ----
    with tab_config:
        st.markdown("##### 🔑 Khóa API & Endpoint")
        api_input = st.text_input("API Key", value=st.session_state.api_key, type="password", placeholder="sk-...")
        if api_input != st.session_state.api_key:
            st.session_state.api_key = api_input

        base_url_input = st.text_input("Base URL", value=st.session_state.base_url, placeholder="https://codex.fosta.app/v1")
        if base_url_input != st.session_state.base_url:
            st.session_state.base_url = base_url_input

        st.markdown("##### 🤖 Mô hình (Model)")
        model_list = list(POPULAR_MODELS)
        if st.session_state.model not in model_list:
            model_list.insert(0, st.session_state.model)

        chosen_model = st.selectbox("Model có sẵn:", options=model_list, index=model_list.index(st.session_state.model) if st.session_state.model in model_list else 0)
        custom_model_str = st.text_input("Hoặc tự nhập tên Model:", value="" if chosen_model in POPULAR_MODELS else chosen_model)
        st.session_state.model = custom_model_str.strip() if custom_model_str.strip() else chosen_model

        st.markdown("##### 🎛️ Siêu tham số")
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.5, float(st.session_state.temperature), 0.05)
        st.session_state.max_tokens = st.slider("Max Output Tokens", 256, 8192, int(st.session_state.max_tokens), 256)

        col_save_cfg, col_test_cfg = st.columns(2)
        with col_save_cfg:
            if st.button("💾 Lưu cài đặt", use_container_width=True):
                save_data = {
                    "api_key": st.session_state.api_key,
                    "base_url": st.session_state.base_url,
                    "model": st.session_state.model,
                    "temperature": st.session_state.temperature,
                    "max_tokens": st.session_state.max_tokens,
                    "user_memory": st.session_state.user_memory,
                    "system_prompt": current_session.get("system_prompt", "")
                }
                if save_config(save_data):
                    st.success("Đã lưu!")
                else:
                    st.error("Lỗi khi lưu!")

        with col_test_cfg:
            if st.button("⚡ Test kết nối", use_container_width=True):
                if not st.session_state.api_key:
                    st.warning("Vui lòng nhập API Key.")
                else:
                    with st.spinner("Đang kiểm tra..."):
                        ok, msg, lat = test_api_connection(st.session_state.base_url, st.session_state.api_key, st.session_state.model)
                        if ok:
                            st.success(f"{msg} ({lat}ms)")
                        else:
                            st.error(f"Thất bại:\n{msg}")

    # ---- TAB 3: RAG KNOWLEDGE BASE ----
    with tab_kb:
        st.markdown("##### 📚 Kho Tri Thức Nội Bộ (RAG Vector Base)")
        st.caption("Tải lên tài liệu tham khảo dài hạn để AI tra cứu tự động cho mọi câu hỏi.")

        kb_upload = st.file_uploader("Nạp tài liệu vào Kho Tri Thức:", type=["pdf", "docx", "txt", "md", "csv", "json"], key="kb_uploader")
        if kb_upload is not None:
            if st.button("📥 Băm nhỏ & Lưu vào Index", use_container_width=True):
                with st.spinner("Đang trích xuất và phân tích vector..."):
                    parsed_kb = parse_uploaded_file(kb_upload)
                    if parsed_kb["success"] and parsed_kb["text"]:
                        c_count = add_document_to_kb(kb_upload.name, parsed_kb["file_type"], parsed_kb["text"])
                        st.success(f"Đã lập chỉ mục '{kb_upload.name}' ({c_count} chunks)!")
                        time.sleep(1)
                        st.rerun()

        st.markdown("---")
        st.markdown("##### 📁 Tài liệu đã được lập chỉ mục:")
        kb_docs = list_kb_documents()
        if not kb_docs:
            st.info("Kho Tri Thức hiện đang trống.")
        else:
            for doc_name, doc_meta in kb_docs.items():
                c_name, c_del = st.columns([4, 1])
                c_name.markdown(f"📄 **{doc_name}** ({doc_meta.get('chunk_count')} chunks)")
                if c_del.button("🗑️", key=f"del_kb_{doc_name}"):
                    delete_kb_document(doc_name)
                    st.rerun()

            if st.button("🗑️ Xóa toàn bộ Kho Tri Thức", type="secondary", use_container_width=True):
                clear_kb()
                st.rerun()

    # ---- TAB 4: PERSONAS & MEMORY ----
    with tab_persona:
        st.markdown("##### 🎭 Chọn Vai trò Chuyên gia")
        persona_keys = list(PERSONAS.keys())
        p_names = [PERSONAS[k]["name"] for k in persona_keys]
        cur_idx = persona_keys.index(st.session_state.persona_key) if st.session_state.persona_key in persona_keys else 0
        chosen_p_name = st.selectbox("Vai trò:", options=p_names, index=cur_idx)
        st.session_state.persona_key = persona_keys[p_names.index(chosen_p_name)]

        persona_info = get_persona(st.session_state.persona_key)
        st.info(f"**{persona_info['icon']} Mô tả:** {persona_info['description']}")

        st.markdown("##### 📝 Lời nhắc hệ thống (System Prompt):")
        default_prompt = persona_info["prompt"] if st.session_state.persona_key != "custom" else config.get("system_prompt", "")
        st.text_area("Chỉ dẫn cho AI:", value=default_prompt, height=120)

        st.markdown("---")
        st.markdown("##### 🧠 Bộ nhớ Cá nhân (User Memory)")
        mem_input = st.text_area("Bộ nhớ cá nhân:", value=st.session_state.user_memory, height=80, placeholder="Ví dụ: Tôi tên là Phúc, kỹ sư lập trình...")
        if mem_input != st.session_state.user_memory:
            st.session_state.user_memory = mem_input

    # ---- TAB 5: PROMPT LIBRARY ----
    with tab_library:
        st.markdown("##### 📚 Kho Prompt Kỹ thuật Mẫu")
        categories = get_all_categories()
        chosen_cat = st.selectbox("Danh mục:", options=categories)
        prompts_in_cat = get_prompts_by_category(chosen_cat)

        for p in prompts_in_cat:
            with st.expander(f"{p['icon']} {p['title']}"):
                st.caption(p['desc'])
                st.code(p['prompt'], language="markdown")
                if st.button("🚀 Nạp vào khung chat", key=f"use_prompt_{p['title']}", use_container_width=True):
                    st.session_state.quick_prompt_to_send = p['prompt']
                    st.rerun()

    # ---- TAB 6: PINNED BOOKMARKS ----
    with tab_pins:
        st.markdown("##### 📌 Ghi chú & Tin nhắn Đã Ghim")
        pinned_list = current_session.get("pinned_messages", [])
        if not pinned_list:
            st.info("Chưa có tin nhắn nào được ghim trong phiên này. Bấm nút 📌 dưới phản hồi của AI để lưu.")
        else:
            for p_idx, pin_m in enumerate(pinned_list):
                with st.expander(f"📌 Ghi chú #{p_idx+1} [{pin_m.get('timestamp', '')}]"):
                    st.markdown(pin_m.get("content", ""))
                    if st.button("❌ Bỏ ghim", key=f"unpin_{p_idx}", use_container_width=True):
                        unpin_message(st.session_state.current_session_id, p_idx)
                        st.rerun()


# ----------------- MAIN WORKSPACE HEADER -----------------

persona_data = get_persona(st.session_state.persona_key)
col_head_title, col_head_tools = st.columns([3, 1.2])

mode_badges = {
    "chat": "<span class='badge-mode' style='color:#38bdf8; border-color:rgba(56,189,248,0.4); background:rgba(56,189,248,0.15);'>💬 Standard Chat</span>",
    "arena": "<span class='badge-mode' style='color:#fbbf24; border-color:rgba(245,158,11,0.4); background:rgba(245,158,11,0.18);'>⚔️ Model Arena</span>",
    "agent": "<span class='badge-mode' style='color:#a855f7; border-color:rgba(168,85,247,0.4); background:rgba(168,85,247,0.18);'>🤖 Autonomous Agent</span>",
    "council": "<span class='badge-mode' style='color:#f472b6; border-color:rgba(244,114,182,0.4); background:rgba(244,114,182,0.18);'>👥 AI Council</span>"
}

with col_head_title:
    st.markdown(
        f"""
        <div class="titanium-header">
            <div>
                <h1 class="titanium-title">{current_session.get('title', 'Cuộc trò chuyện')}</h1>
                <div style="margin-top: 6px;">
                    <span class="glow-badge">⚡ {st.session_state.model}</span>
                    <span class="badge-persona">{persona_data['icon']} {persona_data['name'].split('(')[0].strip()}</span>
                    {mode_badges.get(st.session_state.app_mode, '')}
                    {f'<span class="glow-badge" style="color: #38bdf8; border-color: rgba(56,189,248,0.35); background: rgba(56,189,248,0.15)">🌐 Web On</span>' if st.session_state.web_search_enabled else ''}
                    {f'<span class="glow-badge" style="color: #a855f7; border-color: rgba(168,85,247,0.35); background: rgba(168,85,247,0.15)">📚 RAG Active</span>' if st.session_state.use_kb_search else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_head_tools:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_comp, c_clr = st.columns(2)
    with c_comp:
        if st.button("🧹 Nén Chat", help="Nén lịch sử để tiết kiệm 70% tokens", use_container_width=True):
            if len(current_session.get("messages", [])) > 4:
                with st.spinner("Đang nén ngữ cảnh..."):
                    compacted, old_t, new_t = compact_conversation_history(
                        current_session["messages"], st.session_state.base_url, st.session_state.api_key, st.session_state.model
                    )
                    current_session["messages"] = compacted
                    save_session(current_session)
                    pct = round((1 - new_t / max(1, old_t)) * 100)
                    st.success(f"Nén xong: {old_t} ➔ {new_t} tokens (-{pct}%)!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.info("Hội thoại còn ngắn, chưa cần nén.")
    with c_clr:
        if st.button("🗑️ Xóa", help="Xóa tin nhắn phiên này", use_container_width=True):
            current_session["messages"] = []
            save_session(current_session)
            st.session_state.pending_file = None
            st.session_state.code_exec_results = {}
            st.session_state.last_arena_results = None
            st.session_state.last_council_results = None
            st.session_state.agent_run_data = None
            st.rerun()

# Attachment & Search Toggles Expander
with st.expander("📎 Đính kèm Tệp, Hình ảnh & Công cụ Mở rộng", expanded=(st.session_state.pending_file is not None)):
    col_up_file, col_tool_toggles = st.columns([3, 1.5])

    with col_up_file:
        uploaded_file = st.file_uploader(
            "Tải lên tệp hoặc hình ảnh:",
            type=["pdf", "docx", "xlsx", "xls", "csv", "txt", "py", "json", "md", "png", "jpg", "jpeg", "webp"],
            help="Trích xuất PDF, Word, bảng Excel/CSV và ảnh Vision."
        )
        if uploaded_file is not None:
            if (not st.session_state.pending_file) or (st.session_state.pending_file.get("filename") != uploaded_file.name):
                with st.spinner(f"Đang xử lý '{uploaded_file.name}'..."):
                    parsed = parse_uploaded_file(uploaded_file)
                    st.session_state.pending_file = parsed
                    st.success(f"Đã nạp '{uploaded_file.name}' ({parsed.get('size_kb')} KB - {parsed.get('file_type')})")

    with col_tool_toggles:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.session_state.web_search_enabled = st.checkbox("🌐 Tìm kiếm Web Trực tiếp", value=st.session_state.web_search_enabled)
        st.session_state.use_kb_search = st.checkbox("📚 Tra cứu Kho Tri Thức (RAG)", value=st.session_state.use_kb_search)

    if st.session_state.pending_file:
        pf = st.session_state.pending_file
        st.markdown(f"**Tệp đính kèm sẵn sàng:** `{pf['filename']}` ({pf.get('file_type')}, {pf.get('size_kb')} KB)")
        if pf.get("is_image") and pf.get("image_base64"):
            st.image(io.BytesIO(base64.b64decode(pf["image_base64"])), width=220, caption=pf["filename"])
        else:
            st.caption(f"Xem trước văn bản: *{pf.get('preview', '')}*")
        if st.button("❌ Gỡ tệp này"):
            st.session_state.pending_file = None
            st.rerun()

if not st.session_state.api_key:
    st.warning("⚠️ **Chưa cấu hình API Key:** Mở thanh bên trái (Tab **Cài đặt**) và nhập khóa API của bạn.")


# =========================================================================
# MODE 2: MODEL ARENA VIEW (IF ARENA MODE IS SELECTED)
# =========================================================================
if st.session_state.app_mode == "arena":
    st.markdown("### ⚔️ Model Arena: So Sánh Đối Đầu Song Song")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.session_state.arena_model_a = st.selectbox("Model A (Góc Trái):", options=POPULAR_MODELS, index=POPULAR_MODELS.index(st.session_state.arena_model_a) if st.session_state.arena_model_a in POPULAR_MODELS else 0)
    with c_m2:
        st.session_state.arena_model_b = st.selectbox("Model B (Góc Phải):", options=POPULAR_MODELS, index=POPULAR_MODELS.index(st.session_state.arena_model_b) if st.session_state.arena_model_b in POPULAR_MODELS else 1)

    if st.session_state.last_arena_results:
        res_a, res_b = st.session_state.last_arena_results
        col_res_a, col_res_b = st.columns(2)
        with col_res_a:
            st.markdown(f"#### 🅰️ {res_a.get('model')}")
            if res_a.get("success"):
                st.markdown(res_a.get("content"))
                st.markdown(f"<div class='stats-footer'>⚡ {res_a.get('latency_ms')/1000:.2f}s &bull; ~{res_a.get('tokens')} tokens &bull; {res_a.get('speed')} tok/s</div>", unsafe_allow_html=True)
            else:
                st.error(res_a.get("error"))

        with col_res_b:
            st.markdown(f"#### 🅱️ {res_b.get('model')}")
            if res_b.get("success"):
                st.markdown(res_b.get("content"))
                st.markdown(f"<div class='stats-footer'>⚡ {res_b.get('latency_ms')/1000:.2f}s &bull; ~{res_b.get('tokens')} tokens &bull; {res_b.get('speed')} tok/s</div>", unsafe_allow_html=True)
            else:
                st.error(res_b.get("error"))

        # Voting bar
        st.markdown("##### 🏆 Bình chọn Model nào xuất sắc hơn?")
        c_va, c_vt, c_vb = st.columns(3)
        if c_va.button(f"👈 {res_a.get('model')} Thắng", use_container_width=True):
            st.session_state.arena_votes["model_a"] += 1
            st.success("Đã ghi nhận phiếu cho Model A!")
        if c_vt.button("🤝 Cả hai đều tốt (Hòa)", use_container_width=True):
            st.session_state.arena_votes["tie"] += 1
            st.info("Đã ghi nhận phiếu Hòa!")
        if c_vb.button(f"👉 {res_b.get('model')} Thắng", use_container_width=True):
            st.session_state.arena_votes["model_b"] += 1
            st.success("Đã ghi nhận phiếu cho Model B!")


# =========================================================================
# MODE 3: AUTONOMOUS REACT AGENT VIEW
# =========================================================================
elif st.session_state.app_mode == "agent":
    st.markdown("### 🤖 Autonomous ReAct Agent: Tác Tử Hành Động Tự Chủ")
    st.caption("Agent tự động lập kế hoạch (Thought), gọi công cụ cục bộ (Action) như chạy Python, tra cứu Web, duyệt Kho Tri Thức để giải quyết vấn đề.")

    if st.session_state.agent_run_data:
        ag_data = st.session_state.agent_run_data
        st.markdown("##### 🛠️ Tiến trình Suy luận & Hành động (Execution Trace):")
        for s in ag_data.get("steps", []):
            with st.expander(f"🔹 Bước {s.get('step')}: {s.get('action') or 'Hoàn tất suy luận'}", expanded=True):
                st.markdown(f"**💭 Suy nghĩ:** {s.get('thought')}")
                if s.get("action"):
                    st.markdown(f"**🔧 Công cụ:** `{s.get('action')}`")
                if s.get("observation"):
                    st.markdown("**📊 Kết quả quan sát (Observation):**")
                    st.code(s.get("observation"), language="text")

        st.markdown("---")
        st.markdown("#### 💡 Câu Trả Lời Cuối Cùng Của Tác Tử (Final Answer):")
        st.markdown(ag_data.get("final_answer", ""))
        st.markdown(f"<div class='stats-footer'>⚡ Tổng thời gian chạy tác tử: {ag_data.get('total_latency_ms')/1000:.2f}s</div>", unsafe_allow_html=True)


# =========================================================================
# MODE 4: AI COUNCIL CONSENSUS VIEW
# =========================================================================
elif st.session_state.app_mode == "council":
    st.markdown("### 👥 AI Council: Hội Đồng 3 Mô Hình Đồng Thuận")
    st.caption("3 mô hình AI độc lập cùng phân tích vấn đề song song, sau đó Chủ Tịch Hội Đồng sẽ đúc kết báo cáo đồng thuận và phương án hành động tối ưu.")

    if st.session_state.last_council_results:
        c_res = st.session_state.last_council_results
        st.markdown("#### 🎯 Báo Cáo Đúc Kết Của Hội Đồng AI (Consensus Report):")
        st.markdown(c_res.get("synthesis", ""))
        st.markdown(f"<div class='stats-footer'>⚡ Tổng thời gian họp hội đồng: {c_res.get('total_latency_ms')/1000:.2f}s</div>", unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("🔍 Xem chi tiết ý kiến độc lập của từng thành viên Hội Đồng"):
            c_cols = st.columns(len(c_res.get("council_results", [])))
            for idx, r in enumerate(c_res.get("council_results", [])):
                with c_cols[idx]:
                    st.markdown(f"**Thành viên #{idx+1}: {r.get('model')}**")
                    st.markdown(r.get("content"))


# =========================================================================
# MODE 1: STANDARD CHAT HISTORY & MESSAGES
# =========================================================================
messages = current_session.get("messages", [])

if st.session_state.app_mode == "chat":
    if len(messages) == 0:
        st.markdown("##### 💡 Gợi ý câu hỏi bắt đầu nhanh:")
        sug_cols = st.columns(3)

        if st.session_state.persona_key == "developer":
            prompt_suggestions = [
                "Viết kiến trúc Microservice hoàn chỉnh bằng FastAPI & Redis",
                "Tối ưu thuật toán tìm đường đi ngắn nhất Dijkstra bằng Python",
                "Vẽ biểu đồ Mermaid giải thích luồng xác thực OAuth2 / JWT"
            ]
        elif st.session_state.persona_key == "data_analyst":
            prompt_suggestions = [
                "Viết pipeline phân tích dữ liệu bán hàng với Pandas và vẽ chart Matplotlib",
                "Cách xử lý Missing Values và Outliers trong bộ dữ liệu lớn",
                "Viết hàm tính toán chỉ số RFM (Recency, Frequency, Monetary)"
            ]
        elif st.session_state.persona_key == "ui_ux_designer":
            prompt_suggestions = [
                "Thiết kế Design System cho ứng dụng FinTech hiện đại",
                "Đề xuất bảng màu và cấu trúc layout trang Dashboard quản trị",
                "Viết mã HTML/CSS tạo một landing page hiện đại với glassmorphism"
            ]
        else:
            prompt_suggestions = [
                "👋 Xin chào! Hãy giới thiệu những khả năng siêu việt của bạn.",
                "Phân tích ưu nhược điểm của các kiến trúc hệ thống hiện đại",
                "Giải thích cơ chế hoạt động của Transformers và Self-Attention"
            ]

        for idx, (col, sug) in enumerate(zip(sug_cols, prompt_suggestions)):
            with col:
                if st.button(sug, key=f"starter_chip_{idx}", use_container_width=True):
                    st.session_state.quick_prompt_to_send = sug
                    st.rerun()

    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        avatar = "👤" if role == "user" else "🤖"

        with st.chat_message(role, avatar=avatar):
            # 1. Attached Image or File Pill
            if msg.get("file_info"):
                f_info = msg["file_info"]
                if f_info.get("is_image") and f_info.get("image_base64"):
                    st.image(io.BytesIO(base64.b64decode(f_info["image_base64"])), width=300, caption=f_info.get("filename"))
                else:
                    st.markdown(
                        f"<div class='attachment-pill'>📎 <b>{f_info.get('filename')}</b> ({f_info.get('file_type')}, {f_info.get('size_kb')} KB)</div>",
                        unsafe_allow_html=True
                    )

            # 2. Reasoning Process (<think>) Accordion
            raw_content = msg.get("content", "")
            thought_proc, clean_ans = extract_thought_process(raw_content)

            if thought_proc:
                with st.expander("🧠 Quá trình suy luận (Chain of Thought)", expanded=False):
                    st.markdown(f"<div class='thought-container'>{thought_proc}</div>", unsafe_allow_html=True)
                st.markdown(clean_ans)
            else:
                st.markdown(raw_content)

            # 3. Interactive Mermaid Diagrams (Flowcharts / Sequences / Architecture)
            if role == "assistant":
                mermaid_blocks = extract_mermaid_blocks(raw_content)
                if mermaid_blocks:
                    with st.expander("📊 Sơ đồ Kiến Trúc & Luồng Dữ Liệu (Mermaid.js Diagram)", expanded=True):
                        for m_code in mermaid_blocks:
                            m_html = generate_mermaid_html(m_code)
                            st.components.v1.html(m_html, height=380, scrolling=True)

            # 4. Live Artifacts & HTML/SVG Sandbox Preview
            if role == "assistant":
                artifacts = extract_artifacts(raw_content)
                if artifacts:
                    with st.expander("🎨 Xem trước Artifact (Live Web Preview / Canvas)", expanded=False):
                        for a_idx, art in enumerate(artifacts):
                            st.markdown(f"**Khung vẽ: {art['title']}**")
                            if art["type"] == "html":
                                st.components.v1.html(art["code"], height=320, scrolling=True)
                            elif art["type"] == "svg":
                                st.markdown(art["code"], unsafe_allow_html=True)

            # 5. Interactive Python Code Runner (Code + Matplotlib Plots)
            if role == "assistant":
                py_blocks = extract_python_code_blocks(raw_content)
                if py_blocks:
                    with st.expander("▶️ Trình thực thi Python (Interactive Code Runner)", expanded=False):
                        for b_idx, code_snippet in enumerate(py_blocks):
                            st.markdown(f"**Khối mã #{b_idx+1}:**")
                            st.code(code_snippet, language="python")

                            exec_key = f"exec_btn_{idx}_{b_idx}"
                            if st.button(f"▶️ Chạy mã #{b_idx+1}", key=exec_key):
                                with st.spinner("Đang thực thi mã nguồn..."):
                                    res = execute_python_code(code_snippet)
                                    st.session_state.code_exec_results[exec_key] = res

                            if exec_key in st.session_state.code_exec_results:
                                res = st.session_state.code_exec_results[exec_key]
                                if res["success"]:
                                    st.success("Thực thi thành công!")
                                    if res["stdout"]:
                                        st.markdown("**Kết quả xuất (stdout):**")
                                        st.code(res["stdout"], language="text")
                                    if res.get("has_figure") and res.get("figure"):
                                        st.markdown("**Biểu đồ trực quan hóa:**")
                                        st.pyplot(res["figure"])
                                else:
                                    st.error("Lỗi khi thực thi:")
                                    st.code(res["error"] or "Unknown error", language="text")

            # 6. Stats footer for assistant
            if role == "assistant" and msg.get("stats"):
                stats = msg["stats"]
                lat = stats.get("latency_ms", 0)
                toks = stats.get("tokens", 0)
                spd = stats.get("speed", 0)
                st.markdown(
                    f"<div class='stats-footer'>⚡ {lat/1000:.2f}s &bull; ~{toks} tokens &bull; {spd:.1f} tok/s &bull; <code>{msg.get('model_used', st.session_state.model)}</code></div>",
                    unsafe_allow_html=True
                )

            # 7. Action toolbar under the LATEST assistant message
            if role == "assistant" and idx == len(messages) - 1:
                col_tts, col_pin, col_regen, col_spacer = st.columns([1.5, 1.5, 1.5, 4.5])
                with col_tts:
                    safe_text = json.dumps(clean_ans if thought_proc else raw_content)
                    tts_html = f"""
                    <button onclick='window.speechSynthesis.cancel(); let u=new SpeechSynthesisUtterance({safe_text}); u.lang="vi-VN"; window.speechSynthesis.speak(u);'
                            style="background: transparent; border: 1px solid rgba(128,128,128,0.3); border-radius: 6px; padding: 4px 10px; font-size: 0.8rem; cursor: pointer; color: inherit;">
                        🔊 Đọc to
                    </button>
                    """
                    st.components.v1.html(tts_html, height=35)

                with col_pin:
                    if st.button("📌 Ghim", key=f"pin_btn_{idx}", help="Ghim tin nhắn này vào sổ tay"):
                        pin_message(st.session_state.current_session_id, msg)
                        st.success("Đã ghim!")

                with col_regen:
                    if st.button("🔄 Tạo lại", key="regen_btn_latest", help="Tạo lại phản hồi này"):
                        messages.pop()
                        save_session(current_session)
                        st.rerun()

    # Quick Action Chips under Chat
    if messages and messages[-1]["role"] == "assistant":
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)
        with q_col1:
            if st.button("✂️ Tóm tắt 3 ý chính", key="q_sum_btn", use_container_width=True):
                st.session_state.quick_prompt_to_send = "Hãy tóm tắt câu trả lời trước đó thành 3 ý gạch đầu dòng súc tích và quan trọng nhất."
                st.rerun()
        with q_col2:
            if st.button("🌐 Dịch sang Tiếng Anh", key="q_trans_en_btn", use_container_width=True):
                st.session_state.quick_prompt_to_send = "Hãy dịch câu trả lời phía trên sang Tiếng Anh một cách chuyên nghiệp và tự nhiên."
                st.rerun()
        with q_col3:
            if st.button("🔍 Giải thích chi tiết hơn", key="q_deep_btn", use_container_width=True):
                st.session_state.quick_prompt_to_send = "Hãy giải thích sâu hơn, phân tích chi tiết từng khía cạnh và bổ sung ví dụ thực tế cho câu trả lời trên."
                st.rerun()
        with q_col4:
            if st.button("🐛 Tìm lỗi & Tối ưu", key="q_debug_btn", use_container_width=True):
                st.session_state.quick_prompt_to_send = "Hãy rà soát kỹ đoạn mã nguồn ở trên, tìm các lỗi tiềm ẩn (edge cases), tối ưu hiệu năng và viết unit test."
                st.rerun()


# ----------------- PROMPT ENHANCER, VOICE & INPUT AREA -----------------
with st.expander("✨ Công cụ Tối ưu Prompt AI & Giọng Nói", expanded=False):
    col_raw_p, col_btn_enh = st.columns([4, 1.2])
    with col_raw_p:
        raw_p_input = st.text_input("Nhập yêu cầu ngắn gọn:", placeholder="Ví dụ: xây dựng bot trading crypto")
    with col_btn_enh:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("✨ Tối ưu Prompt", use_container_width=True):
            if raw_p_input.strip() and st.session_state.api_key:
                with st.spinner("Đang tinh chỉnh Prompt chuyên sâu..."):
                    enhanced_p = enhance_user_prompt(raw_p_input, st.session_state.base_url, st.session_state.api_key, st.session_state.model)
                    st.session_state.quick_prompt_to_send = enhanced_p
                    st.rerun()
            else:
                st.warning("Vui lòng nhập yêu cầu và cấu hình API Key.")

    # Voice Input (Speech to Text)
    st.markdown("##### 🎙️ Nhập liệu Bằng Giọng nói (Speech-to-Text):")
    voice_widget_html = """
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
        <button id="record-btn" onclick="toggleVoiceRecording()" style="background: #3b82f6; color: white; border: none; padding: 6px 14px; border-radius: 8px; font-weight: 600; cursor: pointer;">
            🎙️ Bấm để Nói (Tiếng Việt)
        </button>
        <span id="voice-status" style="font-size: 0.85rem; color: #94a3b8;">Sẵn sàng...</span>
    </div>
    <div id="transcript-box" style="margin-top: 8px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; font-size: 0.85rem; min-height: 24px; color: #cbd5e1;">Văn bản giọng nói sẽ xuất hiện ở đây...</div>

    <script>
        let recognition;
        let isRecording = false;

        function toggleVoiceRecording() {
            const btn = document.getElementById("record-btn");
            const status = document.getElementById("voice-status");
            const box = document.getElementById("transcript-box");

            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert("Trình duyệt không hỗ trợ Web Speech API. Vui lòng dùng Chrome hoặc Edge.");
                return;
            }

            if (isRecording) {
                recognition.stop();
                btn.style.background = "#3b82f6";
                btn.innerText = "🎙️ Bấm để Nói (Tiếng Việt)";
                status.innerText = "Đã dừng.";
                isRecording = false;
                return;
            }

            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.lang = 'vi-VN';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onstart = function() {
                isRecording = true;
                btn.style.background = "#ef4444";
                btn.innerText = "⏹ Đang nghe... Bấm để dừng";
                status.innerText = "Đang nhận diện giọng nói...";
            };

            recognition.onresult = function(event) {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    finalTranscript += event.results[i][0].transcript;
                }
                box.innerText = finalTranscript;
            };

            recognition.onerror = function(event) {
                status.innerText = "Lỗi micro: " + event.error;
                btn.style.background = "#3b82f6";
                btn.innerText = "🎙️ Bấm để Nói (Tiếng Việt)";
                isRecording = false;
            };

            recognition.start();
        }
    </script>
    """
    st.components.v1.html(voice_widget_html, height=110)

# Main Chat Input
user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu tại đây...")

prompt_to_process = None
if st.session_state.quick_prompt_to_send:
    prompt_to_process = st.session_state.quick_prompt_to_send
    st.session_state.quick_prompt_to_send = None
elif user_input:
    prompt_to_process = user_input

if prompt_to_process:
    now_str = datetime.now().strftime("%H:%M:%S")

    # 1. Automatic URL Content Reading if link pasted
    detected_links = detect_urls(prompt_to_process)
    url_context_str = ""
    if detected_links:
        with st.spinner(f"Đang đọc nội dung liên kết: {detected_links[0]}..."):
            url_res = fetch_url_content(detected_links[0])
            if url_res["success"]:
                url_context_str = f"\n\n🌐 **[Nội dung trang web trích xuất từ: `{url_res['url']}`]**\nTitle: {url_res['title']}\n{url_res['text']}\n"
                st.info(f"Đã đọc thành công trang web: {url_res['title']}")

    # 2. Live Web Search if toggle enabled
    search_context_str = ""
    if st.session_state.web_search_enabled and not detected_links:
        with st.spinner(f"Đang tìm kiếm thông tin trên Internet cho '{prompt_to_process[:40]}'..."):
            search_items = search_web(prompt_to_process)
            search_context_str = format_search_results_for_prompt(prompt_to_process, search_items)

    # 3. RAG Knowledge Base Retrieval
    kb_context_str = ""
    if st.session_state.use_kb_search:
        with st.spinner("Đang tra cứu Kho Tri Thức nội bộ..."):
            retrieved_kb = query_kb(prompt_to_process, top_k=3)
            kb_context_str = format_kb_context_for_prompt(retrieved_kb)
            if retrieved_kb:
                st.info(f"Đã trích xuất {len(retrieved_kb)} đoạn dữ liệu từ Kho Tri Thức!")

    # 4. Attached File Context
    attached_file_info = None
    file_context_str = ""
    if st.session_state.pending_file:
        attached_file_info = dict(st.session_state.pending_file)
        file_context_str = format_file_context_for_prompt(attached_file_info)
        st.session_state.pending_file = None

    # Aggregate context
    final_extra_context = f"{url_context_str}{search_context_str}{kb_context_str}{file_context_str}".strip()

    # Append user message
    user_msg_entry = {
        "role": "user",
        "content": prompt_to_process,
        "timestamp": now_str,
        "file_info": attached_file_info,
        "file_context": final_extra_context
    }
    messages.append(user_msg_entry)
    current_session["messages"] = messages
    save_session(current_session)

    auto_title_session(current_session, prompt_to_process)


    # =========================================================================
    # DISPATCH BY OPERATING MODE
    # =========================================================================

    # MODE: MODEL ARENA
    if st.session_state.app_mode == "arena":
        with st.spinner(f"⚔️ Arena: Đang chạy đồng thời {st.session_state.arena_model_a} và {st.session_state.arena_model_b}..."):
            sys_prompt = persona_data["prompt"]
            if st.session_state.persona_key == "custom":
                sys_prompt = config.get("system_prompt", "")

            payload = prepare_messages_payload(messages, system_prompt=sys_prompt, user_memory=st.session_state.user_memory)
            res_a, res_b = run_parallel_arena_inference(
                st.session_state.arena_model_a, st.session_state.arena_model_b,
                st.session_state.base_url, st.session_state.api_key, payload,
                temperature=float(st.session_state.temperature), max_tokens=int(st.session_state.max_tokens)
            )
            st.session_state.last_arena_results = (res_a, res_b)
            st.rerun()

    # MODE: AUTONOMOUS REACT AGENT
    elif st.session_state.app_mode == "agent":
        with st.spinner("🤖 Agent đang suy luận, chọn công cụ và thực thi..."):
            agent_result = run_react_agent_loop(
                user_prompt=prompt_to_process,
                base_url=st.session_state.base_url,
                api_key=st.session_state.api_key,
                model=st.session_state.model
            )
            st.session_state.agent_run_data = agent_result
            st.rerun()

    # MODE: AI COUNCIL CONSENSUS
    elif st.session_state.app_mode == "council":
        with st.spinner("👥 Hội Đồng AI 3 Models đang họp và tổng hợp báo cáo..."):
            council_result = run_ai_council(
                user_prompt=prompt_to_process,
                base_url=st.session_state.base_url,
                api_key=st.session_state.api_key,
                council_models=["claude-opus-5-5", "gpt-6.1-sol", "gpt-4o"],
                synthesizer_model=st.session_state.model
            )
            st.session_state.last_council_results = council_result
            st.rerun()

    # MODE: STANDARD CHAT STREAMING
    else:
        with st.chat_message("user", avatar="👤"):
            if attached_file_info and attached_file_info.get("is_image") and attached_file_info.get("image_base64"):
                st.image(io.BytesIO(base64.b64decode(attached_file_info["image_base64"])), width=300)
            st.markdown(prompt_to_process)

        with st.chat_message("assistant", avatar="🤖"):
            if not st.session_state.api_key:
                err_box = "⚠️ Vui lòng cấu hình **API Key** ở thanh bên trái để trò chuyện."
                st.warning(err_box)
                messages.append({"role": "assistant", "content": err_box, "timestamp": now_str})
                save_session(current_session)
            else:
                try:
                    client = OpenAI(base_url=st.session_state.base_url.strip(), api_key=st.session_state.api_key.strip())
                    sys_prompt = persona_data["prompt"] if st.session_state.persona_key != "custom" else config.get("system_prompt", "")
                    payload = prepare_messages_payload(messages, system_prompt=sys_prompt, user_memory=st.session_state.user_memory)

                    t_start = time.time()
                    stream = client.chat.completions.create(
                        model=st.session_state.model.strip(),
                        messages=payload,
                        temperature=float(st.session_state.temperature),
                        max_tokens=int(st.session_state.max_tokens),
                        stream=True,
                    )

                    def response_generator():
                        for chunk in stream:
                            if chunk.choices and chunk.choices[0].delta:
                                content = chunk.choices[0].delta.content
                                if content:
                                    yield content

                    full_text = st.write_stream(response_generator())

                    t_elapsed = max(0.01, time.time() - t_start)
                    gen_tokens = estimate_token_count(full_text)
                    gen_speed = gen_tokens / t_elapsed
                    latency_ms = int(t_elapsed * 1000)

                    bot_msg_entry = {
                        "role": "assistant",
                        "content": full_text,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "stats": {
                            "latency_ms": latency_ms,
                            "tokens": gen_tokens,
                            "speed": round(gen_speed, 1)
                        },
                        "model_used": st.session_state.model
                    }
                    messages.append(bot_msg_entry)
                    current_session["messages"] = messages
                    save_session(current_session)

                    st.rerun()

                except Exception as e:
                    err_text = f"❌ **Lỗi gọi API:** {str(e)}"
                    st.error(err_text)
                    messages.append({"role": "assistant", "content": err_text, "timestamp": datetime.now().strftime("%H:%M:%S")})
                    save_session(current_session)
