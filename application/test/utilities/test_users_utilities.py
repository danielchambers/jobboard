import os
import jwt
import base64
import json
import pytest
from unittest.mock import patch
from datetime import timedelta
from application.users.utilities.authentication import (
    hash_password,
    verify_password,
    create_access_token,
    authenticate_user
)


def test_hash_password():
    # Test case for hashing a password
    plaintext_password = "mysecretpassword"
    hashed_password = hash_password(plaintext_password)
    assert hashed_password is not None
    assert len(hashed_password) > 0


def test_verify_correct_password():
    # Test case for verifying a correct password
    plaintext_password = "mysecretpassword"
    hashed_password = hash_password(plaintext_password)
    assert verify_password(plaintext_password, hashed_password) is True


def test_verify_incorrect_password():
    # Test case for verifying an incorrect password
    plaintext_password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed_password = hash_password(plaintext_password)
    assert verify_password(wrong_password, hashed_password) is False


def test_verify_empty_hash():
    # Test case for verifying against an empty hash (should return False)
    plaintext_password = "mysecretpassword"
    empty_hash = hash_password("")

    # Make sure an empty hash is not accepted as a valid password hash
    assert verify_password(plaintext_password, empty_hash) is False


def test_verify_empty_password():
    # Test case for verifying against an empty password (should return False)
    hashed_password = hash_password("mysecretpassword")
    assert verify_password("", hashed_password) is False


def test_create_access_token():
    os.environ["JWT_SECRET"] = "your_secret_key"
    os.environ["JWT_ALGORITHM"] = "HS256"
    data = {"sub": "test@example.com", "iss": "api:register"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    header, payload, signature = token.split(".")
    decoded_payload = base64.urlsafe_b64decode(payload + "===")
    payload_data = json.loads(decoded_payload)

    assert payload_data["sub"] == "test@example.com"
    assert payload_data["iss"] == "api:register"

    del os.environ["JWT_SECRET"]
    del os.environ["JWT_ALGORITHM"]


@pytest.fixture
def mock_get_user():
    with patch("application.users.utilities.authentication.get_user") as mock_get_user:
        yield mock_get_user


def test_authenticate_user_valid(mock_get_user):
    mock_get_user.return_value = {
        "email": "test@example.com",
        "password": "$2b$12$RspxA0Tlqx2OA4v6/xb8VOYdwqfYK5z0qkLOWrqv2jQ56l6mpbYI2",
    }
    email = "test@example.com"
    password = "123qwe"
    user_data = authenticate_user(email, password)
    assert user_data is not False
    assert user_data["email"] == "test@example.com"


def test_authenticate_user_invalid_user(mock_get_user):
    mock_get_user.return_value = None
    invalid_email = "nonexistent@example.com"
    password = "123qwe"
    invalid_user_data = authenticate_user(invalid_email, password)
    assert invalid_user_data is False


def test_authenticate_user_invalid_password(mock_get_user):
    mock_get_user.return_value = {
        "email": "test@example.com",
        "password": "$2b$12$RspxA0Tlqx2OA4v6/xb8VOYdwqfYK5z0qkLOWrqv2jQ56l6mpbYI2",
    }
    email = "test@example.com"
    invalid_password = "wrong_password"
    invalid_password_data = authenticate_user(email, invalid_password)
    assert invalid_password_data is False


if __name__ == "__main__":
    pytest.main()
