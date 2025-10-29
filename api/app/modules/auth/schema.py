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


class TokenExchangeRequest(BaseModel):
    code: str
    state: str


class UserCreate(BaseModel):
    email: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    email: str | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    id: int
    workos_id: str | None
    email: str | None
    role: UserRole
    created_at: str
    updated_at: str


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    skip: int
    limit: int
