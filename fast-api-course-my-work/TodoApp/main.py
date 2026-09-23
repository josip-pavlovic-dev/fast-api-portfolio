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


@app.get(
    "/todo/{todo_id}",
    status_code=status.HTTP_200_OK,
)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od 0"),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo nije pronađen.")


@app.post(
    "/todo",
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    todo_request: TodoRequest,
    db: db_dependency,
):
    todo_model = Todos(**todo_request.model_dump())

    db.add(
        todo_model
    )  # Priprema model za dodavanje u bazu, ali još uvek nije upisan u bazu. Instanca modela je sada u "pending" stanju.
    db.commit()  # Upisuje promenu u bazu i završava transakciju.
    db.refresh(
        todo_model
    )  # Učitava/ osvežava iz baze generisane i potvrđene vrednosti, npr. id.

    return todo_model


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    # todo_request mora biti pre todo_id jer todo_id ima podrazumevanu vrednost Path(...).
    # Python zahteva da parametri bez podrazumevane (default) vrednosti budu pre parametara sa podrazumevanom vrednošću.
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od 0"),
) -> None:
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    # Prvi način ažuriranja modela je korišćenje petlje kroz sve atribute iz zahteva.
    # Ovaj način je koristan kada imamo mnogo atributa i želimo da ih ažuriramo dinamički.
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)

    # todo_request.model_dump().items() vraća parove ključ-vrednost iz zahteva, koji se koriste za ažuriranje modela. Korak po korak:
    # 1. todo_request.model_dump() -> vraća dict sa podacima iz zahteva.
    # 2. .items() -> vraća parove ključ-vrednost iz dict-a.
    # 3. setattr(todo_model, key, value) -> ažurira atribut modela sa novom vrednošću.

    # Drugi način ažuriranja modela je ručno postavljanje svakog atributa iz zahteva.
    # todo_model.title = todo_request.title
    # todo_model.description = todo_request.description
    # todo_model.priority = todo_request.priority
    # todo_model.complete = todo_request.complete

    db.add(todo_model)  # Priprema model za ažuriranje u bazi.
    db.commit()  # Upisuje promene u bazu i završava transakciju.


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od 0"),
) -> None:
    # todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_model = db.get(Todos, todo_id)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    # db.query(Todos).filter(Todos.id == todo_id).delete() # Direktno izvršavanje SQL DELETE upita, ne koristi ORM instancu. Nema sinhronizacije sa ORM sesijom. Već smo pronašli objekat (linija 96 ili 97 -> todo_model = db.query(Todos).filter(Todos.id == todo_id).first()) ili još bolje koristiti db.get(Todos, todo_id) kao što je prikazano iznad.

    db.delete(todo_model)
    db.commit()
