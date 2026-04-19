import streamlit as st

st.set_page_config(
    page_title="FAQ Bot — AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1535 40%, #0a1628 100%);
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 28px;
    font-weight: 500;
    font-size: 0.9rem;
    color: rgba(255,255,255,0.5);
    border: none;
    background: transparent;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.4);
}

.stTabs [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.8) !important;
    background: rgba(255,255,255,0.06) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 24px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ── Hero header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 40px 20px 10px 20px;">
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 12px 28px;
        backdrop-filter: blur(20px);
        margin-bottom: 20px;
    ">
        <span style="font-size: 2rem;">🧠</span>
        <div style="text-align:left;">
            <div style="font-size: 1.6rem; font-weight: 700;
                background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;">
                FAQ AI Assistant
            </div>
            <div style="font-size: 0.78rem; color: rgba(255,255,255,0.4); margin-top: 2px;">
                Powered by Google Gemini · RAG Architecture
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

from chat_page import render as chat_render   # noqa: E402
from files_page import render as files_render  # noqa: E402
from metrics_page import render as metrics_render  # noqa: E402

tab_chat, tab_files, tab_metrics = st.tabs(["💬  Chat", "📁  Knowledge Base", "📊  Metrics"])

with tab_chat:
    chat_render()

with tab_files:
    files_render()

with tab_metrics:
    metrics_render()
