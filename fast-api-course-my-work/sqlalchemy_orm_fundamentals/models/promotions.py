from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class PromotivniDogadjaj(Base):
    __tablename__ = "promotivni_dogadjaj"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    naziv: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    datum_pocetka: Mapped[date] = mapped_column(Date, nullable=False)
    datum_zavrsetka: Mapped[date] = mapped_column(Date, nullable=False)
    umanjenje_cene: Mapped[int] = mapped_column(Integer, nullable=False)


class VezaProizvodaIPromocije(Base):
    __tablename__ = "veza_proizvoda_i_promocije"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
