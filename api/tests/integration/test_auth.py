from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.modules.auth.schema import UserCreate, UserResponse, UserRole, UserUpdate


@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.get_authorization_url") as mock_get_url:
        mock_get_url.return_value = "https://auth.url"
        response = await client.get("/auth/login")
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert data["authorization_url"] == "https://auth.url"


@pytest.mark.asyncio
async def test_callback(client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.authenticate_with_code") as mock_auth:
        with patch("app.modules.auth.services.auth_service.AuthService.load_sealed_session") as mock_load:
            with patch("app.modules.auth.services.auth_service.AuthService.get_or_create_user_from_workos_user") as mock_get_user:
                mock_auth.return_value = "sealed_session_token"
                mock_session = MagicMock()
                mock_auth_response = MagicMock()
                mock_auth_response.authenticated = True
                mock_auth_response.user = MagicMock()
                mock_auth_response.user.id = "workos_123"
                mock_auth_response.user.email = "test@example.com"
                mock_session.authenticate.return_value = mock_auth_response
                mock_load.return_value = mock_session
                mock_get_user.return_value = AsyncMock()
                
                response = await client.get("/auth/callback?code=test_code")
                assert response.status_code == 307


@pytest.mark.asyncio
async def test_logout(client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.get_logout_url") as mock_logout:
        mock_logout.return_value = "https://logout.url"
        response = await client.get("/auth/logout")
        assert response.status_code == 307


@pytest.mark.asyncio
async def test_get_current_user_info(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "role" in data
    assert data["role"] == UserRole.USER


@pytest.mark.asyncio
async def test_create_user(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.create_user") as mock_create:
        mock_user_response = UserResponse(
            id=3,
            email="newuser@example.com",
            role=UserRole.USER,
            workos_id=None,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        mock_create.return_value = mock_user_response
        
        user_data = UserCreate(email="newuser@example.com", role=UserRole.USER)
        response = await admin_client.post("/auth/users", json=user_data.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_create_user_unauthorized(authenticated_client: AsyncClient) -> None:
    user_data = UserCreate(email="newuser@example.com", role=UserRole.USER)
    response = await authenticated_client.post("/auth/users", json=user_data.model_dump())
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.get_users") as mock_get_users:
        from app.modules.auth.schema import UserListResponse
        mock_response = UserListResponse(
            users=[],
            total=0,
            skip=0,
            limit=100,
        )
        mock_get_users.return_value = mock_response
        
        response = await admin_client.get("/auth/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_get_users_unauthorized(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.get("/auth/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.get_user") as mock_get_user:
        mock_user_response = UserResponse(
            id=1,
            email="test@example.com",
            role=UserRole.USER,
            workos_id=None,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        mock_get_user.return_value = mock_user_response
        
        response = await admin_client.get("/auth/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_user_not_found(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.get_user") as mock_get_user:
        mock_get_user.return_value = None
        
        response = await admin_client.get("/auth/users/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.update_user") as mock_update:
        mock_user_response = UserResponse(
            id=1,
            email="updated@example.com",
            role=UserRole.USER,
            workos_id=None,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        mock_update.return_value = mock_user_response
        
        user_data = UserUpdate(email="updated@example.com")
        response = await admin_client.put("/auth/users/1", json=user_data.model_dump(exclude_none=True))
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.update_user") as mock_update:
        mock_update.return_value = None
        
        user_data = UserUpdate(email="updated@example.com")
        response = await admin_client.put("/auth/users/99999", json=user_data.model_dump(exclude_none=True))
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.delete_user") as mock_delete:
        mock_delete.return_value = True
        
        response = await admin_client.delete("/auth/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


@pytest.mark.asyncio
async def test_delete_user_not_found(admin_client: AsyncClient) -> None:
    with patch("app.modules.auth.services.auth_service.AuthService.delete_user") as mock_delete:
        mock_delete.return_value = False
        
        response = await admin_client.delete("/auth/users/99999")
        assert response.status_code == 404
