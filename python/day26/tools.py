"""Agent 工具：定义 schema + 本地执行。"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

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
