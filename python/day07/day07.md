# Day 07 · SQLite + SQL 够用版 + FastAPI 读库

- **日期**：2026-08-04
- **时段**：15:30–18:00（2 小时 30 分）
- **阶段**：A 路线 · 第 1 个月 · FastAPI + SQL
- **今日主题**：用 SQLite 落成绩表，学会 SELECT/WHERE/GROUP BY，再用 FastAPI 读出来
- **原则**：SQL 只学够用；今天以「建库 + 查询 + GET」为主，完整 CRUD 可明天补写
- **状态**：已完成 ✅

## 今日目标

1. 会用 SQLite 建表、插入、基础查询（对标「前端眼里的 JSON 数组」变成表）
2. 掌握 `WHERE` / `ORDER BY` / `GROUP BY` / `JOIN`（JOIN 先看懂一例）
3. 用 Python `sqlite3` 取数；FastAPI 提供 `GET /students` 与按班级聚合

## 今日不学

PostgreSQL 部署、SQLAlchemy 全家桶、迁移工具、索引调优、鉴权

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 15:30–15:40 | 开工 + 装工具 | `day07` 目录、`scores.db` 就绪 |
| 15:40–16:25 | SQL 入门 + 灌数据 | 表 `students` / `classes` |
| 16:25–16:30 | 休息 | — |
| 16:30–17:20 | Python `sqlite3` 查询 | `db_drill.py` |
| 17:20–17:25 | 休息 | — |
| 17:25–17:55 | FastAPI 读库 API | `main.py` 两个 GET |
| 17:55–18:00 | 复盘 | 对照 JSON 文件方案 |

---

## 环境

```bash
cd ~/code/ai-learning
source .venv/bin/activate
mkdir -p day07 && cd day07
# SQLite 随 Python 自带，不必 pip
# 可选 GUI：DBeaver / DB Browser for SQLite
```

---

## 详细安排

### 15:30–15:40｜开工（10 分）

```bash
cd ~/code/ai-learning
source .venv/bin/activate
cd day06 && uvicorn main:app --port 8000 &
sleep 1
curl -s "http://127.0.0.1:8000/health"
kill %1 2>/dev/null
cd ../day07
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

**验收：** Day06 还能起；能打印 sqlite 版本。

---

### 15:40–16:25｜建库灌数 + SQL 够用（45 分）

对标直觉：

| 概念 | 前端直觉 |
|------|----------|
| 表 table | 一类 JSON 对象的数组 |
| 行 row | 一个对象 |
| 列 column | 对象的字段 |
| 主键 id | 唯一 id |

#### 1) 初始化脚本 `init_db.py`

```python
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("scores.db")

SCHEMA = """
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;

CREATE TABLE classes (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE students (
  id       INTEGER PRIMARY KEY,
  name     TEXT NOT NULL,
  score    INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
  class_id INTEGER NOT NULL,
  FOREIGN KEY (class_id) REFERENCES classes(id)
);
"""

def main():
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO classes (id, name) VALUES (?, ?)",
        [(1, "A"), (2, "B")],
    )
    conn.executemany(
        "INSERT INTO students (name, score, class_id) VALUES (?, ?, ?)",
        [
            ("Alice", 80, 1),
            ("Bob", 95, 2),
            ("Carol", 70, 1),
            ("Dave", 88, 2),
            ("Eve", 92, 1),
            ("Frank", 59, 2),
        ],
    )
    conn.commit()
    conn.close()
    print(f"已写入: {DB.resolve()}")

if __name__ == "__main__":
    main()
```

```bash
python init_db.py
sqlite3 scores.db "SELECT * FROM students;"
```

#### 2) SQL 练习（`queries.sql`）

```sql
-- 全表
SELECT id, name, score, class_id FROM students;

-- 过滤 + 排序 + 限制
SELECT name, score FROM students
WHERE score >= 60
ORDER BY score DESC
LIMIT 3;

-- 聚合（对标 Day02/03 按班统计）
SELECT class_id, COUNT(*) AS cnt, ROUND(AVG(score), 1) AS avg_score
FROM students
GROUP BY class_id;

