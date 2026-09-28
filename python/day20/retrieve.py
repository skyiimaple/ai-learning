"""余弦相似度 Top-K 检索。"""

import sys
from chunk import load_docs
from pathlib import Path

import numpy as np
from embed import embed_texts

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DOCS_DIR = Path(__file__).with_name("docs")


def build_index(docs_dir: Path = DOCS_DIR) -> tuple[list[dict], np.ndarray]:
    docs = load_docs(docs_dir)
    vectors = embed_texts([d["text"] for d in docs])
    return docs, vectors


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
    docs, vectors = build_index()
    for q in ["SSE 流式怎么做", "为什么 Key 不能进前端", "tool_calls 谁来执行"]:
        print("\nQ:", q)
        for h in search(q, docs, vectors, top_k=2):
            print(f"  [{h['score']:.3f}] {h['source']} :: {h['text'][:70]}...")
