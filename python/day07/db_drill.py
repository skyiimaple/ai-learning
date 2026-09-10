import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("scores.db")


def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def list_students(min_score: int = 0):
    with connect() as conn:
        rows = conn.execute(
            """
            select s.name,s.score,c.name class_name 
            from students s 
            join classes c 
            on s.class_id = c.id 
            where s.score >=? 
            order by s.score desc
            """,
            (min_score,),
        ).fetchall()
    return [dict(row) for row in rows]


def class_stats():
    with connect() as conn:
        rows = conn.execute(
            """
            select c.name class_name,count(*) count,ROUND(AVG(s.score),1) avg_score 
            from students s 
            join classes c 
            on s.class_id = c.id
            group by c.id
            order by c.name
            """,
        ).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    print("及格及以上:", list_students(80))
    print("按班:", class_stats())
