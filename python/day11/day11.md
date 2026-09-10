# Day 11 · 结构化输出（JSON + Pydantic）

- **日期**：2026-08-25
- **时段**：20:00–22:20（2 小时 20 分）
- **阶段**：A 路线 · 第 1→2 个月衔接 · Prompt / 结构化输出入门
- **今日主题**：让模型只吐 JSON，用 Pydantic 校验；失败可重试；再挂一个 FastAPI 接口
- **原则**：动手为主；你已有 `json_once.py` / `schemas.py` / `extract.py`，今天是**补齐 + 产品化**，不是重写
- **前置**：Day09/10 的 `common/llm.py`、`.env` 可用
- **状态**：已完成 ✅
- **实际产出**：`json_once.py`、`schemas.py`、`extract.py`、`main.py`

## 今日目标

1. 跑通「Prompt 约束 → 抽 JSON → `model_validate`」整条链路
2. 搞清 `field_validator` vs `model_validator(mode="after")`（跨字段一致性）
3. 校验失败时自动**重试 1 次**（把错误反馈给模型）
4. FastAPI `POST /extract` 返回结构化结果

## 今日不学

Tool Calling、RAG、Next.js、流式 SSE（Day10 已做）、完整 Prompt 工程专题（Few-shot/CoT 留 Day12+）

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 20:00–20:15 | 开工：环境 + 复跑已有脚本 | `json_once.py` 通 |
| 20:15–20:55 | Schema + 跨字段校验 | `schemas.py` 定稿 |
| 20:55–21:00 | 休息 | — |
| 21:00–21:45 | 抽取 + 失败重试 | `extract.py` 定稿 |
| 21:45–21:50 | 休息 | — |
| 21:50–22:15 | FastAPI `/extract` | `main.py` + curl 通 |
| 22:15–22:20 | 复盘 | 对照 TS 类型校验 |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day11
# pydantic / fastapi 若已装可跳过
uv pip install pydantic fastapi uvicorn httpx python-dotenv
```

复用课程根 `.env`（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。

---

## 详细安排

### 20:00–20:15｜开工（15 分）

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('key?', bool(os.getenv('LLM_API_KEY')))"
cd day11
python json_once.py
```

**对照前端：** Prompt 里写「只输出 JSON」≈ 约定 API 响应 shape；但模型可能包 \`\`\`json，所以要有 `extract_json_text` 兜底（你已有）。

**验收：** 打印出 `parsed` 对象和 `usage`；进入 `day11`。

---

### 20:15–20:55｜Schema 定稿（40 分）

把 `schemas.py` 收干净：单字段用 `Field`；`pass_count` 与 `students` 的一致性放到 **model 级**（你已在 `extract.py` 的 `ScoreReportStrict` 里做过，今天统一进 schema）。

建议定稿（可直接覆盖 `schemas.py`）：

```python
from pydantic import BaseModel, Field, model_validator


class StudentScore(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


class ScoreReport(BaseModel):
    summary: str = Field(min_length=1)
    students: list[StudentScore] = Field(min_length=1)
    pass_count: int = Field(ge=0)

    @model_validator(mode="after")
    def pass_count_matches_students(self):
        expected = sum(1 for s in self.students if s.score >= 60)
        if self.pass_count != expected:
            raise ValueError(
                f"pass_count={self.pass_count} 与实际及格人数 {expected} 不一致"
            )
        return self


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, description="原始成绩描述文本")
```

本地先不调 LLM，用假数据验证 schema：

```bash
python - <<'PY'
from schemas import ScoreReport
# 应成功
ok = ScoreReport.model_validate({
    "summary": "三人成绩",
    "students": [
        {"name": "Ada", "score": 91},
        {"name": "Bob", "score": 55},
        {"name": "Cara", "score": 88},
    ],
    "pass_count": 2,
})
print("ok", ok.pass_count)

# 应失败
try:
    ScoreReport.model_validate({
        "summary": "错",
        "students": [{"name": "Ada", "score": 91}],
        "pass_count": 0,
    })
