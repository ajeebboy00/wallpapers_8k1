import uuid
import pytest
from httpx import AsyncClient
from fastapi import Depends, status
from sqlalchemy import select

from app.api.deps import get_current_user, require_admin, require_super_admin
from app.core.constants import UserRole
from app.core.security import get_password_hash
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User

# Register test routes on app for RBAC testing
@app.get("/api/v1/test/admin-only", tags=["Testing"])
async def endpoint_admin_only(user: User = Depends(require_admin)):
    return {"status": "ok", "message": "Admin access granted", "role": user.role.value}

@app.get("/api/v1/test/super-admin-only", tags=["Testing"])
async def endpoint_super_admin_only(user: User = Depends(require_super_admin)):
    return {"status": "ok", "message": "Super admin access granted", "role": user.role.value}


def make_test_user_data():
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Test User {uid}",
        "email": f"user_{uid}@example.com",
        "password": "Password123!"
    }


@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient, db_session):
    """Test 1: Successful user registration returns 201, token pair, and user profile."""
    data = make_test_user_data()
    response = await client.post("/api/v1/auth/register", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    token_data = body["data"]

    # Verify token payload
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] == 1800  # 30 minutes in seconds

    # Verify user profile in payload
    user_info = token_data["user"]
    assert user_info["email"] == data["email"]
    assert user_info["name"] == data["name"]
    assert user_info["role"] == UserRole.USER.value
    assert user_info["is_active"] is True
    assert user_info["email_verified"] is False
    assert "password_hash" not in user_info

    # Verify database state
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.password_hash.startswith("$2b$")
    assert db_user.password_hash != data["password"]


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient):
    """Test 2: Registering with an existing email returns 409 Conflict."""
    data = make_test_user_data()
    # First registration
    resp1 = await client.post("/api/v1/auth/register", json=data)
    assert resp1.status_code == status.HTTP_201_CREATED

    # Duplicate registration
    resp2 = await client.post("/api/v1/auth/register", json=data)
    assert resp2.status_code == status.HTTP_409_CONFLICT
    body = resp2.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_user_registration_weak_password(client: AsyncClient):
    """Test 3: Passwords shorter than 8 characters are rejected with 422."""
    data = make_test_user_data()
    data["password"] = "short"
    response = await client.post("/api/v1/auth/register", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_user_registration_invalid_email(client: AsyncClient):
    """Test 4: Malformed email strings are rejected with 422."""
    data = make_test_user_data()
    data["email"] = "not-a-valid-email"
    response = await client.post("/api/v1/auth/register", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    """Test 5: Valid credentials return 200 and a fresh JWT / refresh token pair."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    assert reg_resp.status_code == status.HTTP_201_CREATED

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    assert login_resp.status_code == status.HTTP_200_OK
    body = login_resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["user"]["email"] == data["email"]


@pytest.mark.asyncio
async def test_user_login_invalid_password(client: AsyncClient):
    """Test 6: Incorrect password returns 401 Unauthorized with INVALID_CREDENTIALS."""
    data = make_test_user_data()
    await client.post("/api/v1/auth/register", json=data)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": "WrongPassword123!"}
    )
    assert login_resp.status_code == status.HTTP_401_UNAUTHORIZED
    body = login_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_user_login_nonexistent_email(client: AsyncClient):
    """Test 7: Non-existent email returns 401 Unauthorized with INVALID_CREDENTIALS."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody_exists_here@example.com", "password": "Password123!"}
    )
    assert login_resp.status_code == status.HTTP_401_UNAUTHORIZED
    body = login_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_user_login_deactivated_account(client: AsyncClient, db_session):
    """Test 8: Deactivated accounts are rejected with 401 ACCOUNT_DEACTIVATED."""
    data = make_test_user_data()
    await client.post("/api/v1/auth/register", json=data)

    # Deactivate account directly in database
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    assert login_resp.status_code == status.HTTP_401_UNAUTHORIZED
    body = login_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ACCOUNT_DEACTIVATED"


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    """Test 9: GET /api/v1/auth/me returns the authenticated user profile."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    access_token = reg_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == data["email"]
    assert body["data"]["name"] == data["name"]
    assert "password_hash" not in body["data"]


@pytest.mark.asyncio
async def test_get_current_user_missing_token(client: AsyncClient):
    """Test 10: GET /api/v1/auth/me without Bearer token returns 401 NOT_AUTHENTICATED."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test 11: GET /api/v1/auth/me with invalid JWT returns 401 UNAUTHORIZED."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_refresh_token_rotation_success(client: AsyncClient):
    """Test 12: Refresh token rotation issues a new token pair and revokes the old token."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    old_access_token = reg_resp.json()["data"]["access_token"]
    old_refresh_token = reg_resp.json()["data"]["refresh_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert refresh_resp.status_code == status.HTTP_200_OK
    body = refresh_resp.json()
    assert body["success"] is True
    new_access_token = body["data"]["access_token"]
    new_refresh_token = body["data"]["refresh_token"]

    assert new_access_token != old_access_token
    assert new_refresh_token != old_refresh_token

    # Verify new access token works on /me
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert me_resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token_reuse_rejected(client: AsyncClient):
    """Test 13: Attempting to reuse a rotated/revoked refresh token is rejected with 401."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    first_refresh_token = reg_resp.json()["data"]["refresh_token"]

    # First rotation succeeds
    rotate_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token}
    )
    assert rotate_resp.status_code == status.HTTP_200_OK

    # Second attempt with same token must fail
    reuse_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token}
    )
    assert reuse_resp.status_code == status.HTTP_401_UNAUTHORIZED
    body = reuse_resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_logout_revokes_session(client: AsyncClient):
    """Test 14: Logout revokes the refresh token and prevents future refreshes."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    refresh_token = reg_resp.json()["data"]["refresh_token"]

    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert logout_resp.status_code == status.HTTP_200_OK
    assert logout_resp.json()["data"]["revoked"] is True

    # Attempting to refresh with revoked token fails
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(client: AsyncClient):
    """Test 15: Forgot password generates a reset token, allowing password update and revoking sessions."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    old_refresh_token = reg_resp.json()["data"]["refresh_token"]

    # 1. Request forgot password
    forgot_resp = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": data["email"]}
    )
    assert forgot_resp.status_code == status.HTTP_200_OK
    reset_token = forgot_resp.json()["data"]["reset_token"]
    assert reset_token is not None

    # 2. Reset password using token
    new_password = "NewSecurePassword456!"
    reset_resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": new_password}
    )
    assert reset_resp.status_code == status.HTTP_200_OK
    assert reset_resp.json()["data"]["updated"] is True

    # 3. Old password fails
    old_login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

    # 4. New password succeeds
    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": new_password}
    )
    assert new_login.status_code == status.HTTP_200_OK

    # 5. Old sessions revoked
    revoked_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert revoked_refresh.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    """Test 16: Resetting password with invalid/tampered token is rejected with 400."""
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "completely.bogus.reset-token", "new_password": "NewSecurePassword456!"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_RESET_TOKEN"


