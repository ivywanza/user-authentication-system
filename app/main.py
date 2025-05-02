from fastapi import FastAPI
from app.routes.user_auth import user_router
from fastapi.security import OAuth2PasswordBearer
import firebase_admin
from firebase_admin import credentials, auth


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def index():
    return{"message": "Hello, World!"}

if not firebase_admin._apps:
    cred = credentials.Certificate("C:\\Users\\Ivy\\Downloads\\authsystem-c4397-firebase-adminsdk-fbsvc-95dcd9a81d.json")
    firebase_admin.initialize_app(cred)

app.include_router(user_router, prefix="/user")