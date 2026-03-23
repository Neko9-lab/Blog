from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    type: str
    content: str
    source_id: int | None = None
    is_read: bool
    created_at: str | None = None
    actor_name: str | None = None
    actor_avatar: str | None = None
