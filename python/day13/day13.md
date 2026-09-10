# Day 13 · Tool Calling 入门

- **日期**：2026-09-07
- **时段**：14:40–16:40（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 2 个月 · Tool Calling
- **今日主题**：模型选工具 → 你执行 → 结果喂回，跑通单轮 + 多步循环
- **原则**：动手为主；不引入 LangChain；复用 `common.llm`
- **状态**：已完成 ✅

## 今日目标

1. 口述 `tools` / `tool_calls` / `role: tool` 一轮顺序
2. 完成 `tools_once.py`（单工具闭环）
3. 完成 `tool_loop.py`（双工具 + 限步循环）

## 今日不学

LangChain、Next.js、复杂并行编排

## 已有基础（开课前已完成）

- [x] `common/llm.py` 的 `chat_completions` 已支持 `tools` / `tool_choice`

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 14:40–14:50 | 快速过概念（对照前端） | 脑中流程图 |
| 14:50–15:30 | 单轮 Tool Call | `tools_once.py` |
| 15:30–15:35 | 休息 | — |
| 15:35–16:20 | 双工具循环 | `tool_loop.py` |
| 16:20–16:25 | 休息 | — |
| 16:25–16:40 | 加练 + 复盘 | 口述 3 点 |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
mkdir -p day13
cd day13
```

---

## 详细安排

### 14:40–14:50｜概念（10 分）

```
用户提问
  → 模型看 tools（像看 API 文档）
  → 决定调哪个 function + 参数
  → 你的代码执行（模型不会真跑业务）
  → role=tool 把结果塞回 messages
  → 模型用自然语言回答
```

**对照前端：** `TOOLS` ≈ OpenAPI 片段；`run_tool` ≈ route handler；第二轮 ≈ 用接口返回渲染 UI。

**验收：**

- [x] 能说清「谁提议调用、谁真正执行」

---

### 14:50–15:30｜单轮闭环（40 分）

`common/llm.py` 中 `chat_completions` 完整实现（今日依赖）：

```python
def chat_completions(
    messages: list[dict],
    temperature: float = 0.7,
    tools: list[dict] | None = None,
    tool_choice: str | dict | None = None,
) -> dict:
    """调用兼容 OpenAI 的 /v1/chat/completions，返回完整 JSON。"""
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    payload: dict = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
    }
    if tools is not None:
        payload["tools"] = tools
    if tool_choice is not None:
        payload["tool_choice"] = tool_choice

    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        return r.json()
```

新建 **`day13/tools_once.py`**（完整可跑）：

```python
"""Day13：单轮 Tool Calling —— 查一个学生成绩。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SCORES = {"Alice": 80, "Bob": 95, "Frank": 59, "Grace": 88}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_score",
            "description": "按学生姓名查询成绩。姓名区分大小写，未知则返回 not found。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "学生英文名，如 Alice",
                    }
                },
                "required": ["name"],
            },
        },
    }
]


def get_score(name: str) -> dict:
    if name not in SCORES:
        return {"ok": False, "error": "not found", "name": name}
    return {"ok": True, "name": name, "score": SCORES[name]}


def run_tool(name: str, arguments: str) -> str:
    args = json.loads(arguments or "{}")
    if name == "get_score":
        result = get_score(**args)
    else:
        result = {"ok": False, "error": f"unknown tool: {name}"}
    return json.dumps(result, ensure_ascii=False)


def main() -> None:
    question = "Frank 考了多少分？用工具查，再口头告诉我。"
    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "你是成绩助手。需要查分时必须调用 get_score，"
                "不要编造分数。拿到工具结果后再用中文简短回答。"
            ),
        },
        {"role": "user", "content": question},
    ]

    print("=== round 1: ask model ===")
    data = chat_completions(messages, temperature=0, tools=TOOLS)
    msg = data["choices"][0]["message"]
    print("content:", msg.get("content"))
    print("tool_calls:", json.dumps(msg.get("tool_calls"), ensure_ascii=False, indent=2))

    tool_calls = msg.get("tool_calls") or []
    if not tool_calls:
        print("模型没有调用工具，直接结束。")
        return

    messages.append(
        {
            "role": "assistant",
            "content": msg.get("content"),
            "tool_calls": tool_calls,
        }
    )

    for tc in tool_calls:
        fn = tc["function"]
        tool_result = run_tool(fn["name"], fn.get("arguments") or "{}")
        print(f"=== execute {fn['name']} ===")
        print(tool_result)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": tool_result,
            }
        )

    print("=== round 2: final answer ===")
    data2 = chat_completions(messages, temperature=0, tools=TOOLS)
    final = data2["choices"][0]["message"]
    print("final:", final.get("content"))
    print("usage:", data2.get("usage"))


if __name__ == "__main__":
    main()
```

```bash
python tools_once.py
```

**验收：**

- [x] 第一轮有 `tool_calls`，`name == get_score`，参数含 Frank
- [x] 最终回答出现 **59**

---

### 15:30–15:35｜休息（5 分）

---

### 15:35–16:20｜双工具循环（45 分）

新建 **`day13/tool_loop.py`**：

```python
"""Day13：多步 Tool Calling 循环（最多 MAX_STEPS）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SCORES = {"Alice": 80, "Bob": 95, "Frank": 59, "Grace": 88}
MAX_STEPS = 5

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_score",
            "description": "按姓名查单个学生成绩。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "学生姓名"}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "avg_score",
            "description": "计算当前成绩表中全体学生的平均分。",
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


