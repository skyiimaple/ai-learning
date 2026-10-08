"""Chroma Top-K 检索。"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chroma_embed import GlmEmbeddingFunction

DB_DIR = Path(__file__).with_name("chroma_db")
COLLECTION = "notes"


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_collection(
        name=COLLECTION,
        embedding_function=GlmEmbeddingFunction(),
    )


def search(query: str, *, top_k: int = 3) -> list[dict]:
    col = get_collection()
    res = col.query(query_texts=[query], n_results=top_k)
    hits: list[dict] = []
    ids = res["ids"][0]
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    for i, doc_id in enumerate(ids):
        dist = float(dists[i])
        hits.append(
            {
                "id": doc_id,
                "source": metas[i].get("source", ""),
                "text": docs[i],
                "distance": dist,
                "score": 1.0 - dist,
            }
        )
    return hits


if __name__ == "__main__":
    for q in [
        "浏览器为什么不能放 LLM_API_KEY？",
        "Tool Calling 里谁真正执行函数？",
        "FastAPI 流式怎么做？",
    ]:
        print("\nQ:", q)
        for h in search(q, top_k=2):
            print(f"  [{h['score']:.3f}] {h['source']} :: {h['text'][:70]}...")
