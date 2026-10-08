"""用 LLM 把问题改写成检索友好的短查询（可关）。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions


def rewrite_query(question: str, *, enabled: bool = True) -> str:
    if not enabled:
        return question
    data = chat_completions(
        [
            {
                "role": "system",
                "content": (
                    "你把用户问题改写成适合在技术笔记里做向量/关键词检索的短查询。"
                    "只输出改写后的查询，不要解释。保留关键术语与文件名线索。"
                ),
            },
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return (data["choices"][0]["message"].get("content") or question).strip()


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "浏览器里为啥不能塞钥匙？"
    print("raw:", q)
    print("rw :", rewrite_query(q))
