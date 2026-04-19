"""Files tab — premium document management UI."""

import io
from pathlib import Path

import pypdf
import streamlit as st
import docx as python_docx

import rag
import vectorstore

ACCEPTED_TYPES = ["pdf", "docx", "md", "txt"]
UPLOADS_DIR = Path("./uploads")

_EXT_ICON  = {"pdf": "📕", "docx": "📘", "doc": "📘", "md": "📗", "txt": "📄"}
_EXT_COLOR = {
    "pdf":  "#ef4444",
    "docx": "#3b82f6",
    "doc":  "#3b82f6",
    "md":   "#10b981",
    "txt":  "#6b7280",
}
_EXT_GRAD = {
    "pdf":  "linear-gradient(135deg, #ef444422, #ef444408)",
    "docx": "linear-gradient(135deg, #3b82f622, #3b82f608)",
    "doc":  "linear-gradient(135deg, #3b82f622, #3b82f608)",
    "md":   "linear-gradient(135deg, #10b98122, #10b98108)",
    "txt":  "linear-gradient(135deg, #6b728022, #6b728008)",
}

_CSS = """
<style>
/* ── Stat cards ── */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    opacity: 0.6;
}
.stat-card:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(255,255,255,0.14);
    transform: translateY(-2px);
}
.stat-number {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 6px;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

/* ── Section heading ── */
.section-heading {
    font-size: 0.72rem;
    font-weight: 700;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 28px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ── Upload zone (placeholder) ── */
.upload-hint {
    background: rgba(59,130,246,0.05);
    border: 2px dashed rgba(59,130,246,0.2);
    border-radius: 16px;
    padding: 36px 24px;
    text-align: center;
    color: rgba(255,255,255,0.35);
    font-size: 0.9rem;
    margin-bottom: 8px;
    transition: all 0.3s;
}
.upload-hint:hover {
    background: rgba(59,130,246,0.08);
    border-color: rgba(59,130,246,0.35);
    color: rgba(255,255,255,0.55);
}
.upload-hint-icon { font-size: 2.5rem; display: block; margin-bottom: 12px; }
.upload-hint-sub { font-size: 0.78rem; opacity: 0.7; margin-top: 6px; }

/* ── Empty state ── */
.empty-state {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 40px 24px;
    text-align: center;
    color: rgba(255,255,255,0.3);
}
.empty-state-icon { font-size: 2.5rem; display: block; margin-bottom: 12px; }

/* ── Document card ── */
.doc-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 18px;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: all 0.2s ease;
    margin-bottom: 8px;
}
.doc-card:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.12);
}
.doc-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.doc-info { flex: 1; min-width: 0; }
.doc-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.doc-meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;
}
.doc-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.doc-chunks {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
}

/* ── Preview header ── */
.preview-header {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 14px;
    color: rgba(255,255,255,0.8);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── Streamlit overrides ── */
.stFileUploader > div {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.85rem !important;
}
</style>
"""


# ── Disk helpers ──────────────────────────────────────────────────────────────

def _save_upload(filename: str, data: bytes):
    UPLOADS_DIR.mkdir(exist_ok=True)
    (UPLOADS_DIR / filename).write_bytes(data)


def _load_upload(filename: str) -> bytes | None:
    p = UPLOADS_DIR / filename
    return p.read_bytes() if p.exists() else None


def _delete_upload(filename: str):
    p = UPLOADS_DIR / filename
    if p.exists():
        p.unlink(missing_ok=True)


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"


# ── Preview ────────────────────────────────────────────────────────────────────

