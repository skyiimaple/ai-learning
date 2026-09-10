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
