from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.modules.auth.middleware import get_current_admin_user, get_current_user
from app.modules.auth.models import User


@pytest.mark.asyncio
async def test_get_current_user_no_session_cookie(mock_request: MagicMock, mock_session: MagicMock) -> None:
    mock_request.cookies = {}
    mock_user_repo = MagicMock()
    mock_auth_service = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, mock_user_repo, mock_auth_service)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_session(mock_request: MagicMock, mock_session: MagicMock) -> None:
    mock_request.cookies = {"wos_session": "invalid"}
    mock_user_repo = MagicMock()
    mock_auth_service = MagicMock()
    mock_auth_service.load_sealed_session.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, mock_user_repo, mock_auth_service)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(mock_request: MagicMock, mock_session: MagicMock, mock_user: User) -> None:
    mock_request.cookies = {"wos_session": "valid_session"}
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_workos_id = AsyncMock(return_value=mock_user)
    mock_auth_service = MagicMock()

    mock_session_obj = MagicMock()
    mock_auth_response = MagicMock()
    mock_auth_response.authenticated = True
    mock_auth_response.user = MagicMock()
    mock_auth_response.user.id = "workos_123"
    mock_auth_response.user.email = "test@example.com"
    mock_session_obj.authenticate.return_value = mock_auth_response
    mock_auth_service.load_sealed_session.return_value = mock_session_obj

    result = await get_current_user(mock_request, mock_user_repo, mock_auth_service)

    assert result == mock_user


@pytest.mark.asyncio
async def test_get_current_user_creates_new_user(mock_request: MagicMock, mock_session: MagicMock) -> None:
    mock_request.cookies = {"wos_session": "valid_session"}
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_workos_id = AsyncMock(return_value=None)
    new_user = User(id=1, workos_id="workos_123", email="test@example.com")
    mock_user_repo.create = AsyncMock(return_value=new_user)
    mock_auth_service = MagicMock()

    mock_session_obj = MagicMock()
    mock_auth_response = MagicMock()
    mock_auth_response.authenticated = True
    mock_auth_response.user = MagicMock()
    mock_auth_response.user.id = "workos_123"
    mock_auth_response.user.email = "test@example.com"
    mock_session_obj.authenticate.return_value = mock_auth_response
    mock_auth_service.load_sealed_session.return_value = mock_session_obj

    result = await get_current_user(mock_request, mock_user_repo, mock_auth_service)

    assert result == new_user
    mock_user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_admin_user_success(mock_admin_user: User) -> None:
    result = await get_current_admin_user(mock_admin_user)
    assert result == mock_admin_user


@pytest.mark.asyncio
async def test_get_current_admin_user_insufficient_permissions(mock_user: User) -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(mock_user)

    assert exc_info.value.status_code == 403
