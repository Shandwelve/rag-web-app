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
from app.modules.auth.schema import Token, TokenData, UserRole, WorkOSUser


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
