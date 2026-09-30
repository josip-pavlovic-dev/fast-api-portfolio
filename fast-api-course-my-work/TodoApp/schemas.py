from pydantic import BaseModel, ConfigDict, Field


class CreateTodoRequest(BaseModel):
    title: str = Field(
        min_length=3, description="Naslov todo zadatka mora imati najmanje 3 karaktera"
    )
    description: str = Field(
        min_length=3, description="Opis todo zadatka mora imati najmanje 3 karaktera"
    )
    priority: int = Field(
        gt=0,
        lt=6,
        description="Prioritet todo zadatka mora biti veći od 0 i manji od 6",
    )
    complete: bool = Field(description="Status završenosti todo zadatka")


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool

    model_config = ConfigDict(from_attributes=True)


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


# Body model za /users/password endpoint iz oblasti authenticate requests.
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)
