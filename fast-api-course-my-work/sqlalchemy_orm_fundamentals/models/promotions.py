from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    # Lekcija 12: uvoz omogućava proveru tipa proizvoda bez runtime kružnog importa.
    from .catalog import Proizvod


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

    # Lekcija 12: promocija može da se poveže sa više proizvoda preko vezne tabele.
    veze_proizvoda: Mapped[list[VezaProizvodaIPromocije]] = relationship(
        back_populates="promotivni_dogadjaj"
    )


class VezaProizvodaIPromocije(Base):
    __tablename__ = "veza_proizvoda_i_promocije"
    # Lekcije 10 i 12: isti proizvod ne može biti povezan sa istom promocijom dvaput.
    __table_args__ = (
        UniqueConstraint(
            "proizvod_id",
            "promotivni_dogadjaj_id",
            name="uq_proizvod_promocija",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    # Lekcija 12: ove FK kolone čine vezu između proizvoda i promocije.
    proizvod_id: Mapped[int] = mapped_column(ForeignKey("proizvod.id"), nullable=False)
    promotivni_dogadjaj_id: Mapped[int] = mapped_column(
        ForeignKey("promotivni_dogadjaj.id"),
        nullable=False,
    )

    # Lekcija 12: ORM veze vode do povezanog proizvoda i promotivnog događaja.
    proizvod: Mapped[Proizvod] = relationship(back_populates="veze_promocija")
    promotivni_dogadjaj: Mapped[PromotivniDogadjaj] = relationship(
        back_populates="veze_proizvoda"
    )
