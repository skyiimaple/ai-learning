"""落盘索引 + glm-5.3 回答。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retrieve import search

from common.llm import chat_completions, get_llm_config


def ask(question: str, docs: list[dict], vectors, *, top_k: int = 3) -> dict:
    cfg = get_llm_config()
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
    data = chat_completions(messages, temperature=0)
    answer = (data["choices"][0]["message"].get("content") or "").strip()
    return {
        "answer": answer,
        "hits": [
            {
                "id": h["id"],
                "source": h["source"],
                "text": h["text"],
                "score": h["score"],
            }
            for h in hits
        ],
        "model": cfg["model"],
    }
