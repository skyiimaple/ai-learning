# Day 06 · Depends + Pydantic 整理 + `/batch`

- **日期**：2026-07-30
- **时段**：14:00–18:00（4 小时）
- **阶段**：A 路线 · 第 1 个月 · FastAPI
- **今日主题**：用 `Depends` 抽公共依赖；Pydantic 模型收干净；把 Day04 批量统计做成 HTTP
- **原则**：在 Day05 成绩 API 上演进，不另起炉灶重写统计
- **状态**：已完成 ✅

## 今日目标

1. 会用 `Depends` 注入「解析文件路径 / 加载学生」（对标 Express middleware / 公共 helper）
2. 请求/响应都用 Pydantic，少返回裸 `dict`
3. 完成 `GET /batch`：扫目录，逐文件或合并汇总
4. （加练）统一异常处理（`ValueError` / `AppError` handler）

## 今日不学

数据库、鉴权、Streaming、前端页、Docker

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 14:00–14:15 | 开工：复跑 Day05 | `uvicorn summary:app` 通 |
| 14:15–15:00 | Pydantic 模型整理 | `models.py` |
| 15:00–15:05 | 休息 | — |
| 15:05–16:00 | `Depends` 抽加载逻辑 | `deps.py` + 改路由 |
| 16:00–16:05 | 休息 | — |
| 16:05–17:20 | 主产出 `GET /batch` | 批量接口跑通 |
| 17:20–17:25 | 休息 | — |
| 17:25–17:50 | 加练：统一异常处理 | `exception_handlers.py` |
| 17:50–18:00 | 复盘 | 对照 middleware |

---

## 环境

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day06 && cd day06
```

禁止在 `dayNN/` 下新建 `.venv`。

---

## 详细安排

### 14:00–14:15｜开工（15 分）

```bash
cd ~/code/ai-learning/day05
uvicorn summary:app --reload --port 8000
# 另开终端
curl "http://127.0.0.1:8000/summary?file=day02/students.csv"
```

建议结构：

```text
day06/
  main.py
  models.py
  deps.py
  exception_handlers.py
```

**验收：** Day05 仍能跑；`day06` 目录就绪。

---

### 14:15–15:00｜Pydantic 模型整理（45 分）

`models.py`：

```python
from pydantic import BaseModel, Field

class SummaryOut(BaseModel):
    count: int
    avg: float
    top_name: str
    top_score: int
    passed: int
    excellent: list[str]

class ClassSummaryOut(BaseModel):
    class_name: str = Field(alias="class")
    count: int
    avg: float
    passed: int
    model_config = {"populate_by_name": True}

