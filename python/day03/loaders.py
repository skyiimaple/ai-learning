import csv
import json
from pathlib import Path

from stats_core import summarize


def parse_score(raw) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError) as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)  # JSON 用 json.load(f)，不要套 DictReader
    return [
        {
            "name": r["name"],
            "score": parse_score(r["score"]),
            "class": r.get("class", "未知"),
        }
        for r in rows
    ]


def load_csv(path: Path):
    print(f"加载CSV文件: {path}")
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [
        {
            "name": r["name"],
            "score": parse_score(r["score"]),
            "class": r.get("class", "未知"),
        }
        for r in rows
    ]


def load_students(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json(path)
    elif suffix == ".csv":
        return load_csv(path)
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")


def main():
    print(summarize(load_students(Path("../day02/students.csv"))))
    print(summarize(load_students(Path("../day01/data.json"))))


if __name__ == "__main__":
    main()
