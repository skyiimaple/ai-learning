"""向量候选 + 关键词重叠，简单融合。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from retrieve_chroma import search as vector_search


def _tokens(s: str) -> set[str]:
    # 中英混排：英文词 + 连续中文按字也可，这里用粗粒度
    en = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", s.lower()))
    zh = set(re.findall(r"[\u4e00-\u9fff]{2,}", s))
    return en | zh


def keyword_score(query: str, text: str, source: str) -> float:
    qt = _tokens(query)
    if not qt:
        return 0.0
    blob = f"{source} {text}".lower()
    hit = sum(1 for t in qt if t.lower() in blob or t in blob)
    return hit / len(qt)


def hybrid_search(
    query: str,
    *,
    top_k: int = 3,
    pool: int = 8,
    alpha: float = 0.7,
) -> list[dict]:
    """alpha 越大越信向量分。"""
    vec_hits = vector_search(query, top_k=pool)
    merged: dict[str, dict] = {}
    for h in vec_hits:
        ks = keyword_score(query, h["text"], h["source"])
        score = alpha * float(h["score"]) + (1 - alpha) * ks
        merged[h["id"]] = {**h, "kw": ks, "score": score}
    ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]


if __name__ == "__main__":
    q = "Tool Calling 谁执行函数？"
    for h in hybrid_search(q, top_k=3):
        print(f"{h['score']:.3f} kw={h['kw']:.2f} {h['source']} {h['text'][:50]}...")
