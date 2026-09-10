from db import get_conn
from fastapi import Depends, FastAPI, Query
from models import ClassStatOut, StudentOut

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
