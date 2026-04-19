"""Metrics tab — live dashboard showing latency, DB stats, and file analytics."""

import streamlit as st
import vectorstore
import metrics as mx

_CSS = """
<style>
/* ── Metrics page layout ── */
.mx-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}
.mx-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
    text-align: center;
    transition: border-color 0.2s;
}
.mx-card:hover { border-color: rgba(99,102,241,0.4); }
.mx-card-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.mx-card-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Section headers ── */
.mx-section {
    font-size: 0.8rem;
    font-weight: 600;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin: 24px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

/* ── File row ── */
.file-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.75);
}
.file-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.file-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.75rem;
    color: #a78bfa;
    white-space: nowrap;
}
.file-badge-hit {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.25);
    color: #34d399;
}

/* ── Query history row ── */
.qh-row {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.83rem;
    color: rgba(255,255,255,0.7);
}
.qh-question {
    font-weight: 500;
    color: rgba(255,255,255,0.88);
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.qh-meta {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.qh-tag {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.74rem;
    color: #60a5fa;
}
.qh-tag-warn {
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.25);
    color: rgba(251,191,36,0.9);
}
</style>
"""


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Refresh control ───────────────────────────────────────────────────────
    col_title, col_btn = st.columns([7, 1.5])
    with col_title:
        st.markdown(
            '<div style="font-size:1.1rem; font-weight:600; color:rgba(255,255,255,0.8);">'
            '📊 Live Metrics Dashboard</div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # ── Fetch data ────────────────────────────────────────────────────────────
    db_docs = vectorstore.list_documents()
    snap = mx.get_snapshot(db_docs)

    q_data = snap["queries"]
    db_data = snap["db"]
    history = snap["query_history"]

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown('<div class="mx-section">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="mx-grid">', unsafe_allow_html=True)

    cards = [
        ("💬", q_data["total"],              "Total Queries"),
        ("⚡", f'{q_data["avg_latency_ms"]} ms', "Avg Latency"),
        ("📉", f'{q_data["p95_latency_ms"]} ms', "p95 Latency"),
        ("📁", db_data["unique_files"],      "Files in DB"),
        ("🔢", db_data["total_chunks"],      "Total Chunks"),
    ]

    cols = st.columns(len(cards))
    for col, (icon, value, label) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="mx-card">'
                f'  <div style="font-size:1.4rem;">{icon}</div>'
                f'  <div class="mx-card-value">{value}</div>'
                f'  <div class="mx-card-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Latency sparkline ─────────────────────────────────────────────────────
    lat_hist = q_data.get("latency_history", [])
    if lat_hist:
        st.markdown('<div class="mx-section">Latency History (last 20 queries, ms)</div>', unsafe_allow_html=True)
        st.line_chart(
            {"Latency (ms)": lat_hist},
            height=160,
            use_container_width=True,
        )

    # ── Per-file breakdown ────────────────────────────────────────────────────
    st.markdown('<div class="mx-section">File Analytics</div>', unsafe_allow_html=True)

    file_stats = db_data.get("files", [])
    if not file_stats:
        st.markdown(
            '<div style="color:rgba(255,255,255,0.35); font-size:0.85rem; padding:12px 0;">'
            'No documents in the knowledge base yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        # Sort: most searched first
        file_stats_sorted = sorted(file_stats, key=lambda x: x["times_searched"], reverse=True)
        total_queries = q_data["total"] or 1  # avoid div-by-zero

        for f in file_stats_sorted:
            fname = f["filename"]
            chunks = f["chunks_in_db"]
            hits = f["times_searched"]
            pct = round(hits / total_queries * 100) if total_queries else 0

            # Build bar fill width (max 100%)
            bar_width = min(100, pct)
            hit_color = "#34d399" if hits > 0 else "rgba(255,255,255,0.15)"

            st.markdown(
                f'<div class="file-row">'
                f'  <span style="font-size:1.1rem;">📄</span>'
                f'  <span class="file-name" title="{fname}">{fname}</span>'
                f'  <span class="file-badge">🔢 {chunks} chunks</span>'
                f'  <span class="file-badge file-badge-hit">🎯 {hits}× searched</span>'
                f'  <span class="file-badge" style="color:rgba(255,255,255,0.45);">{pct}%</span>'
                f'</div>'
                f'<div style="height:3px; background:rgba(255,255,255,0.05); border-radius:2px; margin:-2px 0 8px 0;">'
                f'  <div style="width:{bar_width}%; height:100%; background:{hit_color}; border-radius:2px; transition:width 0.4s;"></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Query history ─────────────────────────────────────────────────────────
    if history:
        st.markdown('<div class="mx-section">Recent Queries</div>', unsafe_allow_html=True)

        for entry in history:
            lat = entry["latency_ms"]
            n_src = entry["n_chunks_used"]
            lat_class = "qh-tag-warn" if lat > 5000 else "qh-tag"

            src_pills = " ".join(
                f'<span class="qh-tag">📄 {s["filename"]} · {s["score"]}</span>'
                for s in entry["sources"]
            )

            st.markdown(
                f'<div class="qh-row">'
                f'  <div class="qh-question">❓ {entry["question"]}</div>'
                f'  <div class="qh-meta">'
                f'    <span class="qh-tag {lat_class}">⚡ {lat} ms</span>'
                f'    <span class="qh-tag">📎 {n_src} chunks used</span>'
                f'    {src_pills}'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
