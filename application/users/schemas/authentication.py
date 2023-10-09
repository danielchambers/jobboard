from pydantic import BaseModel, EmailStr, constr


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class UserRegistration(BaseModel):
    firstname: constr(min_length=2, max_length=50)
    lastname: constr(min_length=2, max_length=50)
    email: EmailStr
    password: constr(min_length=6)
