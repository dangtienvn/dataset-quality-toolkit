"""Unit tests for password hashing and JWT token management."""

import time
from unittest.mock import patch

import pytest

from backend.src.saas_starter.core.exceptions import UnauthorizedError
from backend.src.saas_starter.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password_roundtrip() -> None:
    """Hashing then verifying returns True for the same password."""
    password = "s3cureP@ssw0rd!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_access_token() -> None:
    """Created token decodes back to the original subject."""
    subject = "user-uuid-123"
    token = create_access_token(subject, extra_claims={"role": "admin"})

    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_expired_token_raises_exception() -> None:
    """An expired token raises UnauthorizedError."""
    with patch("backend.src.saas_starter.core.security.settings") as mock_settings:
        mock_settings.access_token_expire_minutes = 0
        mock_settings.jwt_secret = "test-secret"
        mock_settings.jwt_algorithm = "HS256"

        token = create_access_token("user-123")

    time.sleep(1)

    with pytest.raises(UnauthorizedError, match="Invalid token"):
        decode_token(token)


def test_invalid_token_raises_exception() -> None:
    """A garbage token raises UnauthorizedError."""
    with pytest.raises(UnauthorizedError, match="Invalid token"):
        decode_token("not.a.valid.jwt.token")
