# Day 21 · RAG 索引落盘 + `/rag/ask`（GLM） · 已学习

- **日期**：2026-09-21（落盘 2026-09-28）
- **时段**：17:20–19:20（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · RAG 架构
- **今日主题**：文档块 + 向量落盘；查询只 embed 问题；FastAPI `POST /rag/ask`
- **原则**：复用 Day20；Chat / Embed 都走智谱
- **状态**：已学习

## 环境

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3
LLM_EMBED_MODEL=embedding-3
```

| 步骤 | 模型 / 路径 |
|------|-------------|
| 建索引、问题向量 | `embedding-3` → `{BASE}/embeddings` |
| 根据片段写回答 | `glm-5.3` → `{BASE}/chat/completions` |

换模型 / 改 docs 后必须重新 `python index.py`。

## 今日目标

1. 用 `embedding-3` 写出 `data/docs.json` + `data/vectors.npy`
2. `retrieve.py` 从磁盘加载，只对问题 embed
3. `POST /rag/ask` 返回 `answer` + `hits`

## 今日不学

Chroma、pgvector、前端页、Re-rank

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 17:20–17:35 | 对齐 GLM + 复跑 Day20 | embed 通 |
| 17:35–18:10 | 重建索引 + 磁盘检索 | `data/` |
| 18:10–18:15 | 休息 | — |
| 18:15–19:00 | `rag.py` + FastAPI | `/rag/ask` |
| 19:00–19:05 | 休息 | — |
| 19:05–19:20 | curl + 复盘 | 口述落盘原因 |

---

## 环境命令

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day21
python index.py
python main.py
# 端口 8021
```

---

## 详细安排

### 17:20–17:35｜开工（15 分）

```
一次：docs → embedding-3 全部块 → 存盘
之后：问题 → 只 embed 问题 → 余弦 Top-K → glm-5.3 回答
```

| 写法 | 作用 |
|------|------|
| `np.save` / `np.load` | 向量矩阵落盘，避免每次全量 embed |
| `schema.py` 的 Pydantic 模型 | 请求/响应形状 |
| FastAPI `lifespan` | 启动时加载索引到内存 |

**验收：**

- [x] Day20 `embed.py` 能打到 `embedding-3`

---

### 17:35–18:10｜索引落盘（35 分）

**`index.py`：**（完整见仓库）

- `build_and_save`：`load_docs` → `embed_texts` → `docs.json` + `vectors.npy`
- `load_index`：读盘；条数不一致则报错

**`retrieve.py`：** 从 `load_index()` 取矩阵，只对 `query` 调 `embed_texts`。

```bash
python index.py
python retrieve.py
```

**验收：**

- [x] `data/docs.json`、`data/vectors.npy` 存在
- [x] 向量第二维 ≫ 64（真 embedding，非本地哈希 64 维）
- [x] 检索能打出 `score` / `source`

---

### 18:10–18:15｜休息（5 分）

---

### 18:15–19:00｜FastAPI（45 分）

**`schema.py`：** `RagIn` / `RagHit` / `RagOut`

**`rag.py`：** `ask()` = `search` + 拼 Prompt + `chat_completions`（glm-5.3）

**`main.py`：**

- `lifespan` 启动加载索引
- `GET /health` → `{ ok, model, chunks }`
- `POST /rag/ask` → `RagOut`

```bash
curl -s http://127.0.0.1:8021/health | python -m json.tool

curl -s http://127.0.0.1:8021/rag/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"浏览器为什么不能放 LLM_API_KEY？","top_k":3}' \
  | python -m json.tool
```

**验收：**

- [x] `/health` 的 `model` 为 `glm-5.3`，`chunks` > 0
- [x] `/rag/ask` 有 `answer` + `hits[].source`

---

### 19:00–19:05｜休息（5 分）

---

### 19:05–19:20｜复盘（15 分）

1. 文档向量缓存、问题向量实时算
2. `embedding-3` 找证据，`glm-5.3` 写答案
3. 换模型 / 改 docs → 重建索引

口述：「索引落盘避免每次全量 embed；查询只算问题向量；Chat 根据片段回答。」

---

## 验收清单（全日）

- [x] `python index.py` 写出 `data/`
- [x] `python retrieve.py` 磁盘检索通
- [x] `POST /rag/ask` 通，`model=glm-5.3`
- [x] 能口述为何要落盘、为何换模型要重建

## 实际产出文件

- `index.py`
- `retrieve.py`
- `schema.py`
- `rag.py`
- `main.py`
- `data/docs.json`
- `data/vectors.npy`

## 完整代码归档

### `schema.py`

```python
from pydantic import BaseModel, Field


class RagIn(BaseModel):
    question: str = Field(min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=8)


class RagHit(BaseModel):
    id: str
    source: str
    text: str
    score: float


class RagOut(BaseModel):
    answer: str
    hits: list[RagHit]
    model: str
```

### `rag.py`

```python
"""落盘索引 + glm-5.3 回答。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retrieve import search

from common.llm import chat_completions, get_llm_config


def ask(question: str, docs: list[dict], vectors, *, top_k: int = 3) -> dict:
    cfg = get_llm_config()
    hits = search(question, docs, vectors, top_k=top_k)
    context = "\n\n".join(
        f"[{h['source']}#{h['id']}] (score={h['score']:.3f})\n{h['text']}" for h in hits
    )
    messages = [
        {
            "role": "system",
            "content": (
                "你是学习笔记助手。只能根据给定「检索片段」回答；"
                "若片段不足，说不知道。回答末尾列出引用过的 source 文件名。"
            ),
        },
        {
            "role": "user",
            "content": f"检索片段：\n{context}\n\n问题：{question}",
        },
    ]
    data = chat_completions(messages, temperature=0)
    answer = (data["choices"][0]["message"].get("content") or "").strip()
    return {
        "answer": answer,
        "hits": [
            {
                "id": h["id"],
                "source": h["source"],
                "text": h["text"],
                "score": h["score"],
            }
            for h in hits
        ],
        "model": cfg["model"],
    }
```

### `main.py`

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from index import load_index
from rag import ask
from schema import RagIn, RagOut

from common.llm import get_llm_config

_docs: list[dict] = []
_vectors = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动加载索引；yield 后为关闭阶段。"""
    global _docs, _vectors
    try:
        _docs, _vectors = load_index()
    except FileNotFoundError as e:
        raise RuntimeError(str(e)) from e
    yield


app = FastAPI(title="Day21 RAG API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"], "chunks": len(_docs)}


@app.post("/rag/ask", response_model=RagOut)
def rag_ask(body: RagIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if _vectors is None:
        raise HTTPException(status_code=503, detail="索引未加载")
    try:
        out = ask(body.question, _docs, _vectors, top_k=body.top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"rag failed: {e}") from e
    return RagOut(**out)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8021, reload=True)
```

## 明日预告

给 `/rag/ask` 加极简引用 UI，或 Next BFF 代理；或引入 Chroma/pgvector。
