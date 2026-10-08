"""检索评测：Top-K 是否命中期望 source。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from retrieve_chroma import search

GOLD = Path(__file__).with_name("gold.json")


def main(top_k: int = 3) -> None:
    cases = json.loads(GOLD.read_text(encoding="utf-8"))
    hit = 0
    for case in cases:
        results = search(case["question"], top_k=top_k)
        got = {h["source"] for h in results}
        expect = set(case["expect_sources"])
        ok = bool(got & expect)
        hit += int(ok)
        mark = "OK" if ok else "MISS"
        print(f"[{mark}] {case['id']} expect={expect} got={got}")
        if not ok:
            print("   Q:", case["question"])
    total = len(cases)
    rate = hit / total if total else 0.0
    print(f"\n命中率: {hit}/{total} = {rate:.0%} (top_k={top_k})")


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(top_k=k)
