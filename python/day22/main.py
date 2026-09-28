"""Day22：RAG Demo 页 —— 复用 day21 索引与 ask。"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "day21"))

from index import load_index
from rag import ask
from schema import RagIn, RagOut

from common.llm import get_llm_config

_docs: list[dict] = []
_vectors = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载 day21/data 里的索引到内存。"""
    global _docs, _vectors
    try:
        _docs, _vectors = load_index()
    except FileNotFoundError as e:
        raise RuntimeError(str(e) + "（请先在 day21 运行 python index.py）") from e
    yield


app = FastAPI(title="Day22 RAG Demo", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {
        "ok": True,
        "day": 22,
        "model": cfg["model"],
        "chunks": len(_docs),
    }


@app.post("/rag/ask", response_model=RagOut)
def rag_ask(body: RagIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if _vectors is None:
        raise HTTPException(status_code=503, detail="索引未加载")
    try:
        out = ask(body.question, _docs, _vectors, top_k=body.top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"rag failed: {e}") from e
    return RagOut(**out)


# 路由必须先于 StaticFiles mount，否则会被静态抢走
static_dir = Path(__file__).with_name("static")
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8022, reload=True)
