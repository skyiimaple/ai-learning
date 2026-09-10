from collections import defaultdict


def format_stats(vals):
    count = len(vals)
    return {"count": count, "avg": round(sum(vals) / count, 1)}


def summarize(students, pass_line=60):
    """students: list[dict]，每项至少有 name / score，可选 class"""
    if not students:
        return {"count": 0}
    scores = [s["score"] for s in students]
    top = max(students, key=lambda s: s["score"])
    by_class = defaultdict(list)
    for s in students:
        # 这里要 append 分数 int，不要 append 整个学生 dict
        by_class[s.get("class", "未知")].append(s["score"])

    class_stats = {c: format_stats(vals) for c, vals in by_class.items()}
    return {
        "count": len(students),
        "avg": round(sum(scores) / len(scores), 1),
        "top_name": top["name"],
        "top_score": top["score"],
        "passed": sum(1 for s in students if s["score"] >= pass_line),
        "excellent": [s["name"] for s in students if s["score"] >= 90],
        "by_class": class_stats,
    }
