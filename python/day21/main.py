from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from index import load_index
from rag import ask
from schema import RagIn, RagOut

from common.llm import get_llm_config

_docs: list[dict] = []
_vectors = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动加载索引；yield 后为关闭阶段。"""
    global _docs, _vectors
    try:
        _docs, _vectors = load_index()
    except FileNotFoundError as e:
        raise RuntimeError(str(e)) from e
    yield


app = FastAPI(title="Day21 RAG API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"], "chunks": len(_docs)}


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8021, reload=True)
