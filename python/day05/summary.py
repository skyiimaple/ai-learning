import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day03"))

from loaders import load_students
from stats_core import summarize

app = FastAPI(title="Day05 Scores API")


class SummaryOut(BaseModel):
    count: int
    avg: float
    top_name: str
    top_score: int
    passed: int
    excellent: list[str]


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/summary", response_model=SummaryOut)
def get_summary(
    file: str = Query(default="day02/students.csv", description="相对仓库根的路径"),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    path = ROOT / file
    try:
        students = load_students(path)
        result = summarize(students, pass_line=pass_line)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result.get("count", 0) == 0:
        raise HTTPException(status_code=404, detail="没有学生数据")

    return SummaryOut(
        count=result["count"],
        avg=result["avg"],
        top_name=result["top_name"],
        top_score=result["top_score"],
        passed=result["passed"],
        excellent=result["excellent"],
    )


@app.get("/summary/by-class/{class_name}")
def summary_by_class(
    class_name: str,
    file: str = Query(default="day02/students.csv"),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    path = ROOT / file
    try:
        students = load_students(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filtered = [s for s in students if s.get("class") == class_name]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"没有班级: {class_name}")

    result = summarize(filtered, pass_line=pass_line)
    return {
        "class": class_name,
        "count": result["count"],
        "avg": result["avg"],
        "passed": result["passed"],
    }


class StudentIn(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    class_name: str = Field(alias="class", default="未知")
    model_config = {"populate_by_name": True}


@app.post("/summary/from-list")
def summary_from_list(students: list[StudentIn], pass_line: int = 60):
    data = [{"name": s.name, "score": s.score, "class": s.class_name} for s in students]
    return summarize(data, pass_line=pass_line)
