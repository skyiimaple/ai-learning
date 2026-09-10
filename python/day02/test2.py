

import csv
from pathlib import Path


path = Path("students.csv")
with path.open("r",encoding="utf-8",newline="") as f:
    rows = list(csv.DictReader(f))

def parse_score(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e

for row in rows:
    row['score'] = parse_score(row['score'])
print(rows[0])
print(rows[0]["name"], type(rows[0]["score"]))  

