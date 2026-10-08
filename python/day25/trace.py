"""最小 tracing：记录一次 RAG ask。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

LOG = Path(__file__).with_name("traces.jsonl")


def _langfuse():
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    if not pk or not sk:
        return None
    try:
        from langfuse import Langfuse

        return Langfuse(
            public_key=pk,
            secret_key=sk,
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    except Exception:
        return None


def trace_ask(
    *,
    question: str,
    answer: str,
    hits: list[dict],
    model: str,
    latency_ms: float,
    meta: dict[str, Any] | None = None,
) -> None:
    payload = {
        "ts": time.time(),
        "question": question,
        "answer": answer[:2000],
        "sources": [h.get("source") for h in hits],
        "model": model,
        "latency_ms": latency_ms,
        "meta": meta or {},
    }
    lf = _langfuse()
    if lf is not None:
        # langfuse 4.x 没有 client.trace()；用 observation 记一条 span + generation
        with lf.start_as_current_observation(
            name="rag_ask",
            as_type="span",
            input={"question": question},
        ) as span:
            with span.start_as_current_observation(
                name="answer",
                as_type="generation",
                model=model,
                input=question,
            ) as generation:
                generation.update(
                    output=answer,
                    metadata={
                        "sources": payload["sources"],
                        "latency_ms": latency_ms,
                    },
                )
        lf.flush()
        return
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
