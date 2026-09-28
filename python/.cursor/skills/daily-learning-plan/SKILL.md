---
name: daily-learning-plan
description: >-
  Daily Path A learning plan under ai-learning/python. Triggers: 开始学习、
  今天学什么、安排今天、现在开始、Day N 计划. On trigger: mkdir dayNN/ and write
  only dayNN/dayNN.md (full plan). Title must end with「· 未学习」; on 学完了
  flip title (and 状态) to「· 已学习」and update progress.json. Do NOT write
  starter code. Do NOT paste full plan in chat.
---

# 每日学习计划

## 硬性流程（必须遵守）

用户说 **「开始学习」**（以及同义：今天学什么 / 安排今天 / 现在开始 / Day N 计划）时，**只做下面两件事**：

1. `mkdir -p` 课程根下 `dayNN/`
2. 写入 **`dayNN/dayNN.md`**（完整学习计划：目标、时间表、命令、代码示例、验收）

**标题状态（必须）：**

- 新建计划标题格式：`# Day NN · <短主题> · 未学习`
- 正文 `- **状态**：未学习`（与标题一致）
- 不要用「进行中 / 待开始 / 加速」等其它状态词

**其他一律不做：**

- ❌ 不写 `.py` / `.html` / `.json` / 静态资源等起步代码（代码示例只放在 md 里）
- ❌ 不在聊天里输出整篇计划（用户自己打开 md）
- ❌ 不等「没问题」才写 md
- ❌ 不改 `progress.json` 的 `daysDone` / `daysCompleted`（开工最多改 `currentDay`）

聊天回复：**一两句**即可，例如「计划已写入 `python/day23/day23.md`」。

### 学完同步进度

用户明确表示当日学完（`学完了` / `完成了` / `没问题`）时：

1. 把 `dayNN.md` **标题**末尾 `· 未学习` 改为 `· 已学习`；同步 `- **状态**：已学习`
2. 勾选当日验收清单（若有）
3. 更新 `progress.json`（`daysDone`、周状态、`summary`、`currentDay`）

### 例外

- 用户**单独**要求「把计划里的代码落到文件 / 帮我建 py」→ 才写代码文件
- 用户说「只要聊、不用写文件」→ 只聊不写

## 仓库约定

- 课程根：`ai-learning/python/`
- 计划：`dayNN/dayNN.md`（标题带 `· 未学习` / `· 已学习`）
- 路线：`ai-career-plan.html`（A 路线）
- **学习总表**：`learning-outline.md`（Day23 起按日主题；出每日计划必须对齐该表）
- 进度：`progress.json`
- 本 skill：`python/.cursor/skills/daily-learning-plan/`

## 环境约定

```bash
cd ~/code/ai-learning/python
source .venv/bin/activate
cd dayNN
```

装包：`uv pip install ...`（写在 md 的命令里即可）

## 出计划时怎么定内容

1. **Day 编号**：指定则用；否则已有 `dayNN` 最大 N+1
2. **时段**：指定则用；否则当前时刻起 2 小时（可取整 5 分钟）
3. **进度**：跟 `learning-outline.md` 的当日行（齐则跟 A 路线）；节奏：一天 3 个紧密相关里程碑，可并原「一周」内同链内容；禁止跨能力线硬拼；用户说「放慢」再细拆并后移大纲
4. md 要详细：命令可复制、示例代码完整可跑、每段有验收；新 API 一两句说明
5. 用户要「学习大纲 / 重新排期」→ 更新 `learning-outline.md`，默认不批量预写未来 `dayNN.md`
6. 用户明确说「生成全部 / 把大纲都生成计划」→ 按 `learning-outline.md` 为尚未存在的 Day **只**写 `dayNN/dayNN.md`（可 mkdir），仍不写起步代码文件；标题一律 `· 未学习`

## md 模板

```markdown
# Day NN · <短主题> · 未学习

- **日期**：YYYY-MM-DD
- **时段**：HH:MM–HH:MM
- **阶段**：A 路线 · …
- **今日主题**：
- **原则**：
- **状态**：未学习

## 今日目标
## 今日不学
## 时间表
## 详细安排（含完整代码示例与验收）
## 验收清单
## 明日预告
```

标题与正文不要写「加速」等节奏元信息；节奏只体现在内容密度上。状态只允许 `未学习` / `已学习`。

## 不要做的事

- ❌ 「开始学习」时生成除 `dayNN/` + `dayNN.md` 以外的学习文件
- ❌ 等「没问题」才写计划 md
- ❌ 聊天里贴整篇计划
- ❌ 一天塞无关大主题 / 故意拖成微知识点日
- ❌ 标题漏标状态，或使用未学习/已学习以外的状态词
