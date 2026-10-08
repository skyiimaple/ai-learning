"""可开关流水线：rewrite → hybrid|vector → rerank。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from hybrid import hybrid_search
from rerank import rerank
from retrieve_chroma import search as vector_search
from rewrite import rewrite_query


def retrieve(
    question: str,
    *,
    top_k: int = 3,
    use_rewrite: bool = True,
    use_hybrid: bool = True,
    use_rerank: bool = True,
) -> list[dict]:
    q = rewrite_query(question, enabled=use_rewrite)
    if use_hybrid:
        hits = hybrid_search(q, top_k=8 if use_rerank else top_k)
    else:
        hits = vector_search(q, top_k=8 if use_rerank else top_k)
    return rerank(question, hits, enabled=use_rerank, top_k=top_k)
