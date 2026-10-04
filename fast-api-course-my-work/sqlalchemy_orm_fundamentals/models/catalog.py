from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Kategorija(Base):
    __tablename__ = "kategorija"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        # Primarni ključ sam po sebi zabranjuje NULL.
        # Autoincrement zasebno generiše ID ako ga unos ne navede.
        autoincrement=True,
    )
    # naziv kategorije, npr "Elektronika"
    # za razliku od slug-a, naziv može sadržati razmake i specijalne karaktere
    naziv: Mapped[str | None] = mapped_column(String(50))
    # slug predstavlja URL-friendly verziju naziva kategorije
    # koristi se u URL-ovima
    # npr "/kategorija/naziv-kategorije"
    slug: Mapped[str | None] = mapped_column(String(55))
    aktivna: Mapped[bool | None] = mapped_column(Boolean)
    nivo: Mapped[int | None] = mapped_column(SmallInteger)


class Proizvod(Base):
    __tablename__ = "proizvod"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    naziv: Mapped[str | None] = mapped_column(String(50))
    slug: Mapped[str | None] = mapped_column(String(55))
    opis: Mapped[str | None] = mapped_column(Text)
    digitalni: Mapped[bool | None] = mapped_column(Boolean)
    aktivan: Mapped[bool | None] = mapped_column(Boolean)
    kreirano_u: Mapped[datetime | None] = mapped_column(DateTime, default=func.now())
    izmenjeno_u: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())
    cena: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))


class StanjeZaliha(Base):
    __tablename__ = "stanje_zaliha"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    kolicina: Mapped[int | None] = mapped_column(Integer)
    poslednja_provera: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
