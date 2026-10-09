"""Lekcija 08: uporedi text/Core SELECT i ORM rezultate."""

from sqlalchemy import ForeignKey, String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100))


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)


def main() -> None:
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO user_account (id, name, fullname) "
                "VALUES (:id, :name, :fullname)"
            ),
            {"id": 1, "name": "sandy", "fullname": "Sandy Cheeks"},
        )
        connection.execute(
            text(
                "INSERT INTO address (id, email_address, user_id) "
                "VALUES (:id, :email_address, :user_id)"
            ),
            {
                "id": 1,
                "email_address": "sandy@example.test",
                "user_id": 1,
            },
        )

    with engine.connect() as connection:
        raw_rows = connection.execute(text("SELECT name FROM user_account")).all()
        core_rows = connection.execute(select(User.name)).all()
        core_entity_row = connection.execute(select(User)).one()
        assert raw_rows[0].name == "sandy"
        assert core_rows[0].name == "sandy"
        assert not isinstance(core_entity_row[0], User)
        print("text:", raw_rows)
        print("Core select column:", core_rows)
        print("Core select entity columns:", core_entity_row)

    with Session(engine) as session:
        orm_user = session.scalars(select(User)).one()
        assert isinstance(orm_user, User)
        print("ORM object:", orm_user)

    engine.dispose()


if __name__ == "__main__":
    main()
