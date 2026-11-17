from fastapi import FastAPI
from .db.database import engine
from .db.base import Base

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu

app = FastAPI(
    title="Portfolio Items API",
    description="API for managing portfolio items",
    version="1.0.0",
    contact={
        "name": "Josip Pavlović",
        "email": "jolepavlovic@outlook.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Dobrodošli u Portfolio Items API"}
