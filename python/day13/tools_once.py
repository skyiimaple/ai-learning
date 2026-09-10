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
