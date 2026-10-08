# Day 27 · Memory + 重试 + 人机确认 · 已学习

- **日期**：2026-10-08
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 4 个月 · Agent 稳健性
- **今日主题**：对话短记忆/摘要；工具失败重试；高风险动作需确认；Ollama 选做
- **原则**：一套记忆机制即可；危险工具默认 deny
- **状态**：已学习
- **大纲**：`learning-outline.md` Day27

## 今日目标

1. `memory.py`：滑动窗口 + 超长时摘要压缩
2. `agent_safe.py`：工具失败最多重试 N 次；`delete_file` 类工具需 `confirm=True`
3. （选做）`ollama_smoke.py`：本地模型 vs 云端权衡笔记三段话

## 今日不学

向量长期记忆第二套、多 Agent、完整权限系统

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:40 | Memory | memory 单测 |
| 0:40–0:45 | 休息 | — |
| 0:45–1:25 | 重试 + 确认 | agent_safe |
| 1:25–1:30 | 休息 | — |
| 1:30–2:00 | 选做 Ollama / 复盘 | 笔记 |

---

## 开工

```bash
cd ~/code/ai-learning/python && source .venv/bin/activate && cd day27
# 可选：brew install ollama && ollama pull qwen2.5:3b
```

---

## 详细安排

### 0:00–0:40｜Memory（40 分）

**`memory.py`：**

```python
"""短对话记忆：保留最近 K 轮；过长则摘要。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions


def compress_if_needed(messages: list[dict], *, max_messages: int = 12) -> list[dict]:
    """保留 system；其余超长则摘要成一条 system 旁白。"""
    if len(messages) <= max_messages:
        return messages
    system = [m for m in messages if m.get("role") == "system"][:1]
    rest = [m for m in messages if m.get("role") != "system"]
    blob = "\n".join(f"{m.get('role')}: {str(m.get('content'))[:200]}" for m in rest[:-6])
    data = chat_completions(
        [
            {
                "role": "system",
                "content": "把对话历史压缩成不超过 120 字的中文要点，保留用户目标与已确认事实。",
            },
            {"role": "user", "content": blob},
        ],
        temperature=0,
    )
    summary = (data["choices"][0]["message"].get("content") or "").strip()
    return system + [
        {"role": "system", "content": f"历史摘要：{summary}"},
        *rest[-6:],
    ]
```

**验收：** 塞 20 条假消息后长度下降且摘要存在。

---

### 0:45–1:25｜重试 + 确认（40 分）

在 Day26 基础上扩展。

**`tools_safe.py`（节选）：**

```python
"""含高风险工具；执行层做确认与重试。"""
from __future__ import annotations

import json
import time
from pathlib import Path

RISKY = {"delete_file"}


def delete_file(path: str, *, confirm: bool = False) -> str:
    p = Path(path)
    if not confirm:
        return json.dumps({"status": "need_confirm", "path": str(p)})
    if not p.exists():
        return json.dumps({"error": "not found"})
    # 演示：只允许删 day27/tmp_playground 下文件
    playground = Path(__file__).with_name("tmp_playground").resolve()
    rp = p.resolve()
    if playground not in rp.parents and rp != playground:
        return json.dumps({"error": "path not allowed"})
    rp.unlink()
    return json.dumps({"deleted": str(rp)})


def run_tool_with_retry(name: str, arguments: dict, *, retries: int = 2) -> str:
    last = ""
    for i in range(retries + 1):
        if name == "delete_file":
            last = delete_file(
                str(arguments.get("path", "")),
                confirm=bool(arguments.get("confirm", False)),
            )
        else:
            # 复用 day26.run_tool
            from tools_bridge import run_tool

            last = run_tool(name, arguments)
        err = "error" in last or "need_confirm" in last
        if not err or "need_confirm" in last:
            return last
        time.sleep(0.3 * (i + 1))
    return last
```

**`tools_bridge.py`：** `from` day26 `run_tool` / 或把 day26 tools 复制过来并追加 `delete_file` 的 TOOL_SPECS。

**CLI 确认流：**

```python
# agent 检测到 need_confirm → print 询问 → input yes → 再次 call confirm=True
```

**验收：**

- [x] 无 confirm 不删文件
- [x] 人为制造 calc 失败（非法字符）可见重试日志
- [x] playground 外路径拒绝

---

### 1:30–2:00｜Ollama 选做 / 复盘

**`ollama_smoke.py`：**

```python
"""可选：本地 OpenAI 兼容端。"""
import httpx

r = httpx.post(
    "http://127.0.0.1:11434/v1/chat/completions",
    json={
        "model": "qwen2.5:3b",
        "messages": [{"role": "user", "content": "用一句话解释 Tool Calling"}],
    },
    timeout=120.0,
)
print(r.json()["choices"][0]["message"]["content"])
```

笔记写清：延迟、质量、隐私、是否适合当 Agent 主模型。

---

## 验收清单

- [x] memory 压缩可演示
- [x] 高风险工具确认流通
- [x] 失败重试可演示
- [x] （选）Ollama 三段对比笔记

## 明日预告

Day28：毕业项目选题锁定 + 目录/API/空 UI 骨架。
