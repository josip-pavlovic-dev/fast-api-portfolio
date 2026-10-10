"""Lesson 02 source-slide companion: Core Table and declarative metadata."""

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
    inspect,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

core_metadata = MetaData()
user_account_table = Table(
    "core_user_account",
    core_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("fullname", String(100), nullable=True),
    Column("created_at", DateTime(timezone=True)),
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
    )


def main() -> None:
    engine = create_engine("sqlite://", echo=True)

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with engine.begin() as connection:
        core_metadata.create_all(connection)
        Base.metadata.create_all(connection)

    user = User("spongebob", "SpongeBob SquarePants")
    assert user.id is None
    assert user.created_at.tzinfo is UTC
    assert User.__table__ is Base.metadata.tables["user_account"]

    class Address(Base):
        __tablename__ = "address"

        id: Mapped[int] = mapped_column(primary_key=True)
        email_address: Mapped[str] = mapped_column(String(100))
        user_id: Mapped[int] = mapped_column(
            ForeignKey("user_account.id"),
            nullable=False,
        )

    with engine.begin() as connection:
        Base.metadata.create_all(connection)

    table_names = set(inspect(engine).get_table_names())
    assert table_names == {"core_user_account", "user_account", "address"}
    foreign_keys = inspect(engine).get_foreign_keys("address")
    assert foreign_keys[0]["referred_table"] == "user_account"

    print("Core Table:", user_account_table)
    print("Declarative Table:", User.__table__)
    print("Dataclass instance:", user)
    print("Created tables:", sorted(table_names))

    engine.dispose()


if __name__ == "__main__":
    main()
