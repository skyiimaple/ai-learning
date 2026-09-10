# Day 15 · Agent 极简前端页

- **日期**：2026-09-07
- **时段**：15:50–17:50（2 小时）
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 2 个月 · Tool Calling → 产品化过渡
- **今日主题**：给 Day14 `/agent/chat` 做一个本地演示页：提问、看回答、展开工具轨迹
- **原则**：先 HTML + `fetch`；不引入 Next.js / AI SDK；复用 day14 agent
- **状态**：已完成 ✅

## 今日目标

1. `day15` 起一个带静态页的 FastAPI（复用 Day14 `agent` / `schemas`）
2. 页面能发问并展示 `answer` + `steps`
3. 处理 loading / 错误状态（502、空回答）

## 今日不学

- Next.js、Vercel AI SDK、`useChat`
- SSE + Tool Calling 合流
- 登录、历史会话持久化

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:50–16:05 | 复跑 Day14 API + 定 UI 信息架构 | 确认 `/agent/chat` 通 |
| 16:05–16:45 | `main.py` 挂载静态 + 复用 agent | 服务可开 |
| 16:45–16:50 | 休息 | — |
| 16:50–17:35 | `static/index.html` 交互页 | 可点可看 steps |
| 17:35–17:40 | 休息 | — |
| 17:40–17:50 | 验收 + 复盘 | 口述前后端契约 |

---

## 环境

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day15
uvicorn main:app --host 127.0.0.1 --port 8015 --reload
```

浏览器：`http://127.0.0.1:8015/`

---

## 详细安排

### 15:50–16:05｜开工（15 分）

**页面三块：**

1. 输入 + 发送
2. 最终回答 `answer`
3. 工具轨迹 `steps`（tool / arguments / result）

**验收：**

- [x] 清楚：前端只消费 JSON，不自己调 LLM

---

### 16:05–16:45｜FastAPI + 静态挂载（40 分）

**`day15/main.py`：**

```python
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day14"))

from agent import chat_with_tools
from schemas import AgentIn, AgentOut

from common.llm import get_llm_config

app = FastAPI(title="Day15 Score Agent Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"], "day": 15}


@app.post("/agent/chat", response_model=AgentOut)
def agent_chat(body: AgentIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    try:
        out = chat_with_tools(body.message, temperature=body.temperature)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"agent failed: {e}") from e

    if out.get("stopped") and not out.get("answer"):
        raise HTTPException(
            status_code=504,
            detail="超过最大工具步数，未得到最终回答",
        )

    return AgentOut(**out)


static_dir = Path(__file__).with_name("static")
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8015, reload=True)
```

注意：先注册 `/health`、`/agent/chat`，再 `mount` 静态，否则会被静态抢走。

**验收 curl：**

```bash
curl -s http://127.0.0.1:8015/health | python -m json.tool
curl -s http://127.0.0.1:8015/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Frank 考了多少分？","temperature":0}' \
  | python -m json.tool
```

**验收：**

- [x] `/health`、`/agent/chat` 通
- [x] 浏览器打开 `http://127.0.0.1:8015/` 能看到页面

---

### 16:45–16:50｜休息（5 分）

---

### 16:50–17:35｜完整演示页（45 分）

**`day15/static/index.html`：**（完整文件见仓库同路径；要点如下）

- `POST /agent/chat`，body：`{ message, temperature: 0 }`
- 展示 `answer`；遍历 `steps` 显示 tool / args / result
- loading 时禁用按钮；错误时 `status` 可读

试两问：

1. `Frank 考了多少分？`
2. `比较一下 Bob 和平均分，谁更高？差多少？`
3. （加练）`有没有叫 Zack 的同学？`

**验收：**

- [x] 发送后按钮禁用，结束后恢复
- [x] `answer` 正确；`steps` 能看出 tool 名与参数
- [x] 错误态可读

