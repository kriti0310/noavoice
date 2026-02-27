from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_my_profile(current_user = Depends(get_current_user)):
    return {
        "status": True,
        "message": "User fetched",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name
        }
    }
