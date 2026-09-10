# Day 04 · pathlib 扫目录 + 异常分层

- **日期**：2026-07-30
- **时段**：20:00–22:20（2 小时 20 分）
- **阶段**：A 路线 · 第 1 个月 · Python 速通
- **今日主题**：用 `pathlib` 批量找成绩文件 + 自定义异常分层，串起 Day03 的统计
- **原则**：动手为主；复用 `day03` 的 `summarize` / `load_students`，不重写统计
- **状态**：已完成 ✅

## 今日目标

1. 会用 `Path.glob` / `rglob` / `iterdir` 扫目录
2. 会定义并抛出/捕获自定义异常（对标前端「业务错误 vs 系统错误」）
3. 完成主产出：扫一个目录下所有 `.csv`/`.json` → 分别汇总或合并汇总

## 今日不学

FastAPI、`asyncio` 深挖、LLM API、正则进阶

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 20:00–20:10 | 开工 + 复习 Day03 | venv；`cli.py` 能跑 |
| 20:10–20:50 | pathlib 扫文件 | `path_drill.py` |
| 20:50–20:55 | 休息 | — |
| 20:55–21:35 | 自定义异常 | `errors.py` + 改造 loaders |
| 21:35–21:40 | 休息 | — |
| 21:40–22:10 | 主产出批量统计 | `batch_stats.py` |
| 22:10–22:20 | 加练 / 复盘 | 合并模式或 notes |

---

## 环境

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day04 && cd day04
```

禁止在 `dayNN/` 下新建 `.venv`。

---

## 详细安排

### 20:00–20:10｜开工（10 分）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
cd day03
python cli.py ../day02/students.csv -o /tmp/s.csv
cd ../day04
```

**验收：** Day03 CLI 仍能跑；当前在 `day04`。

---

### 20:10–20:50｜pathlib 扫目录（40 分）

对标 Node：`fs.readdir` / `glob`。Python 推荐 `pathlib.Path`。

`path_drill.py`：

```python
from pathlib import Path

root = Path(__file__).resolve().parent.parent  # ai-learning 根

print("根目录:", root)

# 1) 列出某一层
day02 = root / "day02"
for p in day02.iterdir():
    print("iterdir:", p.name, "dir?" if p.is_dir() else "file")

# 2) 通配：当前层
print("--- glob *.csv ---")
for p in day02.glob("*.csv"):
    print(p)

# 3) 递归：整个仓库里的 csv/json（演示用，文件不多）
print("--- rglob ---")
for p in root.rglob("students.csv"):
    print(p)

# 4) 组合过滤
def find_score_files(folder: Path):
    files = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)

print("--- day01+day02 成绩文件 ---")
for p in find_score_files(root / "day01") + find_score_files(root / "day02"):
    print(p.suffix, p)
```

```bash
python path_drill.py
```

**刻意记：**

| 方法 | 作用 |
|------|------|
| `Path / "a"` | 拼路径（不要自己拼字符串） |
| `iterdir()` | 只看一层 |
| `glob("*.csv")` | 一层通配 |
| `rglob("*.csv")` | 递归通配 |
| `resolve()` | 变成绝对路径 |

**验收：**

- [x] 能列出 `day02` 下的 csv
- [x] 写出 `find_score_files(folder)` 返回 `Path` 列表

---

### 20:50–20:55｜休息（5 分）

---

### 20:55–21:35｜自定义异常分层（40 分）

对标 TS：`class AppError extends Error`，再细分子类。

#### 1) `errors.py`

```python
class AppError(Exception):
    """业务可预期错误的基类（给用户看的）"""

class FileFormatError(AppError):
    """扩展名不支持 / 内容格式不对"""

class ScoreParseError(AppError):
    """分数无法转成 int"""

class InputNotFoundError(AppError):
    """输入路径不存在"""
```

**为什么要 `AppError` 基类：** CLI 里 `except AppError` 一把抓住所有业务错误，友好提示后退出；真正的 Bug（如 `NameError`）继续抛出带堆栈。没有基类就要写很长的 `except (A, B, C)`，每加一种错误都要改。

#### 2) `io_load.py`（import Day03，转换异常）

