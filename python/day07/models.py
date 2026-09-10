from pydantic import BaseModel


class StudentOut(BaseModel):
    name: str
    score: int
    class_name: str


class ClassStatOut(BaseModel):
    class_name: str
    count: int
    avg: float
