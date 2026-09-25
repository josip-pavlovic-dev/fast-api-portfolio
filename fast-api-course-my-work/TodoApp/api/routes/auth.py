from fastapi import APIRouter, status

from ...models import Users
from ...schemas import CreateUserRequest, UserResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(create_user_request: CreateUserRequest) -> UserResponse:
    create_user_model = Users(
        email=create_user_request.email,  # raspored argumenata nije bitan zbog imenovanih argumenata (email=..., username=..., itd.)
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=create_user_request.password,  # Za sada koristimo plain text, kasnije ćemo hash-ovati
        is_active=True,
    )
    return create_user_model
