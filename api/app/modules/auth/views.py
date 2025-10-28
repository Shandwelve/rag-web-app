from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from workos.types.sso import SsoProviderType

from app.core.schema import MessageResponse
from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.middleware import get_current_admin_user, get_current_user
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schema import (
    LoginResponse,
    Token,
    UserCreate,
    UserInfo,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.services.state_manager import StateManager

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    state_manager: Annotated[StateManager, Depends(StateManager)],
    provider: SsoProviderType = "GoogleOAuth",
) -> LoginResponse:
    state = state_manager.generate_state()
    authorization_url = auth_service.get_authorization_url(state, provider)
    return LoginResponse(authorization_url=authorization_url)


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    state_manager: Annotated[StateManager, Depends(StateManager)],
) -> Token:
    try:
        if not state_manager.validate_state(state):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter",
            )

        workos_user = auth_service.get_user_info(code)
        token = await auth_service.authenticate_user(workos_user)
        return token
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserInfo:
    return UserInfo(
        id=current_user.id,
        workos_id=current_user.workos_id,
        email=current_user.email,
        role=current_user.role,
    )


@router.post("/refresh")
async def refresh_token(
    token: str,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> Token:
    try:
        token_data = auth_service.verify_token(token)
        user = await user_repository.get_by_workos_id(token_data.workos_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        new_token = auth_service.create_access_token(data={"sub": user.workos_id})
        return Token(access_token=new_token, token_type="bearer")
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> UserResponse:
    try:
        return await auth_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=UserListResponse)
async def get_users(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    return await auth_service.get_users(skip, limit)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> UserResponse:
    user = await auth_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> UserResponse:
    try:
        user = await auth_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    auth_service: Annotated[AuthService, Depends(AuthService)],
    current_admin: Annotated[User, Depends(get_current_admin_user)],
) -> MessageResponse:
    success = await auth_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MessageResponse(message="User deleted successfully")
