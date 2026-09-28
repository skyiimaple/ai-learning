from pydantic import BaseModel, Field


class RagIn(BaseModel):
    question: str = Field(min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=8)


class RagHit(BaseModel):
    id: str
    source: str
    text: str
    score: float


class RagOut(BaseModel):
    answer: str
    hits: list[RagHit]
    model: str
