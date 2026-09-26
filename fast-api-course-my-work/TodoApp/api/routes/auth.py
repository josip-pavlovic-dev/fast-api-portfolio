from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from ...db.session import db_dependency
from ...models import Users
from ...schemas import CreateUserRequest, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# schemes=["bcrypt"] znači da će CryptContext koristiti bcrypt algoritam za hashovanje lozinki. bcrypt algoritam je preporučen za većinu aplikacija, ali može biti zamenjen drugim algoritmima ako je potrebno. On zna kako da pravi hash, kako da proverava hash i kako da prepoznaje format hash-a.

# deprecated="auto" znači da će CryptContext automatski prepoznati zastarele hash-ove i preporučiti njihovu zamenu novim hash-om. Ovo pomaže u održavanju sigurnosti aplikacije bez potrebe za ručnom proverom i zamenom hash-ova.


def authenticate_user(username: str, password: str, db: db_dependency):
    """Vraća korisnika ako username postoji i password odgovara hash-u."""
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False

    hashed_password = cast(str, getattr(user, "hashed_password"))
    is_active = cast(bool, getattr(user, "is_active"))

    if not bcrypt_context.verify(password, hashed_password):
        return False

    if not is_active:
        return False

    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
) -> UserResponse:
    # Brza provera pre upisa da bismo izbegli 500 na unique ograničenjima.
    existing_user = (
        db.query(Users)
        .filter(
            (Users.email == create_user_request.email)
            | (Users.username == create_user_request.username)
        )
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )

    create_user_model = Users(
        email=create_user_request.email,  # raspored argumenata nije bitan zbog imenovanih argumenata (email=..., username=..., itd.)
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(
            create_user_request.password
        ),  # Hash-ujemo lozinku pre čuvanja u bazi
        is_active=True,
    )

    db.add(create_user_model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    db.refresh(create_user_model)

    # response_model=UserResponse filtrira i serializuje odgovor,
    # pa možemo bezbedno vratiti ORM objekat.
    return create_user_model


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    # Swagger napomena:
    # - grant_type mora biti unet kao "password"
    # - username/password moraju odgovarati korisniku koji je već registrovan
    authenticated_user = authenticate_user(
        form_data.username,
        form_data.password,
        db,
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": "token",
        "token_type": "bearer",
    }