```python
import sys
from pathlib import Path

# 让 day03 可被 import
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day03"))

from loaders import load_students as _load_students  # noqa: E402
from stats_core import summarize  # noqa: E402
from errors import FileFormatError, InputNotFoundError, ScoreParseError, AppError

def load_students(path: Path):
    path = Path(path)
    if not path.exists():
        raise InputNotFoundError(f"找不到: {path}")
    try:
        return _load_students(path)
    except FileNotFoundError as e:
        raise InputNotFoundError(str(e)) from e
    except ValueError as e:
        # Day03 里分数/类型问题多是 ValueError
        msg = str(e)
        if "不支持的文件类型" in msg:
            raise FileFormatError(msg) from e
        if "分数不是整数" in msg:
            raise ScoreParseError(msg) from e
        raise AppError(msg) from e
```

CLI 里只抓 `AppError`：

```python
try:
    students = load_students(path)
except AppError as e:
    print(f"业务错误: {e}", file=sys.stderr)
    return 1
```

**验收：**

- [x] 缺文件 → `InputNotFoundError`
- [x] 扩展名 `.txt` → `FileFormatError`
- [x] 分数 `abc` → `ScoreParseError`
- [x] `except AppError` 能一把抓住上面三种

---

### 21:35–21:40｜休息（5 分）

---

### 21:40–22:10｜主产出 `batch_stats.py`（30 分）

准备测试数据：

```bash
mkdir -p data
cp ../day02/students.csv data/class_a.csv
cp ../day01/data.json data/extra.json
```

`batch_stats.py` 骨架：

```python
import argparse
import sys
from pathlib import Path

from errors import AppError
from io_load import load_students, summarize

def build_parser():
    p = argparse.ArgumentParser(description="批量成绩统计")
    p.add_argument("dir", nargs="?", default="data", help="成绩文件目录")
    p.add_argument("--pass-line", type=int, default=60)
    p.add_argument(
        "--merge",
        action="store_true",
        help="合并所有文件后再统计（默认：每个文件各统计一次）",
    )
    return p

def find_score_files(folder: Path):
    files = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)

def main(argv=None):
    args = build_parser().parse_args(argv)
    folder = Path(args.dir)
    if not folder.is_dir():
        print(f"不是目录: {folder}", file=sys.stderr)
        return 1

    files = find_score_files(folder)
    if not files:
        print(f"目录里没有 csv/json: {folder}", file=sys.stderr)
        return 1

    try:
        if args.merge:
            all_students = []
            for f in files:
                all_students.extend(load_students(f))
            result = summarize(all_students, pass_line=args.pass_line)
            print(f"[合并 {len(files)} 个文件] 人数={result['count']} 平均={result['avg']}")
        else:
            for f in files:
                result = summarize(load_students(f), pass_line=args.pass_line)
                print(f"[{f.name}] 人数={result['count']} 平均={result['avg']} 最高={result['top_name']}")
    except AppError as e:
        print(f"业务错误: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

试跑：

```bash
python batch_stats.py data
python batch_stats.py data --merge --pass-line 70
python batch_stats.py -h
```

**验收清单：**

- [x] 能扫出 `data/` 下多个文件并逐个打印
- [x] `--merge` 合并后再统计
- [x] 业务错误走 `AppError`，不是整段 traceback 砸脸

---

### 22:10–22:20｜加练 / 复盘（10 分）

任选：

1. 给 `batch_stats.py` 加 `-o summary.csv`，复用 Day03 的 `DictWriter` 思路
2. 用 `rglob` 从仓库根递归找所有 `students.csv`

复盘口述：`glob` vs `rglob`；为什么要 `AppError` 基类。

---

## 验收清单（全日）

- [x] 会用 `Path.glob` / `rglob` / `/` 拼路径
- [x] 有自定义异常层级，CLI 只抓 `AppError`
- [x] `batch_stats.py` 支持逐文件 + `--merge`
- [x] 复用了 Day03 统计，没有重写一套 `summarize`

## 实际产出文件

- `path_drill.py`
- `errors.py`
- `io_load.py`
- `batch_stats.py`
- `data/class_a.csv` / `data/extra.json`

## 明日预告

开始 **FastAPI 第一课**：装依赖、写一个 `/health` + 读 JSON 返回成绩摘要的 API（对标 Express 最小路由）。
