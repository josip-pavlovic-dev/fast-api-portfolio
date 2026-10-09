"""Lekcija 05: kreiraj User/Address šemu i proveri FK constraint u SQLite-u."""

from sqlalchemy import ForeignKey, String, create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)


def main() -> None:
    engine = create_engine("sqlite://", echo=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.begin() as connection:
        Base.metadata.create_all(connection)

    class Address(Base):
        __tablename__ = "address"

        id: Mapped[int] = mapped_column(primary_key=True)
        email_address: Mapped[str] = mapped_column(String(100), nullable=False)
        user_id: Mapped[int] = mapped_column(
            ForeignKey("user_account.id"),
            nullable=False,
        )

    with engine.begin() as connection:
        Base.metadata.create_all(connection)
    with engine.begin() as connection:
        Base.metadata.create_all(connection)

    assert set(inspect(engine).get_table_names()) == {"user_account", "address"}
    assert (
        inspect(engine).get_foreign_keys("address")[0]["referred_table"]
        == "user_account"
    )

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO address (email_address, user_id) "
                    "VALUES (:email_address, :user_id)"
                ),
                {"email_address": "orphan@example.test", "user_id": 999},
            )
    except IntegrityError:
        print("Nevažeći user_id je odbijen.")
    else:
        raise AssertionError("SQLite nije odbio nevažeći strani ključ")

    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO user_account (id, name) VALUES (:id, :name)"),
            {"id": 1, "name": "sandy"},
        )
        connection.execute(
            text(
                "INSERT INTO address (email_address, user_id) "
                "VALUES (:email_address, :user_id)"
            ),
            {"email_address": "sandy@example.test", "user_id": 1},
        )

    engine.dispose()


if __name__ == "__main__":
    main()
