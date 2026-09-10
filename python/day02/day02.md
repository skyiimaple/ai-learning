# Day 02 · 函数进阶 + CSV 统计

- **日期**：2026-07-28
- **时段**：15:40–18:20（2 小时 40 分）
- **阶段**：A 路线 · 第 1 个月 · Python 速通
- **今日主题**：函数参数进阶（对照 JS）+ 用 csv 模块做成绩统计脚本
- **原则**：动手为主，文档只查不会的点；在 Day01 的 `stats.py` 思路上换数据源
- **状态**：已完成 ✅

## 今日目标

1. 会写默认参数、`*args` / `**kwargs`、以及简单 `lambda`
2. 会用 `csv.DictReader` / `DictWriter` 读写 CSV
3. 完成主产出 `csv_stats.py`：读 CSV → 统计 → 打印，并会处理常见异常

## 今日不学

装饰器深挖、OOP 继承体系、NumPy/Pandas、FastAPI、任何 LLM API

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:40–15:50 | 开工 + 复习 Day01 | 环境就绪，能跑通昨天脚本 |
| 15:50–16:30 | 函数进阶 | 默认参 / *args / **kwargs / lambda |
| 16:30–16:35 | 休息 | — |
| 16:35–17:15 | CSV + 异常处理 | 能读 `students.csv` |
| 17:15–17:20 | 休息 | — |
| 17:20–18:05 | 主产出 `csv_stats.py` | 统计脚本跑通 |
| 18:05–18:15 | 加练：修错 + 写回 CSV | 调试手感 |
| 18:15–18:20 | 复盘收工 | `notes.md` |

---

## 详细安排

### 15:40–15:50｜开工 + 复习 Day01（10 分）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
cd day02

python -c "print('ok')"
python ../day01/stats.py
```

快速回想（口述即可）：
- 列表推导式
- `json.load` + `with open`
- `Path(__file__).with_name(...)`

**验收：** 提示符有 `(.venv)`；昨天的 `stats.py` 仍能跑；当前目录是 `day02`。

> 环境约定：全课程共用仓库根目录 `.venv/`，不要在 `dayNN/` 下新建。

---

### 15:50–16:30｜函数进阶（40 分）

打开交互环境：`python`

#### 1) 默认参数（对标 JS 默认参数）

```python
def greet(name, greeting="你好"):
    return f"{greeting}, {name}"

print(greet("Maple"))
print(greet("Maple", greeting="Hi"))
```

**坑（必看一眼）：** 默认参数不要用可变对象（`[]` / `{}`）。

```python
# 错误示范：别这么写
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket
```

正确写法：

```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

#### 2) `*args` / `**kwargs`（对标 JS 的 rest / 对象展开）

```python
def total(*nums):
    # nums 是 tuple，对标 (...nums)
    return sum(nums)

print(total(1, 2, 3, 4))

def create_user(name, **profile):
    # profile 是 dict，对标剩余字段对象
    return {"name": name, **profile}

print(create_user("Ada", age=30, city="Shanghai"))
```

#### 3) `lambda` + `sorted`（对标箭头函数当回调）

```python
students = [
    {"name": "Bob", "score": 95},
    {"name": "Amy", "score": 80},
]

print(sorted(students, key=lambda s: s["score"], reverse=True))
```

#### 4) 小练习（写在交互里或 `fn_drill.py`）

写一个函数：

```python
def summarize_scores(*scores, pass_line=60):
    """返回 dict: count / avg / passed_count"""
    ...
```

**验收：**
- [x] 能解释 `*args` 和 `**kwargs` 各是什么类型
- [x] `summarize_scores(70, 90, 55)` 能算出人数、平均分、及格数
- [x] 知道默认参数为什么不能写 `bucket=[]`

---

### 16:30–16:35｜休息（5 分）

站起来活动；不要刷短视频。

---

### 16:35–17:15｜CSV 读写 + 异常（40 分）

#### 1) 准备数据 `students.csv`

```csv
name,score,class
Alice,80,A
Bob,95,B
Carol,70,A
Dave,88,B
Eve,92,A
Frank,59,B
```

可用编辑器新建，或：

```bash
cat > students.csv << 'CSV'
name,score,class
Alice,80,A
Bob,95,B
Carol,70,A
Dave,88,B
Eve,92,A
Frank,59,B
CSV
```

#### 2) 读取（对标：把 CSV 当成「没有嵌套的 JSON 数组」）

```python
import csv
from pathlib import Path

path = Path("students.csv")
with path.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(rows[0])
print(rows[0]["name"], type(rows[0]["score"]))  # score 是 str！
```

**关键点：** CSV 读出来的字段默认都是 **字符串**，算平均分前要 `int(row["score"])`。

#### 3) 异常处理（对标 try/catch）

```python
def parse_score(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e

def load_students(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到文件: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    students = []
    for r in rows:
        students.append({
            "name": r["name"],
            "score": parse_score(r["score"]),
            "class": r.get("class", "未知"),
        })
    return students
```

