from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    category_id: int | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None


class PostOut(BaseModel):
    id: int
    title: str
    category_id: int | None = None
