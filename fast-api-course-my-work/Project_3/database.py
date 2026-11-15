from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# NAPOMENA: Import je drugačiji kada se koristi unutar paketa u odnosu na direktno pokretanje skripte. U originalnom projektu koristimo relativne import-e, dok ovde koristimo apsolutne import-e!!!

SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
