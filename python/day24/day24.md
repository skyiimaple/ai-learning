# Day 24 · Query Rewrite + Hybrid + 轻量 Re-rank · 已学习

- **日期**：按实际学习日
- **时段**：2 小时（建议 19:00–21:00）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · 检索优化
- **今日主题**：同一条检索链上可开关 Rewrite / 关键词混合 / LLM 轻量重排；黄金集前后命中率对比
- **原则**：先能量化再谈「感觉更好」；默认复用 Day23 Chroma + `gold.json`
- **状态**：已学习
- **大纲**：`learning-outline.md` Day24

## 环境

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3
LLM_EMBED_MODEL=embedding-3
```

## 今日目标

1. `rewrite.py`：把口语问题改写成适合检索的短查询
2. `hybrid.py`：向量 Top-N ∪ 简单关键词打分，合并去重
3. `rerank.py`：用 LLM 对候选打 0–10 分再排序
4. `eval_compare.py`：baseline vs 优化后命中率对比表

## 今日不学

训练 Cross-Encoder、Elasticsearch、BM25 库、LangChain Retriever

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:15 | 基线跑一遍 gold | 记下 baseline % |
| 0:15–0:50 | Rewrite + Hybrid | 两模块可单独测 |
| 0:50–0:55 | 休息 | — |
| 0:55–1:35 | Re-rank + 对比评测 | eval_compare 表 |
| 1:35–1:40 | 休息 | — |
| 1:40–2:00 | 复盘选默认开关 | 口述取舍 |

---

## 开工

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day24
# 复用 Day23：ln 或复制 gold.json；检索调 day23.retrieve_chroma
cp ../day23/gold.json ./gold.json
```

---

## 详细安排

### 0:00–0:15｜基线（15 分）

```bash
cd ../day23 && python eval_retrieve.py 3
```

把命中率记到本目录 `baseline.txt`（一行即可）。

**验收：** 有数字可对比。

---

### 0:15–0:50｜Rewrite + Hybrid（35 分）

**`rewrite.py`：**

```python
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
```

**`hybrid.py`：**

```python
"""向量候选 + 关键词重叠，简单融合。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from retrieve_chroma import search as vector_search


def _tokens(s: str) -> set[str]:
    # 中英混排：英文词 + 连续中文按字也可，这里用粗粒度
    en = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", s.lower()))
    zh = set(re.findall(r"[\u4e00-\u9fff]{2,}", s))
    return en | zh


def keyword_score(query: str, text: str, source: str) -> float:
    qt = _tokens(query)
    if not qt:
        return 0.0
    blob = f"{source} {text}".lower()
    hit = sum(1 for t in qt if t.lower() in blob or t in blob)
    return hit / len(qt)


def hybrid_search(
    query: str,
    *,
    top_k: int = 3,
    pool: int = 8,
    alpha: float = 0.7,
) -> list[dict]:
    """alpha 越大越信向量分。"""
    vec_hits = vector_search(query, top_k=pool)
    merged: dict[str, dict] = {}
    for h in vec_hits:
        ks = keyword_score(query, h["text"], h["source"])
        score = alpha * float(h["score"]) + (1 - alpha) * ks
        merged[h["id"]] = {**h, "kw": ks, "score": score}
    ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]


if __name__ == "__main__":
    q = "Tool Calling 谁执行函数？"
    for h in hybrid_search(q, top_k=3):
        print(f"{h['score']:.3f} kw={h['kw']:.2f} {h['source']} {h['text'][:50]}...")
```

**验收：**

- [x] `python rewrite.py` 输出更短更术语化
- [x] hybrid 对「文件名/专有名词」问句不比纯向量差

---

### 0:55–1:35｜Re-rank + 对比（40 分）

**`rerank.py`：**

```python
"""对候选列表用 LLM 打分重排（轻量，候选 ≤8）。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions


def rerank(question: str, hits: list[dict], *, enabled: bool = True, top_k: int = 3) -> list[dict]:
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
    scores = {int(x["i"]): float(x["score"]) for x in json.loads(m.group(0) if m else "[]")}
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
```

**`pipeline.py`：**

```python
"""可开关流水线：rewrite → hybrid|vector → rerank。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day23"))

from retrieve_chroma import search as vector_search

from hybrid import hybrid_search
from rewrite import rewrite_query
from rerank import rerank


def retrieve(
    question: str,
    *,
    top_k: int = 3,
    use_rewrite: bool = True,
    use_hybrid: bool = True,
    use_rerank: bool = True,
) -> list[dict]:
    q = rewrite_query(question, enabled=use_rewrite)
    if use_hybrid:
        hits = hybrid_search(q, top_k=8 if use_rerank else top_k)
    else:
        hits = vector_search(q, top_k=8 if use_rerank else top_k)
    return rerank(question, hits, enabled=use_rerank, top_k=top_k)
```

**`eval_compare.py`：**

```python
"""黄金集：baseline vs 全开优化。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "day23"))
from retrieve_chroma import search as baseline_search

from pipeline import retrieve

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
```

```bash
python eval_compare.py
```

**验收：**

- [x] 打印两行命中率
- [x] 能说清哪个开关贵（rerank 调 LLM）

---

### 1:40–2:00｜复盘

1. Rewrite 解决「说法 ≠ 笔记措辞」  
2. Hybrid 救专有名词  
3. Rerank 贵，只对 Top-N 用  
4. 默认建议：rewrite 开、hybrid 开、rerank 可按延迟关

---

## 验收清单

- [x] `eval_compare.py` 有对比数字
- [x] `pipeline.retrieve` 三个开关都能关
- [x] 口述：为何不训练 reranker

## 明日预告

Day25：Langfuse + Chroma 接 UI + README/评测收口（月3 关卡）。
