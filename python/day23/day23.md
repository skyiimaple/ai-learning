# Day 23 · Chroma 索引 + 黄金集命中率 · 已学习

- **日期**：2026-10-08
- **时段**：15:00–17:00（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · RAG 实现 / 评测入门
- **今日主题**：用 Chroma 持久化向量；写 6–8 条黄金问答算检索命中率；Embedding=`embedding-3`
- **原则**：换存储不换心智；先评「该命中哪个文件」
- **状态**：已学习

## 环境

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3
LLM_EMBED_MODEL=embedding-3
```

## 今日目标

1. `build_chroma.py`：Day20 docs → 本地 `chroma_db/`
2. `retrieve_chroma.py`：Top-K，对标 Day21 检索
3. `gold.json` + `eval_retrieve.py`：输出命中率

## 今日不学

LangChain、pgvector、Hybrid/Re-rank、Langfuse

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:00–15:15 | 装 Chroma + 对照 npy | 环境就绪 |
| 15:15–15:55 | 建库 + 检索 | build / retrieve |
| 15:55–16:00 | 休息 | — |
| 16:00–16:40 | 黄金集 + 命中率 | gold / eval |
| 16:40–16:45 | 休息 | — |
| 16:45–17:00 | 复盘 | 口述 |

---

## 开工

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
uv pip install chromadb
cd day23
```

代码示例写在下方；动手时按文件名落到 `day23/` 即可（或说「把代码落到文件」让助手写入）。

---

## 详细安排

### 15:00–15:15｜概念（15 分）

| Day21（npy） | Day23（Chroma） |
|--------------|-----------------|
| `docs.json` + `vectors.npy` | Collection + `chroma_db/` |
| 自己算余弦 | `collection.query(...)` |

| API | 作用 |
|-----|------|
| `chromadb.PersistentClient(path=...)` | 本地目录型向量库 |
| `collection.add(ids, documents, metadatas)` | 写入 chunk |
| `collection.query(query_texts, n_results)` | 近邻检索 |

**验收：** `import chromadb` 无报错。

---

### 15:15–15:55｜建库 + 检索（40 分）

**`chroma_embed.py`：**

```python
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
```

**`build_chroma.py`：**

```python
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
```

**`retrieve_chroma.py`：**

```python
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
```

```bash
python build_chroma.py
python retrieve_chroma.py
```

**验收：**

- [x] 出现 `chroma_db/`
- [x] 三问 top source 大致合理

---

### 16:00–16:40｜黄金集（40 分）

**`gold.json`：**

```json
[
  {"id": "g1", "question": "浏览器为什么不能放 LLM_API_KEY？", "expect_sources": ["bff.md"]},
  {"id": "g2", "question": "NEXT_PUBLIC_ 前缀意味着什么？", "expect_sources": ["bff.md"]},
  {"id": "g3", "question": "Tool Calling 里谁真正执行函数？", "expect_sources": ["tool_calling.md"]},
  {"id": "g4", "question": "Day13 和 Day19 的 tool 循环差在哪？", "expect_sources": ["tool_calling.md"]},
  {"id": "g5", "question": "FastAPI 流式响应常用什么？", "expect_sources": ["fastapi.md"]},
  {"id": "g6", "question": "Day10 的 /chat/stream 是干什么的？", "expect_sources": ["fastapi.md"]},
  {"id": "g7", "question": "BFF 为什么要藏内网端口？", "expect_sources": ["bff.md"]},
  {"id": "g8", "question": "assistant 消息里的 tool_calls 要不要写回 history？", "expect_sources": ["tool_calling.md"]}
]
```

**`eval_retrieve.py`：**

```python
"""检索评测：Top-K 是否命中期望 source。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from retrieve_chroma import search

GOLD = Path(__file__).with_name("gold.json")


def main(top_k: int = 3) -> None:
    cases = json.loads(GOLD.read_text(encoding="utf-8"))
    hit = 0
    for case in cases:
        results = search(case["question"], top_k=top_k)
        got = {h["source"] for h in results}
        expect = set(case["expect_sources"])
        ok = bool(got & expect)
        hit += int(ok)
        mark = "OK" if ok else "MISS"
        print(f"[{mark}] {case['id']} expect={expect} got={got}")
        if not ok:
            print("   Q:", case["question"])
    total = len(cases)
    rate = hit / total if total else 0.0
    print(f"\n命中率: {hit}/{total} = {rate:.0%} (top_k={top_k})")


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(top_k=k)
```

```bash
python eval_retrieve.py
python eval_retrieve.py 5
```

**验收：**

- [x] 打印 OK/MISS 与命中率
- [x] 明白这是检索评测，不是答案质量评测

---

### 16:45–17:00｜复盘

1. Chroma 管存与搜；Embedding 函数仍是你的  
2. 黄金集先评 source 是否进 Top-K  
3. 改 docs → 重建 `build_chroma.py`

---

## 验收清单

- [x] build + retrieve 通
- [x] eval 输出命中率
- [x] 能口述 Chroma vs npy

## 明日预告

Day24：Query Rewrite + Hybrid + 轻量 Re-rank，黄金集前后命中率对比（见 `learning-outline.md`）。
