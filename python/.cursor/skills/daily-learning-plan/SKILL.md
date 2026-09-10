---
name: daily-learning-plan
description: >-
  Creates a detailed daily learning schedule for the frontend-to-AI (Path A)
  curriculum under ai-learning/python. Use when the user asks for 今日学习计划、
  今天学什么、安排今天、开始学习、Day N 计划、daily learning plan. Default:
  output the full plan in chat first; on「今天学什么」also mkdir dayNN/;
  on「开始学习」write starter code; write dayNN/dayNN.md only after「没问题」。
---

# 每日学习计划

## 硬性流程（必须遵守）

1. **「今天学什么 / 安排今天」**：在聊天输出完整计划；**同时** `mkdir` 课程根下当日 `dayNN/`（空目录即可，便于用户立刻看到文件夹）。**不写** `dayNN.md`、起步代码、不改 `progress`
2. **「开始学习」**（或「开工 / 建目录」）：确保 `dayNN/` 存在；把计划里的**完整可跑文件**写入目录。已有同名文件且用户未要求覆盖 → **不覆盖**，只补缺失。**仍不写** `dayNN.md`、**不改** `progress`
3. **不要**在用户确认完成前写入 `dayNN/dayNN.md`
4. 用户学完并明确说「没问题 / 可以生成 / 写入」之后，才写入 `dayNN/dayNN.md`，并同步 `progress.json`
5. 若用户只要聊天版、明确说不用落盘，则只聊不写文件

## 何时使用

用户要「今天的学习安排 / Day N 计划 / 开始学习」时使用本 skill。

## 仓库约定

- **课程根目录**：`ai-learning/python/`（本 skill 所在侧；与仓库根下的 `node/` 并列）
- 每日目录：`dayNN/`（两位数字，如 `day01`、`day12`）——相对课程根
- 计划文件：`dayNN/dayNN.md`（与目录同名）——**仅确认后写入**
- 总路线参考：课程根 `ai-career-plan.html`；默认跟 **A 路线**
- 进度与周考：`progress.json`；试卷在 `exams/weekNN/`；作答页 `exam.html`（均在课程根）
- 本 skill 路径：`python/.cursor/skills/daily-learning-plan/`（各一级目录各自维护 skill）

## 环境约定（必须）

- **只维护一个虚拟环境**：课程根 `.venv/`（`ai-learning/python/.venv`）
- **禁止**在 `dayNN/` 下新建 `.venv`，也**不要**写 `source ../day01/.venv/bin/activate`
- 每日开工固定：

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd dayNN   # 进入当天目录写代码
```

- 需要装包时在课程根激活后 `uv pip install ...`（Python 课程共用）

## 执行步骤

### A. 出计划（默认，确认前）

1. **确定 Day 编号**
   - 用户指定则用指定值（`day01` / 第 3 天 → `day03`）
   - 未指定：扫描课程根下已有 `dayNN`，取最大 N+1；若无则 `day01`
2. **确定时段**
   - 用户给了起止时间 → 用之；时间表加总必须等于该时段
   - **未指定时段（默认）**：从**当前时刻**起，时长 **2 小时**（例如现在 14:21 → `14:21–16:21`）
   - 可将开始时间取整到最近 5 分钟，便于时间表阅读（如 14:21 → 14:20）
   - 中间若用户声明午休等固定打断，从 2 小时净学习里扣除并写进时间表
3. **对齐课程进度**（结合已完成目录、用户进度、A 路线）
   - 月 1：Python → FastAPI → LLM API/Streaming
   - 月 2：Prompt / Tool Calling / Next.js AI
   - 月 3：RAG + 评测
   - 月 4：Agent + 毕业项目
   - 月 5：工程化上线
   - 月 6：面试 + 按需补课
   - 传统 ML/DL、过深 SQL 默认不进主线
4. **在聊天输出完整计划**（结构见下方模板），并 **`mkdir -p` 当日 `dayNN/`**（仅空目录；不写 md / 代码）
5. 末尾加两句：
   - 准备动手时回复「开始学习」（写入起步代码）
   - 学完回复「没问题」后再生成 `dayNN.md`
6. **此阶段禁止写 md / 起步代码 / 改 progress**（除非用户说「开始学习」或要求落盘）

### A2. 开始学习（写入起步代码）

触发词：`开始学习` / `开工`（在已有当日聊天计划的前提下；若还没有计划，先按 A 出计划再执行本步）。

1. 确定 `dayNN`（与当日计划一致），确保目录存在
2. 把计划中的**完整可跑文件**写入目录（如 `main.py`、`static/index.html`）；已有同名文件且用户未要求覆盖 → **不覆盖**，只补缺失文件
3. 聊天简短确认：文件列表 + 建议的启动命令；**不要**整篇重贴计划，**不要**写 `dayNN.md`

### B. 用户确认后落盘

1. 确保 `dayNN/` 存在（相对课程根）
2. 写入 `dayNN/dayNN.md`：**必须与已确认的聊天版完整一致**（含全部命令、代码草稿、验收步骤）；可标「已完成」、勾选清单、补实际产出文件名，**禁止**落盘时删减代码示例或改成摘要版
3. **同步进度**
   - 更新 `progress.json`：该 `dayNN` 写入对应周 `daysDone`
   - 周若为 `locked` → `in_progress`；`exam.status` 从 `locked` → `pending`
   - 刷新 `summary` 计数
4. 聊天里只确认路径与已更新进度，勿整篇再贴一遍计划

## 聊天 / md 共用模板

用中文：

```markdown
# Day NN · <短主题>

- **日期**：YYYY-MM-DD
- **时段**：HH:MM–HH:MM（时长）
- **阶段**：A 路线 · 第 X 个月 · <阶段名>
- **今日主题**：一句话
- **原则**：动手为主，文档只查不会的点

## 今日目标

1. ...
2. ...
3. ...

## 今日不学

（明确边界）

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| ... | ... | ... |

---

## 详细安排

### HH:MM–HH:MM｜<标题>（N 分）

步骤、命令、代码草稿、**验收标准**。
含休息块（约每 50–60 分钟休息 5 分钟）。

---

## 验收清单

- [ ] ...

## 明日预告

一句话
```

## 内容质量要求

- 越详细越好：命令可复制、代码可粘贴、每段有验收
- 一次一事：当天一个主产出
- 对照前端经验：Python/API 用 JS/TS 类比
- 时间表加总 = 用户时段（未指定则为当前起 2 小时）
- 需要运行的代码给**完整可跑文件**，禁止只贴「核心几行」让用户自己拼
- 装 Python 包写 `uv pip install ...`（不要默认写裸 `pip install`）
- 参考：`day01/day01.md` 的详细程度

## 不要做的事

- ❌ 用户未确认就写 `dayNN.md` 或让用户「去看 md」
- ❌ 「今天学什么」却不建空的 `dayNN/` 目录
- ❌ 用户说「开始学习」却只口头说命令、不真正写起步文件
- ❌ 只写文件却不在聊天给出可读计划
- ❌ 一天塞多个大主题（NumPy + FastAPI + RAG）
- ❌ 默认开启完整 ML/数学长课
- ❌ 未指定时段时仍写死 `20:00–22:20`（已改为「现在 + 2h」）
