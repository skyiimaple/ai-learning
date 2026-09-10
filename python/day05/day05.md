# Day 05 · FastAPI 第一课

- **日期**：2026-07-30
- **时段**：11:00–12:00（上午集中学完；原计划午后块提前完成）
- **阶段**：A 路线 · 第 1 个月 · 开始 FastAPI
- **今日主题**：最小 FastAPI 服务 + 接上前几天的成绩统计，对标 Express 路由
- **原则**：动手为主；统计逻辑继续复用 Day03，不重写
- **状态**：已完成 ✅

## 今日目标

1. 装好 `fastapi` / `uvicorn`，跑通 `/health`
2. 会写路由、查询参数、路径参数，用 Pydantic 做响应模型
3. 完成主产出：读 CSV/JSON → 返回成绩摘要的 HTTP API
4. （加练）CORS 或一个 POST 接口

## 今日不学

数据库/SQLAlchemy、JWT 鉴权、Streaming/SSE、LLM API、前端页面

---

## 时间表（原计划）

| 时间 | 内容 | 产出 |
|------|------|------|
| 11:00–11:15 | 开工 + 复习 | venv；Day03/04 还能跑 |
| 11:15–12:00 | 安装 + Hello FastAPI | `/health` 200 |
| 12:00–14:00 | **午餐午休** | — |
| 14:00–14:50 | 路由 / 查询参数 / Pydantic | 几个练习接口 |
| 14:50–14:55 | 休息 | — |
| 14:55–15:45 | 接入成绩统计 | `GET /summary` |
| 15:45–15:50 | 休息 | — |
| 15:50–16:40 | 路径参数 + 校验 + 错误处理 | 404/业务错误友好返回 |
| 16:40–16:45 | 休息 | — |
| 16:45–17:30 | 主产出整理 | `day05` 可 `uvicorn` 启动 |
| 17:30–17:35 | 休息 | — |
| 17:35–17:55 | 加练 | CORS 或 POST |
| 17:55–18:00 | 复盘 | 对照 Express |

---

## 环境

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day05 && cd day05
pip install "fastapi[standard]"
```

全课程共用根目录 `.venv`，不要在 `day05/` 再建虚拟环境。

---

## 详细安排

### 11:00–11:15｜开工（15 分）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
python day03/cli.py day02/students.csv -o /tmp/s.csv
python day04/batch_stats.py day04/data
cd day05
```

**验收：** 前两天脚本正常；在 `day05` 目录。

---

### 11:15–12:00｜Hello FastAPI（45 分）

对标 Express：

```js
app.get("/health", (req, res) => res.json({ ok: true }));
```

`main.py`（练习）：

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Day05 API")

