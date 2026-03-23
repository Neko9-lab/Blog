from pydantic import BaseModel


class CommentCreate(BaseModel):
    post_id: int
    content: str
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    post_id: int
    content: str
    parent_id: int | None = None
    level: int
