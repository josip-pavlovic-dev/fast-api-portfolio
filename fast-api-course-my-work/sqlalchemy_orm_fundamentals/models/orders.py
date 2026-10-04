from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Korisnik(Base):
    __tablename__ = "korisnik"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class Porudzbina(Base):
    __tablename__ = "porudzbina"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class StavkaPorudzbine(Base):
    __tablename__ = "stavka_porudzbine"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
