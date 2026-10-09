"""Lekcija 04: uporedi Core Table sa tipizovanim ORM dataclass modelom."""

from datetime import UTC, datetime

from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

core_metadata = MetaData()
core_user = Table(
    "core_user",
    core_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("fullname", String(100), nullable=True),
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "orm_user"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50))
    fullname: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(UTC),
    )


def main() -> None:
    user = User("sandy", "Sandy Cheeks")

    assert list(core_user.c.keys()) == ["id", "name", "fullname"]
    assert User.__table__ is Base.metadata.tables["orm_user"]
    assert User.__table__.c.name.nullable is False
    assert User.__table__.c.fullname.nullable is True
    assert user.id is None
    assert user.created_at.tzinfo is UTC

    print("Core columns:", list(core_user.c.keys()))
    print("ORM table:", User.__table__)
    print("Dataclass instance:", user)


if __name__ == "__main__":
    main()
