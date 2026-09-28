"""最小 RAG：检索 + 拼 Prompt + GLM Chat。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retrieve import build_index, search

from common.llm import chat_completions, get_llm_config


def answer(question: str, *, top_k: int = 3) -> None:
    cfg = get_llm_config()
    docs, vectors = build_index()
    hits = search(question, docs, vectors, top_k=top_k)

    context = "\n\n".join(
        f"[{h['source']}#{h['id']}] (score={h['score']:.3f})\n{h['text']}" for h in hits
    )
    messages = [
        {
            "role": "system",
            "content": (
                "你是学习笔记助手。只能根据给定「检索片段」回答；"
                "若片段不足，说不知道。回答末尾列出引用过的 source 文件名。"
            ),
        },
        {
            "role": "user",
            "content": f"检索片段：\n{context}\n\n问题：{question}",
        },
    ]

    print("=== model ===", cfg["model"])
    print("=== hits ===")
    for h in hits:
        print(f"- {h['source']} ({h['score']:.3f})")

    data = chat_completions(messages, temperature=0)
    print("\n=== answer ===")
    print(data["choices"][0]["message"]["content"])
    print("\nusage:", data.get("usage"))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "浏览器为什么不能放 LLM_API_KEY？"
    answer(q)
