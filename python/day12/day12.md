# Day 12 · Prompt 工程入门（Zero / Few-shot + 格式约束）

- **日期**：2026-08-25
- **时段**：20:00–22:20（2 小时 20 分；此后未指定时段默认「当前时刻起 2 小时」）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 2 个月 · Prompt Engineering
- **今日主题**：对比 Zero-shot / Few-shot；加强输出格式；可选对照 `response_format`（JSON mode）
- **原则**：复用 `common.llm`；装包用 `uv pip`；代码给完整可跑文件
- **状态**：已完成 ✅

## 今日目标

1. 同一任务分别用 Zero-shot、Few-shot，能说出差异
2. 会写带角色边界 + 输出格式的 System Prompt
3. （加练）`response_format: json_object` 对照 Day11 纯 Prompt 抽 JSON

## 今日不学

Tool Calling、RAG、Next.js Chat 页、微调

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 20:00–20:15 | 开工：复跑 Day11 extract | 确认抽取仍通 |
| 20:15–21:00 | Zero-shot vs Few-shot 对照 | `prompt_compare.py` |
| 21:00–21:05 | 休息 | — |
| 21:05–21:50 | System：角色边界 + 格式约束 | `prompt_guard.py` |
| 21:50–21:55 | 休息 | — |
| 21:55–22:10 | 加练：JSON mode | `json_mode.py` |
| 22:10–22:20 | 复盘 | Prompt 原则笔记 |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
mkdir -p day12 && cd day12
uv pip install httpx python-dotenv
```

---

## 详细安排

### 20:00–20:15｜开工（15 分）

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day11
python extract.py
cd ../day12
```

**验收：** Day11 抽取仍通；进入 `day12`。

---

### 20:15–21:00｜Zero-shot vs Few-shot（45 分）

完整文件 `prompt_compare.py`：

```python
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

COMPLAINT = "我上周买的耳机左耳没声，已经找过两次客服了，非常生气，要退货。"


def ask(messages: list[dict], label: str) -> None:
    data = chat_completions(messages, temperature=0)
    raw = data["choices"][0]["message"]["content"]
    print(f"\n===== {label} =====")
    print(raw)
    print("usage:", data.get("usage"))


def zero_shot() -> None:
    ask(
        [
            {
                "role": "system",
                "content": (
                    "把用户投诉整理成 JSON，字段："
                    "category, urgency(low|mid|high), summary, need_refund(boolean)。"
                    "只输出 JSON。"
                ),
            },
            {"role": "user", "content": COMPLAINT},
        ],
        "Zero-shot",
    )


def few_shot() -> None:
    ask(
        [
            {
                "role": "system",
                "content": (
                    "把用户投诉整理成 JSON，字段："
                    "category, urgency(low|mid|high), summary, need_refund(boolean)。"
                    "只输出 JSON。参考示例学习分类口径。"
                ),
            },
            {
                "role": "user",
                "content": "外卖迟到 40 分钟，餐冷了，要赔偿。",
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "category": "delivery_delay",
                        "urgency": "mid",
                        "summary": "外卖严重迟到导致餐品变冷，用户要求赔偿",
                        "need_refund": False,
                    },
                    ensure_ascii=False,
                ),
            },
            {
                "role": "user",
                "content": "支付了两次钱，订单却显示失败，请尽快退款。",
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "category": "payment",
                        "urgency": "high",
                        "summary": "重复扣款且订单失败，用户要求退款",
                        "need_refund": True,
                    },
                    ensure_ascii=False,
                ),
            },
            {"role": "user", "content": COMPLAINT},
        ],
        "Few-shot",
    )


if __name__ == "__main__":
    zero_shot()
    few_shot()
```

```bash
python prompt_compare.py
```

**对照：**

| | Zero-shot | Few-shot |
|--|-----------|----------|
| 输入 | 只给规则 | 规则 + 1～3 个完整例子 |
| 适合 | 任务简单、格式短 | 分类口径、边界案例要统一 |
| 代价 | 省 token | 更稳，但 prompt 更长更贵 |

**验收：**

- [x] 两种都能出 JSON
- [x] 能说出 Few-shot 更稳的地方

---

### 21:00–21:05｜休息（5 分）

---

### 21:05–21:50｜角色边界 + 格式约束（45 分）

完整文件 `prompt_guard.py`：

```python
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = """你是「校内成绩问答助手」，不是全能聊天机器人。

【允许】
- 只根据用户消息里明确给出的成绩作答
- 回答是否及格、谁更高、平均分（仅基于已给数据）

【禁止】
- 编造不存在的学生或分数
- 回答与成绩无关的问题（政治、医疗、写代码等）
- 输出 Markdown 代码块

【输出格式】严格 JSON：
{
  "ok": boolean,
  "answer": string,
  "refuse_reason": string | null
}
若问题越权或信息不足：ok=false，并填写 refuse_reason。
"""


def extract_json(raw: str) -> dict:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def ask(user: str) -> None:
    data = chat_completions(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    raw = data["choices"][0]["message"]["content"]
    print("\nQ:", user)
    print("raw:", raw)
    try:
        print("parsed:", json.dumps(extract_json(raw), ensure_ascii=False))
    except Exception as e:
        print("parse failed:", e)


if __name__ == "__main__":
    ask("Alice 80，Bob 95。谁更高？")
    ask("帮我写一段 React useEffect 示例")
    ask("Carol 考得怎么样？")
```

```bash
python prompt_guard.py
```

**验收：**

- [x] 成绩问题合理作答
- [x] 越权问题拒绝
- [x] 未知学生不编造

---

### 21:50–21:55｜休息（5 分）

---

### 21:55–22:10｜加练：JSON mode（15 分）

完整文件 `json_mode.py`：

```python
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import get_llm_config


def chat_json(messages: list[dict]) -> dict:
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "messages": messages,
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    data = chat_json(
        [
            {
                "role": "system",
                "content": (
                    "抽取成绩为 JSON，字段：summary(string), "
                    "students([{name,score}]), pass_count(number)。只输出 JSON 对象。"
                ),
            },
            {
                "role": "user",
                "content": "Alice 80，Bob 95，Frank 59。",
            },
        ]
    )
    raw = data["choices"][0]["message"]["content"]
    print("raw:", raw)
    print("parsed:", json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
    print("usage:", data.get("usage"))
```

```bash
python json_mode.py
```

**对照：**

| 方式 | 优点 | 缺点 |
|------|------|------|
| 纯 Prompt「只输出 JSON」 | 通用 | 偶发 Markdown/废话 |
| `response_format: json_object` | 更易得到合法 JSON | 字段仍靠约定；非所有模型支持 |

**验收：**

- [x] `json_mode.py` 跑通（或不支持时已记录）

---

### 22:10–22:20｜复盘（10 分）

Prompt 原则（示例）：

1. 规则写清「允许 / 禁止 / 输出形状」
2. 口径不稳就加 Few-shot
3. JSON = Prompt 契约 + 解析 + Schema；有 JSON mode 再加一道保险

---

## 验收清单（全日）

- [x] `prompt_compare.py`：Zero / Few-shot 对照完成
- [x] `prompt_guard.py`：越权会拒绝
- [x] （加练）`json_mode.py` 跑通或记录不支持原因
- [x] 能口述 ≥3 条 Prompt 原则

## 实际产出文件

- `prompt_compare.py`
- `prompt_guard.py`
- `json_mode.py`

## 明日预告

Tool Calling / Function Calling 入门；或 Next.js 接 Day10 Streaming（二选一）。
