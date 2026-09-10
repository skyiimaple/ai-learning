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
