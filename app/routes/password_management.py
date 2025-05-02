from pydantic import BaseModel, EmailStr
from app.schemas import ResetPasswordRequest,ForgotPasswordRequest
from fastapi import APIRouter,HTTPException
from app.dbservice import User, db
from app.security import create_reset_token,hash_password, verify_reset_token

router = APIRouter()


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user.email)

    # TODO: Send this token via email with a password reset link
    return {"message": "Password reset token created", "token": reset_token}




@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
