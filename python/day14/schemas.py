from pydantic import BaseModel, Field


class AgentIn(BaseModel):
    message: str = Field(min_length=1, description="用户自然语言问题")
    temperature: float = Field(default=0, ge=0, le=2)


class ToolStep(BaseModel):
    tool: str
    arguments: dict
    result: dict | list | str | int | float | bool | None


class AgentOut(BaseModel):
    answer: str
    steps: list[ToolStep]
    model: str
    stopped: bool = False
