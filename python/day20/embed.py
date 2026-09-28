"""Embedding：优先调 LLM_EMBED_MODEL；未配置或失败则本地哈希向量兜底。

DeepSeek 官方目前无 embeddings，只配 Chat 时会走本地兜底。
智谱可设 LLM_EMBED_MODEL=embedding-3。
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
LLM_EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "").strip()


def _local_embed(texts: list[str], dim: int = 64) -> np.ndarray:
    mat = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for tok in text.lower().split():
            h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
            mat[i, h % dim] += 1.0
        n = np.linalg.norm(mat[i])
        if n > 0:
            mat[i] /= n
    return mat


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 64), dtype=np.float32)

    if not LLM_API_KEY or not LLM_EMBED_MODEL:
        print("[embed] 未配置 LLM_EMBED_MODEL（或无 Key），使用本地哈希向量")
        return _local_embed(texts)

    url = f"{LLM_BASE_URL}/embeddings"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_EMBED_MODEL,
                    "input": texts,
                },
            )
            r.raise_for_status()
            data = r.json()["data"]
            data = sorted(data, key=lambda x: x["index"])
            vecs = np.array([d["embedding"] for d in data], dtype=np.float32)
            print(f"[embed] {LLM_EMBED_MODEL} ok, shape={vecs.shape}")
            return vecs
    except Exception as e:
        print(f"[embed] API 失败，改用本地哈希: {e}")
        return _local_embed(texts)


if __name__ == "__main__":
    vecs = embed_texts(["FastAPI StreamingResponse", "Tool Calling maxSteps"])
    print(vecs.shape, vecs[0][:8])
