"""Lekcija 07: prosledi više skupova parametara jednom Core INSERT-u."""

from datetime import datetime

from sqlalchemy import DateTime, String, create_engine, func, insert, select
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

    parameters = [
        {"name": "spongebob", "fullname": "SpongeBob SquarePants"},
        {"name": "patrick", "fullname": "Patrick Star"},
        {"name": "sandy", "fullname": "Sandy Cheeks"},
    ]

    with engine.begin() as connection:
        result = connection.execute(insert(User), parameters)
        assert result.rowcount == len(parameters)

    with engine.connect() as connection:
        users = connection.execute(
            select(User.name, User.created_at).order_by(User.id)
        ).all()
        assert [user.name for user in users] == ["spongebob", "patrick", "sandy"]
        assert all(user.created_at is not None for user in users)
        print(users)

    engine.dispose()


if __name__ == "__main__":
    main()
