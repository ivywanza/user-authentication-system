from fastapi import FastAPI
from app.routes.user_auth import user_router
from fastapi.security import OAuth2PasswordBearer
import base64
import json
import os
import firebase_admin
from firebase_admin import credentials



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def index():
    return{"message": "Hello, World!"}

firebase_key_base64 = os.environ.get("FIREBASE_KEY_BASE64")

if not firebase_admin._apps and firebase_key_base64:
    key_dict = json.loads(base64.b64decode(firebase_key_base64))
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)


app.include_router(user_router, prefix="/user")