from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    # Lekcija 12: uvoz omogućava proveru tipa proizvoda bez runtime kružnog importa.
    from .catalog import Proizvod


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

    # Lekcija 12: korisnik može da ima više porudžbina.
    porudzbine: Mapped[list[Porudzbina]] = relationship(back_populates="korisnik")


class Porudzbina(Base):
    __tablename__ = "porudzbina"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    # Lekcija 12: svaka porudžbina pripada postojećem korisniku.
    korisnik_id: Mapped[int] = mapped_column(ForeignKey("korisnik.id"), nullable=False)
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

    # Lekcija 12: ORM atributi povezuju porudžbinu sa korisnikom i stavkama.
    korisnik: Mapped[Korisnik] = relationship(back_populates="porudzbine")
    stavke: Mapped[list[StavkaPorudzbine]] = relationship(back_populates="porudzbina")


class StavkaPorudzbine(Base):
    __tablename__ = "stavka_porudzbine"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    # Lekcija 12: stavka pripada postojećoj porudžbini i referencira proizvod.
    porudzbina_id: Mapped[int] = mapped_column(
        ForeignKey("porudzbina.id"),
        nullable=False,
    )
    proizvod_id: Mapped[int] = mapped_column(ForeignKey("proizvod.id"), nullable=False)
    kolicina: Mapped[int] = mapped_column(Integer, nullable=False)

    # Lekcija 12: stavka omogućava navigaciju ka porudžbini i proizvodu.
    porudzbina: Mapped[Porudzbina] = relationship(back_populates="stavke")
    proizvod: Mapped[Proizvod] = relationship(back_populates="stavke_porudzbine")
