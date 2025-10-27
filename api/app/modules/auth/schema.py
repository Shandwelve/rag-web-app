from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    workos_id: str


class WorkOSUser(BaseModel):
    workos_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None


class UserInfo(BaseModel):
    id: int
    workos_id: str | None
    email: str | None
    role: UserRole


class LoginResponse(BaseModel):
    authorization_url: str
