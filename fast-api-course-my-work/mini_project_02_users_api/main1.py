from typing import Literal

from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Users API",
    version="1.0.0",
    description="API za upravljanje korisnicima.",
)


# Pydantic modeli za kreiranje i prikaz korisnika.
# Statički tipovi i validacija polja koristeći Pydantic Field i Literal su obavezni za UserCreate model. Definišu se default vrednosti za role i is_active polja kako bi se sprečila greška prilikom kreiranja korisnika kada ta polja nisu prosleđena od strane klijenta.
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=100)
    role: Literal["admin", "user"] = Field(
        default="user", description="Uloga korisnika (npr. admin ili user)"
    )
    is_active: bool = Field(default=True, description="da li je korisnik aktivan")

    # Primer JSON objekta koji ilustruje kako izgleda validan zahtev za kreiranje korisnika.
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Marko",
                "email": "marko@example.com",
                "role": "user",
                "is_active": True,
            }
        }
    }


# Response model za prikaz korisnika. Ne sadrži default vrednosti, samo opisuje stvarne podatke koje server vraća. Ovo omogućava preciznu validaciju i dokumentaciju API-ja.
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Literal["admin", "user"]
    is_active: bool


# In-memory lista korisnika.
users: list[dict[str, str | int | bool]] = [
    {
        "id": 1,
        "name": "Marko",
        "email": "marko@example.com",
        "role": "admin",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Ana",
        "email": "ana@example.com",
        "role": "user",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Petar",
        "email": "petar@example.com",
        "role": "user",
        "is_active": False,
    },
]


# Endpoint za dobijanje liste korisnika sa opcionalnim filtriranjem po ulozi i aktivnom statusu.
@app.get("/users", response_model=list[UserResponse])
async def get_users(
    role: Literal["admin", "user"] | None = Query(
        default=None, description="Filter korisnika po ulozi."
    ),
    is_active: bool | None = Query(
        default=None, description="Filter po aktivnom statusu."
    ),
):
    filtered_users = users

    if role is not None:
        filtered_users = [user for user in filtered_users if user["role"] == role]

    if is_active is not None:
        filtered_users = [
            user for user in filtered_users if user["is_active"] == is_active
        ]

    return filtered_users


# Endpoint za dobijanje pojedinačnog korisnika po ID-u.
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(gt=0, description="ID korisnika mora biti veći od 0")
):
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")


# Endpoint za kreiranje novog korisnika.
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    new_user: dict[str, str | bool | int] = {
        "id": len(users) + 1,
        **user.model_dump(),
    }

    users.append(new_user)

    return new_user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user: UserCreate,
    user_id: int = Path(gt=0, description="ID korisnika mora biti veći od 0"),
):
    for index, existing_user in enumerate(users):
        if existing_user["id"] == user_id:
            updated_user: dict[str, str | int | bool] = {
                "id": user_id,
                **user.model_dump(),
            }

            users[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")


@app.delete("/users/{user_id}")
async def user_del(
    user_id: int = Path(gt=0, description="ID korisnika mora biti veći od 0")
):
    for index, existing_user in enumerate(users):
        if existing_user["id"] == user_id:
            user_delete = users.pop(index)

            return {"detail": "Korisnik je obrisan.", "obrisan_korisnik": user_delete}
    raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
