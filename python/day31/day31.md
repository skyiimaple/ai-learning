# Day 31 · 成本与延迟 · 未学习

- **日期**：按实际学习日
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 5 个月 · 工程化
- **今日主题**：常见问缓存；context 裁剪；简单题小模型路由；token/延迟表
- **原则**：改毕业项目或知识库其一即可，数字要可复现
- **状态**：未学习
- **大纲**：`learning-outline.md` Day31

## 今日目标

1. `cache.py`：相同 question 命中缓存（磁盘 JSON）
2. `trim.py`：检索片段总长上限（字符或估算 token）
3. `router.py`：简单规则走小模型 / 复杂走主模型（可用 env 两个 model 名）
4. `COST.md`：优化前后 latency 与粗算 token 对比表

## 今日不学

自建 API 网关、Redis 集群、精确 tokenizer 对齐计费

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:20 | 量基线 | 3 问延迟 |
| 0:20–1:00 | 缓存 + 裁剪 | 模块 |
| 1:00–1:05 | 休息 | — |
| 1:05–1:40 | 路由 + 接主路径 | 可开关 |
| 1:40–2:00 | COST 表 | 文档 |

---

## 关键代码骨架

**`cache.py`：**

```python
import hashlib, json, time
from pathlib import Path

CACHE = Path(__file__).with_name(".cache")
CACHE.mkdir(exist_ok=True)


def key_of(question: str) -> str:
    return hashlib.sha256(question.strip().encode()).hexdigest()[:16]


def get(question: str):
    p = CACHE / f"{key_of(question)}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def set_(question: str, value: dict) -> None:
    value = {**value, "cached_at": time.time()}
    (CACHE / f"{key_of(question)}.json").write_text(
        json.dumps(value, ensure_ascii=False), encoding="utf-8"
    )
```

**`trim.py`：** 按 `max_chars` 截断 hits 文本，优先保留高分。

**`router.py`：**

```python
import os
import re

SIMPLE = re.compile(r"^(什么是|定义|who|what)\b", re.I)

def pick_model(question: str) -> str:
    if len(question) < 40 and SIMPLE.search(question):
        return os.getenv("LLM_MODEL_SMALL", os.getenv("LLM_MODEL", "glm-5.3"))
    return os.getenv("LLM_MODEL", "glm-5.3")
```

把 `chat_completions` 调用处传入 `model`（若 `common.llm` 尚不支持，今日加可选 `model=` 参数）。

**`COST.md` 表：**

| 场景 | 缓存 | 裁剪 | 模型 | latency_ms | 估算 prompt_chars |
|------|------|------|------|------------|-------------------|
| Q1 冷 | 关 | 关 | 主 |  |  |
| Q1 热 | 开 | 关 | — |  | 0 |
| Q2 | 关 | 开 | 主 |  |  |
| Q3 简单 | 关 | 开 | 小 |  |  |

---

## 验收清单

- [ ] 同一问题第二次明显更快（缓存）
- [ ] 裁剪后仍能答对至少 1 道金牌问
- [ ] COST.md 有数字

## 明日预告

Day32：密钥与注入防护、工具权限、Docker Compose 一键起。
