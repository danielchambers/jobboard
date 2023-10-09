import pytest
from application.users.utilities.authentication import hash_password, verify_password


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


if __name__ == "__main__":
    pytest.main()
