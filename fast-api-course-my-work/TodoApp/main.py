from fastapi import FastAPI

from .db.base import Base
from .db.database import engine

app = FastAPI()

Base.metadata.create_all(bind=engine)
