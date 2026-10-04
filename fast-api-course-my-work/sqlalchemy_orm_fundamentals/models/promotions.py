from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class PromotivniDogadjaj(Base):
    __tablename__ = "promotivni_dogadjaj"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class VezaProizvodaIPromocije(Base):
    __tablename__ = "veza_proizvoda_i_promocije"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
