"""Lekcija 09: filteri, label-e, redosled i JOIN tipovi."""

from sqlalchemy import ForeignKey, String, create_engine, literal, or_, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    user_ids = {
        "spongebob": 1,
        "sandy": 2,
        "patrick": 3,
        "squidward": 4,
    }
    with engine.connect() as connection:
        for name, fullname in (
            ("spongebob", "SpongeBob SquarePants"),
            ("sandy", "Sandy Cheeks"),
            ("patrick", "Patrick Star"),
            ("squidward", None),
        ):
            connection.execute(
                text(
                    "INSERT INTO user_account (id, name, fullname) "
                    "VALUES (:id, :name, :fullname)"
                ),
                {"id": user_ids[name], "name": name, "fullname": fullname},
            )

        for address_id, (email, name) in enumerate(
            (
                ("spongebob@example.test", "spongebob"),
                ("sandy1@example.test", "sandy"),
                ("sandy2@example.test", "sandy"),
                ("patrick@example.test", "patrick"),
            ),
            start=1,
        ):
            connection.execute(
                text(
                    "INSERT INTO address (id, email_address, user_id) "
                    "VALUES (:id, :email_address, :user_id)"
                ),
                {
                    "id": address_id,
                    "email_address": email,
                    "user_id": user_ids[name],
                },
            )

        connection.commit()

    selected = (
        select(User.name.label("username"))
        .where(User.name.in_(["spongebob", "patrick"]))
        .order_by(User.name)
    )
    filtered_and = (
        select(User.name)
        .where((User.id > 1) & (User.name != "patrick"))
        .order_by(User.name)
    )
    filtered_or = (
        select(User.name)
        .where(or_(User.name == "sandy", User.name == "patrick"))
        .order_by(User.name)
    )
    outer_join = (
        select(
            (literal("User: ") + User.name).label("display_name"),
            Address.email_address.label("email"),
        )
        .outerjoin_from(User, Address)
        .order_by(User.name)
    )

    with engine.connect() as connection:
        assert connection.execute(selected).scalars().all() == ["patrick", "spongebob"]
        assert connection.execute(
            select(User.name).where(User.name.ilike("%SANDY%"))
        ).scalars().all() == ["sandy"]
        assert connection.execute(
            select(User.name).where(User.name.contains("ob"))
        ).scalars().all() == ["spongebob"]
        assert connection.execute(filtered_and).scalars().all() == [
            "sandy",
            "squidward",
        ]
        assert connection.execute(filtered_or).scalars().all() == ["patrick", "sandy"]
        joined_rows = connection.execute(outer_join).all()
        assert any(
            row.display_name == "User: squidward" and row.email is None
            for row in joined_rows
        )
        print(joined_rows)

    engine.dispose()


if __name__ == "__main__":
    main()
