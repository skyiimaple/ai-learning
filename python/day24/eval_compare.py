"""黄金集：baseline vs 全开优化。"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "day23"))
from pipeline import retrieve
from retrieve_chroma import search as baseline_search

GOLD = Path(__file__).with_name("gold.json")


def hit_rate(fn, cases, top_k=3) -> float:
    hit = 0
    for c in cases:
        got = {h["source"] for h in fn(c["question"], top_k=top_k)}
        hit += int(bool(got & set(c["expect_sources"])))
    return hit / len(cases) if cases else 0.0


def main() -> None:
    cases = json.loads(GOLD.read_text(encoding="utf-8"))
    b = hit_rate(lambda q, top_k: baseline_search(q, top_k=top_k), cases)
    o = hit_rate(
        lambda q, top_k: retrieve(
            q, top_k=top_k, use_rewrite=True, use_hybrid=True, use_rerank=True
        ),
        cases,
    )
    print(f"baseline : {b:.0%}")
    print(f"optimized: {o:.0%}")
    print("（若优化更差：关 rerank 或降 alpha 再测）")


if __name__ == "__main__":
    main()
