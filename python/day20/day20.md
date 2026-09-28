# Day 20 · RAG 入门（GLM）：Chunking + Embedding + 检索 · 已学习

- **日期**：2026-09-14（落盘 2026-09-15）
- **时段**：17:50–19:50（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · RAG 架构
- **今日主题**：本地笔记切块 → 智谱 `embedding-3` → 余弦 Top-K → `glm-4.7` 带引用回答
- **原则**：手写最小链路；复用 `common.llm`；不上 LangChain/Chroma
- **状态**：已学习

## 环境约定（GLM）

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4.7          # Chat：根据检索片段生成回答
LLM_EMBED_MODEL=embedding-3  # Embedding：文本 → 向量
LLM_API_KEY=...
```

| 用途 | 模型 | 路径（接在 `LLM_BASE_URL` 后） |
|------|------|--------------------------------|
| 对话 | `glm-4.7` | `/chat/completions` |
| 向量 | `embedding-3` | `/embeddings` |

智谱 base 已是 `.../v4`，**不要**再拼 `/v1`。

## 今日目标

1. `chunk.py` + `docs/` 切块可跑
2. `embed.py` 调用智谱 `embedding-3`（失败则本地哈希兜底）
3. `retrieve.py` + `rag_once.py` 端到端：提问 → Top-K → 带 source 回答

## 今日不学

Chroma / pgvector / LangChain、PDF、Hybrid、Next 接 RAG

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 17:50–18:05 | RAG 五步 + chunk | `docs/` + `chunk.py` |
| 18:05–18:45 | GLM Embedding | `embed.py` |
| 18:45–18:50 | 休息 | — |
| 18:50–19:30 | 检索 + RAG | `retrieve.py` / `rag_once.py` |
| 19:30–19:35 | 休息 | — |
| 19:35–19:50 | 复盘 | Chat vs Embedding |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
uv pip install numpy
cd day20
```

---

## 详细安排

### 17:50–18:05｜概念 + 切块（15 分）

```
问题 → Chunk → Embedding(embedding-3) → Top-K → Prompt → glm-4.7 回答+引用
```

**Embedding（嵌入）**：把文字变成固定长度数字向量，用远近衡量语义像不像。  
Chat 模型写答案；Embedding 模型只负责语义坐标，不写文章。

**`docs/`**：`fastapi.md` / `tool_calling.md` / `bff.md`

**`chunk.py`：**

```python
"""固定窗口切块（字符级，够用版）。"""

from pathlib import Path


def chunk_text(text: str, *, chunk_size: int = 180, overlap: int = 40) -> list[str]:
    """将文本按字符级切块。"""
    chunks: list[str] = []
    text = " ".join(text.split())
    if not text:
        return chunks
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def load_docs(docs_dir: Path) -> list[dict]:
    """返回[{id,source,text},...]."""
    rows: list[dict] = []
    docs = sorted(docs_dir.glob("*.md"))
    for doc in docs:
        raw = doc.read_text(encoding="utf-8")
        file = enumerate(chunk_text(raw))
        for i, chunk in file:
            rows.append({"id": f"{doc.stem}-{i}", "source": doc.name, "text": chunk})
    return rows


if __name__ == "__main__":
    docs = load_docs(Path(__file__).with_name("docs"))
    print(f"chunks count: {len(docs)}")
    for d in docs[:3]:
        print(d["id"], d["source"], d["text"][:60], "...")
```

```bash
python chunk.py
```

**验收：**

- [x] `chunks count` > 0

---

### 18:05–18:45｜Embedding（40 分）

**`embed.py`：**（智谱 `/embeddings` + 本地哈希兜底）

```python
"""Embedding：智谱 embedding-3；失败则本地哈希向量兜底。"""

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
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4").rstrip(
    "/"
)
LLM_EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "embedding-3")


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
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY is not set")
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
            print(f"[embed] GLM {LLM_EMBED_MODEL} ok, shape={vecs.shape}")
            return vecs
    except Exception as e:
        print(f"[embed] API 失败，改用本地哈希: {e}")
        return _local_embed(texts)


if __name__ == "__main__":
    vecs = embed_texts(["FastAPI StreamingResponse", "Tool Calling maxSteps"])
    print(vecs.shape, vecs[0][:8])
```

```bash
python embed.py
```

**验收：**

- [x] 能打到智谱 `/embeddings`（或明确走了兜底）

---

### 18:45–18:50｜休息（5 分）

---

### 18:50–19:30｜检索 + RAG（40 分）

**`retrieve.py` 核心 `search`（余弦 Top-K）：**

- `embed_texts([query])[0]`：问题向量  
- `np.linalg.norm(..., axis=1, keepdims=True)`：每行文档向量长度  
- 除以范数归一化后，`docs_n @ qn`：点积 ≈ 余弦相似度  
- `np.argsort(-scores)[:top_k]`：分数从高到低下标  

**`retrieve.py` / `rag_once.py`：** 见仓库完整文件。

```bash
python retrieve.py
python rag_once.py "浏览器为什么不能放 LLM_API_KEY？"
python rag_once.py "Tool Calling 里谁真正执行函数？"
python rag_once.py "量子计算怎么做菜？"
```

**验收：**

- [x] 前两问命中相关笔记并带引用
- [x] 第三问倾向「不知道 / 片段不足」

---

### 19:30–19:35｜休息（5 分）

---

### 19:35–19:50｜复盘（15 分）

**Chat vs Embedding：**

- Embedding：文本 → 向量，只做语义坐标 / 检索  
- Chat：看检索片段 + 问题 → 自然语言回答  
- RAG：Embedding 找证据，Chat 写答案  

口述：「Embedding 把文字变成向量用来语义检索；Chat 根据检索到的片段生成回答。」

---

## 验收清单（全日）

- [x] `.env` 含 `LLM_EMBED_MODEL=embedding-3`（或等价配置）
- [x] `chunk` / `embed` / `retrieve` / `rag_once` 可跑
- [x] 能口述 Chat 模型 vs Embedding 模型分工
- [x] 理解 Embedding = 嵌入（文本 → 向量）

## 实际产出文件

- `docs/fastapi.md`、`docs/tool_calling.md`、`docs/bff.md`
- `chunk.py`
- `embed.py`
- `retrieve.py`
- `rag_once.py`

## 明日预告

向量索引落盘（避免每次全量 embed），或 FastAPI `/rag/ask`。
