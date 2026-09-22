from typing import Annotated
from collections.abc import Generator
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu
from .db.base import Base
from .db.database import SessionLocal, engine
from .models import Todos

app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
    contact={"name": "TodoApp Support", "email": "support@todoapp.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
