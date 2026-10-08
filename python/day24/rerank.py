"""对候选列表用 LLM 打分重排（轻量，候选 ≤8）。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions


def rerank(
    question: str, hits: list[dict], *, enabled: bool = True, top_k: int = 3
) -> list[dict]:
    if not enabled or not hits:
        return hits[:top_k]
    lines = []
    for i, h in enumerate(hits):
        lines.append(f"[{i}] source={h['source']}\n{h['text'][:400]}")
    data = chat_completions(
        [
            {
                "role": "system",
                "content": (
                    "根据问题给每个候选相关性打分 0-10。"
                    '只输出 JSON 数组，如 [{"i":0,"score":8},...]，不要其它文字。'
                ),
            },
            {
                "role": "user",
                "content": f"问题：{question}\n\n候选：\n" + "\n\n".join(lines),
            },
        ],
        temperature=0,
    )
    raw = data["choices"][0]["message"].get("content") or "[]"
    m = re.search(r"\[.*\]", raw, re.S)
    scores = {
        int(x["i"]): float(x["score"]) for x in json.loads(m.group(0) if m else "[]")
    }
    scored = []
    for i, h in enumerate(hits):
        scored.append({**h, "rerank": scores.get(i, 0.0)})
    scored.sort(key=lambda x: x["rerank"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "day23"))
    from retrieve_chroma import search

    q = "浏览器为什么不能放 LLM_API_KEY？"
    base = search(q, top_k=5)
    for h in rerank(q, base, top_k=3):
        print(h["rerank"], h["source"])