@pytest.mark.asyncio
async def test_rbac_standard_user_forbidden_on_admin_endpoint(client: AsyncClient):
    """Test 17: Standard USER role receives 403 FORBIDDEN_ROLE on admin routes."""
    data = make_test_user_data()
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    user_token = reg_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN_ROLE"


@pytest.mark.asyncio
async def test_rbac_admin_allowed_on_admin_endpoint(client: AsyncClient, db_session):
    """Test 18: ADMIN role is granted access on admin routes."""
    data = make_test_user_data()
    await client.post("/api/v1/auth/register", json=data)

    # Elevate role to ADMIN directly in database
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    user.role = UserRole.ADMIN
    await db_session.commit()

    # Log in as ADMIN to acquire token with ADMIN claims
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    admin_token = login_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == UserRole.ADMIN.value


@pytest.mark.asyncio
async def test_rbac_admin_forbidden_on_super_admin_endpoint(client: AsyncClient, db_session):
    """Test 19: ADMIN role is rejected with 403 on SUPER_ADMIN-only routes."""
    data = make_test_user_data()
    await client.post("/api/v1/auth/register", json=data)

    # Elevate to ADMIN
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    user.role = UserRole.ADMIN
    await db_session.commit()

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    admin_token = login_resp.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/test/super-admin-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "FORBIDDEN_ROLE"


@pytest.mark.asyncio
async def test_rbac_super_admin_allowed_on_all_endpoints(client: AsyncClient, db_session):
    """Test 20: SUPER_ADMIN role is granted access on both admin and super-admin routes."""
    data = make_test_user_data()
    await client.post("/api/v1/auth/register", json=data)

    # Elevate to SUPER_ADMIN
    stmt = select(User).where(User.email == data["email"])
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    user.role = UserRole.SUPER_ADMIN
    await db_session.commit()

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]}
    )
    super_admin_token = login_resp.json()["data"]["access_token"]

    # Test admin route
    resp_admin = await client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert resp_admin.status_code == status.HTTP_200_OK

    # Test super-admin route
    resp_super = await client.get(
        "/api/v1/test/super-admin-only",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert resp_super.status_code == status.HTTP_200_OK
    assert resp_super.json()["role"] == UserRole.SUPER_ADMIN.value
