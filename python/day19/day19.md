# Day 19 · AI SDK Tool Calling（成绩工具）

- **日期**：2026-09-08（落盘 2026-09-10）
- **时段**：17:35–19:35（2 小时）
- **计划目录**：`~/code/ai-learning/python/day19`
- **代码目录**：`~/code/ai-learning/node/day16-help`
- **阶段**：A 路线 · 第 2 个月 · Next.js AI 产品化
- **今日主题**：在 `/api/chat-tools` 用 `streamText` + `tool()` 实现 `get_score` / `avg_score`，前端 `useChat` 流式多轮并看到工具调用
- **原则**：工具在 Next 服务端 `execute`；Key 只在 `.env.local`；钉 AI SDK v4
- **状态**：已完成 ✅

## 今日目标

1. 用 `tool` + `zod` 声明两个成绩工具，`maxSteps` 限步
2. 新页面 `/tools`：`useChat({ api: "/api/chat-tools" })`
3. 能口述：AI SDK 自动多步 vs Day13 手写 `tool_calls` 循环

## 今日不学

- 继续改 Day15 Python Agent
- RAG / 向量库
- AI SDK v5 迁移

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 17:35–17:50 | 对照 Day13/14 + 装 `zod` | 概念对齐 |
| 17:50–18:30 | 实现 `/api/chat-tools` | 服务端 tools |
| 18:30–18:35 | 休息 | — |
| 18:35–19:15 | `/tools` 页 + 联调 | 可演示 |
| 19:15–19:20 | 休息 | — |
| 19:20–19:35 | 验收 + 复盘 | 口述对照表 |

---

## 环境

```bash
cd ~/code/ai-learning/node/day16-help
npm install zod
# .env.local 需有 LLM_API_KEY（无 NEXT_PUBLIC_）
npm run dev
```

打开：`http://localhost:3000/tools`

---

## 详细安排

### 17:35–17:50｜对照 + 装包（15 分）

| Day13/14（Python） | Day19（AI SDK） |
|--------------------|-----------------|
| `TOOLS` JSON schema | `tool({ parameters: z.object(...) })` |
| 手写 `for` + `tool_calls` | `maxSteps` 自动多轮 |
| `run_tool` / `execute` | `execute: async (...) => ...` |
| 返回 JSON 再喂模型 | SDK 把 tool result 接回 messages |

**验收：**

- [x] 能说出「谁执行工具」——永远是你的 `execute`

---

### 17:50–18:30｜API：chat-tools（40 分）

**`src/lib/scores.ts`：**

```ts
export const SCORES: Record<string, number> = {
  Alice: 80,
  Bob: 95,
  Frank: 59,
  Grace: 88,
};

export function getScore(name: string) {
  if (!(name in SCORES)) {
    return { ok: false as const, error: "not found", name };
  }
  return { ok: true as const, name, score: SCORES[name] };
}

export function avgScore() {
  const vals = Object.values(SCORES);
  return {
    ok: true as const,
    count: vals.length,
    average:
      Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 100) / 100,
  };
}
```

**`src/app/api/chat-tools/route.ts`：**

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { streamText, tool } from "ai";
import { z } from "zod";

import { avgScore, getScore } from "@/lib/scores";

export const runtime = "nodejs";
export const maxDuration = 60;

const provider = createOpenAI({
  apiKey: process.env.LLM_API_KEY,
  baseURL: `${(process.env.LLM_BASE_URL ?? "https://api.deepseek.com").replace(/\/$/, "")}/v1`,
});

export async function POST(req: Request) {
  if (!process.env.LLM_API_KEY) {
    return Response.json({ error: "缺少 LLM_API_KEY" }, { status: 500 });
  }

  const { messages } = await req.json();

  const result = streamText({
    model: provider(process.env.LLM_MODEL ?? "deepseek-chat"),
    system:
      "你是成绩助手。查分用 get_score，算平均用 avg_score。禁止编造数字。用中文简短回答。",
    messages,
    temperature: 0,
    maxSteps: 5,
    tools: {
      get_score: tool({
        description: "按姓名查单个学生成绩。未知返回 not found。",
        parameters: z.object({
          name: z.string().describe("学生英文名，如 Frank"),
        }),
        execute: async ({ name }) => getScore(name),
      }),
      avg_score: tool({
        description: "计算成绩表全体学生的平均分。",
        parameters: z.object({}),
        execute: async () => avgScore(),
      }),
    },
  });

  return result.toDataStreamResponse();
}
```

**验收：**

- [x] 服务端 tools + `maxSteps: 5` 就绪

---

### 18:30–18:35｜休息（5 分）

---

### 18:35–19:15｜前端 `/tools`（40 分）

**`src/app/tools/page.tsx`：**（完整文件见仓库）

- `useChat({ api: "/api/chat-tools", maxSteps: 5 })`
- 渲染 `messages` 与 `toolInvocations`

**联调题：**

1. `Frank 考了多少分？` → `get_score`，含 59
2. `比较 Bob 和平均分` → `get_score` + `avg_score`
3. `有没有 Zack？` → `not found`

**验收：**

- [x] 可见工具调用或最终数字正确
- [x] 与 `/stream`（无工具）可区分

---

### 19:15–19:20｜休息（5 分）

---

### 19:20–19:35｜复盘（15 分）

1. **`maxSteps`** ≈ Day13 `MAX_STEPS`
2. 两套成绩 Agent：Python Day15（`/api/agent`）vs Next tools（`/api/chat-tools`）
3. `toolInvocations` ≈ Day15 页的 `steps`

另：Day18 BFF 切换（`/api/agent`）= 浏览器只打 Next，由服务端转发 8015。

---

## 验收清单（全日）

- [x] `/api/chat-tools` + `/tools` 就绪
- [x] 能口述 AI SDK tools 与手写 tool_calls 的对应
- [x] 理解 Day18：`AGENT_URL = "/api/agent"` 的数据流

## 实际产出文件

- `node/day16-help/src/lib/scores.ts`
- `node/day16-help/src/app/api/chat-tools/route.ts`
- `node/day16-help/src/app/tools/page.tsx`
- `node/day16-help/src/app/page.tsx`（增加 `/tools` 入口）
- 依赖：`zod`

## 明日预告

收敛产品路径（只保留一套 Agent），或进入 **RAG**（Embedding / Chunking 入门）。
