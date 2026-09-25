from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .db.base import Base


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(
        Boolean, default=True
    )  # default je True zato što je nalog aktivan prilikom kreiranja
    role = Column(
        String
    )  # možemo staviti i da je default="user" zato što je većina korisnika obični korisnici, ali to zavisi od tvoje aplikacije