def _render_preview(filename: str, file_bytes: bytes):
    ext   = _ext(filename)
    icon  = _EXT_ICON.get(ext, "📄")

    st.markdown(
        f'<div class="preview-header">{icon}&nbsp; {filename}</div>',
        unsafe_allow_html=True,
    )

    if ext == "pdf":
        col_dl, _ = st.columns([2, 5])
        with col_dl:
            st.download_button(
                "⬇️ Download PDF",
                data=file_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = "\n\n— page break —\n\n".join(
            p.extract_text() or "" for p in reader.pages
        ).strip()
        if text:
            with st.expander("📄 Extracted text", expanded=True):
                st.text_area(
                    "Extracted content",
                    text,
                    height=480,
                    disabled=True,
                    label_visibility="collapsed",
                )
        else:
            st.info("No extractable text found (scanned PDF?).", icon="ℹ️")

    elif ext in ("docx", "doc"):
        doc = python_docx.Document(io.BytesIO(file_bytes))
        text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        st.text_area(
            "Document content",
            text,
            height=480,
            disabled=True,
            label_visibility="collapsed",
        )

    elif ext == "md":
        st.markdown(file_bytes.decode("utf-8", errors="replace"))

    else:
        st.text_area(
            "File content",
            file_bytes.decode("utf-8", errors="replace"),
            height=480,
            disabled=True,
            label_visibility="collapsed",
        )


# ── Main render ────────────────────────────────────────────────────────────────

def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    # feedback messages
    result = st.session_state.pop("upload_result", None)
    if result:
        for msg in result.get("successes", []):
            st.success(msg, icon="✅")
        for msg in result.get("errors", []):
            st.error(msg, icon="❌")

    # ── Stats ──────────────────────────────────────────────────────────────
    docs = vectorstore.list_documents()
    total_chunks = sum(d["chunks"] for d in docs)
    formats = list({_ext(d["filename"]) for d in docs})
    fmt_str = " · ".join(f.upper() for f in formats) if formats else "—"

    c1, c2, c3 = st.columns(3)
    for col, number, label in [
        (c1, len(docs),     "Documents"),
        (c2, total_chunks,  "Chunks Indexed"),
        (c3, fmt_str,       "Formats"),
    ]:
        num_style = "font-size:1.1rem;padding-top:8px" if isinstance(number, str) else ""
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'  <div class="stat-number" style="{num_style}">{number}</div>'
                f'  <div class="stat-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Upload ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-heading">📤 Upload documents</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload files",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        names = "  ·  ".join(f.name for f in uploaded)
        st.caption(f"Selected: {names}")
        if st.button(
            "⚡ Embed & Add to Knowledge Base",
            type="primary",
            use_container_width=True,
        ):
            successes, errors = [], []
            bar = st.progress(0, text="Starting…")
            for i, f in enumerate(uploaded):
                bar.progress(i / len(uploaded), text=f"Embedding {f.name}…")
                try:
                    data = f.read()
                    _save_upload(f.name, data)
                    doc_id, n = rag.process_upload(data, f.name)
                    successes.append(f"**{f.name}** — {n} chunks indexed")
                except Exception as e:
                    errors.append(f"**{f.name}**: {e}")
            bar.progress(1.0, text="Done!")
            st.session_state.upload_result = {"successes": successes, "errors": errors}
            st.rerun()
    else:
        st.markdown(
            '<div class="upload-hint">'
            '  <span class="upload-hint-icon">📂</span>'
            '  Drop files here or click to browse'
            '  <div class="upload-hint-sub">PDF · DOCX · MD · TXT</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Document list ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-heading">📋 Indexed documents</div>',
        unsafe_allow_html=True,
    )

    if not docs:
        st.markdown(
            '<div class="empty-state">'
            '  <span class="empty-state-icon">🗄️</span>'
            '  No documents yet — upload something above'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for doc in docs:
            ext   = _ext(doc["filename"])
            icon  = _EXT_ICON.get(ext, "📄")
            color = _EXT_COLOR.get(ext, "#6b7280")
            grad  = _EXT_GRAD.get(ext, "rgba(255,255,255,0.04)")
            on_disk = (UPLOADS_DIR / doc["filename"]).exists()

            info_col, view_col, del_col = st.columns([7, 1.3, 1.3])

            with info_col:
                st.markdown(
                    f'<div class="doc-card">'
                    f'  <div class="doc-icon" style="background:{grad};">{icon}</div>'
                    f'  <div class="doc-info">'
                    f'    <div class="doc-name">{doc["filename"]}</div>'
                    f'    <div class="doc-meta-row">'
                    f'      <span class="doc-badge" style="background:{color}22;color:{color};">{ext.upper()}</span>'
                    f'      <span class="doc-chunks">{doc["chunks"]} chunks</span>'
                    f'    </div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with view_col:
                st.write("")
                if st.button(
                    "👁 View",
                    key=f"view_{doc['doc_id']}",
                    use_container_width=True,
                    disabled=not on_disk,
                    help="Preview file" if on_disk else "Original file not on disk",
                ):
                    st.session_state["preview_target"] = doc["filename"]
                    st.rerun()

            with del_col:
                st.write("")
                if st.button(
                    "🗑 Delete",
                    key=f"del_{doc['doc_id']}",
                    use_container_width=True,
                ):
                    vectorstore.delete_document(doc["doc_id"])
                    _delete_upload(doc["filename"])
                    if st.session_state.get("preview_target") == doc["filename"]:
                        st.session_state.pop("preview_target", None)
                    st.session_state.upload_result = {
                        "successes": [
                            f"**{doc['filename']}** removed ({doc['chunks']} chunks deleted)"
                        ],
                        "errors": [],
                    }
                    st.rerun()

    # ── Preview ─────────────────────────────────────────────────────────────
    target = st.session_state.get("preview_target")
    if target:
        data = _load_upload(target)
        if data:
            st.markdown(
                '<div class="section-heading">🔍 File preview</div>',
                unsafe_allow_html=True,
            )
            col_close, _ = st.columns([1.5, 7])
            with col_close:
                if st.button("✕ Close preview", use_container_width=True):
                    st.session_state.pop("preview_target", None)
                    st.rerun()
            _render_preview(target, data)
        else:
            st.session_state.pop("preview_target", None)
