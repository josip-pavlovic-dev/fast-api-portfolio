from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    # Lekcija 12: uvozi služe tipovima veza bez runtime kružnih importa.
    from .orders import StavkaPorudzbine
    from .promotions import VezaProizvodaIPromocije


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

    # Lekcija 13: NULL dozvoljava korenskoj kategoriji da nema roditelja.
    # Lekcija 14: baza odbija brisanje kategorije dok postoje potkategorije.
    roditelj_id: Mapped[int | None] = mapped_column(
        ForeignKey("kategorija.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # Lekcija 13: remote_side označava ID roditelja u samoreferencirajućoj vezi.
    roditelj: Mapped[Kategorija | None] = relationship(
        back_populates="deca",
        remote_side=lambda: [Kategorija.id],
    )
    # Lekcija 13: svaka kategorija može imati više direktnih potkategorija.
    # Lekcija 14: ORM prepušta bazi da odbije brisanje roditeljske kategorije.
    deca: Mapped[list[Kategorija]] = relationship(
        back_populates="roditelj",
        passive_deletes="all",
    )

    # Lekcija 12: jedna kategorija može da ima više proizvoda.
    # Lekcija 14: ORM ne poništava FK pre provere RESTRICT pravila u bazi.
    proizvodi: Mapped[list[Proizvod]] = relationship(
        back_populates="kategorija",
        passive_deletes="all",
    )


class Proizvod(Base):
    __tablename__ = "proizvod"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    # Lekcija 12: svaki proizvod referencira postojeću obaveznu kategoriju.
    # Lekcija 14: kategorija sa proizvodima ne može da se obriše.
    kategorija_id: Mapped[int] = mapped_column(
        ForeignKey("kategorija.id", ondelete="RESTRICT"),
        nullable=False,
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
        default=func.now(), # Postavlja podrazumevanu vrednost na trenutno vreme u bazi.
        onupdate=func.now(), # Ažurira vreme izmene na trenutno vreme u bazi.
        nullable=False,
    )
    cena: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Lekcija 12: ORM atributi omogućavaju navigaciju do povezanih objekata.
    kategorija: Mapped[Kategorija] = relationship(back_populates="proizvodi")
    stavke_porudzbine: Mapped[list[StavkaPorudzbine]] = relationship(
        back_populates="proizvod"
    )
    veze_promocija: Mapped[list[VezaProizvodaIPromocije]] = relationship(
        back_populates="proizvod"
    )


class StanjeZaliha(Base):
    __tablename__ = "stanje_zaliha"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    kolicina: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    poslednja_provera: Mapped[datetime] = mapped_column(
        # Traži timezone-aware SQL tip ako ga dijalekt baze podržava.
        # Ne garantuje čuvanje originalne vremenske zone ili offset-a.
        DateTime(timezone=True),
        nullable=False,
    )
