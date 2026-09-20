from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel

# FastAPI aplikacija za korisnike.
# Ovaj projekat je malo složeniji od prvog jer pokazuje i query parametre.
app = FastAPI(
    title="Users API",
    version="1.0.0",
    description="API za korisnike sa filtriranjem po query parametrima.",
)


# Request model za POST i PUT.
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"
    is_active: bool = True


# Response model za odgovore servera.
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
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


# GET /users
# Ovaj endpoint vraća listu korisnika.
# Query parametri: role i is_active su opcioni.
# Na primer: /users?role=admin&is_active=true
@app.get("/users", response_model=list[UserResponse])
def get_users(
    role: str | None = Query(default=None, description="Filter korisnika po roli."),
    is_active: bool | None = Query(
        default=None, description="Filter po aktivnom statusu."
    ),
):
    filtered_users = users

    # Filtriranje korisnika po query parametrima role i is_active
    if role is not None:
        filtered_users = [user for user in filtered_users if user["role"] == role]

    if is_active is not None:
        filtered_users = [
            user for user in filtered_users if user["is_active"] == is_active
        ]

    return filtered_users


# GET /users/{user_id}
# Vraća jednog korisnika po ID-u.
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")


# POST /users
# Kreira novog korisnika.
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    new_user: dict[str, str | int | bool] = {
        "id": len(users) + 1,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }
    users.append(new_user)
    return new_user


# PUT /users/{user_id}
# Menja podatke postojećeg korisnika.
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    for index, existing_user in enumerate(users):
        if existing_user["id"] == user_id:
            updated_user: dict[str, str | int | bool] = {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            }
            users[index] = updated_user
            return updated_user

    raise HTTPException(status_code=404, detail="User not found")


# DELETE /users/{user_id}
# Briše korisnika po ID-u.
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user["id"] == user_id:
            deleted_user = users.pop(index)
            return {
                "message": "User deleted successfully",
                "deleted_user": deleted_user,
            }

    raise HTTPException(status_code=404, detail="User not found")
