# Day 18 · Next BFF 代理 Score Agent

- **日期**：2026-09-08
- **时段**：16:50–18:50（2 小时）
- **计划目录**：`~/code/ai-learning/python/day18`
- **代码目录**：`~/code/ai-learning/node/day16-help`
- **阶段**：A 路线 · 第 2 个月 · Next.js AI 产品化
- **今日主题**：新增 `POST /api/agent`，由 Next 服务端转发到 Day15；浏览器只打同源接口
- **原则**：前端零密钥、零直连后端端口；和 Day17 `/api/chat` 同一套 BFF 思路
- **状态**：已完成 ✅

## 今日目标

1. 写通 `src/app/api/agent/route.ts`（服务端 `fetch` → `8015/agent/chat`）
2. 改 `/agent` 页：改为请求 `/api/agent`，去掉对 `NEXT_PUBLIC_AGENT_URL` 的依赖
3. 能口述：为何 Agent 也要进 BFF

## 今日不学

- AI SDK Tool Calling
- 改 Python Agent 逻辑
- 部署、鉴权中间件

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 16:50–17:05 | 复跑 Day15 + 画数据流 | 确认 8015 通 |
| 17:05–17:45 | 实现 `/api/agent` | Route Handler |
| 17:45–17:50 | 休息 | — |
| 17:50–18:30 | 改 `/agent` 页 + 联调 | 同源调用 |
| 18:30–18:35 | 休息 | — |
| 18:35–18:50 | 验收 + 复盘 | 口述对比表 |

---

## 环境

**终端 1 — Day15：**

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

可选 `.env.local`（无 `NEXT_PUBLIC_`）：

```bash
AGENT_UPSTREAM_URL=http://127.0.0.1:8015/agent/chat
```

---

## 详细安排

### 16:50–17:05｜开工（15 分）

```
浏览器 /agent
  → POST /api/agent          （Next 服务端）
      → http://127.0.0.1:8015/agent/chat
  ← { answer, steps, model }
```

**验收：**

- [x] Day15 `/health` 通；清楚「浏览器不再出现 8015」

---

### 17:05–17:45｜BFF Route（40 分）

**`src/app/api/agent/route.ts`：**

```ts
export const runtime = "nodejs";
export const maxDuration = 60;

const UPSTREAM =
  process.env.AGENT_UPSTREAM_URL ?? "http://127.0.0.1:8015/agent/chat";

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ detail: "无效 JSON" }, { status: 400 });
  }

  const message =
    typeof body === "object" &&
    body !== null &&
    "message" in body &&
    typeof (body as { message: unknown }).message === "string"
      ? (body as { message: string }).message.trim()
      : "";

  if (!message) {
    return Response.json({ detail: "message 不能为空" }, { status: 400 });
  }

  const temperature =
    typeof body === "object" &&
    body !== null &&
    "temperature" in body &&
    typeof (body as { temperature: unknown }).temperature === "number"
      ? (body as { temperature: number }).temperature
      : 0;

  try {
    const upstream = await fetch(UPSTREAM, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, temperature }),
      // Node 18+ 可用；超时靠 maxDuration
      cache: "no-store",
    });

    const data = await upstream.json().catch(() => ({}));

    if (!upstream.ok) {
      const detail =
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        typeof (data as { detail: unknown }).detail === "string"
          ? (data as { detail: string }).detail
          : `上游错误 HTTP ${upstream.status}`;
      return Response.json({ detail }, { status: upstream.status });
    }

    return Response.json(data);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      { detail: `无法连接 Agent 上游（请确认 Day15 在 8015）：${msg}` },
      { status: 502 },
    );
  }
}
```

**冒烟：**

```bash
curl -s http://localhost:3000/api/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"Frank 考了多少分？","temperature":0}' \
  | python -m json.tool
```

**验收：**

- [x] curl 能拿到 `answer` + `steps`
- [x] 关掉 Day15 再 curl，应得到 502 且文案可读

---

### 17:45–17:50｜休息（5 分）

---

### 17:50–18:30｜改前端页（40 分）

**`src/app/agent/page.tsx` 关键变更：**

```ts
const AGENT_URL = "/api/agent";
```

其余 `fetch` / `steps` 渲染逻辑保持；页面说明改为「经 Next BFF」。

**验收：**

- [x] 两问成功，`steps` 可见
- [x] Network 无直连 `8015`
- [x] 停掉 Day15 后错误可读

---

### 18:30–18:35｜休息（5 分）

---

### 18:35–18:50｜复盘（15 分）

| 入口 | 浏览器打谁 | 谁持有秘密/内网地址 |
|------|------------|---------------------|
| Day16 旧 `/agent` | `8015` 直连 | 前端暴露上游 URL |
| Day17 `/stream` | `/api/chat` | Next 持有 `LLM_API_KEY` |
| Day18 新 `/agent` | `/api/agent` | Next 持有 `AGENT_UPSTREAM_URL` |

1. BFF = 统一大门：限流、鉴权、日志以后都加在 Route Handler
2. `AGENT_UPSTREAM_URL` 不要加 `NEXT_PUBLIC_`
3. Python Agent 仍是工具真相；Next 只转发

---

## 验收清单（全日）

- [x] `POST /api/agent` curl 通
- [x] `/agent` 页只请求同源 BFF
- [x] 上游挂了时错误可读
- [x] 能口述 Day16 直连 vs Day18 BFF 的差别

## 实际产出文件

- `node/day16-help/src/app/api/agent/route.ts`
- `node/day16-help/src/app/agent/page.tsx`（改为 `/api/agent`）
- `node/day16-help/src/app/page.tsx`（入口文案）

## 明日预告

AI SDK `tools` + `streamText`（在 Next 侧做 Tool Calling），或开始 RAG 月准备。