完整 HTML：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Day15 · Score Agent</title>
  <style>
    :root {
      --bg: #f6f3ee;
      --ink: #1c1917;
      --muted: #78716c;
      --line: #e7e5e4;
      --accent: #0f766e;
      --card: #fffcf8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(ellipse 80% 50% at 10% 0%, #d8ebe7 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 100% 100%, #f0e6d8 0%, transparent 50%),
        var(--bg);
    }
    main {
      max-width: 40rem;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 3rem;
    }
    .brand {
      font-size: 0.75rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin: 0 0 0.5rem;
    }
    h1 {
      font-size: clamp(1.75rem, 4vw, 2.25rem);
      font-weight: 600;
      margin: 0 0 0.4rem;
      line-height: 1.2;
    }
    .lead {
      margin: 0 0 1.75rem;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.5;
    }
    label {
      display: block;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 0.4rem;
    }
    textarea {
      width: 100%;
      min-height: 5.5rem;
      padding: 0.85rem 1rem;
      border: 1px solid var(--line);
      border-radius: 0.35rem;
      background: var(--card);
      font: inherit;
      resize: vertical;
    }
    .actions {
      display: flex;
      gap: 0.75rem;
      align-items: center;
      margin-top: 0.75rem;
    }
    button {
      appearance: none;
      border: none;
      background: var(--accent);
      color: #fff;
      padding: 0.65rem 1.25rem;
      border-radius: 0.35rem;
      font: inherit;
      font-size: 0.95rem;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
    .status {
      font-size: 0.85rem;
      color: var(--muted);
    }
    .status.err { color: #b91c1c; }
    section {
      margin-top: 1.75rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--line);
    }
    section h2 {
      font-size: 1rem;
      margin: 0 0 0.65rem;
      letter-spacing: 0.02em;
    }
    #answer {
      white-space: pre-wrap;
      line-height: 1.55;
      min-height: 1.5rem;
    }
    #steps {
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 0.65rem;
    }
    #steps li {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 0.35rem;
      padding: 0.75rem 0.9rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.78rem;
      line-height: 1.45;
    }
    #steps .tool {
      color: var(--accent);
      font-weight: 600;
      margin-bottom: 0.35rem;
      font-family: inherit;
      font-size: 0.85rem;
    }
    .empty { color: var(--muted); font-size: 0.9rem; }
  </style>
</head>
<body>
  <main>
    <p class="brand">Day15 · Score Agent</p>
    <h1>问成绩，看工具怎么走</h1>
    <p class="lead">请求打到本机 /agent/chat；回答下方展开每一步 tool 调用。</p>

    <label for="q">你的问题</label>
    <textarea id="q">比较一下 Bob 和平均分，谁更高？差多少？</textarea>
    <div class="actions">
      <button id="send" type="button">发送</button>
      <span class="status" id="status"></span>
    </div>

    <section>
      <h2>回答</h2>
      <div id="answer" class="empty">尚未提问</div>
    </section>

    <section>
      <h2>工具轨迹</h2>
      <ul id="steps">
        <li class="empty" style="border:none;background:transparent;padding:0">发送后显示 steps</li>
      </ul>
    </section>
  </main>

  <script>
    const q = document.getElementById("q");
    const send = document.getElementById("send");
    const status = document.getElementById("status");
    const answer = document.getElementById("answer");
    const stepsEl = document.getElementById("steps");

    function setStatus(text, isErr) {
      status.textContent = text || "";
      status.classList.toggle("err", !!isErr);
    }

    function renderSteps(steps) {
      stepsEl.innerHTML = "";
      if (!steps || !steps.length) {
        const li = document.createElement("li");
        li.className = "empty";
        li.style.border = "none";
        li.style.background = "transparent";
        li.style.padding = "0";
        li.textContent = "本次没有调用工具";
        stepsEl.appendChild(li);
        return;
      }
      for (const s of steps) {
        const li = document.createElement("li");
        const title = document.createElement("div");
        title.className = "tool";
        title.textContent = s.tool;
        const body = document.createElement("div");
        body.textContent =
          "args: " + JSON.stringify(s.arguments, null, 0) +
          "\nresult: " + JSON.stringify(s.result, null, 0);
        li.appendChild(title);
        li.appendChild(body);
        stepsEl.appendChild(li);
      }
    }

    send.onclick = async () => {
      const message = q.value.trim();
      if (!message) {
        setStatus("请先输入问题", true);
        return;
      }
      send.disabled = true;
      setStatus("请求中…");
      answer.classList.remove("empty");
      answer.textContent = "";
      try {
        const resp = await fetch("/agent/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, temperature: 0 }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
          const detail = data.detail || ("HTTP " + resp.status);
          setStatus(String(detail), true);
          answer.textContent = "";
          answer.classList.add("empty");
          renderSteps([]);
          return;
        }
        answer.textContent = data.answer || "(空回答)";
        renderSteps(data.steps || []);
        setStatus(data.model ? "model: " + data.model : "完成");
      } catch (e) {
        setStatus(String(e), true);
      } finally {
        send.disabled = false;
      }
    };
  </script>
</body>
</html>
```

---

### 17:35–17:40｜休息（5 分）

---

### 17:40–17:50｜复盘（10 分）

1. UI 只展示 `answer` / `steps`，业务真相在工具函数里
2. API 路由注册必须在 `StaticFiles` mount 之前
3. 同域 `fetch("/agent/chat")` 可避开跨域

---

## 验收清单（全日）

- [x] `uvicorn` 在 **8015** 跑通
- [x] 页面两问成功，轨迹可见
- [x] 错误态可读
- [x] 能口述：为何 day15 复用 day14、而不是再抄一份 agent

## 实际产出文件

- `main.py`
- `static/index.html`

## 明日预告

在 `node/` 起 Next.js，接 Day10 Streaming 或本 Agent API（Vercel AI SDK / 自写 fetch 二选一）。
