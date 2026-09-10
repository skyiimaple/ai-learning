import json
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schemas import ChatIn

from common.llm import chat_completions_stream, get_llm_config

app = FastAPI(title="Day10 Chat Streaming API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event_stream(messages: list[dict], temperature: float):
    try:
        for piece in chat_completions_stream(messages, temperature):
            # SSE 一帧：data: <text>\n\n
            yield f"data: {json.dumps({'content': piece}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except httpx.HTTPStatusError as e:
        err = {"error": str(e)}
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        err = {"error": f"stream failed: {e}"}
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@app.get("/health")
def health():
    cfg = get_llm_config()
    return {"ok": True, "model": cfg["model"]}


@app.post("/chat/stream")
def chat_stream(body: ChatIn):
    try:
        get_llm_config()  # 提前检查 Key
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        sse_event_stream(messages, body.temperature),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# 静态演示页（17:00 段用）
static_dir = Path(__file__).with_name("static")
static_dir.mkdir(exist_ok=True)
app.mount("/demo", StaticFiles(directory=static_dir, html=True), name="demo")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
