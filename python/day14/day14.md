# Day 14 · Tool Calling × FastAPI

- **日期**：2026-09-07
- **时段**：14:55–16:55（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 2 个月 · Tool Calling
- **今日主题**：把 Day13 的工具循环挂到 FastAPI，变成可 HTTP 调用的成绩 Agent
- **原则**：复用 `common.llm`；脚本逻辑抽成模块；装包用 `uv pip`
- **状态**：已完成 ✅

## 今日目标

1. 抽出可复用的 `agent.py`（工具定义 + `chat_with_tools`）
2. 提供 `POST /agent/chat`：入参一句话，返回最终回答 + 调用轨迹
3. 用 `curl` 验收至少两问（查分、比平均）

## 今日不学

- Next.js / Vercel AI SDK（下周产品化再开）
- Streaming + Tool Calling 同时做（先同步 JSON）
- 鉴权、多用户会话持久化

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 14:55–15:10 | 复跑 Day13 + 设计 API 形状 | 确认工具仍通 |
| 15:10–15:50 | 抽出 `agent.py` + `schemas.py` | 模块可 import |
| 15:50–15:55 | 休息 | — |
| 15:55–16:40 | FastAPI `main.py` + curl 验收 | `/agent/chat` |
| 16:40–16:45 | 休息 | — |
| 16:45–16:55 | 复盘 | 口述接口契约 |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day13
python tools_once.py
mkdir -p ../day14 && cd ../day14
```

---

## 详细安排

### 14:55–15:10｜开工（15 分）

**目标 API 形状：**

```http
POST /agent/chat
Content-Type: application/json

{"message": "Frank 考了多少分？", "temperature": 0}

→ 200
{
  "answer": "Frank 考了 59 分。",
  "steps": [
    {"tool": "get_score", "arguments": {"name": "Frank"}, "result": {...}}
  ],
  "model": "deepseek-chat"
}
```

**验收：**

- [x] Day13 仍能跑；清楚 `answer` vs `steps` 分工

---

### 15:10–15:50｜抽出 Agent 模块（40 分）

**`day14/schemas.py`：**

```python
from pydantic import BaseModel, Field


class AgentIn(BaseModel):
    message: str = Field(min_length=1, description="用户自然语言问题")
    temperature: float = Field(default=0, ge=0, le=2)


class ToolStep(BaseModel):
    tool: str
    arguments: dict
    result: dict | list | str | int | float | bool | None


class AgentOut(BaseModel):
    answer: str
    steps: list[ToolStep]
    model: str
    stopped: bool = False
```

**`day14/agent.py`：**

```python
"""Day14：成绩 Agent —— tools + 限步循环，供 CLI / FastAPI 共用。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions, get_llm_config

SCORES = {"Alice": 80, "Bob": 95, "Frank": 59, "Grace": 88}
MAX_STEPS = 5

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_score",
            "description": "按姓名查单个学生成绩。未知返回 not found。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "学生姓名"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "avg_score",
            "description": "计算成绩表全体学生的平均分。",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]


def get_score(name: str) -> dict:
    if name not in SCORES:
        return {"ok": False, "error": "not found", "name": name}
    return {"ok": True, "name": name, "score": SCORES[name]}


def avg_score() -> dict:
    vals = list(SCORES.values())
    return {
        "ok": True,
        "count": len(vals),
        "average": round(sum(vals) / len(vals), 2),
    }


def run_tool(name: str, arguments: str) -> dict:
    args = json.loads(arguments or "{}")
    if name == "get_score":
        return get_score(**args)
    if name == "avg_score":
        return avg_score()
    return {"ok": False, "error": f"unknown tool: {name}"}


def chat_with_tools(
    user_text: str,
    temperature: float = 0,
) -> dict:
    """返回 {answer, steps, model, stopped}。"""
    cfg = get_llm_config()
    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "你是成绩助手。查分用 get_score，算平均用 avg_score。"
                "禁止编造数字。用中文简短回答。"
            ),
        },
        {"role": "user", "content": user_text},
    ]
    steps: list[dict] = []

    for _ in range(MAX_STEPS):
        data = chat_completions(messages, temperature=temperature, tools=TOOLS)
        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            return {
                "answer": (msg.get("content") or "").strip(),
                "steps": steps,
                "model": cfg["model"],
                "stopped": False,
            }

        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": tool_calls,
            }
        )
        for tc in tool_calls:
            fn = tc["function"]
            raw_args = fn.get("arguments") or "{}"
            result = run_tool(fn["name"], raw_args)
            steps.append(
                {
                    "tool": fn["name"],
                    "arguments": json.loads(raw_args),
                    "result": result,
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return {
        "answer": "",
        "steps": steps,
        "model": cfg["model"],
        "stopped": True,
    }


if __name__ == "__main__":
    out = chat_with_tools("比较一下 Bob 和平均分，谁更高？差多少？")
    print(json.dumps(out, ensure_ascii=False, indent=2))
```

```bash
python agent.py
```

**验收：**

- [x] CLI 打印出 `answer` + 非空 `steps`
- [x] `steps` 里能看到 `get_score` / `avg_score` 的 `arguments` 与 `result`

---

### 15:50–15:55｜休息（5 分）

---

### 15:55–16:40｜FastAPI 挂载（45 分）

**`day14/main.py`：**

```python
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import chat_with_tools
from schemas import AgentIn, AgentOut

from common.llm import get_llm_config

app = FastAPI(title="Day14 Score Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/agent/chat", response_model=AgentOut)
def agent_chat(body: AgentIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    try:
        out = chat_with_tools(body.message, temperature=body.temperature)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"agent failed: {e}") from e

    if out.get("stopped") and not out.get("answer"):
        raise HTTPException(
            status_code=504,
            detail="超过最大工具步数，未得到最终回答",
        )

    return AgentOut(**out)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8014, reload=True)
```

**启动：**

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day14
uvicorn main:app --host 127.0.0.1 --port 8014 --reload
# 或：python main.py
```

**验收 curl：**

```bash
curl -s http://127.0.0.1:8014/health | python -m json.tool

curl -s http://127.0.0.1:8014/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Frank 考了多少分？","temperature":0}' \
  | python -m json.tool

curl -s http://127.0.0.1:8014/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"比较 Bob 和平均分，谁更高？差多少？","temperature":0}' \
  | python -m json.tool
```

**验收：**

- [x] `/health` 返回 `ok: true`
- [x] Frank 问能看到 `steps[].tool == get_score`，`answer` 含 59
- [x] Bob vs 平均：`steps` 含相关工具，答案合理
- [x] （可选）`http://127.0.0.1:8014/docs` 可试调

**对照前端：** 这个接口 ≈ BFF；`steps` ≈ 调试面板里的 tool trace。

---

### 16:40–16:45｜休息（5 分）

---

### 16:45–16:55｜复盘（10 分）

1. Agent 核心仍是「模型提议 → 本地执行 → 再问模型」，HTTP 只是外壳
2. 循环放进 `agent.py`，路由保持薄，方便日后换 UI
3. 同步接口先稳；流式 + tool 要处理中间事件，复杂度高一档

---

## 验收清单（全日）

- [x] `agent.py` CLI 能跑出带 `steps` 的 JSON
- [x] `POST /agent/chat` 两问都通
- [x] 缺 Key 时 `/agent/chat` 返回 500 且信息可读（可测）
- [x] 能口述：为何不在路由里直接堆 tool 循环

## 实际产出文件

- `schemas.py`
- `agent.py`
- `main.py`

## 明日预告

给 Agent 加极简前端页，或开始 `node/` 里 Next.js 接 Day10 `/chat/stream`。
