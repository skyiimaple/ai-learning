import argparse
import csv
import sys
from pathlib import Path

from loaders import load_students
from stats_core import summarize


def build_parser():
    p = argparse.ArgumentParser(description="学生成绩统计")
    p.add_argument(
        "file",
        nargs="?",
        default="../day02/student.csv",
    )
    p.add_argument(
        "--pass-line",
        type=int,
        default=60,
        help="及格线",
    )
    p.add_argument("-o", "--output", default="summary.csv")
    return p


def write_summary(path: Path, result: dict):
    rows = [
        {
            "scope": all,
            "name": result.get("name", ""),
            "count": result.get("count", 0),
            "avg": result.get("avg", ""),
            "passed": result.get("passed", ""),
            "excellent": ",".join(result.get("excellent", [])),
        }
    ]
    for c, st in result.get("by_class", {}).items():
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
    with path.open("w", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["scope", "name", "count", "avg", "passed", "excellent"]
        )
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    try:
        students = load_students(path)
        result = summarize(students, args.pass_line)
    except (FileNotFoundError, ValueError) as e:
        print(f"失败: {e}", file=sys.stderr)
        return 1

    print(f"人数: {result.get('count', 0)}")
    print(f"平均分: {result.get('avg', 0)}")
    print(f"及格人数: {result.get('passed', 0)}")
    print(f"优秀人数: {result.get('excellent', 0)}")
    print(f"优秀学生: {','.join(result.get('excellent', []))}")
    for c, st in result["by_class"].items():
        print(f"{c}:{st['count']}人,平均分{st['avg']}")
    out = Path(args.output)
    write_summary(out, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
