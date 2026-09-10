# SQL 操作数据库
from db import get_conn
from schemas import StudentCreate

STUDENT_SELECT = """
select s.id,s.name,s.score,c.id class_id,c.name class_name
from students s 
join classes c on s.class_id = c.id
"""


def get_student(id: int):
    conn = get_conn()
    try:
        row = conn.execute(
            STUDENT_SELECT + " where s.id = ?",
            (id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_student(student: StudentCreate):
    conn = get_conn()
    try:
        class_row = conn.execute(
            """
            select id from classes where id = ?
            """,
            (student.class_id,),
        ).fetchone()
        if not class_row:
            raise ValueError(f"班级不存在: class_id={student.class_id}")
        row = conn.execute(
            """
            insert into students (name, score, class_id) values (?, ?, ?)
            """,
            (student.name, student.score, student.class_id),
        )
        conn.commit()
        new_id = row.lastrowid
    finally:
        conn.close()

    student = get_student(new_id)
    assert student is not None
    return student


def delete_student(student_id: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def update_student(student_id: int, **fields) -> dict | None:
    # 只更新传入的非 None 字段
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


def list_students(min_score: int = 0) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            STUDENT_SELECT + " WHERE s.score >= ? ORDER BY s.score DESC",
            (min_score,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
