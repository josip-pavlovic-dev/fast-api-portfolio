from fastapi import FastAPI

from app import models as _models  # noqa: F401
from app.api.routes import health, items
from app.db.base import Base
from app.db.database import engine

app = FastAPI(title="FastAPI Portfolio")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(health.router)
app.include_router(items.router, prefix="/items", tags=["items"])
