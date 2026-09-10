from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Day05 API")


class GreetOut(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"message": "Hello, World!", "ok": True}


@app.get("/hellow", response_model=GreetOut)
def hellow(name: str):
    return {"message": f"Hello, {name}!", "ok": True}


@app.get("/add")
def add(a: int = Query(..., ge=0, deprecated="必填"), b: int = Query(default=5)):
    # Query(...) = 必填，对标 zod 必填字段
    return {"result": a + b}
