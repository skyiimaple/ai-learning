# 简便：在 deps 里同时导出 summarize
import sys
from pathlib import Path

from deps import ROOT, students_from_file
from exception_handlers import register_exception_handlers
from fastapi import Depends, FastAPI, HTTPException, Query
from models import BatchFileResult, BatchOut, SummaryOut
from stats_core import summarize  # 同样需 path 或从 deps 再导出

sys.path.insert(0, str(ROOT / "day03"))
sys.path.insert(0, str(ROOT / "day04"))
from io_load import load_students  # noqa: E402

app = FastAPI(title="Day06 Scores API")
register_exception_handlers(app)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/summary", response_model=SummaryOut)
def get_summary(
    students: list[dict] = Depends(students_from_file),
    pass_line: int = Query(default=60, ge=0, le=100),
):
    result = summarize(students, pass_line=pass_line)
    if not result.get("count"):
        raise HTTPException(status_code=404, detail="没有学生数据")
    return SummaryOut(**{k: result[k] for k in SummaryOut.model_fields})


def find_score_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)


@app.get("/batch", response_model=BatchOut)
def batch_summary(
    dir: str = Query(default="day04/data", description="相对仓库根的目录"),
    pass_line: int = Query(default=60, ge=0, le=100),
    merge: bool = Query(default=False),
):
    folder = ROOT / dir
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"不是目录: {dir}")
    files = find_score_files(folder)
    if not files:
        raise HTTPException(status_code=404, detail=f"没有 csv/json: {dir}")
    names = [str(p.relative_to(ROOT)) for p in files]
    if merge:
        all_students: list[dict] = []
        for f in files:
            try:
                all_students.extend(load_students(f))
            except ValueError as e:
                raise ValueError(f"{f.name}: {e}") from e
        result = summarize(all_students, pass_line=pass_line)
        return BatchOut(
            mode="merge",
            files=names,
            merged=SummaryOut(
                count=result["count"],
                avg=result["avg"],
                top_name=result["top_name"],
                top_score=result["top_score"],
                passed=result["passed"],
                excellent=result["excellent"],
            ),
        )
    results = []
    for f in files:
        try:
            result = summarize(load_students(f), pass_line=pass_line)
        except ValueError as e:
            raise ValueError(f"{f.name}: {e}") from e
        results.append(
            BatchFileResult(
                file=str(f.relative_to(ROOT)),
                count=result["count"],
                avg=result["avg"],
                top_name=result["top_name"],
            )
        )
    return BatchOut(mode="each", files=names, results=results)
