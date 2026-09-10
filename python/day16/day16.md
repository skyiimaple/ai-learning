# Day 16 · Next.js 接 Score Agent

- **日期**：2026-09-07
- **时段**：16:00–18:00（2 小时）
- **课程根（计划）**：`~/code/ai-learning/python`
- **代码根（Next）**：`~/code/ai-learning/node/day16-help`
- **阶段**：A 路线 · 第 2 个月 · Next.js AI 产品化（起步）
- **今日主题**：在 `node/` 起 Next.js App Router，用 `fetch` 调 Day15 `/agent/chat`，页面展示回答 + 工具轨迹
- **原则**：先打通前后端契约；不上 Vercel AI SDK / `useChat`
- **状态**：已完成 ✅

## 今日目标

1. 用 `create-next-app` 在 `ai-learning/node/` 落地可跑项目
2. Chat 页：提问 → Day15 `/agent/chat` → 渲染 `answer` + `steps`
3. 处理 loading / 错误；理解 `NEXT_PUBLIC_` 与 Key 不上前端

## 今日不学

- Vercel AI SDK、`useChat`、Tool UI 官方组件
- SSE Streaming（Day10）接到 Next
- 部署到 Vercel、鉴权、数据库会话

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 16:00–16:15 | 确认 Day15 API + 定目录结构 | Agent 通 |
| 16:15–16:50 | `create-next-app` + 跑通首页 | `node/day16-help` |
| 16:50–16:55 | 休息 | — |
| 16:55–17:40 | Agent Chat 页（fetch + steps） | `/agent` |
| 17:40–17:45 | 休息 | — |
| 17:45–18:00 | 验收 + 复盘 | `NEXT_PUBLIC_` / Key |

---

## 环境

**终端 1 — Day15 Agent：**

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day15
uvicorn main:app --host 127.0.0.1 --port 8015 --reload
```

**终端 2 — Next：**

```bash
cd ~/code/ai-learning/node/day16-help
npm run dev
```

- Agent：`http://127.0.0.1:8015`
- Next：`http://localhost:3000` → `/agent`

---

## 详细安排

### 16:00–16:15｜开工（15 分）

| 路径 | 用途 |
|------|------|
| `python/day16/` | 学习计划归档（本文件） |
| `node/day16-help/` | Next.js 应用代码 |

**验收：**

- [x] `/health` 通；清楚「Next 只调 HTTP，不碰 LLM Key」

---

### 16:15–16:50｜脚手架（35 分）

实际落地目录：`node/day16-help`（因 `node/` 非空，用子目录）。

```bash
cd ~/code/ai-learning/node
npx create-next-app@15 day16-help --typescript --eslint --app --src-dir --import-alias "@/*" --turbopack --no-tailwind
cd day16-help
npm run dev
```

**验收：**

- [x] `npm run dev` 可跑
- [x] `localhost:3000` 可开

---

### 16:50–16:55｜休息（5 分）

---

### 16:55–17:40｜Chat 页对接 Agent（45 分）

**`src/app/page.tsx`：**

```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>ai-learning / node</h1>
      <p>
        <Link href="/agent">打开 Score Agent 页 →</Link>
      </p>
    </main>
  );
}
```

**`src/app/agent/page.tsx`：**

```tsx
"use client";

import { FormEvent, useState } from "react";

type ToolStep = {
  tool: string;
  arguments: Record<string, unknown>;
  result: unknown;
};

type AgentOut = {
  answer: string;
  steps: ToolStep[];
  model: string;
  stopped?: boolean;
};

const AGENT_URL =
  process.env.NEXT_PUBLIC_AGENT_URL ?? "http://127.0.0.1:8015/agent/chat";

export default function AgentPage() {
  const [message, setMessage] = useState(
    "比较一下 Bob 和平均分，谁更高？差多少？",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<AgentOut | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = message.trim();
    if (!text) {
      setError("请先输入问题");
      return;
    }
    setLoading(true);
    setError("");
    setData(null);
    try {
      const resp = await fetch(AGENT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, temperature: 0 }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(
          typeof json.detail === "string"
            ? json.detail
            : `HTTP ${resp.status}`,
        );
      }
      setData(json as AgentOut);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <p
        style={{
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          fontSize: 12,
        }}
      >
        Day16 · Next.js × Score Agent
      </p>
      <h1 style={{ marginTop: 8 }}>问成绩（经 Day15 API）</h1>
      <p style={{ color: "#666" }}>
        浏览器 → Next 页面 → <code>{AGENT_URL}</code>
      </p>

      <form onSubmit={onSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          style={{ width: "100%", padding: 12 }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
          {loading ? "请求中…" : "发送"}
        </button>
      </form>

      {error ? (
        <p style={{ color: "#b91c1c", marginTop: 16 }}>错误：{error}</p>
      ) : null}

      {data ? (
        <section style={{ marginTop: 24 }}>
          <h2>回答</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>{data.answer}</pre>
          <p style={{ color: "#666", fontSize: 14 }}>model: {data.model}</p>

          <h2>工具轨迹</h2>
          {data.steps?.length ? (
            <ul style={{ paddingLeft: 18 }}>
              {data.steps.map((s, i) => (
                <li key={`${s.tool}-${i}`} style={{ marginBottom: 12 }}>
                  <strong>{s.tool}</strong>
                  <pre style={{ fontSize: 12 }}>
                    {JSON.stringify(
                      { arguments: s.arguments, result: s.result },
                      null,
                      2,
                    )}
                  </pre>
                </li>
              ))}
            </ul>
          ) : (
            <p>本次没有调用工具</p>
          )}
        </section>
      ) : null}
    </main>
  );
}
```

可选 `.env.local`（参考 `.env.local.example`）：

```bash
NEXT_PUBLIC_AGENT_URL=http://127.0.0.1:8015/agent/chat
```

**验收：**

- [x] `/agent` 能出 `answer` + `steps`
- [x] loading 时按钮禁用
- [x] Agent 关掉时错误可读

---

### 17:40–17:45｜休息（5 分）

---

### 17:45–18:00｜复盘（15 分）

1. **Key 只在 Python**：Next 前端绝不放 `LLM_API_KEY`
2. **`NEXT_PUBLIC_*`**：会打进浏览器 bundle，只放可公开配置（如 Agent 基址）
3. **契约**：`{ message }` → `{ answer, steps, model }`，换 UI 不改后端

---

## 验收清单（全日）

- [x] `node/day16-help` 可 `npm run dev`
- [x] `/agent` 对接 Day15
- [x] 能口述：为何 Agent URL 用 `NEXT_PUBLIC_`、Key 为何不能进前端

## 实际产出文件

- `node/day16-help/`（Next 项目）
- `node/day16-help/src/app/page.tsx`
- `node/day16-help/src/app/agent/page.tsx`
- `node/day16-help/.env.local.example`

## 明日预告

Vercel AI SDK `useChat` 接 Day10 Streaming，或给 Agent 加多轮 messages。
