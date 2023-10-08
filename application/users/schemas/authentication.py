from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegistration(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str
