---
name: weekly-exam
description: >-
  Generates a weekly exam in real time for the Path A curriculum under
  ai-learning/python. Writes exams/weekNN/exam.json, exam.md, and answers.md,
  and updates progress.json. Use when the user says 开始考试、开始第N周考试、
  周考、出题、批改第N周考试, or wants to start/grade the weekly quiz.
---

# 每周考试 · 实时出题

## 何时使用

用户说「开始本周考试 / 开始第 N 周考试 / 周考出题 / 批改第 N 周考试」时执行本 skill。

## 仓库约定

- **课程根目录**：`ai-learning/python/`（本 skill 所在侧）
- 进度：`progress.json`
- 大纲：`ai-career-plan.html`
- 试卷目录：`exams/weekNN/`（两位数字）
- 作答页：`exam.html`
- 本 skill 路径：`python/.cursor/skills/weekly-exam/`
- 必写文件（均在 `exams/weekNN/` 下）：
  - `exam.json` — 供 `exam.html` 作答（含客观题答案字段）
  - `exam.md` — 可读试卷（**不含**答案）
  - `answers.md` — 参考答案与简答评分要点（考生应交前不要剧透）

## 「开始考试」流程

1. **确定周次**
   - 用户指定 `第 N 周` → 用 N
   - 否则读 `progress.json` 的 `currentWeek`
2. **收集本周学过什么**
   - 读该周 `focus`
   - 扫描本周相关 `dayNN/`（`daysDone` + 邻近未归档的 day 笔记/代码）
   - 对照 `ai-career-plan.html` 对应周主题
3. **出题（实时生成，禁止固定题库照抄）**
   - 总分 100，建议 8–12 题，时长 30–45 分钟
   - 题型组合：
     - `single` 单选 4–6 题
     - `multi` 多选 1–2 题（可选）
     - `short` 简答 2–3 题
     - `code` 读题改错/补全 1–2 题（用 short 文本作答即可）
   - 难度紧扣本周，20% 可关联上周易错点
   - 对照前端经验出题（JS vs Python 等）加分
4. **写入文件**
   - 创建 `exams/weekNN/`
   - 写 `exam.json` / `exam.md` / `answers.md`
5. **更新进度**
   - 将该周 `exam.status` 设为 `in_progress`（若为 `locked` 先确认用户要开考再解锁）
   - 不自动改 `score`
6. **告知用户**
   - 路径、题量、建议时长
   - 打开：在课程根 `python/` 下 `python3 -m http.server 8765`，访问 `exam.html?week=N`
   - 聊天里只给题量与入口，不要把答案贴出来

## exam.json schema

```json
{
  "week": 1,
  "title": "Python 语法速通①",
  "durationMin": 40,
  "totalScore": 100,
  "generatedAt": "ISO-8601",
  "basedOn": ["day01", "progress focus..."],
  "questions": [
    {
      "id": "q1",
      "type": "single",
      "score": 10,
      "prompt": "题目...",
      "options": ["A...", "B...", "C...", "D..."],
      "answer": 1
    },
    {
      "id": "q2",
      "type": "multi",
      "score": 10,
      "prompt": "...",
      "options": ["..."],
      "answer": [0, 2]
    },
    {
      "id": "q3",
      "type": "short",
      "score": 15,
      "prompt": "...",
      "rubric": "得分点1；得分点2",
      "answer": "参考答案摘要"
    }
  ]
}
```

说明：`single`/`multi` 的 `answer` 为选项下标（从 0 起）；`short`/`code` 的 `answer` 仅写入 json 与 `answers.md`，`exam.md` 不要出现。

## exam.md 结构

```markdown
# 第 N 周考试 · <标题>

- 时长：xx 分钟
- 总分：100
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 10 分）
...
```

## 「批改考试」流程

1. 读 `exams/weekNN/exam.json` 与用户作答（聊天粘贴或 `exam.html` 交卷 JSON）
2. 客观题按标准答案判；简答按 `rubric` 给分并指出缺口
3. 计算总分；写入 `exams/weekNN/result.md`
4. 更新 `progress.json`：
   - `exam.status = "done"`
   - `exam.score = <总分>`
   - `exam.takenAt = ISO日期`
   - 若分数 ≥ 70：可将该周 `status` 设为 `done`，并解锁下一周为 `in_progress`（若仍 locked）
   - 若分数 < 70：保持 `exam.status = "done"`，建议生成错题复习日计划，不强制锁下周
5. 更新 `summary` 计数（examsPassed / weeksCompleted）
6. 简短反馈：分数、弱项、下一周预告

## 不要做的事

- 不要在开考时把 `answers.md` 内容发到聊天
- 不要用不相关大模型八股替代本周实操内容
- 不要跳过写入 `exam.json`（否则 exam.html 无法作答）
