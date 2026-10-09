"""Lekcija 01: upoznaj SQLAlchemy Core i ORM opise tabele."""

from sqlalchemy import Column, Integer, MetaData, String, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

core_metadata = MetaData()
core_user = Table(
    "core_user",
    core_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "orm_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


def main() -> None:
    core_statement = select(core_user.c.name)
    orm_statement = select(User.name)

    assert core_user.metadata is core_metadata
    assert User.__table__ is Base.metadata.tables["orm_user"]
    assert "FROM core_user" in str(core_statement)
    assert "FROM orm_user" in str(orm_statement)

    print("Core opis:", core_user)
    print("ORM opis:", User.__table__)
    print("Core SELECT:", core_statement)
    print("SELECT preko ORM atributa:", orm_statement)


if __name__ == "__main__":
    main()