class GreetOut(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/hello", response_model=GreetOut)
def hello(name: str = Query(default="Maple", min_length=1)):
    return GreetOut(message=f"你好, {name}")

@app.get("/add")
def add(a: int = Query(...), b: int = Query(default=0)):
    return {"sum": a + b}
```

启动：

```bash
uvicorn main:app --reload --port 8000
# 或：fastapi dev main.py
```

```bash
curl http://127.0.0.1:8000/health
# 文档：http://127.0.0.1:8000/docs
```

**刻意记：**

- `app = FastAPI()` ≈ `const app = express()`
- `@app.get` ≈ `app.get`
- `--reload` ≈ nodemon
- `/docs` 是自动 OpenAPI

**验收：**

- [x] `/health` 通
- [x] 打开过 `/docs`

---

### 路由 / 查询参数 / Pydantic

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class GreetOut(BaseModel):
    message: str

@app.get("/hello", response_model=GreetOut)
def hello(name: str = Query(default="Maple", min_length=1)):
    return GreetOut(message=f"你好, {name}")

@app.get("/add")
def add(a: int = Query(...), b: int = Query(default=0)):
    # Query(...) = 必填，对标 zod 必填字段
    return {"sum": a + b}
```

```bash
curl "http://127.0.0.1:8000/hello?name=Ada"
curl "http://127.0.0.1:8000/add?a=3&b=4"
curl "http://127.0.0.1:8000/add"   # 应 422
```

**验收：**

- [x] 知道 `Query` / `response_model` 干什么
- [x] 缺必填参数会 422

---

### 接入成绩摘要（主文件 `summary.py`）

复用 Day03：

```python
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day03"))

from loaders import load_students
from stats_core import summarize

app = FastAPI(title="Day05 Scores API")

class SummaryOut(BaseModel):
    count: int
    avg: float
    top_name: str
    top_score: int
    passed: int
    excellent: list[str]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/summary", response_model=SummaryOut)
def get_summary(
    file: str = Query(default="day02/students.csv", description="相对仓库根的路径"),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    path = ROOT / file
    try:
        students = load_students(path)
        result = summarize(students, pass_line=pass_line)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result.get("count", 0) == 0:
        raise HTTPException(status_code=404, detail="没有学生数据")

    return SummaryOut(
        count=result["count"],
        avg=result["avg"],
        top_name=result["top_name"],
        top_score=result["top_score"],
        passed=result["passed"],
        excellent=result["excellent"],
    )
```

启动成绩 API：

```bash
uvicorn summary:app --reload --port 8000
```

```bash
curl "http://127.0.0.1:8000/summary"
curl "http://127.0.0.1:8000/summary?file=day01/data.json&pass_line=90"
curl "http://127.0.0.1:8000/summary?file=nope.csv"
```

**验收：**

- [x] CSV / JSON 都能返回摘要
- [x] 缺文件 → 404；坏分数 → 400
- [x] `/docs` 里能看到 `SummaryOut`

---

### 路径参数 + 按班级

```python
@app.get("/summary/by-class/{class_name}")
def summary_by_class(
    class_name: str,
    file: str = Query(default="day02/students.csv"),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    path = ROOT / file
    try:
        students = load_students(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filtered = [s for s in students if s.get("class") == class_name]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"没有班级: {class_name}")

    result = summarize(filtered, pass_line=pass_line)
    return {
        "class": class_name,
        "count": result["count"],
        "avg": result["avg"],
        "passed": result["passed"],
    }
```

```bash
curl "http://127.0.0.1:8000/summary/by-class/A"
curl "http://127.0.0.1:8000/summary/by-class/Z"   # 404
```

**对比：**

| FastAPI | Express 直觉 |
|---------|----------------|
| `/summary/by-class/{class_name}` | `/summary/by-class/:className` |
| `Query` | `req.query` |
| `HTTPException` | `res.status(404).json(...)` |
| Pydantic | Zod + 响应类型 |

**验收：**

- [x] 路径参数能取到班级
- [x] 不存在的班级 404

---

### 加练：POST from-list

```python
class StudentIn(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    class_name: str = Field(alias="class", default="未知")
    model_config = {"populate_by_name": True}

@app.post("/summary/from-list")
def summary_from_list(students: list[StudentIn], pass_line: int = 60):
    data = [{"name": s.name, "score": s.score, "class": s.class_name} for s in students]
    return summarize(data, pass_line=pass_line)
```

```bash
curl -X POST "http://127.0.0.1:8000/summary/from-list?pass_line=60" \
  -H "Content-Type: application/json" \
  -d '[{"name":"Ada","score":95,"class":"A"},{"name":"Bob","score":55,"class":"B"}]'
```

---

## 验收清单（全日）

- [x] `uvicorn` 能启动，`/health` 通
- [x] `GET /summary` 支持换文件、换及格线
- [x] `GET /summary/by-class/{class_name}` 通
- [x] `/docs` 用过
- [x] （加练）POST `/summary/from-list`

## 实际产出文件

- `main.py`（Hello / Query 练习）
- `summary.py`（成绩 API 主文件）

## 明日预告

Pydantic 模型再扎实一点 + 依赖注入（`Depends`）整理「加载文件」；或把 Day04 批量扫目录做成 `GET /batch`。
