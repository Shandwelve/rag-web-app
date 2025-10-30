from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.schema import MessageResponse
from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.middleware import get_current_admin_user, get_current_user
from app.modules.auth.models import User
from app.modules.auth.schema import (
    LoginResponse,
    UserCreate,
    UserInfo,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.auth.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> LoginResponse:
    authorization_url = auth_service.get_authorization_url()
    return LoginResponse(authorization_url=authorization_url)


@router.get("/callback")
async def callback(
    code: str,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> RedirectResponse:
    try:
        sealed_session = auth_service.authenticate_with_code(code)
        
        session = auth_service.load_sealed_session(sealed_session)
        if not session:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=auth_failed")
        
        auth_response = session.authenticate()
        if not auth_response.authenticated or not auth_response.user:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=auth_failed")
        
        workos_user = auth_response.user
        await auth_service.get_or_create_user_from_workos_user(
            workos_user_id=workos_user.id,
            email=workos_user.email if workos_user.email else "",
        )
        
        response = RedirectResponse(url=settings.FRONTEND_URL)
        response.set_cookie(
            "wos_session",
            sealed_session,
            secure=False,
            httponly=True,
            samesite="lax",
        )
        return response
    except AuthenticationError as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?error={str(e)}")
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=auth_failed")


@router.get("/logout")
async def logout(
    request: Request,
    auth_service: Annotated[AuthService, Depends(AuthService)],
) -> RedirectResponse:
    sealed_session = request.cookies.get("wos_session")
    logout_url = auth_service.get_logout_url(sealed_session)
    
    if logout_url:
        response = RedirectResponse(url=logout_url)
    else:
        response = RedirectResponse(url=settings.FRONTEND_URL)
    
    response.delete_cookie("wos_session")
    return response


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