class StudentIn(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    class_name: str = Field(alias="class", default="未知")
    model_config = {"populate_by_name": True}

class BatchFileResult(BaseModel):
    file: str
    count: int
    avg: float
    top_name: str

class BatchOut(BaseModel):
    mode: str  # "each" | "merge"
    files: list[str]
    results: list[BatchFileResult] | None = None
    merged: SummaryOut | None = None
```

**验收：**

- [x] 模型独立成文件
- [x] `StudentIn` 支持 JSON 里的 `"class"` 字段

---

### 15:00–15:05｜休息（5 分）

---

### 15:05–16:00｜`Depends` 抽依赖（55 分）

对标：Express 里把 `loadUser` 做成 middleware / 公共函数。

`deps.py`：

```python
import sys
from pathlib import Path

from fastapi import HTTPException, Query

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day03"))
from loaders import load_students  # noqa: E402

def get_root() -> Path:
    return ROOT

def students_from_file(
    file: str = Query(default="day02/students.csv", description="相对仓库根"),
) -> list[dict]:
    path = ROOT / file
    try:
        return load_students(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

`main.py` 里用：

```python
from fastapi import Depends, FastAPI, HTTPException, Query
from deps import ROOT, students_from_file
from models import SummaryOut

import sys
sys.path.insert(0, str(ROOT / "day03"))
from stats_core import summarize

app = FastAPI(title="Day06 Scores API")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/summary", response_model=SummaryOut)
def get_summary(
    students: list[dict] = Depends(students_from_file),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    result = summarize(students, pass_line=pass_line)
    if not result.get("count"):
        raise HTTPException(status_code=404, detail="没有学生数据")
    return SummaryOut(**{k: result[k] for k in SummaryOut.model_fields})
```

**刻意记：**

- `Depends(fn)`：FastAPI 先跑 `fn`，把返回值塞进参数
- 查询参数写在依赖函数上，`/docs` 里也会出现
- 加载逻辑一处修改，多路由复用

**验收：**

- [x] `/summary` 行为与 Day05 一致
- [x] 路由里看不到 `ROOT / file` 拼路径细节（由 deps 完成）

---

### 16:00–16:05｜休息（5 分）

---

### 16:05–17:20｜主产出 `GET /batch`（75 分）

复用 Day04「扫目录 + merge」：

```python
from pathlib import Path
from fastapi import Query, HTTPException
from deps import ROOT
from models import BatchFileResult, BatchOut, SummaryOut
from io_load import load_students  # 或 day03 loaders
from stats_core import summarize

def find_score_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)

@app.get("/batch", response_model=BatchOut)
def batch_summary(
    dir: str = Query(default="day04/data", description="相对仓库根的目录"),
    pass_line: int = Query(default=60, ge=0, le=100),
    merge: bool = Query(default=False),
):
    folder = ROOT / dir
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"不是目录: {dir}")

    files = find_score_files(folder)
    if not files:
        raise HTTPException(status_code=404, detail=f"没有 csv/json: {dir}")

    names = [str(p.relative_to(ROOT)) for p in files]

    if merge:
        all_students: list[dict] = []
        for f in files:
            try:
                all_students.extend(load_students(f))
            except ValueError as e:
                raise ValueError(f"{f.name}: {e}") from e
        result = summarize(all_students, pass_line=pass_line)
        return BatchOut(
            mode="merge",
            files=names,
            merged=SummaryOut(
                count=result["count"],
                avg=result["avg"],
                top_name=result["top_name"],
                top_score=result["top_score"],
                passed=result["passed"],
                excellent=result["excellent"],
            ),
        )

    results = []
    for f in files:
        try:
            result = summarize(load_students(f), pass_line=pass_line)
        except ValueError as e:
            raise ValueError(f"{f.name}: {e}") from e
        results.append(
            BatchFileResult(
                file=str(f.relative_to(ROOT)),
                count=result["count"],
                avg=result["avg"],
                top_name=result["top_name"],
            )
        )
    return BatchOut(mode="each", files=names, results=results)
```

试跑：

```bash
uvicorn main:app --reload --port 8000
curl "http://127.0.0.1:8000/batch?dir=day04/data"
curl "http://127.0.0.1:8000/batch?dir=day04/data&merge=true&pass_line=70"
```

**验收清单：**

- [x] 逐文件模式返回多个 `results`
- [x] `merge=true` 返回 `merged`
- [x] 坏目录 / 空目录有合理 4xx

---

### 17:20–17:25｜休息（5 分）

---

### 17:25–17:50｜加练：统一异常处理（25 分）

#### 1) `ValueError` handler（已实现于 `exception_handlers.py`）

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
```

`main.py`：

```python
from exception_handlers import register_exception_handlers

app = FastAPI(title="Day06 Scores API")
register_exception_handlers(app)
```

#### 2) 进阶：注册 Day04 `AppError`（推荐写法）

```python
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day04"))

from errors import AppError, InputNotFoundError, FileFormatError, ScoreParseError

_STATUS = {
    InputNotFoundError: 404,
    FileFormatError: 400,
    ScoreParseError: 400,
}

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    status = _STATUS.get(type(exc), 400)
    return JSONResponse(
        status_code=status,
        content={"detail": str(exc)},
    )
```

路由里可直接 `raise InputNotFoundError(...)`，由 handler 转成 JSON（对标 Express 错误中间件）。

**验收：**

- [x] `ValueError` 不再砸 traceback，返回 `{"detail": "..."}`
- [x] 理解 `AppError` handler 可按子类映射状态码

---

### 17:50–18:00｜复盘（10 分）

口述：

1. `Depends` 解决了什么重复代码
2. `/batch` 和 Day04 CLI 的对应关系
3. 为什么响应要用 `response_model`；handler 和 `HTTPException` 的分工

---

## 验收清单（全日）

- [x] `models.py` + `deps.py` + `main.py` 分层清楚
- [x] `/summary` 改用 `Depends` 后行为不变
- [x] `/batch` 支持 each / merge
- [x] `/docs` 里参数与模型正确
- [x] 统一异常处理（至少 `ValueError` handler）

## 实际产出文件

- `models.py`
- `deps.py`
- `main.py`
- `exception_handlers.py`
- `app_start.py`（从 Day05 拷的起点备份）

## 明日预告

SQL 够用版入门（SQLite + 原始 SQL 或 SQLModel）或 FastAPI CRUD 第一张表；按精力二选一。
