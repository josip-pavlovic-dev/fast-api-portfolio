from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..db.session import db_dependency
from ..models import Users
from .config import settings

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency,
) -> Users:
    # Jedinstven 401 odgovor za sve slučajeve nevalidnog tokena/korisnika.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as error:
        raise credentials_exception from error

    # sub claim nosi user_id koji je upisan prilikom encode faze.
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise credentials_exception

    try:
        user_id = int(subject)
    except ValueError as error:
        raise credentials_exception from error

    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Dodatna zaštita: samo aktivan korisnik prolazi kroz dependency.
    is_active = getattr(user, "is_active", None)
    if not isinstance(is_active, bool) or not is_active:
        raise credentials_exception

    return user
