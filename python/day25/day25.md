# Day 25 · Langfuse + 知识库收口 · 未学习

- **日期**：按实际学习日
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · 评测与观测 / RAG 必交关卡
- **今日主题**：Tracing 看见 prompt/延迟/token；问答走 Chroma（可挂 Day24 pipeline）；README + 架构草图 + 评测记录
- **原则**：观测要「能截图进简历」；不换框架大搬家
- **状态**：未学习
- **大纲**：`learning-outline.md` Day25

## 环境

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3
LLM_EMBED_MODEL=embedding-3
# Langfuse Cloud 或本地；没有账号可用「简易 JSONL 日志」兜底（见下）
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## 今日目标

1. `trace.py`：每次 ask 记 latency / model / prompt 摘要（Langfuse 或 JSONL）
2. `main.py` + 静态页：Chroma（或 Day24 pipeline）驱动 `/rag/ask`，引用展示
3. `README.md` + `EVAL.md` + 架构草图：月3 必交包

## 今日不学

换 LlamaIndex/LangChain、pgvector 迁移、新前端框架

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:20 | 观测接入 | trace 通 |
| 0:20–1:00 | API + UI 接 Chroma | 浏览器可问 |
| 1:00–1:05 | 休息 | — |
| 1:05–1:45 | README / 架构 / 评测记录 | 交付文档 |
| 1:45–2:00 | 关卡自检 | 勾清单 |

---

## 开工

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
uv pip install langfuse
# 若暂无 Langfuse 账号：跳过安装，用 JSONL 分支即可
cd day25
```

---

## 详细安排

### 0:00–0:20｜观测（20 分）

**`trace.py`（Langfuse 优先，失败则 JSONL）：**

```python
"""最小 tracing：记录一次 RAG ask。"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

LOG = Path(__file__).with_name("traces.jsonl")


def _langfuse():
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    if not pk or not sk:
        return None
    try:
        from langfuse import Langfuse

        return Langfuse(
            public_key=pk,
            secret_key=sk,
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    except Exception:
        return None


def trace_ask(
    *,
    question: str,
    answer: str,
    hits: list[dict],
    model: str,
    latency_ms: float,
    meta: dict[str, Any] | None = None,
) -> None:
    payload = {
        "ts": time.time(),
        "question": question,
        "answer": answer[:2000],
        "sources": [h.get("source") for h in hits],
        "model": model,
        "latency_ms": latency_ms,
        "meta": meta or {},
    }
    lf = _langfuse()
    if lf is not None:
        trace = lf.trace(name="rag_ask", input={"question": question})
        trace.generation(
            name="answer",
            model=model,
            input=question,
            output=answer,
            metadata={"sources": payload["sources"], "latency_ms": latency_ms},
        )
        lf.flush()
        return
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
```

**验收：** 问一次后 Langfuse UI 有 trace，或本地出现 `traces.jsonl`。

---

### 0:20–1:00｜API + UI（40 分）

复用 Day22 静态页思路；检索改为 Day23/24。

**`rag.py`：**

```python
"""Chroma + 可选 Day24 pipeline → 回答。"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from common.llm import chat_completions, get_llm_config

from trace import trace_ask

# 优先 Day24 优化检索；没有则退回 chroma
try:
    sys.path.insert(0, str(ROOT / "day24"))
    from pipeline import retrieve as search_fn
except Exception:
    from retrieve_chroma import search as search_fn


def ask(question: str, *, top_k: int = 3) -> dict:
    t0 = time.perf_counter()
    cfg = get_llm_config()
    hits = search_fn(question, top_k=top_k)
    context = "\n\n".join(
        f"[{h['source']}#{h.get('id','')}] (score={float(h.get('score',0)):.3f})\n{h['text']}"
        for h in hits
    )
    data = chat_completions(
        [
            {
                "role": "system",
                "content": (
                    "你是学习笔记助手。只能根据检索片段回答；不足则说不知道。"
                    "末尾列出引用过的 source。"
                ),
            },
            {"role": "user", "content": f"检索片段：\n{context}\n\n问题：{question}"},
        ],
        temperature=0,
    )
    answer = (data["choices"][0]["message"].get("content") or "").strip()
    latency_ms = (time.perf_counter() - t0) * 1000
    out = {
        "answer": answer,
        "hits": [
            {
                "id": h.get("id"),
                "source": h.get("source"),
                "text": h.get("text"),
                "score": float(h.get("score", 0)),
            }
            for h in hits
        ],
        "model": cfg["model"],
        "latency_ms": round(latency_ms, 1),
    }
    trace_ask(
        question=question,
        answer=answer,
        hits=out["hits"],
        model=cfg["model"],
        latency_ms=out["latency_ms"],
    )
    return out
```

**`main.py`：**

```python
"""Day25 知识库 API + 静态页。"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag import ask

app = FastAPI(title="day25-kb")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RagIn(BaseModel):
    question: str = Field(min_length=1)


@app.post("/rag/ask")
def rag_ask(body: RagIn):
    try:
        return ask(body.question)
    except Exception as e:
        raise HTTPException(500, str(e)) from e


static = Path(__file__).with_name("static")
static.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=static, html=True), name="static")
```

**`static/index.html`：** 可直接复制 `day22/static/index.html`，把 fetch URL 指到本机 `8025`；展示 `hits` 与 `latency_ms`。

```bash
uvicorn main:app --host 127.0.0.1 --port 8025
```

**验收：**

- [ ] 浏览器问答有引用
- [ ] 响应含 `latency_ms`；trace 有记录

---

### 1:05–1:45｜交付文档（40 分）

**`README.md` 大纲（自己填满）：**

```markdown
# 个人知识库问答（Day20–25）

## 问题
## 架构（文字 + 见 architecture.md）
## 技术选型（为何 Chroma / 不用 LangChain）
## 如何运行
## 评测结果（链到 EVAL.md）
## 观测（Langfuse 或 traces.jsonl）
## 踩坑
```

**`architecture.md`：**

```text
User → FastAPI /rag/ask → (可选 Rewrite/Hybrid/Rerank)
      → Chroma(embedding-3) → Prompt + glm-5.3 → Answer + citations
      → Trace(Langfuse|JSONL)
```

**`EVAL.md`：**

```markdown
# 评测记录

| 日期 | 集 | top_k | baseline | optimized | 备注 |
|------|----|-------|----------|-----------|------|
|      | gold.json | 3 |  |  | Day23/24 |

截图：Langfuse / 命中率终端
```

把 Day23/24 的命中率数字抄进来。

**验收：** 陌生人按 README 能在 10 分钟内跑起来（假设有 `.env`）。

---

### 1:45–2:00｜月3 关卡自检

- [ ] 本地可跑 + 引用
- [ ] 命中率数字写入 EVAL
- [ ] Tracing 可展示
- [ ] README + 架构草图

---

## 验收清单

- [ ] `/rag/ask` + UI 通
- [ ] trace 至少 1 条
- [ ] README / EVAL / architecture 三件套

## 明日预告

Day26：手写 Agent 循环 Thought→Action→Observation，≥3 工具。
