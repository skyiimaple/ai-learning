# Pydantic In/Out
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    score: int = Field(ge=0, le=100)
    class_id: int = Field(ge=1)


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    score: int | None = Field(default=None, ge=0, le=100)
    class_id: int | None = Field(default=None, ge=1)


class StudentOut(BaseModel):
    id: int
    name: str
    score: int
    class_id: int
    class_name: str
