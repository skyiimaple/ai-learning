import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import chat_with_tools
from schemas import AgentIn, AgentOut

from common.llm import get_llm_config

app = FastAPI(title="Day14 Score Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/agent/chat", response_model=AgentOut)
def agent_chat(body: AgentIn):
    try:
        get_llm_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    try:
        out = chat_with_tools(body.message, temperature=body.temperature)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"agent failed: {e}") from e

    if out.get("stopped") and not out.get("answer"):
        raise HTTPException(
            status_code=504,
            detail="超过最大工具步数，未得到最终回答",
        )

    return AgentOut(**out)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8014, reload=True)
