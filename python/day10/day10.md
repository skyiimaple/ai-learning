# Day 10 · LLM Streaming（SSE）

- **日期**：2026-08-12
- **时段**：15:00–18:00（3 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 1 个月 · 第 4 周
- **今日主题**：上游 `stream=true`，用 FastAPI `StreamingResponse` 把字流式推给客户端
- **原则**：在 Day09 的 `/chat` 旁加 `/chat/stream`；装包用 `uv pip`；代码均为完整可跑文件
- **状态**：已完成 ✅

## 今日目标

1. 脚本端能边收边打印模型输出的 delta
2. FastAPI 提供 `POST /chat/stream`（SSE：`text/event-stream`）
3. 用 `curl` 或小 HTML 页验证「逐字出现」
4. 把流式调用抽进 `common/llm.py`，与非流式并存

## 今日不学

Next.js / Vercel AI SDK、Tool Calling、RAG、鉴权

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:00–15:15 | 开工：复跑 Day09 `/chat` | 确认 Key 与非流式仍通 |
| 15:15–16:00 | 上游 stream 脚本 | `stream_once.py` |
| 16:00–16:05 | 休息 | — |
| 16:05–16:55 | FastAPI SSE 接口 | `main.py` 的 `/chat/stream` |
| 16:55–17:00 | 休息 | — |
| 17:00–17:40 | 客户端验证 | `curl` + `static/index.html` |
| 17:40–17:45 | 休息 | — |
| 17:45–17:55 | 抽到 `common/llm.py` | `chat_completions_stream` |
| 17:55–18:00 | 复盘 | 对照 fetch ReadableStream |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
mkdir -p day10/static && cd day10
uv pip install httpx python-dotenv fastapi uvicorn
```

复用课程根 `.env`。

---

## 详细安排

### 15:00–15:15｜开工（15 分）

```bash
cd ~/code/ai-learning/python/day09
source ../.venv/bin/activate
uvicorn main:app --port 8000 &
sleep 1
curl -s -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"ping，回一个字：好"}]}'
kill %1 2>/dev/null
cd ../day10
```

**验收：** Day09 非流式仍通；进入 `day10`。

---

### 15:15–16:00｜上游流式脚本（45 分）

完整文件 `stream_once.py`：

```python
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import get_llm_config


def stream_print(user_text: str) -> None:
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": user_text}],
        "temperature": 0.7,
        "stream": True,
    }

    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if data == "[DONE]":
                        print()
                        break
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta") or {}
                    piece = delta.get("content") or ""
                    if piece:
                        print(piece, end="", flush=True)


if __name__ == "__main__":
    stream_print("用三句话介绍 Python，语速感要像在打字")
```

```bash
python stream_once.py
```

**刻意记：**

- 流式：多行 `data:`；正文在 `choices[0].delta.content`
- 结束标记：`data: [DONE]`
- 用 `httpx` 的 `client.stream` + `iter_lines`

**验收：**

- [x] 终端里字陆续出现
- [x] 能解释 `[DONE]`

---

### 16:00–16:05｜休息（5 分）

---

### 16:05–16:55｜FastAPI SSE（50 分）

#### `schemas.py`

```python
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatIn(BaseModel):
    messages: list[Message] = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)
```

#### `main.py`

```python
import json
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import get_llm_config, chat_completions_stream
from schemas import ChatIn

app = FastAPI(title="Day10 Chat Streaming API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event_stream(messages: list[dict], temperature: float):
    try:
        for piece in chat_completions_stream(messages, temperature):
            yield f"data: {json.dumps({'content': piece}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except httpx.HTTPStatusError as e:
        err = {"error": str(e)}
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        err = {"error": f"stream failed: {e}"}
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/chat/stream")
def chat_stream(body: ChatIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        sse_event_stream(messages, body.temperature),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


static_dir = Path(__file__).with_name("static")
static_dir.mkdir(exist_ok=True)
app.mount("/demo", StaticFiles(directory=static_dir, html=True), name="demo")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

```bash
uvicorn main:app --reload --port 8000
```

**验收：**

- [x] 服务能启动；`/health` 通

---

### 16:55–17:00｜休息（5 分）

---

### 17:00–17:40｜客户端验证（40 分）

#### curl

```bash
curl -N -X POST "http://127.0.0.1:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"数到5，每个数字单独一行"}]}'
```

#### `static/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>Day10 Stream Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; }
    #out { white-space: pre-wrap; border: 1px solid #ddd; padding: 12px; min-height: 120px; }
    button { margin-top: 8px; }
  </style>
</head>
<body>
  <h1>Day10 · SSE Chat</h1>
  <textarea id="input" rows="3" style="width:100%">用两句话介绍 FastAPI</textarea>
  <br />
  <button id="btn">发送（流式）</button>
  <h3>输出</h3>
  <div id="out"></div>
  <script>
    const out = document.getElementById("out");
    const btn = document.getElementById("btn");
    const input = document.getElementById("input");

    btn.onclick = async () => {
      out.textContent = "";
      btn.disabled = true;
      try {
        const resp = await fetch("http://127.0.0.1:8000/chat/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: [{ role: "user", content: input.value }],
            temperature: 0.7,
          }),
        });
        if (!resp.ok) {
          out.textContent = "HTTP " + resp.status;
          return;
        }
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";
          for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith("data:")) continue;
            const data = line.slice(5).trim();
            if (data === "[DONE]") continue;
            try {
              const obj = JSON.parse(data);
              if (obj.error) {
                out.textContent += "\n[error] " + obj.error;
              } else if (obj.content) {
                out.textContent += obj.content;
              }
            } catch (e) {
              out.textContent += data;
            }
          }
        }
      } catch (e) {
        out.textContent = String(e);
      } finally {
        btn.disabled = false;
      }
    };
  </script>
</body>
</html>
```

浏览器：`http://127.0.0.1:8000/demo/`

**验收：**

- [x] curl 能刷出 `data: ...`
- [x] 页面文字陆续出现

---

### 17:40–17:55｜抽到 `common/llm.py` + 休息

在 `chat_completions` 后追加：

```python
def chat_completions_stream(messages: list[dict], temperature: float = 0.7):
    """生成器：yield 文本片段 str。"""
    import json

    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta") or {}
                piece = delta.get("content") or ""
                if piece:
                    yield piece
```

**验收：**

- [x] `common/llm.py` 同时有非流式与流式

---

### 17:55–18:00｜复盘

1. `stream=true` → 多行 `data:`；正文在 `delta.content`
2. SSE ≈ 服务端持续 `data: ...\n\n`
3. 浏览器用 `fetch` + `ReadableStream`

---

## 验收清单（全日）

- [x] `stream_once.py` 终端流式打印
- [x] `POST /chat/stream` 返回 `text/event-stream`
- [x] curl `-N` 或 demo 页看到逐字输出
- [x] `common/llm.py` 有 `chat_completions_stream`

## 实际产出文件

- `stream_once.py`
- `schemas.py`
- `main.py`
- `static/index.html`
- `../common/llm.py`（新增流式生成器）

## 明日预告

前端侧用 Next.js / 简单页面正经接 Streaming；或 Prompt 结构化输出（JSON mode）二选一。
