"""Integration tests for auth API endpoints."""

from httpx import AsyncClient

from backend.src.saas_starter.models.user import UserRole
from tests.conftest import seed_tenant_and_user


async def test_register_returns_tokens(client: AsyncClient) -> None:
    """POST /register creates tenant+user and returns tokens."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@startup.io",
            "password": "s3cure!",
            "full_name": "New Owner",
            "tenant_name": "Startup Inc",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_returns_tokens(client: AsyncClient) -> None:
    """POST /login with valid credentials returns tokens."""
    await seed_tenant_and_user(email="login@acme.com", tenant_slug="login-acme")

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@acme.com", "password": "pass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_me_requires_auth(client: AsyncClient) -> None:
    """GET /me without token returns 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 422)


async def test_refresh_works(client: AsyncClient) -> None:
    """POST /refresh returns a new access token."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@test.io",
            "password": "pass",
            "full_name": "R",
            "tenant_name": "RefreshCo",
        },
    )
    refresh_token = resp.json()["refresh_token"]

    resp2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


async def test_tenant_isolation(client: AsyncClient) -> None:
    """User from tenant A cannot see users from tenant B."""
    _t_a, _u_a, token_a = await seed_tenant_and_user(email="a@tenant-a.com", tenant_slug="tenant-a")
    _t_b, _u_b, _token_b = await seed_tenant_and_user(
        email="b@tenant-b.com", tenant_slug="tenant-b"
    )

    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    emails = [u["email"] for u in body["users"]]
    assert "a@tenant-a.com" in emails
    assert "b@tenant-b.com" not in emails


async def test_invite_requires_owner_role(client: AsyncClient) -> None:
    """POST /users/invite as member returns 401."""
    _t, _u, member_token = await seed_tenant_and_user(
        role=UserRole.MEMBER, email="member@acme.com", tenant_slug="acme-member"
    )

    resp = await client.post(
        "/api/v1/users/invite",
        headers={"Authorization": f"Bearer {member_token}"},
        json={
            "email": "invited@acme.com",
            "password": "pass",
            "full_name": "Invited",
            "role": "member",
        },
    )
    assert resp.status_code == 401


async def test_logout_invalidates_token(client: AsyncClient) -> None:
    """After logout, the refresh token is revoked and /me still works with access token."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout@test.io",
            "password": "pass123",
            "full_name": "Logout User",
            "tenant_name": "LogoutCo",
        },
    )
    tokens = resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Logout (revoke refresh token)
    resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200

    # Refresh with revoked token should fail
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 401

    # Access token still works for /me
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "logout@test.io"


async def test_update_user_role_by_admin(client: AsyncClient) -> None:
    """Admin can update another user's role."""
    _t, admin_user, admin_token = await seed_tenant_and_user(
        role=UserRole.ADMIN, email="admin-upd@test.com", tenant_slug="admin-upd"
    )
    # Invite a member via owner first — seed directly
    import uuid

    from backend.src.saas_starter.core.security import hash_password
    from backend.src.saas_starter.models.user import User
    from tests.conftest import TestSessionLocal

    member_id = uuid.uuid4()
    async with TestSessionLocal() as db:
        member = User(
            id=member_id,
            email="member-upd@test.com",
            hashed_password=hash_password("pass123"),
            full_name="Member",
            role=UserRole.MEMBER,
            tenant_id=_t.id,
        )
        db.add(member)
        await db.commit()

    resp = await client.put(
        f"/api/v1/users/{member_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "admin"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


async def test_deactivate_user_by_owner(client: AsyncClient) -> None:
    """Owner can deactivate a user."""
    _t, _owner, owner_token = await seed_tenant_and_user(
        email="owner-deact@test.com", tenant_slug="owner-deact"
    )
    import uuid

    from backend.src.saas_starter.core.security import hash_password
    from backend.src.saas_starter.models.user import User
    from tests.conftest import TestSessionLocal

    member_id = uuid.uuid4()
    async with TestSessionLocal() as db:
        member = User(
            id=member_id,
            email="deact-member@test.com",
            hashed_password=hash_password("pass123"),
            full_name="DeactMember",
            role=UserRole.MEMBER,
            tenant_id=_t.id,
        )
        db.add(member)
        await db.commit()

    resp = await client.delete(
        f"/api/v1/users/{member_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "deactivated"


async def test_invite_user_by_owner(client: AsyncClient) -> None:
    """Owner can invite a new user."""
    _t, _owner, owner_token = await seed_tenant_and_user(
        email="invite-owner@test.com", tenant_slug="invite-owner"
    )
    resp = await client.post(
        "/api/v1/users/invite",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "email": "new-invite@test.com",
            "password": "pass123",
            "full_name": "New Invited",
            "role": "member",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new-invite@test.com"
    assert body["role"] == "member"


async def test_list_users_returns_tenant_users(client: AsyncClient) -> None:
    """GET /users returns users for the authenticated tenant."""
    _t, _u, token = await seed_tenant_and_user(
        email="list-users@test.com", tenant_slug="list-users"
    )
    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert any(u["email"] == "list-users@test.com" for u in body["users"])
