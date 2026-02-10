from fastapi import FastAPI

from app.api.routes import health, items

app = FastAPI(title="FastAPI Portfolio")

app.include_router(health.router)
app.include_router(items.router, prefix="/items", tags=["items"])
