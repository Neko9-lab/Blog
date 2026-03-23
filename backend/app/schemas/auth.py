from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    account: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str | None = None
    phone: str | None = None
    password: str
    code: str


class ResetPasswordRequest(BaseModel):
    account: str
    code: str
    new_password: str
