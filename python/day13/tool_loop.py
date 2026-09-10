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
