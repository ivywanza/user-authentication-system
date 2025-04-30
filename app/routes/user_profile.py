from fastapi import APIRouter, HTTPException
from app.schemas import UserProfileUpdate

profile_router=APIRouter()

# editing profile
@profile_router.put("/user/update_profile/{user_id}")
def update_user_profile(profile:UserProfileUpdate):
    try:
        user=user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to update user profile, {e} ")