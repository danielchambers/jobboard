import os
import jwt
from typing import Optional, Dict
from datetime import datetime, timedelta
from passlib.context import CryptContext
from application.models.user import User

SECRET_KEY = os.getenv('JWT_SECRET')
ALGORITHM = os.getenv('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize a password context using the bcrypt hashing scheme
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(user_password: str) -> str:
    """
    Hashes a user's password using the configured CryptContext.

    Args:
        user_password (str): The user's plaintext password.

    Returns:
        str: The hashed password.
    """
    return password_context.hash(user_password)


def verify_password(user_password: str, user_hash: str) -> bool:
    """
    Verifies a user's password against a stored hashed password using the configured CryptContext.

    Args:
        user_password (str): The user's plaintext password.
        user_hash (str): The hashed password to compare against.

    Returns:
        bool: True if the user_password matches the user_hash, False otherwise.
    """
    return password_context.verify(user_password, user_hash)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiration time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not password_context.verify(password, user.password):
        return None
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return access_token
