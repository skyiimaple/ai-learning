# Day 22 · RAG Demo 页 + 引用展示 · 已学习

- **日期**：2026-09-28（补写计划；代码已完成）
- **时段**：约 2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 3 个月 · RAG 实现
- **今日主题**：FastAPI 托管静态页；复用 Day21 索引与 `ask`；浏览器展示回答 + hits 引用
- **原则**：不重写检索；同源 `/rag/ask`，前端只负责展示
- **状态**：已学习

## 环境

```bash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3
LLM_EMBED_MODEL=embedding-3
```

先确保 Day21 已建索引：

```bash
cd ~/code/ai-learning/python/day21 && python index.py
```

## 今日目标

1. `main.py`：lifespan 加载 `day21/data`；`POST /rag/ask`；挂载 `static/`
2. `static/index.html`：提问 → 显示 answer + 每条 hit（source / id / score / text）
3. 本地 `8022` 可演示「问笔记、看引用」

## 今日不学

Chroma、Hybrid、Re-rank、Langfuse（后续 Day）

---

## 时间表（回顾）

| 内容 | 产出 |
|------|------|
| 复用 day21 `load_index` / `ask` / schema | 无重复索引逻辑 |
| FastAPI + StaticFiles（路由先于 mount） | `/health`、`/rag/ask`、首页 |
| 引用 UI | hits 列表可核对 grounded |

---

## 环境命令

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd day22
python main.py
# http://127.0.0.1:8022
```

或：

```bash
uvicorn main:app --host 127.0.0.1 --port 8022
```

---

## 实现要点

### 后端 `main.py`

- `sys.path` 引入 `day21`，直接 `from index import load_index`、`from rag import ask`
- `lifespan` 启动时加载索引；缺文件则提示先跑 `day21/index.py`
- **先注册** `/health`、`/rag/ask`，**再** `app.mount("/", StaticFiles(...))`，避免静态路由吞掉 API

### 前端 `static/index.html`

- `fetch("/rag/ask", { question, top_k })`（同源，无跨域配置负担）
- 回答区 + hits：展示 `source`、`id`、`score`、片段原文
- 错误时用 `detail` 提示（索引未加载、LLM 失败等）

### 验收（已完成）

- [x] `/health` 返回 `chunks` 与 model
- [x] 浏览器提问有回答
- [x] hits 与回答引用可对照
- [x] 能口述：引用 UI 解决「答案从哪来」的信任问题

---

## 复盘

1. Demo 页价值：把 Day21 API 变成可给人看的产品切片  
2. 复用索引避免两套向量不一致  
3. StaticFiles 挂载顺序是常见坑  

## 明日预告

Day23：Chroma 持久化 + 黄金集命中率 → `day23/day23.md`
