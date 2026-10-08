"""Day25 知识库 API + 静态页。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from rag import ask

app = FastAPI(title="day25-kb")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RagIn(BaseModel):
    question: str = Field(min_length=1)


@app.post("/rag/ask")
def rag_ask(body: RagIn):
    try:
        return ask(body.question)
    except Exception as e:
        raise HTTPException(500, str(e)) from e


static = Path(__file__).with_name("static")
static.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=static, html=True), name="static")
