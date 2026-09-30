from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from ...core.security import get_current_user
from ...db.session import db_dependency
from ...models import Todos, Users
from ...schemas import TodoResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

current_user_dependency = Annotated[Users, Depends(get_current_user)]


def _require_admin(current_user: Users) -> None:
    # Centralizovana role provera za sve admin endpoint-e u ovom modulu.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos_for_admin(
    db: db_dependency,
    current_user: current_user_dependency,
) -> list[TodoResponse]:
    _require_admin(current_user)

    # Admin vidi sve todo zapise, bez owner_id filtera.
    todo_models = db.query(Todos).all()
    return [TodoResponse.model_validate(todo) for todo in todo_models]


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_for_admin(
    db: db_dependency,
    current_user: current_user_dependency,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veci od nule."),
) -> None:
    _require_admin(current_user)

    # Admin delete radi po ID-u globalno, nezavisno od ownership pravila.
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo nije pronadjen.",
        )

    db.delete(todo_model)
    db.commit()
