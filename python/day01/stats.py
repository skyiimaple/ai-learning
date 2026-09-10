import json
from pathlib import Path

def load_students(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def summarize(students):
    if not students:
        return {"count": 0}

    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    passed = [s for s in students if s["score"] >= 60]
    excellent = [s["name"] for s in students if s["score"] >= 90]

    return {
        "count": len(students),
        "avg": round(sum(scores) / len(scores), 1),
        "top_name": top["name"],
        "top_score": top["score"],
        "passed": len(passed),
        "excellent": excellent,
    }

def main():
    path = Path(__file__).with_name("data.json")
    students = load_students(path)
    result = summarize(students)

    print(f"人数: {result['count']}")
    print(f"平均分: {result['avg']}")
    print(f"最高分: {result['top_name']} ({result['top_score']})")
    print(f"及格人数: {result['passed']}")
    print(f"优秀名单: {', '.join(result['excellent'])}")
    # 按分数从高到低排序打印
    print('按分数从高到低排序',sorted(students, key=lambda x: x["score"], reverse=True))

if __name__ == "__main__":
    main()