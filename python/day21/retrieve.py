"""Day21：基于落盘索引的余弦检索。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day20"))

from embed import embed_texts
from index import load_index


def search(
    query: str,
    docs: list[dict],
    vectors: np.ndarray,
    *,
    top_k: int = 3,
) -> list[dict]:
    q = embed_texts([query])[0]
    doc_norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    doc_norms[doc_norms == 0] = 1.0
    docs_n = vectors / doc_norms
    qn = q / (np.linalg.norm(q) or 1.0)
    scores = docs_n @ qn
    idx = np.argsort(-scores)[:top_k]
    return [{**docs[int(i)], "score": float(scores[int(i)])} for i in idx]


if __name__ == "__main__":
    docs, vectors = load_index()
    q = "浏览器为什么不能放 LLM_API_KEY？"
    print("Q:", q)
    for h in search(q, docs, vectors, top_k=2):
        print(f"  [{h['score']:.3f}] {h['source']} :: {h['text'][:70]}...")