**验收：**
- [x] `list(csv.DictReader(...))` 能读出 6 行
- [x] 把某个分数改成 `九十五`，能看到清晰报错（须走到 `int`/`parse_score`，仅 DictReader 打印不会报）
- [x] 文件名写错时，能捕获 `FileNotFoundError`

---

### 17:15–17:20｜休息（5 分）

---

### 17:20–18:05｜主产出：完成 `csv_stats.py`（45 分）

把 Day01 的统计逻辑迁到 CSV，并增加「按班级汇总」。

**要求输出：**

1. 总人数、平均分（1 位小数）
2. 最高分是谁
3. 及格人数（默认及格线 60，做成函数参数）
4. 优秀名单（≥90）
5. 按 `class` 分组：每班人数 + 平均分

先自己写；卡住再对照下面骨架：

```python
import csv
from pathlib import Path
from collections import defaultdict


def parse_score(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e


def load_students(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到文件: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [
        {
            "name": r["name"],
            "score": parse_score(r["score"]),
            "class": r.get("class", "未知"),
        }
        for r in rows
    ]


def summarize(students, pass_line=60):
    if not students:
        return {"count": 0}

    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    by_class = defaultdict(list)
    for s in students:
        by_class[s["class"]].append(s["score"])

    class_stats = {
        c: {
            "count": len(vals),
            "avg": round(sum(vals) / len(vals), 1),
        }
        for c, vals in by_class.items()
    }

    return {
        "count": len(students),
        "avg": round(sum(scores) / len(scores), 1),
        "top_name": top["name"],
        "top_score": top["score"],
        "passed": sum(1 for s in students if s["score"] >= pass_line),
        "excellent": [s["name"] for s in students if s["score"] >= 90],
        "by_class": class_stats,
    }


def main():
    path = Path(__file__).with_name("students.csv")
    try:
        students = load_students(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"读取失败: {e}")
        return

    result = summarize(students)
    print(f"人数: {result['count']}")
    print(f"平均分: {result['avg']}")
    print(f"最高分: {result['top_name']} ({result['top_score']})")
    print(f"及格人数: {result['passed']}")
    print(f"优秀名单: {', '.join(result['excellent'])}")
    print("按班级:")
    for c, st in result["by_class"].items():
        print(f"  {c}: {st['count']}人, 平均 {st['avg']}")


if __name__ == "__main__":
    main()
```

运行：

```bash
python csv_stats.py
```

**验收清单：**
- [x] `python csv_stats.py` 无报错
- [x] 平均分、最高分正确
- [x] 有按班级统计
- [x] 用了函数默认参数（如 `pass_line=60`）
- [x] 缺文件或坏分数时有友好报错，而不是堆栈直接炸脸

---

### 18:05–18:15｜加练（10 分）

任选完成（已做写回 CSV + `sys.argv`）：

1. **写回结果**：把汇总写到 `summary.csv`（用 `csv.DictWriter`）

```python
def write_summary(path: Path, result: dict):
    rows = [
        {
            "scope": "all",
            "name": result["top_name"],
            "count": result["count"],
            "avg": result["avg"],
            "passed": result["passed"],
            "excellent": ",".join(result["excellent"]),
        }
    ]
    for c, st in result["by_class"].items():
        rows.append({
            "scope": "class",
            "name": c,
            "count": st["count"],
            "avg": st["avg"],
            "passed": "",
            "excellent": "",
        })

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["scope", "name", "count", "avg", "passed", "excellent"]
        )
        writer.writeheader()
        writer.writerows(rows)
```

2. **命令行参数雏形**（对标 `node script.js --file x` / `process.argv`）：

```python
import sys
path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("students.csv")
```

- `sys.argv[0]` → 脚本名
- `sys.argv[1]` → 传入的文件路径
- 未传参 → 默认同目录 `students.csv`

试跑：`python csv_stats.py students.csv`

3. 把 `Frank` 的分数改成 `abc`，确认报错信息读得懂，再改回来

---

### 18:15–18:20｜复盘收工（5 分）

写 `notes.md`：

```md
# Day02
- 今天学会：默认参数、*args/**kwargs、csv.DictReader、try/except
- 和 JS 对比：...
- 卡过的点：...
- 明天预告：pathlib 整理 + 异常分层 + 小 CLI（argparse）
```

收工确认：

- [x] 目录有：`students.csv`、`csv_stats.py`、`day02.md`、`summary.csv`
- [x] 明天从 `cd ~/code/ai-learning` + `source .venv/bin/activate` + `cd day03` 开始

---

## 验收清单（全日）

- [x] 函数进阶三个点都会用
- [x] CSV 读写跑通，知道 score 要转 int
- [x] `csv_stats.py` 含班级汇总
- [x] 有基础异常处理
- [x] 接触 `sys.argv`（可明天用 argparse 加深）
- [x] 写回 `summary.csv`（DictWriter）

## 实际产出文件

- `students.csv`
- `csv_stats.py`
- `summary.csv`（及练习文件 `test1.py` / `test2.py` / `test3.py`）

## 明日预告

`argparse` 做真正的小 CLI（输入文件路径 / 及格线）+ 把 JSON 版与 CSV 版统计抽成可复用函数；若还有余力，接触 `httpx` 发一次 GET（为后面调 LLM API 热身）
