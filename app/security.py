from passlib.context import CryptContext
import jwt
from datetime import datetime,timedelta
from typing import Union
from firebase_admin import auth
from fastapi import HTTPException


# Create a context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


algorithm  = "HS256"
access_token_expire_minutes = 30 


# Hashing function
def hash_password(password: str):
    return pwd_context.hash(password)

# Verification function
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.PyJWTError:
        return None
    
def verify_firebase_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token  # contains uid, email, etc.
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    

def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    return jwt.encode({"sub": email, "exp": expire}, secret_key, algorithm=algorithm)

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload.get("sub")
    except Exception:
        return None