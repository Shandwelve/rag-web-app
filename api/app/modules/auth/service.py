from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import workos
from fastapi import Depends
from jose import JWTError, jwt
from workos.types.sso import SsoProviderType

from app.core.config import settings
from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schema import Token, TokenData, UserRole, WorkOSUser, UserCreate, UserUpdate, UserResponse, UserListResponse


class AuthService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
    ) -> None:
        self.client = workos.WorkOSClient(api_key=settings.WORKOS_API_KEY, client_id=settings.WORKOS_CLIENT_ID)
        self.user_repository = user_repository

    def create_access_token(self, data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            workos_id: str = payload.get("sub")
            if workos_id is None:
                raise AuthenticationError("Invalid token")
            return TokenData(workos_id=workos_id)
        except JWTError:
            raise AuthenticationError("Invalid token")

    def get_authorization_url(self, state: str, provider: SsoProviderType) -> str:
        return self.client.sso.get_authorization_url(
            redirect_uri=settings.WORKOS_REDIRECT_URI,
            state=state,
            provider=provider,
        )

    def get_user_info(self, code: str) -> WorkOSUser:
        try:
            profile = self.client.sso.get_profile_and_token(code=code)
            user_info = profile.profile

            return WorkOSUser(
                workos_id=user_info.id,
                email=user_info.email,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to get user info: {str(e)}")

    async def get_or_create_user(self, workos_user: WorkOSUser) -> User:
        user = await self.user_repository.get_by_workos_id(workos_user.workos_id)

        if user:
            user.email = workos_user.email
            return await self.user_repository.update(user)

        user = User(
            workos_id=workos_user.workos_id,
            email=workos_user.email,
            role=UserRole.USER,
        )
        return await self.user_repository.create(user)

    async def authenticate_user(self, workos_user: WorkOSUser) -> Token:
        user = await self.get_or_create_user(workos_user)
        access_token = self.create_access_token(data={"sub": user.workos_id})
        return Token(access_token=access_token, token_type="bearer")

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user = User(
            email=user_data.email,
            role=user_data.role,
            workos_id=None
        )
        created_user = await self.user_repository.create(user)
        return UserResponse(
            id=created_user.id,
            workos_id=created_user.workos_id,
            email=created_user.email,
            role=created_user.role,
            created_at=created_user.created_at.isoformat(),
            updated_at=created_user.updated_at.isoformat()
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
            updated_at=updated_user.updated_at.isoformat()
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
            updated_at=user.updated_at.isoformat()
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
                updated_at=user.updated_at.isoformat()
            )
            for user in users
        ]
        return UserListResponse(
            users=user_responses,
            total=total,
            skip=skip,
            limit=limit
        )
