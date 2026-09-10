# Day 17 · Vercel AI SDK · useChat 流式对话

- **日期**：2026-09-07
- **时段**：16:20–18:20（2 小时）
- **计划目录**：`~/code/ai-learning/python/day17`
- **代码目录**：`~/code/ai-learning/node/day16-help`
- **阶段**：A 路线 · 第 2 个月 · Next.js AI 产品化
- **今日主题**：`useChat` + Route Handler `streamText`，对接 DeepSeek，多轮流式对话
- **原则**：Key 只进服务端 `.env.local`（绝不 `NEXT_PUBLIC_`）
- **状态**：已完成 ✅

## 今日目标

1. 安装 `ai` + `@ai-sdk/openai`，写通 `POST /api/chat`
2. 用 `useChat` 做多轮流式页（`/stream`）
3. 能口述 Day16 vs Day17 数据流差异

## 今日不学

- Tool Calling + AI SDK 合流
- 改 Day10 SSE 兼容 AI SDK
- 部署 Vercel

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 16:20–16:35 | 概念：AI SDK 分层 | 脑中数据流 |
| 16:35–17:15 | 装包 + `/api/chat` + env | 流式接口 |
| 17:15–17:20 | 休息 | — |
| 17:20–18:00 | `useChat` 页面 `/stream` | 可多轮聊天 |
| 18:00–18:05 | 休息 | — |
| 18:05–18:20 | 验收 + 复盘 | 安全边界 |

---

## 环境

```bash
cd ~/code/ai-learning/node/day16-help
npm install ai@4.3.16 @ai-sdk/openai@1.3.22
cp .env.local.example .env.local   # 填入真实 Key
npm run dev
```

打开：`http://localhost:3000/stream`

---

## 详细安排

### 16:20–16:35｜概念（15 分）

| | Day16 | Day17 |
|--|--------|--------|
| 谁持有 Key | Python `.env` | Next **服务端** `.env.local` |
| 浏览器打谁 | `8015/agent/chat` | 同源 `/api/chat` |
| 响应形态 | 一次 JSON | **流式** token |
| 前端钩子 | 手写 `fetch` | `useChat` |

```
浏览器 useChat
  → POST /api/chat   （Route Handler，可读无 NEXT_PUBLIC 的密钥）
      → DeepSeek /v1/chat/completions stream
  ← AI SDK 数据流
  → 界面逐字更新
```

**验收：**

- [x] 能说清「为何 Key 可进 Next，却不能进前端组件」

---

### 16:35–17:15｜API Route（40 分）

**`.env.local`**（勿提交；参考 `.env.local.example`）：

```bash
LLM_API_KEY=sk-你的密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

**`src/app/api/chat/route.ts`：**

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { streamText } from "ai";

export const runtime = "nodejs";
export const maxDuration = 60;

const provider = createOpenAI({
  apiKey: process.env.LLM_API_KEY,
  baseURL: `${(process.env.LLM_BASE_URL ?? "https://api.deepseek.com").replace(/\/$/, "")}/v1`,
});

export async function POST(req: Request) {
  if (!process.env.LLM_API_KEY) {
    return new Response(JSON.stringify({ error: "缺少 LLM_API_KEY" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const body = await req.json();
  const messages = body.messages ?? [];

  const result = streamText({
    model: provider(process.env.LLM_MODEL ?? "deepseek-chat"),
    messages,
    temperature: 0.7,
  });

  return result.toDataStreamResponse();
}
```

**验收：**

- [x] 依赖已装
- [x] `.env.local` 无 `NEXT_PUBLIC_LLM_*`

---

### 17:15–17:20｜休息（5 分）

---

### 17:20–18:00｜useChat 页面（40 分）

**`src/app/stream/page.tsx`：**

```tsx
"use client";

import { useChat } from "ai/react";

export default function StreamChatPage() {
  const { messages, input, setInput, handleSubmit, isLoading, error, stop } =
    useChat({
      api: "/api/chat",
    });

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <p
        style={{
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          fontSize: 12,
        }}
      >
        Day17 · AI SDK useChat
      </p>
      <h1 style={{ marginTop: 8 }}>流式多轮对话</h1>
      <p style={{ color: "#666" }}>
        浏览器只打同源 <code>/api/chat</code>；Key 在 Route Handler。
      </p>

      <div
        style={{
          border: "1px solid #e5e5e5",
          borderRadius: 8,
          padding: 12,
          minHeight: 240,
          whiteSpace: "pre-wrap",
          marginBottom: 16,
        }}
      >
        {messages.length === 0 ? (
          <span style={{ color: "#999" }}>发一条消息开始…</span>
        ) : (
          messages.map((m) => (
            <div key={m.id} style={{ marginBottom: 12 }}>
              <strong>{m.role === "user" ? "你" : "助手"}：</strong>
              <div>{m.content}</div>
            </div>
          ))
        )}
      </div>

      {error ? (
        <p style={{ color: "#b91c1c" }}>错误：{error.message}</p>
      ) : null}

      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={3}
          placeholder="例如：用两句话介绍 FastAPI"
          style={{ width: "100%", padding: 12 }}
          disabled={isLoading}
        />
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? "生成中…" : "发送"}
          </button>
          {isLoading ? (
            <button type="button" onClick={() => stop()}>
              停止
            </button>
          ) : null}
        </div>
      </form>
    </main>
  );
}
```

**`src/app/page.tsx`：**

```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>ai-learning / node</h1>
      <ul>
        <li>
          <Link href="/agent">Day16 · Score Agent（JSON）</Link>
        </li>
        <li>
          <Link href="/stream">Day17 · AI SDK 流式 Chat</Link>
        </li>
      </ul>
    </main>
  );
}
```

**验收：**

- [x] 流式逐字/逐段出现
- [x] 多轮上下文有效
- [x] 缺 Key 时错误可读

---

### 18:00–18:05｜休息（5 分）

---

### 18:05–18:20｜复盘（15 分）

1. `useChat` 管 messages / input / loading / 流式拼接
2. Route Handler = BFF：密钥放这里
3. Day10 手写 SSE vs AI SDK data stream：协议不同，可二选一或写适配层

---

## 验收清单（全日）

- [x] `/api/chat` + `/stream` 流式多轮通
- [x] `.env.local` 无 `NEXT_PUBLIC_` 密钥
- [x] 能口述 Day16 vs Day17 数据流差异

## 实际产出文件

- `node/day16-help/src/app/api/chat/route.ts`
- `node/day16-help/src/app/stream/page.tsx`
- `node/day16-help/src/app/page.tsx`（首页双入口）
- `node/day16-help/.env.local.example`
- 依赖：`ai@4.3.16`、`@ai-sdk/openai@1.3.22`

## 明日预告

AI SDK 接 Tool Calling，或 Next BFF 代理 Day15 Agent（前端不再直连 8015）。
