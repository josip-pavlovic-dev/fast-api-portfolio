from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from ...core.security import get_current_user
from ...db.session import db_dependency
from ...models import Todos, Users
from ...schemas import CreateTodoRequest, TodoResponse

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

# Skraćenica za dependency koji vraća verifikovanog korisnika iz JWT-a.
current_user_dependency = Annotated[Users, Depends(get_current_user)]


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_all(
    db: db_dependency,
    current_user: current_user_dependency,
) -> list[TodoResponse]:
    # Ownership filter: korisnik vidi samo svoje todo stavke.
    todo_models = db.query(Todos).filter(Todos.owner_id == current_user.id).all()
    return [TodoResponse.model_validate(todo) for todo in todo_models]


@router.get(
    "/{todo_id}",
    status_code=status.HTTP_200_OK,
)
async def read_todo(
    db: db_dependency,
    current_user: current_user_dependency,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od nule."),
) -> TodoResponse:

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
        .first()
    )

    if todo_model is not None:
        return TodoResponse.model_validate(todo_model)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Todo nije pronađen."
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    db: db_dependency,
    current_user: current_user_dependency,
    todo_request: CreateTodoRequest,
) -> TodoResponse:
    # owner_id se postavlja iz tokena, nikad iz klijentskog input-a.
    todo_model = Todos(**todo_request.model_dump(), owner_id=current_user.id)

    db.add(todo_model)

    db.commit()

    db.refresh(todo_model)

    return TodoResponse.model_validate(todo_model)


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency,
    current_user: current_user_dependency,
    todo_request: CreateTodoRequest,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od nule"),
) -> None:
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
        .first()
    )
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo nije pronađen.",
        )
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)

    # Završavamo samo sa commit jer nam db.add(todo_model) nije potreban za update pošto je model već učitan iz baze. Takođe, ne treba nam ni db.refresh(todo_model) jer ne vraćamo model nazad pa nema potrebe za tim. Nema ni return-a zato što koristimo status_code=status.HTTP_204_NO_CONTENT.

    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: db_dependency,
    current_user: current_user_dependency,
    todo_id: int = Path(
        gt=0,
        description="ID todo zadatka mora biti veći od nule",
    ),
) -> None:
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
        .first()
    )
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo nije pronađen.",
        )

    db.delete(todo_model)

    db.commit()
