from fastapi import FastAPI
from app.routes.user_auth import user_router
from fastapi.security import OAuth2PasswordBearer



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def index():
    return{"message": "Hello, World!"}

app.include_router(user_router, prefix="/user", tags=["user"])