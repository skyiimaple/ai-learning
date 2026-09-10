# Day 03 · argparse 小 CLI + 抽公共统计

- **日期**：2026-07-29
- **时段**：15:45–18:15（2 小时 30 分；17:30 后内容晚上补完）
- **阶段**：A 路线 · 第 1 个月 · Python 速通
- **今日主题**：用 `argparse` 做正式小 CLI，并把统计逻辑抽成可复用模块
- **原则**：动手为主；环境用仓库根目录同一个 `.venv`
- **状态**：已完成 ✅

## 今日目标

1. 会用 `argparse` 定义参数（输入文件、及格线、输出路径），替代手写 `sys.argv`
2. 把「统计」从读写/CLI 里拆出来，Day01 JSON 与 Day02 CSV 共用同一套 `summarize`
3. 完成主产出：脚本能按参数跑通，并写出 `summary.csv`
4. （加练）用 `httpx` 发一次 GET，对标前端 `fetch`

## 今日不学

FastAPI、异步深入、`asyncio` 全家桶、LLM API、装饰器/OOP

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:45–15:55 | 开工 + 复习 Day02 | 根目录 venv，`csv_stats.py` 能跑 |
| 15:55–16:35 | `argparse` 入门 | 能解析 `--file` / `--pass-line` |
| 16:35–16:40 | 休息 | — |
| 16:40–17:25 | 抽公共模块 + 双数据源 | `stats_core.py` + JSON/CSV 加载 |
| 17:25–17:30 | 休息 | — |
| 17:30–18:00 | 主产出 CLI | `cli.py` 跑通并写 `summary.csv` |
| 18:00–18:10 | 加练 `httpx` | 一次 GET 打印状态码/片段 |
| 18:10–18:15 | 复盘 | 过一遍要点 |

---

## 环境（全课程共用）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day03 && cd day03
```

禁止在 `dayNN/` 下新建 `.venv`。

---

## 详细安排

### 15:45–15:55｜开工 + 复习 Day02（10 分）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
cd day02
python csv_stats.py students.csv
cd ../day03
```

口述回顾：

- CSV 字段默认是 `str`，要 `int`
- 默认参数不要用 `[]`/`{}`
- `sys.argv[1]` 是第一个参数（和 Node 下标不同）

**验收：** `(.venv)` 在；Day02 脚本仍能跑；当前在 `day03`。

---

### 15:55–16:35｜`argparse` 入门（40 分）

对标：Node 里手写 `process.argv` → 用 `commander` / `yargs` 这类库。Python 标准库就是 `argparse`。

先写练习文件 `argparse_drill.py`：

```python
import argparse
from pathlib import Path

def build_parser():
    p = argparse.ArgumentParser(description="学生成绩统计 CLI")
    p.add_argument(
        "file",
        nargs="?",  # 可选位置参数
        default="students.csv",
        help="输入文件路径（csv 或 json）",
    )
    p.add_argument(
        "--pass-line",
        type=int,
        default=60,
        help="及格线（默认 60）",
    )
    p.add_argument(
        "-o", "--output",
        default="summary.csv",
        help="汇总输出路径",
    )
    return p

if __name__ == "__main__":
    args = build_parser().parse_args()
    print("file:", Path(args.file))
    print("pass_line:", args.pass_line)
    print("output:", args.output)
```

试跑：

```bash
python argparse_drill.py
python argparse_drill.py ../day02/students.csv --pass-line 70 -o out.csv
python argparse_drill.py -h
```

**刻意记：**

1. `type=int` 会自动转换，非法数字直接报错退出
2. `-h` / `--help` 免费自带
3. `nargs="?"`：位置参数可省略，用 `default`

**验收：**

- [x] `-h` 能看懂帮助
- [x] 能打出解析后的三个字段
- [x] 传 `--pass-line abc` 会失败（预期行为）

---

### 16:35–16:40｜休息（5 分）

站起来；不要刷短视频。

---

### 16:40–17:25｜抽公共统计模块（45 分）

目标：Day01 的 JSON 与 Day02 的 CSV，**统计逻辑只写一份**。

#### 1) `stats_core.py`（纯统计，不碰文件格式）

```python
from collections import defaultdict

def format_stats(vals):
    count = len(vals)
    return {"count": count, "avg": round(sum(vals) / count, 1)}

def summarize(students, pass_line=60):
    """students: list[dict]，每项至少有 name / score，可选 class"""
    if not students:
        return {"count": 0}

    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    by_class = defaultdict(list)
    for s in students:
        # 这里要 append 分数 int，不要 append 整个学生 dict
        by_class[s.get("class", "未知")].append(s["score"])

    class_stats = {
        c: format_stats(vals)
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
```

#### 2) `loaders.py`（只负责读入成统一结构）

```python
import csv
import json
from pathlib import Path

def parse_score(raw) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError) as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)  # JSON 用 json.load(f)，不要套 DictReader
    return [
        {
            "name": r["name"],
            "score": parse_score(r["score"]),
            "class": r.get("class", "未知"),
        }
        for r in rows
    ]

def load_csv(path: Path):
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

def load_students(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json(path)
    if suffix == ".csv":
        return load_csv(path)
    raise ValueError(f"不支持的文件类型: {suffix}")
```

