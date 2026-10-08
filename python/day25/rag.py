"""Chroma + 可选 Day24 pipeline → 回答。"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from trace import trace_ask

from common.llm import chat_completions, get_llm_config

# 优先 Day24 优化检索；没有则退回 chroma
try:
    sys.path.insert(0, str(ROOT / "day24"))
    from pipeline import retrieve as search_fn
except Exception:
    from retrieve_chroma import search as search_fn


def ask(question: str, *, top_k: int = 3) -> dict:
    t0 = time.perf_counter()
    cfg = get_llm_config()
    hits = search_fn(question, top_k=top_k)
    context = "\n\n".join(
        f"[{h['source']}#{h.get('id', '')}] (score={float(h.get('score', 0)):.3f})\n{h['text']}"
        for h in hits
    )
    data = chat_completions(
        [
            {
                "role": "system",
                "content": (
                    "你是学习笔记助手。只能根据检索片段回答；不足则说不知道。"
                    "末尾列出引用过的 source。"
                ),
            },
            {"role": "user", "content": f"检索片段：\n{context}\n\n问题：{question}"},
        ],
        temperature=0,
    )
    answer = (data["choices"][0]["message"].get("content") or "").strip()
    latency_ms = (time.perf_counter() - t0) * 1000
    out = {
        "answer": answer,
        "hits": [
            {
                "id": h.get("id"),
                "source": h.get("source"),
                "text": h.get("text"),
                "score": float(h.get("score", 0)),
            }
            for h in hits
        ],
        "model": cfg["model"],
        "latency_ms": round(latency_ms, 1),
    }
    trace_ask(
        question=question,
        answer=answer,
        hits=out["hits"],
        model=cfg["model"],
        latency_ms=out["latency_ms"],
    )
    return out
