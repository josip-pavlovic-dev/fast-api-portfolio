from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/")
async def get_users():
    return {"user": "authenticated"}