可直接复用 `../day01/data.json` 和 `../day02/students.csv` 测：

```bash
python -c "
from pathlib import Path
from loaders import load_students
from stats_core import summarize
print(summarize(load_students(Path('../day02/students.csv'))))
print(summarize(load_students(Path('../day01/data.json'))))
"
```

**踩坑记录：**

- `by_class[...].append(s)` 会把整个 dict 塞进去 → `sum(vals)` 报 `int + dict`；应 `append(s["score"])`
- `top = max(scores)` 得到的是数字，不能再取 `top["name"]`；应 `max(students, key=lambda s: s["score"])`
- `json.load(csv.DictReader(f))` 是错的；JSON 文件用 `json.load(f)`

**验收：**

- [x] CSV / JSON 两套数据都能算出人数、平均分
- [x] `stats_core` 里没有 `csv`/`json`/`argparse` import
- [x] 坏分数有清晰 `ValueError`

---

### 17:25–17:30｜休息（5 分）

---

### 17:30–18:00｜主产出：拼上 CLI（30 分）

写 `cli.py`：

```python
import argparse
import csv
import sys
from pathlib import Path

from loaders import load_students
from stats_core import summarize

def build_parser():
    p = argparse.ArgumentParser(description="学生成绩统计")
    p.add_argument("file", nargs="?", default="../day02/students.csv")
    p.add_argument("--pass-line", type=int, default=60)
    p.add_argument("-o", "--output", default="summary.csv")
    return p

def write_summary(path: Path, result: dict):
    rows = [{
        "scope": "all",
        "name": result.get("top_name", ""),
        "count": result.get("count", 0),
        "avg": result.get("avg", ""),
        "passed": result.get("passed", ""),
        "excellent": ",".join(result.get("excellent", [])),
    }]
    for c, st in result.get("by_class", {}).items():
        rows.append({
            "scope": "class",
            "name": c,
            "count": st["count"],
            "avg": st["avg"],
            "passed": "",
            "excellent": "",
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["scope", "name", "count", "avg", "passed", "excellent"]
        )
        w.writeheader()
        w.writerows(rows)

def main(argv=None):
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    try:
        students = load_students(path)
        result = summarize(students, pass_line=args.pass_line)
    except (FileNotFoundError, ValueError) as e:
        print(f"失败: {e}", file=sys.stderr)
        return 1

    print(f"人数: {result['count']}")
    print(f"平均分: {result['avg']}")
    print(f"最高分: {result['top_name']} ({result['top_score']})")
    print(f"及格人数: {result['passed']}")
    print(f"优秀名单: {', '.join(result['excellent'])}")
    for c, st in result["by_class"].items():
        print(f"  {c}: {st['count']}人, 平均 {st['avg']}")

    out = Path(args.output)
    write_summary(out, result)
    print(f"已写入: {out.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

试跑：

```bash
python cli.py ../day02/students.csv --pass-line 60 -o summary.csv
python cli.py ../day01/data.json --pass-line 90 -o summary_json.csv
python cli.py -h
```

**验收清单：**

- [x] CSV / JSON 都能跑
- [x] `--pass-line` 改及格人数会变
- [x] 生成 `summary.csv`
- [x] 缺文件 / 坏分数：stderr 友好提示，退出码非 0

---

### 18:00–18:10｜加练：`httpx` 一次 GET（10 分）

```bash
# 在仓库根、已激活 .venv 后
pip install httpx
cd day03
```

`http_getdrill.py`（对标 JS：`fetch(url).then(r => r.json())`）：

```python
import httpx

url = "https://jsonplaceholder.typicode.com/todos/1"
with httpx.Client(timeout=10.0) as client:
    r = client.get(url, params={"from": "day03"})
    print("status:", r.status_code)
    print("content-type:", r.headers.get("content-type"))
    data = r.json()
    print(data)
```

**验收：** 打出 `status: 200` 和一段 JSON。（若网络不行，记下错误即可。）

---

### 18:10–18:15｜复盘（5 分）

过一遍：

- `argparse` vs 手写 `sys.argv`
- 「加载 / 统计 / CLI / 写出」分层
- `httpx.get` ≈ `fetch`

---

## 验收清单（全日）

- [x] 会写带 `--pass-line` / `-o` 的 `ArgumentParser`
- [x] `stats_core.summarize` 不依赖文件格式
- [x] 同一套统计能跑 JSON + CSV
- [x] CLI 能写 `summary.csv`，错误有友好提示
- [x] （加练）`httpx` GET 跑通

## 实际产出文件

- `argparse_drill.py`
- `stats_core.py`
- `loaders.py`
- `cli.py`
- `summary.csv` / `summary_json.csv`
- `http_getdrill.py`

## 明日预告

pathlib 批量扫文件 + 异常分层（自定义错误类型）+ 小目录工具；或开始碰 FastAPI 第一课（按周进度微调）。
