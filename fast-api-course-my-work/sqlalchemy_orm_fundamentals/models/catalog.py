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
    naziv: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # slug predstavlja URL-friendly verziju naziva kategorije
    # koristi se u URL-ovima
    # npr "/kategorija/naziv-kategorije"
    slug: Mapped[str] = mapped_column(String(55), nullable=False, unique=True)
    aktivna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nivo: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)


class Proizvod(Base):
    __tablename__ = "proizvod"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    naziv: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(55), nullable=False, unique=True)
    opis: Mapped[str] = mapped_column(Text, nullable=False)
    digitalni: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    aktivan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
    cena: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class StanjeZaliha(Base):
    __tablename__ = "stanje_zaliha"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    kolicina: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    poslednja_provera: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
