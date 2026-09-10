import sys
from pathlib import Path

from fastapi import HTTPException, Query

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day03"))
from loaders import load_students  # noqa: E402


def get_root() -> Path:
    return ROOT


def students_from_file(file: str = Query(default="day02/students.csv")) -> list[dict]:
    path = ROOT / file
    try:
        return load_students(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到文件: {file}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
