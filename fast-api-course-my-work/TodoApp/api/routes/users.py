from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from ...core.security import get_current_user
from ...db.session import db_dependency
from ...models import Users
from ...schemas import ChangePasswordRequest, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Reuse-ujemo isti security dependency obrazac kao na todo rutama.
current_user_dependency = Annotated[Users, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_current_user_profile(
    current_user: current_user_dependency,
) -> UserResponse:
    # Vraća samo bezbedna javna user polja (bez hashed_password).
    return UserResponse.model_validate(current_user)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: db_dependency,
    current_user: current_user_dependency,
    password_request: ChangePasswordRequest,
) -> None:
    # Minimalna business validacija pre hashovanja.
    if password_request.current_password == password_request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password.",
        )

    hashed_password = getattr(current_user, "hashed_password", None)
    if not isinstance(hashed_password, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stored password hash is invalid.",
        )

    if not bcrypt_context.verify(
        password_request.current_password,
        hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # Lozinka se uvek upisuje kao hash, nikad kao plaintext.
    setattr(
        current_user,
        "hashed_password",
        bcrypt_context.hash(password_request.new_password),
    )
    db.commit()
