# Day 08 · FastAPI 学生表 CRUD

- **日期**：2026-08-04
- **时段**：15:00–18:00（3 小时）
- **阶段**：A 路线 · 第 1 个月 · FastAPI + SQL
- **今日主题**：在 Day07 的 SQLite 上补齐 POST / GET/:id / PUT / DELETE
- **原则**：先跑通 REST 直觉（对标 Express），SQL 仍用手写 `?` 占位符
- **状态**：已完成 ✅

## 今日目标

1. 完成学生对资源的 CRUD 四个动词
2. 请求体用 Pydantic 校验；不存在资源返回 404
3. （加练）`pandas.read_sql` 读一版聚合

## 今日不学

SQLAlchemy ORM、Alembic 迁移、鉴权、分页深挖、PostgreSQL

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:00–15:15 | 开工：从 Day07 拷贝演进 | `day08` + `scores.db` |
| 15:15–16:00 | POST 创建 + GET 详情 | 能增、能按 id 查 |
| 16:00–16:05 | 休息 | — |
| 16:05–16:50 | PUT 更新 + DELETE | CRUD 闭环 |
| 16:50–16:55 | 休息 | — |
| 16:55–17:40 | 分层整理 + 错误处理 | `db` / `schemas` / `crud` / `main` |
| 17:40–17:45 | 休息 | — |
| 17:45–17:55 | 加练 pandas | 一行聚合 |
| 17:55–18:00 | 复盘 | 对照前端 fetch |

---

## 环境

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day08 && cd day08

cp ../day07/init_db.py .
cp ../day07/db.py .
python init_db.py

# pip install pandas   # 加练需要时
```

---

## 详细安排

### 15:00–15:15｜开工（15 分）

```bash
cd ~/code/ai-learning/day07
uvicorn main:app --port 8000 &
sleep 1
curl -s "http://127.0.0.1:8000/stats/by-class"
kill %1 2>/dev/null
cd ../day08
python init_db.py
```

建议结构：

```text
day08/
  init_db.py
  scores.db
  db.py
  schemas.py
  crud.py
  main.py
  pandas_drill.py
```

**验收：** `scores.db` 有学生数据；目录就绪。

---

### 15:15–16:00｜POST + GET by id（45 分）

对标 Express：`app.post('/students')` / `app.get('/students/:id')`。

#### 1) `schemas.py`

```python
from pydantic import BaseModel, Field

class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    score: int = Field(ge=0, le=100)
    class_id: int = Field(ge=1)

class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    score: int | None = Field(default=None, ge=0, le=100)
    class_id: int | None = Field(default=None, ge=1)

class StudentOut(BaseModel):
    id: int
    name: str
    score: int
    class_id: int
    class_name: str
```

#### 2) `crud.py`（创建与按 id 查）

```python
from db import get_conn

STUDENT_SELECT = """
SELECT s.id, s.name, s.score, s.class_id, c.name AS class_name
FROM students AS s
JOIN classes AS c ON s.class_id = c.id
"""

