from pydantic import BaseModel


class UserRequest(BaseModel):
    fullName: str
    email: str
    role:str
    phone:str
    hashed_password:str

class UserLogin(BaseModel):
    email:str
    password:str

class UserProfileUpdate(BaseModel):
    name:str
    email:str
    phone:str