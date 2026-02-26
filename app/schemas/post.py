from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    content: str


class PostOut(BaseModel):
    id: int
    content: str
    image_url: str | None
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
