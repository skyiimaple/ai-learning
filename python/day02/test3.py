# 要求输出：

# 总人数、平均分（1 位小数）
# 最高分是谁
# 及格人数（及格线做成参数，默认 60）
# 优秀名单（≥90）
# 按 class 分组：每班人数 + 平均分

from collections import defaultdict
import csv
from pathlib import Path

def parse_score(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"分数不是整数: {raw!r}") from e


def summarize_scores(scores):

    total = round(len(scores), 1)
    avg = round(sum(map(lambda x:x["score"], scores)) / total, 1)
    by_class = defaultdict(list)
    print(1,by_class)
    for s in scores:
        by_class[s["class"]].append(s["score"])
    # class_stats = {
    #     c: {"count": len(vals), "avg": round(sum(vals) / len(vals), 1)}
    #     for c, vals in by_class.items()
    # }
    class_stats = {}
    for c, vals in by_class.items():
        class_stats[c] = {"count": len(vals), "avg": round(sum(vals) / len(vals), 1)}
    return {
        'total': total,
        'avg': avg,
        'max_score': max(scores,key = lambda x:x["score"])["name"],
        'passed': len([s for s in scores if s["score"] >= 60]),
        'excellent': [s for s in scores if s["score"] >= 90],
        'class_stats': class_stats,
    }

def main():
    path = Path("students.csv")
    with path.open("r",encoding="utf-8",newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row['score'] = parse_score(row['score'])
    data = summarize_scores(rows)
    print(data)
    print(f"总人数: {data['total']}")
    print(f"平均分: {data['avg']}")
    print(f"最高分: {data['max_score']}")
    print(f"及格人数: {data['passed']}")
    print(f"优秀名单: {data['excellent']}")
    print(f"按班级分组: {data['class_stats']}")
    with Path("summary1.csv").open("w",encoding="utf-8",newline="") as f:
        writer = csv.DictWriter(f,data.keys())
        writer.writeheader()
        writer.writerow(data)
if __name__ == "__main__":
    main()


#     任选：

# 把汇总写到 summary.csv（csv.DictWriter）
# 支持 python csv_stats.py students.csv（sys.argv）
# 故意把分数改成 abc，看报错后再改回来