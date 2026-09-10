import csv
import sys
from pathlib import Path
from collections import defaultdict


def parse_score(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e


def load_students(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"找不到文件: {path}")
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


def summarize(students, pass_line=60):
    if not students:
        return {"count": 0}

    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    by_class = defaultdict(list)
    for s in students:
        by_class[s["class"]].append(s["score"])

    class_stats = {
        c: {"count": len(vals), "avg": round(sum(vals) / len(vals), 1)}
        for c, vals in by_class.items()
    }

    return {
        "count": len(students),
        "avg": round(sum(scores) / len(scores), 1),
        "top_name": top["name"],
        "top_score": top["score"],
        "passed": sum(1 for s in students if s["score"] >= pass_line),
        "excellent": [s["name"] for s in students if s["score"] >= 90],
        "by_class": class_stats,
    }


def write_summary(path: Path, result: dict):
    """把汇总写成 summary.csv（总体一行 + 各班一行）"""
    rows = [
        {
            "scope": "all",
            "name": result["top_name"],
            "count": result["count"],
            "avg": result["avg"],
            "passed": result["passed"],
            "excellent": ",".join(result["excellent"]),
        }
    ]
    for c, st in result["by_class"].items():
        rows.append(
            {
                "scope": "class",
                "name": c,
                "count": st["count"],
                "avg": st["avg"],
                "passed": "",
                "excellent": "",
            }
        )

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["scope", "name", "count", "avg", "passed", "excellent"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    # python csv_stats.py students.csv  → 用参数；不传则默认同目录 students.csv
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).with_name("students.csv")
    )
    try:
        students = load_students(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"读取失败: {e}")
        return

    result = summarize(students)
    print(f"人数: {result['count']}")
    print(f"平均分: {result['avg']}")
    print(f"最高分: {result['top_name']} ({result['top_score']})")
    print(f"及格人数: {result['passed']}")
    print(f"优秀名单: {', '.join(result['excellent'])}")
    print("按班级:")
    for c, st in result["by_class"].items():
        print(f"  {c}: {st['count']}人, 平均 {st['avg']}")

    out = Path(__file__).with_name("summary.csv")
    write_summary(out, result)
    print(f"已写入: {out}")


if __name__ == "__main__":
    main()