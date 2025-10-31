from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schema import UserCreate, UserListResponse, UserResponse, UserRole, UserUpdate
from app.modules.auth.services.auth_service import AuthService


def test_get_authorization_url(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        url = service.get_authorization_url()

        assert url == "https://auth.url"


def test_load_sealed_session_success(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        session = service.load_sealed_session("sealed_session")

        assert session is not None


def test_load_sealed_session_none(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    mock_workos_client.user_management.load_sealed_session.side_effect = Exception()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        session = service.load_sealed_session("invalid")

        assert session is None


def test_load_sealed_session_empty(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        session = service.load_sealed_session(None)

        assert session is None


def test_authenticate_with_code_success(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    mock_workos_client.user_management.authenticate_with_code.return_value.sealed_session = "sealed_token"
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        with patch("app.modules.auth.services.auth_service.settings") as mock_settings:
            mock_settings.WORKOS_COOKIE_PASSWORD = "x" * 43
            service = AuthService(user_repository=mock_user_repo)
            result = service.authenticate_with_code("code")

            assert result == "sealed_token"


def test_authenticate_with_code_no_password(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        with patch("app.modules.auth.services.auth_service.settings") as mock_settings:
            mock_settings.WORKOS_COOKIE_PASSWORD = ""
            service = AuthService(user_repository=mock_user_repo)
            with pytest.raises(AuthenticationError):
                service.authenticate_with_code("code")


def test_authenticate_with_code_short_password(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        with patch("app.modules.auth.services.auth_service.settings") as mock_settings:
            mock_settings.WORKOS_COOKIE_PASSWORD = "short"
            service = AuthService(user_repository=mock_user_repo)
            with pytest.raises(AuthenticationError):
                service.authenticate_with_code("code")


@pytest.mark.asyncio
async def test_get_or_create_user_from_workos_user_existing(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    existing_user = User(id=1, workos_id="workos_123", email="test@example.com")
    mock_user_repo.get_by_workos_id = AsyncMock(return_value=existing_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.get_or_create_user_from_workos_user("workos_123", "test@example.com")

        assert result == existing_user


@pytest.mark.asyncio
async def test_get_or_create_user_from_workos_user_new(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_workos_id = AsyncMock(return_value=None)
    new_user = User(id=1, workos_id="workos_123", email="test@example.com")
    mock_user_repo.create = AsyncMock(return_value=new_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.get_or_create_user_from_workos_user("workos_123", "test@example.com")

        assert result == new_user
        mock_user_repo.create.assert_called_once()


def test_get_logout_url_success(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    mock_session = MagicMock()
    mock_session.get_logout_url.return_value = "https://logout.url"
    mock_workos_client.user_management.load_sealed_session.return_value = mock_session
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        url = service.get_logout_url("sealed_session")

        assert url == "https://logout.url"


def test_get_logout_url_none(mock_workos_client: MagicMock) -> None:
    mock_user_repo = MagicMock()
    mock_workos_client.user_management.load_sealed_session.return_value = None
    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient", return_value=mock_workos_client):
        service = AuthService(user_repository=mock_user_repo)
        url = service.get_logout_url("invalid")

        assert url is None


@pytest.mark.asyncio
async def test_create_user_success(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_email = AsyncMock(return_value=None)
    new_user = User(id=1, email="new@example.com", role=UserRole.USER)
    mock_user_repo.create = AsyncMock(return_value=new_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        user_data = UserCreate(email="new@example.com", role=UserRole.USER)
        result = await service.create_user(user_data)

        assert isinstance(result, UserResponse)
        assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(mock_session: MagicMock, mock_user: User) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        user_data = UserCreate(email="test@example.com", role=UserRole.USER)
        with pytest.raises(ValueError):
            await service.create_user(user_data)


@pytest.mark.asyncio
async def test_update_user_success(mock_session: MagicMock, mock_user: User) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)
    mock_user_repo.get_by_email = AsyncMock(return_value=None)
    updated_user = User(id=1, email="updated@example.com", role=UserRole.ADMIN)
    mock_user_repo.update = AsyncMock(return_value=updated_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        user_data = UserUpdate(email="updated@example.com", role=UserRole.ADMIN)
        result = await service.update_user(1, user_data)

        assert isinstance(result, UserResponse)
        assert result.email == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_id = AsyncMock(return_value=None)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        user_data = UserUpdate(email="updated@example.com")
        result = await service.update_user(999, user_data)

        assert result is None


@pytest.mark.asyncio
async def test_delete_user_success(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.delete = AsyncMock(return_value=True)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.delete_user(1)

        assert result is True


@pytest.mark.asyncio
async def test_get_user_success(mock_session: MagicMock, mock_user: User) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.get_user(1)

        assert isinstance(result, UserResponse)
        assert result.id == mock_user.id


@pytest.mark.asyncio
async def test_get_user_not_found(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_id = AsyncMock(return_value=None)

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.get_user(999)

        assert result is None


@pytest.mark.asyncio
async def test_get_users(mock_session: MagicMock) -> None:
    mock_user_repo = MagicMock(spec=UserRepository)
    users = [User(id=i, email=f"user{i}@example.com") for i in range(3)]
    mock_user_repo.get_all_paginated = AsyncMock(return_value=(users, 3))

    with patch("app.modules.auth.services.auth_service.workos.WorkOSClient"):
        service = AuthService(user_repository=mock_user_repo)
        result = await service.get_users(skip=0, limit=100)

        assert isinstance(result, UserListResponse)
        assert result.total == 3
