from fastapi import FastAPI, HTTPException, Path, status

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu
from .db.base import Base
from .db.database import engine
from .db.session import db_dependency
from .models import Todos
from .schemas import TodoRequest

app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
    contact={"name": "TodoApp Support", "email": "support@todoapp.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od 0"),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo nije pronađen.")


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,
    db: db_dependency,
):
    todo_model = Todos(**todo_request.model_dump())

    db.add(
        todo_model
    )  # Priprema model za dodavanje u bazu, ali još uvek nije upisan u bazu. Instanca modela je sada u "pending" stanju.
    db.commit()  # Upisuje promenu u bazu i završava transakciju.
    db.refresh(todo_model)  # Učitava iz baze generisane i potvrđene vrednosti, npr. id.

    return todo_model
