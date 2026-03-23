from pydantic import BaseModel, Field, model_validator


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


class BanUserRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)
    permanent: bool = False
    duration_days: int | None = None

    @model_validator(mode="after")
    def validate_duration(self):
        if not self.permanent and (self.duration_days is None or self.duration_days < 1):
            raise ValueError("duration_days is required for temporary bans")
        return self
