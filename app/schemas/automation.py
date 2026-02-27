from pydantic import BaseModel, Field


class N8NPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    author_email: str | None = None
