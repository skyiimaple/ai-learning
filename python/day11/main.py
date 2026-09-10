import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extract import extract_score_report
from schemas import ExtractIn, ScoreReport

app = FastAPI(title="Day11 Structured Extract")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/extract", response_model=ScoreReport)
def extract(body: ExtractIn):
    try:
        return extract_score_report(body.text)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
