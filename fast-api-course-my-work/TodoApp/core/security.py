from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from .config import settings


def create_access_token(
    *,  # sve argumente nakon * je potrebno proslediti po imenu (keyword arguments)
    username: str,
    user_id: int,
    expires_delta: timedelta | None = None,
) -> str:
    expire_delta = expires_delta or timedelta(
        minutes=settings.access_token_expire_minutes
    )
    expire = datetime.now(timezone.utc) + expire_delta

    # sub nosi stabilan identitet (user_id), username je pomoćni claim.
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