def run_tool(name: str, arguments: str) -> str:
    args = json.loads(arguments or "{}")
    if name == "get_score":
        result = get_score(**args)
    elif name == "avg_score":
        result = avg_score()
    else:
        result = {"ok": False, "error": f"unknown tool: {name}"}
    return json.dumps(result, ensure_ascii=False)


def chat_with_tools(user_text: str) -> str:
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

    for step in range(1, MAX_STEPS + 1):
        print(f"\n----- step {step} -----")
        data = chat_completions(messages, temperature=0, tools=TOOLS)
        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            answer = (msg.get("content") or "").strip()
            print("final content:", answer)
            return answer

        print("tool_calls:", json.dumps(tool_calls, ensure_ascii=False, indent=2))
        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": tool_calls,
            }
        )
        for tc in tool_calls:
            fn = tc["function"]
            out = run_tool(fn["name"], fn.get("arguments") or "{}")
            print(f"exec {fn['name']} -> {out}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": out,
                }
            )

    return "[stopped] 超过 MAX_STEPS，未拿到最终自然语言回答"


if __name__ == "__main__":
    q = "比较一下 Bob 和平均分，谁更高？差多少？"
    print("Q:", q)
    print("A:", chat_with_tools(q))
```

```bash
python tool_loop.py
```

**验收：**

- [x] 至少用到 `get_score(Bob)` 与 `avg_score`
- [x] 最终能比较 Bob **95** 与平均约 **80.5**
- [x] 不会死循环（`MAX_STEPS` 生效）

---

### 16:20–16:25｜休息（5 分）

---

### 16:25–16:40｜加练 + 复盘（15 分）

加练（可选）：

```python
print(chat_with_tools("有没有叫 Zack 的同学？"))
```

应走 `not found`，不胡编。

复盘三点：

1. 模型只提议，执行永远是你的代码
2. 带 `tool_calls` 的 `assistant` 必须进 history
3. 工具失败返回结构化错误，别把会话抛崩

---

## 验收清单（全日）

- [x] `common/llm.py` 的 `chat_completions` 支持 `tools` / `tool_choice`
- [x] `tools_once.py`：Frank → 59
- [x] `tool_loop.py`：Bob vs 平均分答对
- [x] 能口述完整一轮 Tool Calling 顺序

## 实际产出文件

- `tools_once.py`
- `tool_loop.py`
- （共用）`../common/llm.py` 增加 `tools` / `tool_choice`

## 明日预告

Tool Calling 挂 FastAPI（如 `POST /agent/chat`），或 Next.js 接 Day10 Streaming。
