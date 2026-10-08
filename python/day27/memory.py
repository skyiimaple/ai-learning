"""短对话记忆：保留最近 K 轮；过长则摘要。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions


def compress_if_needed(messages: list[dict], *, max_messages: int = 12) -> list[dict]:
    """保留 system；其余超长则摘要成一条 system 旁白。"""
    if len(messages) <= max_messages:
        return messages
    system = [m for m in messages if m.get("role") == "system"][:1]
    rest = [m for m in messages if m.get("role") != "system"]
    blob = "\n".join(
        f"{m.get('role')}: {str(m.get('content'))[:200]}" for m in rest[:-6]
    )
    data = chat_completions(
        [
            {
                "role": "system",
                "content": "把对话历史压缩成不超过 120 字的中文要点，保留用户目标与已确认事实。",
            },
            {"role": "user", "content": blob},
        ],
        temperature=0,
    )
    summary = (data["choices"][0]["message"].get("content") or "").strip()
    return system + [
        {"role": "system", "content": f"历史摘要：{summary}"},
        *rest[-6:],
    ]
