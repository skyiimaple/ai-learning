from pydantic import BaseModel, Field


class SummaryOut(BaseModel):
    count: int
    avg: float
    top_name: str
    top_score: int
    passed: int
    excellent: list[str]


class ClassSummaryOut(BaseModel):
    class_name: str = Field(alias="class")
    count: int
    avg: float
    passed: int
    model_config = {"populate_by_name": True}


class StudentIn(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    class_name: str = Field(alias="class", default="未知")
    model_config = {"populate_by_name": True}


class BatchFileResult(BaseModel):
    file: str
    count: int
    avg: float
    top_name: str


class BatchOut(BaseModel):
    mode: str
    files: list[str]
    results: list[BatchFileResult] | None = None
    merged: SummaryOut | None = None
