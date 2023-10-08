from fastapi import APIRouter, FastAPI, Depends, HTTPException
from application.database import database_context
from application.users.schemas.authentication import UserLogin, UserRegistration
from application.users.utilities.authentication import create_access_token, authenticate_user

users_router = APIRouter(prefix='/user')
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@users_router.post("/test")
async def test_user():
    return {'test': 'user'}

# @users_router.post("/register")
# async def register_user(user_data: UserRegistration):
#     # Hash the user's password before storing it in the database
#     hashed_password = password_context.hash(user_data.password)
#     user_data.password = hashed_password

#     new_user = User(
#         firstname=user_data.firstname,
#         lastname=user_data.lastname,
#         password=hashed_password,
#         email=user_data.email
#     )

#     # Create a new user in the database
#     with database_context() as db:
#         db.add(new_user)

#     # Generate an access token for the registered user
#     access_token = create_access_token(
#         data={"sub": user_data.email},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )

#     return {"access_token": access_token, "token_type": "bearer"}


# @users_router.post("/login")
# async def login_user(email: str, password: str):
#     with database_context() as db:
#         access_token = authenticate_user(db, email, password)

#         if not access_token:
#             raise HTTPException(
#                 status_code=401, detail="Incorrect email or password")
#         return {"access_token": access_token, "token_type": "bearer"}
