from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    phone: str | None = None
    is_admin: bool


class UpdateProfileRequest(BaseModel):
    username: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
