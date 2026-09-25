from fastapi import APIRouter, status
from passlib.context import CryptContext

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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
) -> UserResponse:
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
    db.commit()
    db.refresh(create_user_model)

    return UserResponse.model_validate(create_user_model)
