from sqlalchemy import Integer
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


class Proizvod(Base):
    __tablename__ = "proizvod"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class StanjeZaliha(Base):
    __tablename__ = "stanje_zaliha"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
