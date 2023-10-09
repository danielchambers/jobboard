import os
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from application.database import database_context
from application.models.user import User
from application.users.schemas.authentication import UserLogin, UserRegistration
from application.users.utilities.authentication import (
    create_access_token,
    authenticate_user,
    get_user,
    hash_password,
    authorize_user,
    authorize_member
)


JWT_ACCESS_EXPIRE = os.getenv('JWT_ACCESS_TOKEN_EXPIRE')
users_router = APIRouter(prefix='/user')


@users_router.post("/register")
async def register_user(user_data: UserRegistration):
    """
    Register a new user.

    Args:
        user_data (UserRegistration): User registration data.

    Returns:
        dict: An access token and token type.
    """
    user = get_user(user_data.email)

    if user != None:
        return {'error': 'user exists!'}

    with database_context() as db:
        user_data.password = hash_password(user_data.password)
        new_user = User(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            password=user_data.password,
            email=user_data.email
        )
        db.add(new_user)

    jwt_data = {
        'sub': user_data.email,
        'iss': 'api:register',
        'staff': False,
        'member': False,
        'basic': True
    }
    jwt_expiration = timedelta(minutes=30)
    access_token = create_access_token(jwt_data, jwt_expiration)
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.post("/login")
async def login_user(user_data: UserLogin):
    """
    Login with a user's credentials.

    Args:
        user_data (UserLogin): User login data.

    Returns:
        dict: An access token and token type.
    """
    valid_user = authenticate_user(user_data.email, user_data.password)

    if not valid_user:
        raise HTTPException(
            status_code=401, detail='Invalid email or password.')

    jwt_data = {
        'sub': valid_user['email'],
        'iss': 'api:login',
        'staff': valid_user['is_staff'],
        'member': valid_user['is_member'],
        'basic': valid_user['is_basic'],
    }
    jwt_expiration = timedelta(minutes=30)
    access_token = create_access_token(jwt_data, jwt_expiration)
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get("/test")
async def secure_test(current_user: dict = Depends(authorize_user)):
    return {"message": "This is a secured route for users", "user": current_user}


@users_router.get("/test2")
async def secure_test2(current_user: dict = Depends(authorize_member)):
    return {"message": "This is a secured route for members", "member": current_user}