except Exception as e:
    print("expected fail:", e)
PY
```

**刻意记：**

| | 时机 | 适合 |
|--|--|--|
| `Field(ge=0)` | 单字段 | 范围、长度 |
| `model_validator(after)` | 整对象建好后 | `pass_count` vs `students` |

**验收：** 正确样例通过；`pass_count` 故意写错会报错。

---

### 21:00–21:45｜抽取 + 重试（45 分）

把 `extract.py` 改成：校验失败 → 把错误信息塞回对话再要一次 JSON（最多 2 次尝试）。`ScoreReportStrict` 可删掉，直接用统一的 `ScoreReport`。

核心草稿：

```python
import json
import re
import sys
from pathlib import Path

from pydantic import ValidationError
from schemas import ScoreReport

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = """你是数据抽取助手。
规则：
1. 只输出一个 JSON 对象，不要 Markdown，不要代码块，不要解释。
2. 字段必须且只能是：
   - summary: string
   - students: array，每项 {"name": string, "score": number}
   - pass_count: number（score>=60 的人数，必须与 students 一致）
3. 不要编造文本中未出现的学生。
"""


def extract_json_text(raw: str) -> str:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        return fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def extract_score_report(text: str, max_attempts: int = 2) -> ScoreReport:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        data = chat_completions(messages, temperature=0)
        raw = data["choices"][0]["message"]["content"]
        try:
            obj = json.loads(extract_json_text(raw))
            return ScoreReport.model_validate(obj)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = e
            if attempt >= max_attempts:
                break
            # 把失败原因喂回模型，再要一版
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"输出不符合 schema，请只返回修正后的 JSON。错误：{e}",
            })
    raise RuntimeError(f"结构化失败: {last_err}\n最后原始输出见上轮 assistant") from last_err


if __name__ == "__main__":
    sample = "期末：Ada 91，Bob 55，Cara 88。请抽取。"
    report = extract_score_report(sample)
    print(report.model_dump_json(indent=2, ensure_ascii=False))
```

```bash
python extract.py
```

**对照前端：** 重试 ≈ 前端拿到 422 后把校验信息回传再提交；Agent/评测后面都靠这套「schema + 反馈」。

**验收：** 打印合法 JSON；`pass_count` 与及格人数一致；故意改 SYSTEM 放宽规则时，重试逻辑仍可能救回（可选自测）。

---

### 21:50–22:15｜FastAPI `/extract`（25 分）

新建 `main.py`：

```python
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extract import extract_score_report
from schemas import ExtractIn, ScoreReport

app = FastAPI(title="Day11 Structured Extract")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/extract", response_model=ScoreReport)
def extract(body: ExtractIn):
    try:
        return extract_score_report(body.text)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
```

```bash
uvicorn main:app --reload --port 8011
```

另开终端：

```bash
curl -s -X POST "http://127.0.0.1:8011/extract" \
  -H "Content-Type: application/json" \
  -d '{"text":"期末：Ada 91，Bob 55，Cara 88。请抽取。"}' | python -m json.tool
```

**验收：** HTTP 200；响应含 `summary` / `students` / `pass_count`；空 `text` 被 FastAPI/Pydantic 直接 422。

---

### 22:15–22:20｜复盘（5 分）

自问三句：

1. 为什么「只靠 Prompt」不够，还要 Pydantic？
2. 为什么一致性检查用 `model_validator(after)` 而不是 `field_validator`？
3. 重试时为什么要把 **assistant 原文 + 错误信息** 一起塞回 messages？

---

## 验收清单

- [x] `python json_once.py` 能解析出 JSON
- [x] `schemas.py`：错 `pass_count` 会失败，对的会通过
- [x] `python extract.py` 抽成绩成功（含可选重试）
- [x] `POST /extract` curl 返回结构化结果
- [x] 知道 `field_validator` vs `model_validator` 的分工

## 明日预告

Day 12：Prompt 工程入门（Zero/Few-shot、输出格式约束加强），或在结构化上加「JSON mode / response_format」对照。