-- JOIN（班级名拼上来）
SELECT s.name, s.score, c.name AS class_name
FROM students AS s
JOIN classes AS c ON s.class_id = c.id
ORDER BY s.score DESC;
```

**刻意记：**

- `WHERE` 过滤行；`GROUP BY` 分组后再聚合
- `JOIN ... ON` 把两表按外键拼在一起
- `?` 占位符防 SQL 注入

**验收：**

- [x] `scores.db` 存在，6 个学生
- [x] 能口述 WHERE / GROUP BY / JOIN 各干什么

---

### 16:25–16:30｜休息（5 分）

---

### 16:30–17:20｜Python `sqlite3`（50 分）

`db_drill.py`：

```python
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("scores.db")

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # 行能用列名取，像 dict
    return conn

def list_students(min_score: int = 0):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT s.name, s.score, c.name AS class_name
            FROM students AS s
            JOIN classes AS c ON s.class_id = c.id
            WHERE s.score >= ?
            ORDER BY s.score DESC
            """,
            (min_score,),
        ).fetchall()
    return [dict(r) for r in rows]

def class_stats():
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT c.name AS class_name,
                   COUNT(*) AS count,
                   ROUND(AVG(s.score), 1) AS avg
            FROM students AS s
            JOIN classes AS c ON s.class_id = c.id
            GROUP BY c.id
            ORDER BY c.name
            """
        ).fetchall()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    print("及格及以上:", list_students(60))
    print("按班:", class_stats())
```

```bash
python db_drill.py
```

对比 Day03「读 CSV 再 Python 聚合」：今天聚合可以下推到 SQL。

**验收：**

- [x] `row_factory = Row` 后能 `r["name"]`
- [x] 参数用 `(min_score,)` 元组，不要 f-string 拼 SQL

---

### 17:20–17:25｜休息（5 分）

---

### 17:25–17:55｜FastAPI 读库（30 分）

`db.py`：

```python
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("scores.db")

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn
```

`models.py`：

```python
from pydantic import BaseModel

class StudentOut(BaseModel):
    name: str
    score: int
    class_name: str

class ClassStatOut(BaseModel):
    class_name: str
    count: int
    avg: float
```

`main.py`：

```python
from fastapi import Depends, FastAPI, Query
from models import ClassStatOut, StudentOut
from db import get_conn

app = FastAPI(title="Day07 Scores DB API")

def students_from_db(min_score: int = Query(default=0, ge=0, le=100)):
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT s.name, s.score, c.name AS class_name
            FROM students AS s
            JOIN classes AS c ON s.class_id = c.id
            WHERE s.score >= ?
            ORDER BY s.score DESC
            """,
            (min_score,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/students", response_model=list[StudentOut])
def list_students(rows: list[dict] = Depends(students_from_db)):
    return rows

@app.get("/stats/by-class", response_model=list[ClassStatOut])
def stats_by_class():
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT c.name AS class_name,
                   COUNT(*) AS count,
                   ROUND(AVG(s.score), 1) AS avg
            FROM students AS s
            JOIN classes AS c ON s.class_id = c.id
            GROUP BY c.id
            ORDER BY c.name
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
```

```bash
uvicorn main:app --reload --port 8000
curl "http://127.0.0.1:8000/students?min_score=90"
curl "http://127.0.0.1:8000/stats/by-class"
```

**验收清单：**

- [x] `/students` 能按 `min_score` 过滤
- [x] `/stats/by-class` 人数、平均分合理
- [x] `/docs` 里模型正确

---

### 17:55–18:00｜复盘（5 分）

口述三句：

1. 表 ≈ 一类对象的数组；JOIN ≈ 按 id 把两个数组 merge
2. 聚合用 SQL `GROUP BY`，不必先 `load` 再 Python
3. 明天可补：`POST/PUT/DELETE` 完整 CRUD

---

## 验收清单（全日）

- [x] `init_db.py` 生成 `scores.db`
- [x] 会写 SELECT + WHERE + GROUP BY + JOIN（各一例）
- [x] `db_drill.py` 跑通
- [x] FastAPI：`GET /students`、`GET /stats/by-class`

## 实际产出文件

- `init_db.py`
- `queries.sql`
- `db_drill.py`
- `db.py`
- `models.py`
- `main.py`
- `scores.db`（运行 `init_db.py` 生成）

## 明日预告

FastAPI 对学生表做完整 CRUD（POST/PUT/DELETE）+ 简单校验；有余力再试 `pandas.read_sql`。
