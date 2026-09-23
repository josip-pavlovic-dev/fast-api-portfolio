from fastapi import APIRouter, HTTPException, Path, status

from ...db.session import db_dependency
from ...models import Todos
from ...schemas import TodoRequest

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency) -> list[Todos]:
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID todo zatatka mora biti veći od nule."),
) -> Todos:

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Todo nije pronađen."
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest) -> Todos:
    todo_model = Todos(**todo_request.model_dump())

    db.add(todo_model)

    db.commit()

    db.refresh(todo_model)

    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0, description="ID todo zatatka mora biti veći od nule"),
) -> None:
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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
    todo_id: int = Path(
        gt=0,
        description="ID mora biti veći od nule",
    ),
) -> None:
    # todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_model = db.get(Todos, todo_id)
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo nije pronađen.",
        )

    # db.query(Todos).filter(Todos.id == todo_id).delete()

    db.delete(todo_model)

    db.commit()
