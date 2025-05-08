from fastapi import APIRouter, HTTPException
from app.schemas import UserProfileUpdate
from app.dbservice import User,db

profile_router=APIRouter()

# editing profile
@profile_router.put("/user/update_profile/{user_id}")
def update_user_profile(user_id: int, profile: UserProfileUpdate):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields from the request
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.phone_number = profile.phone_number
        user.role = profile.role

        db.commit()
        db.refresh(user)
        return {"message": "Profile updated successfully", "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role
        }}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")