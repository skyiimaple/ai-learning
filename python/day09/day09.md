# Day 09 · LLM API 第一课（Chat Completions）

- **日期**：2026-08-05
- **时段**：10:00–15:30（午休 12:00–13:30；净学习约 4 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 1 个月 · 第 4 周起步
- **今日主题**：用 `httpx` 调通 Chat Completions；再包一层 FastAPI（先非流式）
- **原则**：密钥进 `.env`；装包用 `uv pip`；代码给完整可跑文件
- **状态**：已完成 ✅

## 今日目标

1. 配置好 `LLM_API_KEY` / `BASE_URL` / `MODEL`
2. `chat_once.py` 一问一答跑通
3. `chat_multi.py` System + 多轮跑通
4. FastAPI `POST /chat` 跑通
5. （可选）CORS / 上游 502 处理

## 今日不学

SSE Streaming、Tool Calling、RAG、前端 Chat 页

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 10:00–10:15 | 开工 + `.env` + 装依赖 | 环境就绪 |
| 10:15–11:10 | 第一次 Chat Completions | `chat_once.py` |
| 11:10–11:15 | 休息 | — |
| 11:15–12:00 | System + 多轮 | `chat_multi.py` |
| 12:00–13:30 | **午休** | — |
| 13:30–14:15 | 多轮巩固 + usage/成本 | 会看 token |
| 14:15–14:20 | 休息 | — |
| 14:20–15:10 | FastAPI `/chat` | `common/llm.py` + `schemas.py` + `main.py` |
| 15:10–15:15 | 休息 | — |
| 15:15–15:25 | 加练 CORS / 错误处理 | 可选 |
| 15:25–15:30 | 复盘 | — |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day09

# 用 uv，不要裸 pip
uv pip install httpx python-dotenv fastapi uvicorn
```

`.env`（课程根，勿提交）：

```env
LLM_API_KEY=sk-你的密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

```bash
cd ~/code/ai-learning/python
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('key?', bool(os.getenv('LLM_API_KEY'))); print(os.getenv('LLM_MODEL'))"
```

---

## 详细安排

### 10:00–10:15｜开工（15 分）

激活环境、确认 Key。`.gitignore` 含 `.env`。

**验收：** `key? True`；在 `python/day09`。

---

### 10:15–11:10｜`chat_once.py`（55 分）

```python
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent  # python/
sys.path.insert(0, str(ROOT))
from common.llm import get_llm_config

llm_config = get_llm_config()


def chat_once(msg: str) -> str:
    url = f"{llm_config['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {llm_config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": llm_config["model"],
        "messages": [{"role": "user", "content": msg}],
        "temperature": 0.7,
    }
    t0 = time.perf_counter()
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    elapsed = time.perf_counter() - t0
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage") or {}
    print(f"耗时: {elapsed:.2f}s")
    print(f"usage: {usage}")
    return content


if __name__ == "__main__":
    print(chat_once("用一句话介绍你自己"))
```

```bash
python chat_once.py
```

**验收：**

- [x] 打出模型回复
- [x] 能看到 usage / 耗时

---

### 11:10–11:15｜休息

---

### 11:15–12:00｜`chat_multi.py`（45 分）

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = (
    "你是严格的成绩助手。只根据用户提供的分数作答；"
    "不知道就说不知道，不要编造学生。"
)


def complete(messages: list[dict]) -> tuple[str, dict]:
    data = chat_completions(messages, temperature=0.2)
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage") or {}
    return content, usage


def main():
    messages = [{"role": "system", "content": SYSTEM}]
    print("输入空行退出。")
    while True:
        user = input("you> ").strip()
        if not user:
            break
        messages.append({"role": "user", "content": user})
        reply, usage = complete(messages)
        messages.append({"role": "assistant", "content": reply})
        print("bot>", reply)
        print(f"(messages={len(messages)}, usage={usage})")


if __name__ == "__main__":
    main()
```

**验收：**

- [x] 多轮能引用历史
- [x] 知道每次请求带完整 `messages`

---

### 12:00–13:30｜午休

---

### 13:30–14:15｜巩固 + 成本意识（45 分）

观察：`messages` 变长 → `prompt_tokens` 变大；对比不同 `temperature`。

**验收：**

- [x] 能说清「历史越长越贵/越慢」

---

### 14:15–14:20｜休息

---

### 14:20–15:10｜FastAPI `/chat`（50 分）

#### `python/common/llm.py`

```python
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def get_llm_config() -> dict:
    if not LLM_API_KEY:
        raise RuntimeError("缺少环境变量 LLM_API_KEY，请在 .env 里配置")
    return {
        "api_key": LLM_API_KEY,
        "base_url": LLM_BASE_URL,
        "model": LLM_MODEL,
    }


def chat_completions(messages: list[dict], temperature: float = 0.7) -> dict:
    """调用兼容 OpenAI 的 /v1/chat/completions，返回完整 JSON。"""
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
                "temperature": temperature,
            },
        )
        r.raise_for_status()
        return r.json()
```

#### `day09/schemas.py`

```python
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatIn(BaseModel):
    messages: list[Message] = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatOut(BaseModel):
    content: str
    model: str
    usage: dict | None = None
```

#### `day09/main.py`

```python
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions, get_llm_config
from schemas import ChatIn, ChatOut

app = FastAPI(title="Day09 Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn):
    try:
        data = chat_completions(
            [m.model_dump() for m in body.messages],
            temperature=body.temperature,
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"上游模型错误: {e.response.status_code} {e.response.text[:200]}",
        ) from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"请求上游失败: {e}") from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    cfg = get_llm_config()
    return ChatOut(
        content=data["choices"][0]["message"]["content"],
        model=data.get("model", cfg["model"]),
        usage=data.get("usage"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

```bash
cd ~/code/ai-learning/python/day09
source ../.venv/bin/activate
uvicorn main:app --reload --port 8000

curl -s -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"用一句话介绍你自己"}]}'
```

**验收：**

- [x] `/chat` 返回 `content`
- [x] 上游错误为 502（可读 `detail`）
- [x] 已加 CORS（`localhost:3000`）

---

### 15:10–15:25｜休息 + 加练

可选：错 Key 测 502；`/docs` 试多轮 messages。

---

### 15:25–15:30｜复盘

1. Chat API ≈ POST JSON → `choices[0].message.content`
2. 多轮靠客户端维护 `messages`
3. Key 只放 `.env` / 服务端

---

## 验收清单（全日）

- [x] `.env` 配置好且未进 git
- [x] `chat_once.py` 通
- [x] `chat_multi.py` 能多轮
- [x] `POST /chat` 通
- [x] 会看 `usage` / 耗时
- [x] 装包用 `uv pip`

## 实际产出文件

- `chat_once.py`
- `chat_multi.py`
- `schemas.py`（及 `schema.py` 若有备份）
- `main.py`
- `../common/llm.py`（公共封装）

## 明日预告

**Streaming（SSE）**：上游 `stream=true`，FastAPI `StreamingResponse` 往前端推字。
