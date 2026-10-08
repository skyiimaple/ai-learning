"""把 Day20 笔记切块写入 Chroma 持久化库。"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day20"))

from chunk import load_docs

from chroma_embed import GlmEmbeddingFunction

DB_DIR = Path(__file__).with_name("chroma_db")
SRC_DOCS = ROOT / "day20" / "docs"
COLLECTION = "notes"


def build() -> None:
    docs = load_docs(SRC_DOCS)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(
        name=COLLECTION,
        embedding_function=GlmEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )
    col.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[{"source": d["source"]} for d in docs],
    )
    print(f"[chroma] upserted {len(docs)} chunks → {DB_DIR}")
    print(f"[chroma] count={col.count()}")


if __name__ == "__main__":
    build()
