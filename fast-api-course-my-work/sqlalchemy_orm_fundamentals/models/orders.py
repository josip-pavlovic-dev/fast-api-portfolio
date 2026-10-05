from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Korisnik(Base):
    __tablename__ = "korisnik"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    korisnicko_ime: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    lozinka: Mapped[str] = mapped_column(String(100), nullable=False)


class Porudzbina(Base):
    __tablename__ = "porudzbina"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    kreirano_u: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    izmenjeno_u: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class StavkaPorudzbine(Base):
    __tablename__ = "stavka_porudzbine"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    kolicina: Mapped[int] = mapped_column(Integer, nullable=False)
