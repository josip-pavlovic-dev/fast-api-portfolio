from fastapi import FastAPI

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu
from .api.routes import auth, todos
from .db.base import Base
from .db.database import engine

app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
    contact={"name": "TodoApp Support", "email": "support@todoapp.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
