"""最小 Agent：限步 Tool Calling 循环。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import TOOL_SPECS, run_tool

from common.llm import chat_completions

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
