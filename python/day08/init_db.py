import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("scores.db")

SCHEMA = """
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;

CREATE TABLE classes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
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
    conn.executemany("INSERT INTO classes(id,name) VALUES (?,?)", [(1, "A"), (2, "B")])
    conn.executemany(
        "INSERT INTO students(name,score,class_id) VALUES (?,?,?)",
        [
            ("Alice", 85, 1),
            ("Bob", 90, 2),
            ("Charlie", 78, 1),
            ("David", 88, 2),
            ("Eve", 92, 1),
            ("Frank", 80, 2),
            ("George", 75, 1),
            ("Helen", 85, 2),
        ],
    )
    conn.commit()
    conn.close()
    print(f"已写入：{DB.resolve()}")


if __name__ == "__main__":
    main()
