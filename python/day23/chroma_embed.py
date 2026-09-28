"""给 Chroma 用的 Embedding 函数：内部调用 day20.embed_texts。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day20"))

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embed import embed_texts


class GlmEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        mat = embed_texts(list(input))
        return mat.tolist()
