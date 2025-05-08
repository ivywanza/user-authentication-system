from fastapi import APIRouter,HTTPException, Request
from app.dbservice import User, db, UserDetail
from app.schemas import UserRequest,UserLogin
from app.security import hash_password,verify_password,create_access_token,verify_firebase_token
from firebase_admin import auth,credentials
import firebase_admin
# from firebase_admin import auth as firebase_auth
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import logging

user_router = APIRouter()

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# user database user-registration
@user_router.post("/user-registration", tags=["user registration1"])
def register_user(user:UserRequest):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            return {"error": "User with this email already exists"}
        
        hash_pw = hash_password(user.hashed_password)
        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hash_pw,
            role=user.role,
            phone_number=user.phone
        )
        db.add(new_user)
        db.commit()
    except Exception as e:
        return {"error": str(e)}
    return {"message": "User registered successfully"}

@user_router.get("/get-user/{user_id}")
def get_users(user_id:int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    return {
        "id": user.id,
        "fullName": user.fullName,
        "email": user.email,
        "role": user.role,
        "phone": user.phone,
        "password": user.hashed_password
    }

access_token_expire_minutes = 60
# user login using email and password
@user_router.post("/email-password-login", tags=["email-pasword auth"])
def email_password_login(user: UserLogin):
    try:
      
        # Check if user exists in local DB
        print(user)
        existing_user = db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(user.password, existing_user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        access_token_expires = timedelta(minutes=access_token_expire_minutes)
        access_token = create_access_token(
        data={"sub": user.email},  # Customize the payload
        expires_delta=access_token_expires
        )
        try:
            user_detail = db.query(UserDetail).filter_by(uid=existing_user.id).first()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not user_detail:
                new_user=UserDetail(
                    uid=existing_user.id,
                    last_login = current_time
                )
                db.add(new_user)
                db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
        
        # user_detail.last_login = current_time

        # 4. Check if the user has not logged in for 30 days and update account_status
        last_login_time = datetime.strptime(user_detail.last_login, "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_login_time > timedelta(days=30):
            user_detail.account_status = "inactive"
        else:
            user_detail.account_status = "active"

        return {"message": "Login successful", "user_id": existing_user.id, "access_token": access_token}
    


    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# adding user to firebase and local db
@user_router.post("/register", tags=["user registration2"])
def register_user(user : UserRequest):

    try:
        # 1. Create user in Firebase using Admin SDK
        user_record = auth.create_user(
            email=user.email,
            password=user.hashed_password,
        )
        print(user_record)

        firebase_uid = user_record.uid

        # 2. Save user in local database
        new_user = User(
            firebase_id=firebase_uid,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            phone_number=user.phone,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        
        # 3. Optionally: Get idToken using REST (like auto-login)
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        token_response = requests.post(auth_url, json={
            "email": user.email,
            "password": user.hashed_password,
            "returnSecureToken": True
        })
        token_data = token_response.json()

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Firebase token creation failed")

        return {
            "message": "User registered successfully",
            "email": new_user.email,
            "uid": new_user.uid,
            "idToken": token_data.get("idToken")
        }

    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered in Firebase")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 
# email and password user authentication using firebase
@user_router.post("/login",tags=["email-password firebase auth "])
async def login_user(email: str, password: str):
    try:
        user= db.query(User).filter(User.email == email).first()
        firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(firebase_auth_url, json=payload)
        result = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail=result.get("error", {}).get("message", "Login failed"))
        

        user_detail = db.query(UserDetail).filter_by(uid=user.id).first()

        # add user detail if it does not exixt in the database
        if not user_detail:
            new_user=UserDetail(
                uid=user.id
            )
            db.add(new_user)
            db.commit()
        
        # 3. Update last_login with the current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_detail.last_login = current_time

        # 4. Check if the user has not logged in for 30 days and update account_status
        last_login_time = datetime.strptime(user_detail.last_login, "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_login_time > timedelta(days=30):
            user_detail.account_status = "inactive"
        else:
            user_detail.account_status = "active"


        # Optionally: store user info in your DB if needed
        return {
            "idToken": result["idToken"],
            "refreshToken": result["refreshToken"],
            "email": result["email"],
            "uid": result["localId"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# google and github login in firebase
@user_router.post("/firebase-oauth-login", tags=["google&github firebase auth"])
def firebase_oauth_login(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")

    id_token = token.split(" ")[1]
    decoded_token = verify_firebase_token(id_token)

    email = decoded_token.get("email")
    uid = decoded_token.get("uid")
    name = decoded_token.get("name", "")
    
    # Check if user exists in local DB
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email, fullName=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"message": "Login successful", "user_id": user.id}
