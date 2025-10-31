from typing import Annotated

import workos
from fastapi import Depends
from workos.session import Session

from app.core.config import settings
from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schema import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserRole,
    UserUpdate,
)


class AuthService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
    ) -> None:
        self.client = workos.WorkOSClient(api_key=settings.WORKOS_API_KEY, client_id=settings.WORKOS_CLIENT_ID)
        self.user_repository = user_repository

    def get_authorization_url(self) -> str:
        return self.client.user_management.get_authorization_url(
            provider="authkit",
            redirect_uri=settings.WORKOS_REDIRECT_URI,
        )

    def load_sealed_session(self, sealed_session: str | None) -> Session | None:
        if not sealed_session:
            return None
        try:
            return self.client.user_management.load_sealed_session(
                sealed_session=sealed_session,
                cookie_password=settings.WORKOS_COOKIE_PASSWORD,
            )
        except Exception:
            return None

    def authenticate_with_code(self, code: str) -> str:
        if not settings.WORKOS_COOKIE_PASSWORD:
            raise AuthenticationError("WORKOS_COOKIE_PASSWORD is not configured. Please set it in your .env file.")

        cookie_password = settings.WORKOS_COOKIE_PASSWORD.strip()
        if len(cookie_password) < 43:
            raise AuthenticationError(
                "WORKOS_COOKIE_PASSWORD must be a Fernet key (32 bytes URL-safe base64 encoded, 43-44 characters). "
                'Generate one with: python3 -c "import secrets, base64; key = secrets.token_bytes(32); '
                'print(base64.urlsafe_b64encode(key).decode())"'
            )

        try:
            auth_response = self.client.user_management.authenticate_with_code(
                code=code,
                session={"seal_session": True, "cookie_password": cookie_password},
            )
            return auth_response.sealed_session
        except Exception as e:
            error_msg = str(e)
            if "Fernet key" in error_msg:
                raise AuthenticationError(
                    f"{error_msg}. Generate a valid Fernet key with: "
                    'python3 -c "import secrets, base64; key = secrets.token_bytes(32); '
                    'print(base64.urlsafe_b64encode(key).decode())"'
                )
            raise AuthenticationError(f"Failed to authenticate with code: {error_msg}")

    async def get_or_create_user_from_workos_user(self, workos_user_id: str, email: str) -> User:
        user = await self.user_repository.get_by_workos_id(workos_user_id)

        if user:
            if user.email != email:
                user.email = email
                return await self.user_repository.update(user)
            return user

        user = User(
            workos_id=workos_user_id,
            email=email,
            role=UserRole.USER,
        )
        return await self.user_repository.create(user)

    def get_logout_url(self, sealed_session: str | None) -> str | None:
        if not sealed_session:
            return None
        try:
            session = self.load_sealed_session(sealed_session)
            if session:
                return session.get_logout_url()
        except Exception:
            pass
        return None

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        user = User(email=user_data.email, role=user_data.role, workos_id=None)
        created_user = await self.user_repository.create(user)
        return UserResponse(
            id=created_user.id,
            workos_id=created_user.workos_id,
            email=created_user.email,
            role=created_user.role,
            created_at=created_user.created_at.isoformat(),
            updated_at=created_user.updated_at.isoformat(),
        )

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        if user_data.email is not None:
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("User with this email already exists")
            user.email = user_data.email

        if user_data.role is not None:
            user.role = user_data.role

        updated_user = await self.user_repository.update(user)
        return UserResponse(
            id=updated_user.id,
            workos_id=updated_user.workos_id,
            email=updated_user.email,
            role=updated_user.role,
            created_at=updated_user.created_at.isoformat(),
            updated_at=updated_user.updated_at.isoformat(),
        )

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repository.delete(user_id)

    async def get_user(self, user_id: int) -> UserResponse | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        return UserResponse(
            id=user.id,
            workos_id=user.workos_id,
            email=user.email,
            role=user.role,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

    async def get_users(self, skip: int = 0, limit: int = 100) -> UserListResponse:
        users, total = await self.user_repository.get_all_paginated(skip, limit)
        user_responses = [
            UserResponse(
                id=user.id,
                workos_id=user.workos_id,
                email=user.email,
                role=user.role,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat(),
            )
            for user in users
        ]
        return UserListResponse(users=user_responses, total=total, skip=skip, limit=limit)
