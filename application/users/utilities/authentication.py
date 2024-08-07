import os
import jwt
from typing import Optional, Dict, Union
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from application.models.user import User
from application.database import database_context

SECRET_KEY = os.getenv('JWT_SECRET')
ALGORITHM = os.getenv('JWT_ALGORITHM')

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """
    Hashes a user's password using the configured CryptContext.

    Args:
        password (str): The user's plaintext password.

    Returns:
        str: The hashed password.
    """
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a user's password against a stored hashed password using the configured CryptContext.

    Args:
        plain_password (str): The user's plaintext password.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the plain_password matches the hashed_password, False otherwise.
    """
    return password_context.verify(plain_password, hashed_password)


def get_user(email: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Retrieve a user's data by their email address.

    Args:
        email (str): The email address of the user to retrieve.

    Returns:
        dict or None: A dictionary containing user data if the user is found,
        or None if the user is not found.
    """
    with database_context() as db:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return {
                'id': user.id,
                'password': user.password,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_member': user.is_member
            }
        else:
            return None


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create an access token.

    Args:
        data (dict): The data to be encoded into the token.
        expires_delta (timedelta, optional): The token expiration duration. Defaults to 30 minutes.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, str]]:
    """
    Decode and verify an access token.

    Args:
        token (str): JWT access token.

    Returns:
        dict: Decoded token payload if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    except jwt.exceptions.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid audience')


def authenticate_user(email: str, password: str) -> Union[Dict[str, Union[str, int]], bool]:
    """
    Authenticate a user by email and password.

    Args:
        email (str): The user's email address.
        password (str): The user's plaintext password.

    Returns:
        Union[Dict[str, Union[str, int]], bool]: A dictionary containing user data if authentication
        is successful, or False if authentication fails.
    """
    user = get_user(email)

    if user == None:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


def authorize_user(token: str = Depends(oauth2_scheme)):
    """
    Authorize a user based on an access token.

    Args:
        token (str): The JWT access token.

    Returns:
        dict: The payload extracted from the token if authorization is successful.

    Raises:
        HTTPException: If the token is invalid or expired, a 401 Unauthorized response is raised.

    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def authorize_member(token: str = Depends(oauth2_scheme)):
    """
    Authorize a user as a member based on an access token.

    Args:
        token (str): The JWT access token.

    Returns:
        dict: The payload extracted from the token if authorization is successful.

    Raises:
        HTTPException: If the token is invalid or expired, a 401 Unauthorized response is raised.
                      If the user is not a member (based on the token payload), a 403 Forbidden response is raised.

    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not payload["member"]:
        raise HTTPException(status_code=403, detail="User is not a member")

    return payload
