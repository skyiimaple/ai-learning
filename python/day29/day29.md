# Day 29 · 毕业项目 Day2：主流程打通 · 未学习

- **日期**：按实际学习日
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 4 个月 · 毕业项目 MVP①
- **今日主题**：把 Day28 mock 换成真实 LLM+工具链路；一条 happy path；UI 能演示
- **原则**：只打通主路径，边缘功能一律不做
- **状态**：未学习
- **大纲**：`learning-outline.md` Day29
- **依赖**：Day28 `CHOICE.md` 已锁定

## 今日目标

1. 真实数据进入模型（diff 或 CSV profile）
2. ≥2 个业务工具（描述/查询/静态检查等）
3. UI 展示结构化结果（评论列表或结论+表）

## 今日不学

Webhook、权限矩阵、漂亮图表库深挖、多文件批处理

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:15 | 对齐 CHOICE Demo 步骤 | 清单 |
| 0:15–1:00 | 核心 analyze/review 真实现 | 无 UI 可 CLI |
| 1:00–1:05 | 休息 | — |
| 1:05–1:45 | 接 API + UI | 可演示 |
| 1:45–2:00 | 录一条 60s 自测 | 问题列表 |

---

## 方向 B（CSV）要点

**`profile.py`：** pandas 读 CSV → `dtypes` / `head(5)` / `null` 计数（注意行数上限，如 5k）。

**工具建议：**

- `list_columns`
- `value_counts(column)`
- `sql_like_filter` 或受限 `run_pandas_code`（禁止 `open/exec/import os`）

**Agent：** 复用 Day26 循环，goal=用户问题，system 强调「先探查再回答」。

**最终 JSON：**

```json
{
  "answer": "...",
  "steps": [{"tool": "...", "ok": true}],
  "preview": {"columns": [], "shape": [0, 0]}
}
```

## 方向 A（PR Review）要点

**`github_client.py`：** `GET /repos/{owner}/{repo}/pulls/{n}/files`（PAT 只读）。

**工具建议：**

- `fetch_pr_files`
- `read_patch(filename)`
- `add_finding(level, path, message)`（写入内存列表）

**最终 JSON：** `findings[]` + `summary`。

环境：`GITHUB_TOKEN` 放 `.env`，勿提交。

---

## UI 最低要求

- 输入：文件或 owner/repo/pr
- 输出：markdown/JSON 可读区
- 显示：用了哪些工具（steps）

端口建议 `8029`（或继续 8028）。

---

## 验收清单

- [ ] CLI 或 API 对样例数据给出非 mock 结果
- [ ] UI 完成 CHOICE 里 Demo 步骤 1–2
- [ ] 已知问题记入 `ISSUES.md`（≥3 条也行）

## 明日预告

Day30：错误处理 + 3 分钟 Demo 脚本定稿 + 已知问题收敛。
