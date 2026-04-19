"""In-memory metrics store for FAQ Bot.

Collected data
--------------
- total_queries        : number of user questions processed
- total_latency_ms     : cumulative LLM+retrieval latency (ms)
- latency_history      : last 50 latency values for sparkline / avg
- db_total_chunks      : current ChromaDB chunk count
- db_unique_files      : number of unique source documents in DB
- file_hit_counts      : {filename: hit_count} — how often each file was
                         referenced across all queries
- file_searched_counts : {filename: searched_count} — how often each file
                         appeared in the vector search results
- query_history        : last 20 queries with latency + sources snapshot
"""

from __future__ import annotations

import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional

# ── Thread-safe lock ──────────────────────────────────────────────────────────
_lock = threading.Lock()


@dataclass
class _Store:
    total_queries: int = 0
    total_latency_ms: float = 0.0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=50))
    # Per-file counters
    file_hit_counts: dict = field(default_factory=lambda: defaultdict(int))
    # Query history (last 20)
    query_history: deque = field(default_factory=lambda: deque(maxlen=20))


_store = _Store()


# ── Public API ────────────────────────────────────────────────────────────────

def record_query(
    question: str,
    chunks: list[dict],
    latency_ms: float,
) -> None:
    """Record a completed RAG query with its retrieved source chunks."""
    with _lock:
        _store.total_queries += 1
        _store.total_latency_ms += latency_ms
        _store.latency_history.append(latency_ms)

        # Count per-file hits
        for c in chunks:
            fname = c.get("filename", "unknown")
            _store.file_hit_counts[fname] += 1

        # Snapshot for history
        _store.query_history.appendleft(
            {
                "question": question[:120],
                "latency_ms": round(latency_ms, 1),
                "sources": [
                    {"filename": c.get("filename", "?"), "score": c.get("score", 0)}
                    for c in chunks
                ],
                "n_chunks_used": len(chunks),
            }
        )


def get_snapshot(db_docs: list[dict]) -> dict:
    """Return a full metrics snapshot.

    Parameters
    ----------
    db_docs : list of dicts returned by ``vectorstore.list_documents()``
              Each item: {doc_id, filename, chunks}
    """
    with _lock:
        hist = list(_store.latency_history)
        avg_latency = (
            round(sum(hist) / len(hist), 1) if hist else 0.0
        )
        p95_latency = _p95(hist)

        db_total_chunks = sum(d.get("chunks", 0) for d in db_docs)
        db_unique_files = len(db_docs)

        # Per-file stats: merge DB info with runtime hit counts
        file_stats = []
        for doc in db_docs:
            fname = doc.get("filename", "unknown")
            file_stats.append(
                {
                    "filename": fname,
                    "chunks_in_db": doc.get("chunks", 0),
                    "times_searched": _store.file_hit_counts.get(fname, 0),
                }
            )
        # Also include files that were hit but not currently in DB (edge case)
        db_filenames = {d.get("filename") for d in db_docs}
        for fname, count in _store.file_hit_counts.items():
            if fname not in db_filenames:
                file_stats.append(
                    {
                        "filename": fname,
                        "chunks_in_db": 0,
                        "times_searched": count,
                    }
                )

        return {
            "queries": {
                "total": _store.total_queries,
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "latency_history": hist[-20:],  # last 20 for chart
            },
            "db": {
                "total_chunks": db_total_chunks,
                "unique_files": db_unique_files,
                "files": file_stats,
            },
            "query_history": list(_store.query_history),
        }


def reset() -> None:
    """Reset all counters (useful for testing)."""
    global _store
    with _lock:
        _store = _Store()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = max(0, int(len(sorted_vals) * 0.95) - 1)
    return round(sorted_vals[idx], 1)


# ── Context manager for timing ────────────────────────────────────────────────

class Timer:
    """Usage::

        with Timer() as t:
            ... heavy work ...
        elapsed_ms = t.elapsed_ms
    """

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
