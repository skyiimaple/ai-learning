# Day 26 · Agent 核心循环 · 已学习

- **日期**：2026-10-08
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 4 个月 · Agent 核心
- **今日主题**：手写 Thought→Action→Observation；限步；≥3 工具完成一个真实任务
- **原则**：不用重型 Agent 框架；工具真执行，模型只规划
- **状态**：已学习
- **大纲**：`learning-outline.md` Day26

## 环境

同前；`common.llm.chat_completions(..., tools=...)`。

## 今日目标

1. `tools.py`：至少 3 个工具（建议：`get_time`、`calc`、`kb_search` 调 Day23/25）
2. `agent.py`：限步循环，打印每步 Thought/Action/Observation
3. 真实任务：例如「查笔记里 BFF 要点，再算 17*23，最后给出当前时间并总结」

## 今日不学

LangGraph/AutoGen/CrewAI、多 Agent、复杂规划器

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:15 | 循环心智 + schema | 口述清楚 |
| 0:15–0:55 | 三工具 + 注册 | tools 可单测 |
| 0:55–1:00 | 休息 | — |
| 1:00–1:40 | agent 循环 + 限步 | 任务跑通 |
| 1:40–2:00 | 复盘失败路径 | 口述何时停 |

---

## 开工

```bash
cd ~/code/ai-learning/python && source .venv/bin/activate && cd day26
```

---

## 详细安排

### 0:00–0:15｜心智（15 分）

```
用户目标
  → LLM（可带 tools）→ tool_calls?
      有 → 执行工具 → observation 写回 messages → 再调 LLM（计步）
      无 → 最终回答，结束
步数 ≥ MAX_STEPS → 强制停并说明
```

**验收：** 能口述「谁执行函数」（你的代码，不是模型）。

---

### 0:15–0:55｜工具（40 分）

**`tools.py`：**

```python
"""Agent 工具：定义 schema + 本地执行。"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from retrieve_chroma import search as kb_search_impl

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "返回当前本地时间 ISO 字符串",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "计算简单算术表达式，仅支持数字与 +-*/()",
            "parameters": {
                "type": "object",
                "properties": {"expr": {"type": "string"}},
                "required": ["expr"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kb_search",
            "description": "在学习笔记知识库中检索相关片段",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
]


def _calc(expr: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not expr or any(c not in allowed for c in expr):
        return json.dumps({"error": "invalid expr"})
    try:
        return json.dumps({"result": float(eval(expr, {"__builtins__": {}}, {}))})
    except Exception as e:
        return json.dumps({"error": str(e)})


def run_tool(name: str, arguments: str | dict) -> str:
    args = json.loads(arguments) if isinstance(arguments, str) else (arguments or {})
    if name == "get_time":
        return json.dumps({"now": datetime.now().isoformat(timespec="seconds")})
    if name == "calc":
        return _calc(str(args.get("expr", "")))
    if name == "kb_search":
        hits = kb_search_impl(str(args["query"]), top_k=int(args.get("top_k", 3)))
        return json.dumps(
            [{"source": h["source"], "text": h["text"][:300]} for h in hits],
            ensure_ascii=False,
        )
    return json.dumps({"error": f"unknown tool {name}"})
```

```bash
python -c "from tools import run_tool; print(run_tool('calc','{\"expr\":\"17*23\"}'))"
```

---

### 1:00–1:40｜Agent 循环（40 分）

**`agent.py`：**

```python
"""最小 Agent：限步 Tool Calling 循环。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

from tools import TOOL_SPECS, run_tool

MAX_STEPS = 6


def run_agent(goal: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是工具型助手。需要事实时调用工具；"
                "不要编造检索或计算结果。完成目标后直接给最终回答。"
            ),
        },
        {"role": "user", "content": goal},
    ]
    for step in range(1, MAX_STEPS + 1):
        print(f"\n=== step {step}/{MAX_STEPS} ===")
        data = chat_completions(messages, temperature=0, tools=TOOL_SPECS)
        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls") or []
        content = (msg.get("content") or "").strip()
        if content:
            print("thought/content:", content[:300])
        if not tool_calls:
            print("final.")
            return content
        # 写回 assistant（含 tool_calls）
        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": tool_calls,
            }
        )
        for tc in tool_calls:
            name = tc["function"]["name"]
            args = tc["function"].get("arguments") or "{}"
            print(f"action: {name}({args})")
            obs = run_tool(name, args)
            print("observation:", obs[:400])
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": obs,
                }
            )
    return "（达到步数上限，请缩小目标或提高 MAX_STEPS）"


if __name__ == "__main__":
    goal = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "先检索笔记里「为什么不能把 API Key 放浏览器」的要点，再计算 17*23，最后附上当前时间，用三句话总结。"
    )
    print(run_agent(goal))
```

```bash
python agent.py
```

**验收：**

- [x] 日志里至少看到 3 种工具被调用（或合理解释跳过）
- [x] 步数触顶时有明确失败信息（可把 MAX_STEPS 临时改 2 验证）

---

### 1:40–2:00｜复盘

1. Observation 必须写回 messages  
2. 限步防止死循环烧钱  
3. 工具参数要用 JSON schema 约束

---

## 验收清单

- [x] ≥3 工具定义且可本地执行
- [x] 真实任务端到端成功
- [x] 能口述循环与停机条件

## 明日预告

Day27：短记忆 / 失败重试 / 高风险人机确认；Ollama 选做。
