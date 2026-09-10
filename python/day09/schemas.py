from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatIn(BaseModel):
    messages: list[Message] = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatOut(BaseModel):
    content: str
    model: str
    usage: dict | None = None
