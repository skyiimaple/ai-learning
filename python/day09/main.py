import sys
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent  # python/
sys.path.insert(0, str(ROOT))

from schemas import ChatIn, ChatOut  # noqa: E402

from common.llm import chat_completions, get_llm_config  # noqa: E402

app = FastAPI(title="Day09 Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn):
    try:
        data = chat_completions(
            [m.model_dump() for m in body.messages],
            temperature=body.temperature,
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"上游模型错误: {e.response.status_code} {e.response.text[:200]}",
        ) from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"请求上游失败: {e}") from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    cfg = get_llm_config()
    return ChatOut(
        content=data["choices"][0]["message"]["content"],
        model=data.get("model", cfg["model"]),
        usage=data.get("usage"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
