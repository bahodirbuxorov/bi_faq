"""Chat tab — premium RAG-powered conversational interface."""

import html as html_lib
import streamlit as st

import llm
import vectorstore
import metrics
from config import TOP_K

_CSS = """
<style>
/* ── Chat page layout ── */
.chat-page-wrapper {
    max-width: 900px;
    margin: 0 auto;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 30px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    backdrop-filter: blur(10px);
}
.stat-chip strong { color: rgba(255,255,255,0.85); }

/* ── Chat window ── */
.chat-window {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 24px;
    min-height: 420px;
    backdrop-filter: blur(10px);
    margin-bottom: 16px;
}

/* ── Empty state ── */
.chat-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
}
.chat-empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    filter: drop-shadow(0 0 20px rgba(139,92,246,0.6));
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
.chat-empty-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.7);
    margin-bottom: 8px;
}
.chat-empty-hint {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.3);
    max-width: 340px;
    line-height: 1.6;
}

/* ── Messages ── */
.u-row {
    display: flex;
    justify-content: flex-end;
    margin: 10px 0;
    animation: slideUp 0.3s ease;
}
.u-bubble {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: #ffffff;
    padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 72%;
    word-wrap: break-word;
    font-size: 0.93rem;
    line-height: 1.65;
    white-space: pre-wrap;
    box-shadow: 0 4px 20px rgba(59,130,246,0.35);
}
.b-row {
    display: flex;
    justify-content: flex-start;
    margin: 10px 0;
    align-items: flex-end;
    gap: 10px;
    animation: slideUp 0.3s ease;
}
.b-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(99,102,241,0.4);
}
.b-bubble {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.85);
    padding: 12px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 72%;
    word-wrap: break-word;
    font-size: 0.93rem;
    line-height: 1.65;
    white-space: pre-wrap;
    backdrop-filter: blur(10px);
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Thinking indicator ── */
.thinking-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    margin: 10px 0;
}
.thinking-bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px 20px 20px 4px;
    padding: 12px 18px;
    display: flex;
    gap: 5px;
    align-items: center;
}
.dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    animation: pulse 1.4s ease-in-out infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40% { transform: scale(1); opacity: 1; }
}

/* ── Source pills ── */
.src-section {
    margin-top: 12px;
    padding: 14px 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
}
.src-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.src-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.77rem;
    color: #60a5fa;
    margin: 3px 4px 3px 0;
    transition: all 0.2s;
}

/* ── No-docs warning ── */
.no-docs-banner {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 14px;
    padding: 14px 18px;
    color: rgba(251,191,36,0.85);
    font-size: 0.88rem;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
</style>
"""


def _init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "generating" not in st.session_state:
        st.session_state.generating = False


def _user_bubble(text: str):
    st.markdown(
        f'<div class="u-row"><div class="u-bubble">{html_lib.escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


def _bot_bubble(text: str):
    st.markdown(
        f'<div class="b-row">'
        f'  <div class="b-avatar">🧠</div>'
        f'  <div class="b-bubble">{html_lib.escape(text)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _thinking_bubble():
    st.markdown(
        '<div class="thinking-row">'
        '  <div class="b-avatar">🧠</div>'
        '  <div class="thinking-bubble">'
        '    <div class="dot"></div>'
        '    <div class="dot"></div>'
        '    <div class="dot"></div>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render():
    _init_state()
    st.markdown(_CSS, unsafe_allow_html=True)

    doc_count = vectorstore.collection_count()
    msgs = len(st.session_state.messages)

    # ── Stats bar ───────────────────────────────────────────────────────────
    col_stats, col_btn = st.columns([8, 1.5])
    with col_stats:
        st.markdown(
            f'<div class="stats-bar">'
            f'  <div class="stat-chip">📚 <strong>{doc_count}</strong> chunks indexed</div>'
            f'  <div class="stat-chip">💬 <strong>{msgs // 2}</strong> exchanges</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.session_state.messages:
            if st.button("🗑 Clear chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.pop("last_sources", None)
                st.session_state.generating = False
                st.rerun()

    # ── No-docs warning ─────────────────────────────────────────────────────
    if doc_count == 0:
        st.markdown(
            '<div class="no-docs-banner">'
            '  ⚠️ Knowledge base is empty. Upload documents in the <strong>Knowledge Base</strong> tab first.'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Chat window ─────────────────────────────────────────────────────────
    st.markdown('<div class="chat-window">', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            '<div class="chat-empty">'
            '  <div class="chat-empty-icon">🧠</div>'
            '  <div class="chat-empty-title">Ask anything about your documents</div>'
            '  <div class="chat-empty-hint">Upload PDFs, DOCX, MD or TXT files in the Knowledge Base tab, then start chatting here.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                _user_bubble(msg["content"])
            else:
                _bot_bubble(msg["content"])

        if st.session_state.generating:
            _thinking_bubble()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Generate response ────────────────────────────────────────────────────
    if st.session_state.generating:
        last_q = st.session_state.messages[-1]["content"]
        with metrics.Timer() as t:
            chunks = vectorstore.query(last_q, top_k=TOP_K) if doc_count > 0 else []
            history = st.session_state.messages[:-1]
            try:
                answer = llm.ask(last_q, chunks, history)
            except Exception as e:
                answer = f"⚠️ Error generating response: {e}"
                chunks = []
        # Record metrics after each query
        metrics.record_query(
            question=last_q,
            chunks=chunks,
            latency_ms=t.elapsed_ms,
        )
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state["last_sources"] = chunks
        st.session_state.generating = False
        st.rerun()

    # ── Sources ──────────────────────────────────────────────────────────────
    sources = st.session_state.get("last_sources", [])
    if sources:
        pills = "".join(
            f'<span class="src-pill">📄 {c["filename"]} · {c["score"]}</span>'
            for c in sources
        )
        with st.expander(f"📎 {len(sources)} source chunks used", expanded=False):
            st.markdown(
                f'<div class="src-section">'
                f'  <div class="src-title">Referenced documents</div>'
                f'  <div>{pills}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.divider()
            for i, c in enumerate(sources, 1):
                st.caption(
                    f"**[{i}]** `{c['filename']}` — score {c['score']}\n\n"
                    f"{c['text'][:300]}{'…' if len(c['text']) > 300 else ''}"
                )

    # ── Input ────────────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask a question about your documents…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pop("last_sources", None)
        st.session_state.generating = True
        st.rerun()
