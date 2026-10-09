"""Lekcija 06: izvrši jedan Core INSERT i pročitaj serverski timestamp."""

from datetime import datetime

from sqlalchemy import DateTime, String, create_engine, func, insert, inspect, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


def main() -> None:
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    statement = insert(User).values(
        name="spongebob",
        fullname="SpongeBob SquarePants",
    )
    compiled = statement.compile(engine)
    assert "created_at" not in str(compiled)
    assert compiled.params == {
        "name": "spongebob",
        "fullname": "SpongeBob SquarePants",
    }
    assert inspect(engine).get_columns("user_account")[3]["default"] is not None

    with engine.begin() as connection:
        user_id = connection.execute(statement).inserted_primary_key[0]

    with engine.connect() as connection:
        row = connection.execute(
            select(User.id, User.name, User.created_at).where(User.id == user_id)
        ).one()
        assert row.created_at is not None
        print(row)

    engine.dispose()


if __name__ == "__main__":
    main()