def get_student(student_id: int) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute(
            STUDENT_SELECT + " WHERE s.id = ?",
            (student_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_student(name: str, score: int, class_id: int) -> dict:
    conn = get_conn()
    try:
        cls = conn.execute(
            "SELECT id FROM classes WHERE id = ?", (class_id,)
        ).fetchone()
        if not cls:
            raise ValueError(f"班级不存在: class_id={class_id}")

        cur = conn.execute(
            "INSERT INTO students (name, score, class_id) VALUES (?, ?, ?)",
            (name, score, class_id),
        )
        conn.commit()
        new_id = cur.lastrowid
    finally:
        conn.close()
    student = get_student(new_id)
    assert student is not None
    return student
```

#### 3) 路由

```python
from fastapi import FastAPI, HTTPException, status
from schemas import StudentCreate, StudentOut
import crud

app = FastAPI(title="Day08 Students CRUD")

@app.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(body: StudentCreate):
    try:
        return crud.create_student(body.name, body.score, body.class_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/students/{student_id}", response_model=StudentOut)
def read_student(student_id: int):
    row = crud.get_student(student_id)
    if not row:
        raise HTTPException(status_code=404, detail="学生不存在")
    return row
```

```bash
uvicorn main:app --reload --port 8000

curl -s -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{"name":"Grace","score":91,"class_id":1}'

curl -s "http://127.0.0.1:8000/students/1"
curl -s "http://127.0.0.1:8000/students/999"   # 404
```

**验收：**

- [x] POST 返回 201 + 带 `id`
- [x] 不存在 id → 404
- [x] 非法 `class_id` → 400

---

### 16:00–16:05｜休息（5 分）

---

### 16:05–16:50｜PUT + DELETE（45 分）

```python
# crud.py 追加

def update_student(student_id: int, **fields) -> dict | None:
    data = {k: v for k, v in fields.items() if v is not None}
    if not data:
        return get_student(student_id)

    conn = get_conn()
    try:
        if "class_id" in data:
            cls = conn.execute(
                "SELECT id FROM classes WHERE id = ?", (data["class_id"],)
            ).fetchone()
            if not cls:
                raise ValueError(f"班级不存在: class_id={data['class_id']}")

        cols = ", ".join(f"{k} = ?" for k in data)
        values = list(data.values()) + [student_id]
        cur = conn.execute(
            f"UPDATE students SET {cols} WHERE id = ?",
            values,
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
    finally:
        conn.close()
    return get_student(student_id)

def delete_student(student_id: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
```

路由：

```python
from schemas import StudentUpdate
from fastapi import Response

@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, body: StudentUpdate):
    try:
        row = crud.update_student(
            student_id,
            name=body.name,
            score=body.score,
            class_id=body.class_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not row:
        raise HTTPException(status_code=404, detail="学生不存在")
    return row

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    ok = crud.delete_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="学生不存在")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

```bash
curl -s -X PUT "http://127.0.0.1:8000/students/1" \
  -H "Content-Type: application/json" \
  -d '{"score":85}'

curl -s -o /dev/null -w "%{http_code}\n" -X DELETE "http://127.0.0.1:8000/students/6"
# 期望 204
```

**刻意记：**

| 方法 | 含义 | 常见状态码 |
|------|------|------------|
| POST | 新建 | 201 |
| GET | 读取 | 200 / 404 |
| PUT | 更新 | 200 / 404 |
| DELETE | 删除 | 204 / 404 |

**验收：**

- [x] 改分数后再 GET 能看到变化
- [x] 删除成功 204；再 GET 404

---

### 16:50–16:55｜休息（5 分）

---

### 16:55–17:40｜整理 + 列表接口（45 分）

把列表也迁过来：

```python
@app.get("/students", response_model=list[StudentOut])
def list_students(min_score: int = 0):
    conn = get_conn()
    try:
        rows = conn.execute(
            STUDENT_SELECT + " WHERE s.score >= ? ORDER BY s.score DESC",
            (min_score,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
```

```bash
curl -s "http://127.0.0.1:8000/students?min_score=60"
# /docs 里 Try it out 走一遍 CRUD
```

**验收清单：**

- [x] CRUD 路径都在 `/docs`
- [x] 非法 body（如 score=200）→ 422
- [x] `crud.py` 里没有 FastAPI import（纯数据层）

---

### 17:40–17:45｜休息（5 分）

---

### 17:45–17:55｜加练：`pandas.read_sql`（10 分）

```bash
pip install pandas
```

`pandas_drill.py`：

```python
import pandas as pd
from db import get_conn

conn = get_conn()
df = pd.read_sql(
    """
    SELECT c.name AS class_name, AVG(s.score) AS avg_score, COUNT(*) AS cnt
    FROM students s
    JOIN classes c ON s.class_id = c.id
    GROUP BY c.id
    """,
    conn,
)
conn.close()
print(df)
```

---

### 17:55–18:00｜复盘（5 分）

口述：

1. REST 四动词 ↔ SQL INSERT/SELECT/UPDATE/DELETE
2. body 用 Pydantic；路径参数 `student_id: int`
3. 404 vs 422 vs 400 分别何时出现

---

## 验收清单（全日）

- [x] `POST /students` 创建成功
- [x] `GET /students/{id}`、`PUT`、`DELETE` 行为正确
- [x] 分层：`schemas` / `crud` / `main`
- [x] （加练）`pandas.read_sql` 打出按班平均分

## 实际产出文件

- `init_db.py` / `db.py` / `scores.db`
- `schemas.py`
- `crud.py`
- `main.py`
- `pandas_drill.py`

## 明日预告

给 CRUD 加 CORS；或开始 **LLM API 第一课**（接一个国内模型 Chat Completions，为第 4 周 Streaming 打底）——按精力二选一。
