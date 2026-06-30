"""Security utility tests."""

from lra_api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    password = "StrongPassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_access_token_encode_decode() -> None:
    token = create_access_token("user-123")
    payload = decode_token(token, expected_type="access")

    assert payload["sub"] == "user-123"
    assert payload["typ"] == "access"


def test_refresh_token_encode_decode() -> None:
    token, _ = create_refresh_token("user-456")
    payload = decode_token(token, expected_type="refresh")

    assert payload["sub"] == "user-456"
    assert payload["typ"] == "refresh"
