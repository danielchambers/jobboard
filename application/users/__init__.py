import os
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from application.database import database_context
from application.models.user import (
    User,
    UserJobWatched,
    UserJobApplied
)
from application.users.schemas.authentication import (
    UserLogin,
    UserRegistration,
)
from application.users.schemas.jobs import UserSaveJob
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
        'id': valid_user['id'],
        'sub': valid_user['email'],
        'iss': 'api:login',
        'staff': valid_user['is_staff'],
        'member': valid_user['is_member'],
    }
    jwt_expiration = timedelta(minutes=30)
    access_token = create_access_token(jwt_data, jwt_expiration)
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.post("/jobs/save")
async def secure_test(payload: UserSaveJob, current_user: dict = Depends(authorize_user)):
    """
    Save a job for the current user.

    Args:
        payload (UserSaveJob): The payload containing the job information to be saved.
        current_user (dict): The authenticated user's information.

    Returns:
        dict: A response message and the current user's information.
    """
    user_id = current_user['id']

    with database_context() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        job = UserJobWatched(
            user_id=user_id, job_id=payload.job_id, platform=payload.platform)
        existing_user.jobs_watched.append(job)
        db.add(job)
    return {"message": "Job saved!", "user": current_user}


@users_router.get("/jobs/saved")
async def secure_test2(current_user: dict = Depends(authorize_user)):
    """
    Retrieve jobs saved by the current user.

    Args:
        current_user (dict): The authenticated user's information.

    Returns:
        dict: A list of saved jobs and the current user's information.
    """
    user_id = current_user['id']

    with database_context() as db:
        existing_user = db.query(User).filter(User.id == user_id).first()
        jobs = [{'jobs': job.job_id, 'platform': job.platform}
                for job in existing_user.jobs_watched]
        return {"jobs": jobs, "user": current_user}
