# Day 01 · Python 起步

- **日期**：2026-07-27
- **时段**：20:00–22:20（2 小时 20 分）
- **阶段**：A 路线 · 第 1 个月 · Python 速通
- **今日主题**：环境 + 和 JS 对照的基础语法 + 一个能跑的小脚本
- **原则**：动手为主，视频/文档只查不会的点

## 今日目标

1. 建好 venv，确认能跑 Python
2. 搞清和 JS 最不一样的几处语法
3. 完成 `stats.py`：读 JSON → 统计 → 打印

## 今日不学

装饰器、OOP、NumPy、Pandas、FastAPI、任何 LLM API

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 20:00–20:15 | 环境搭建 | venv 可用 |
| 20:15–20:35 | 变量 / 条件 / 循环 | 交互练习 |
| 20:35–20:55 | 列表 / 字典 / 函数 | 列表推导式会写 |
| 20:55–21:00 | 休息 | — |
| 21:00–21:25 | JSON 文件读取 | 能读 `data.json` |
| 21:25–21:55 | 完成统计脚本 | `stats.py` 跑通 |
| 21:55–22:00 | 休息 | — |
| 22:00–22:15 | 修错加练 | 调试手感 |
| 22:15–22:20 | 复盘收工 | `notes.md` |

---

## 详细安排

### 20:00–20:15｜开场 + 环境（15 分）

```bash
mkdir -p ~/code/ai-learning/day01 && cd ~/code/ai-learning/day01
python3 -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.version)"
```

看到版本号（建议 3.10+）就算过关。同时准备 `data.json`、`stats.py`。

**验收：** 提示符前有 `(.venv)`，`python` 能打印版本。

---

### 20:15–20:35｜语法对照①：变量 / 类型 / 条件 / 循环（20 分）

```bash
python
```

```python
name = "maple"
score = 90
ok = True
empty = None          # 对标 null/undefined

if score >= 90:
    print("A")
elif score >= 60:
    print("B")
else:
    print("C")

for i in range(5):
    print(i)

nums = [1, 2, 3]
for n in nums:
    print(n * 2)
```

**刻意记 3 个差异：**

1. 用缩进，不用 `{}`
2. 布尔是 `True` / `False`（大写）
3. 空值是 `None`

**验收：** 不看资料能写出一个 `if/elif/else` + 一个 `for`。

---

### 20:35–20:55｜语法对照②：列表 / 字典 / 函数（20 分）

```python
scores = [80, 95, 70]
scores.append(88)
print(scores[0], len(scores), sum(scores) / len(scores))

evens = [x for x in range(10) if x % 2 == 0]
doubled = [s * 2 for s in scores]

user = {"name": "a", "score": 80}
print(user["name"])
user["score"] = 85
print(user.get("age", 0))

def average(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)

print(average(scores))
```

**验收：** 能手写列表推导式、字典读写、带 `return` 的函数。

---

### 20:55–21:00｜休息（5 分）

站起来、喝水。不要刷短视频。

---

### 21:00–21:25｜文件读写：JSON（25 分）

`data.json`：

```json
[
  {"name": "Alice", "score": 80},
  {"name": "Bob", "score": 95},
  {"name": "Carol", "score": 70},
  {"name": "Dave", "score": 88},
  {"name": "Eve", "score": 92}
]
```

`stats.py` 先只读：

```python
import json
from pathlib import Path

data_path = Path(__file__).with_name("data.json")

with data_path.open("r", encoding="utf-8") as f:
    students = json.load(f)

print(type(students), len(students))
print(students[0])
```

```bash
python stats.py
```

**验收：** 终端打印出人数和第一条记录。

---

### 21:25–21:55｜今日主产出：完成 `stats.py`（30 分）

要求输出：

1. 总人数
2. 平均分（保留 1 位小数）
3. 最高分是谁
4. 及格人数（≥60）
5. 分数 ≥90 的名单（用列表推导式）

参考实现（先自己写，卡住再对照）：

```python
import json
from pathlib import Path

def load_students(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def summarize(students):
    if not students:
        return {"count": 0}

    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    passed = [s for s in students if s["score"] >= 60]
    excellent = [s["name"] for s in students if s["score"] >= 90]

    return {
        "count": len(students),
        "avg": round(sum(scores) / len(scores), 1),
        "top_name": top["name"],
        "top_score": top["score"],
        "passed": len(passed),
        "excellent": excellent,
    }

def main():
    path = Path(__file__).with_name("data.json")
    students = load_students(path)
    result = summarize(students)

    print(f"人数: {result['count']}")
    print(f"平均分: {result['avg']}")
    print(f"最高分: {result['top_name']} ({result['top_score']})")
    print(f"及格人数: {result['passed']}")
    print(f"优秀名单: {', '.join(result['excellent'])}")

if __name__ == "__main__":
    main()
```

**验收清单：**

- [ ] `python stats.py` 无报错
- [ ] 平均分算对
- [ ] 用了至少一次列表推导式
- [ ] 改 `data.json` 再跑，结果会变

---

### 21:55–22:00｜休息（5 分）

---

### 22:00–22:15｜加练：主动制造并修好一个错误（15 分）

1. 把 `data.json` 写坏（多余逗号 / 少 `]`），看报错再修好
2. 把某个 `score` 改成字符串 `"95"`，看 `sum` 报错，再改回

加分题：

```python
for s in sorted(students, key=lambda x: x["score"], reverse=True):
    print(s["name"], s["score"])
```

---

### 22:15–22:20｜复盘收工（5 分）

写 `notes.md`（约 5 行）：

```md
# Day01
- 今天学会：venv、缩进、列表推导式、dict、json.load
- 和 JS 最大不同：...
- 卡过的点：...
- 明天预告：函数进阶（默认参数/*args）+ 写 CSV 版统计
```

收工确认：

- [ ] 目录有 `.venv/`、`data.json`、`stats.py`、`notes.md`
- [ ] 明天从 `cd` + `source .venv/bin/activate` 开始

---

## 明日预告

函数进阶（默认参数 / `*args` / `**kwargs`）+ CSV 读写版统计脚本
