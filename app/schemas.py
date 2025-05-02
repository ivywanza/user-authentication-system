from pydantic import BaseModel
from datetime import datetime


class UserRequest(BaseModel):
    first_name: str
    last_name:str
    email: str
    role:str
    phone:str
    hashed_password:str

class UserLogin(BaseModel):
    email:str
    password:str

class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    role: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
