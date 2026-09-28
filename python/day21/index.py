"""Day21：把 Day20 的文档块 + 向量落盘，查询时只 embed 问题。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day20"))

from chunk import load_docs

from embed import embed_texts

DATA_DIR = Path(__file__).with_name("data")
DOCS_JSON = DATA_DIR / "docs.json"
VECTORS_NPY = DATA_DIR / "vectors.npy"
SRC_DOCS = ROOT / "day20" / "docs"


def build_and_save(docs_dir: Path = SRC_DOCS) -> tuple[list[dict], np.ndarray]:
    DATA_DIR.mkdir(exist_ok=True)
    docs = load_docs(docs_dir)
    vectors = embed_texts([d["text"] for d in docs])
    DOCS_JSON.write_text(
        json.dumps(docs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    np.save(VECTORS_NPY, vectors)
    print(f"[index] saved {len(docs)} chunks → {DOCS_JSON.name} + {VECTORS_NPY.name}")
    print(f"[index] vectors shape={vectors.shape}")
    return docs, vectors


def load_index() -> tuple[list[dict], np.ndarray]:
    if not DOCS_JSON.exists() or not VECTORS_NPY.exists():
        raise FileNotFoundError("索引不存在，请先运行: python index.py")
    docs = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    vectors = np.load(VECTORS_NPY)
    if len(docs) != vectors.shape[0]:
        raise RuntimeError("docs.json 与 vectors.npy 条数不一致，请重建索引")
    return docs, vectors


if __name__ == "__main__":
    build_and_save()
