from pydantic import BaseModel, Field, model_validator


class StudentScore(BaseModel):
    name: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


class ScoreReport(BaseModel):
    summary: str = Field(min_length=1)
    students: list[StudentScore] = Field(min_length=1)
    pass_count: int = Field(ge=0)

    @model_validator(mode="after")
    def pass_count_matches_students(self):
        expected = sum(1 for s in self.students if s.score >= 60)
        if self.pass_count != expected:
            raise ValueError(
                f"pass_count={self.pass_count} 与实际及格人数 {expected} 不一致"
            )
        return self


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, description="原始成绩描述文本")
