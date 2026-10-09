"""Lekcija 02: otvori Engine konekciju i obradi Result/Row vrednosti."""

from sqlalchemy import create_engine, text


def main() -> None:
    engine = create_engine("sqlite://", echo=True)

    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT :message AS greeting"),
            {"message": "Hello, SQLAlchemy!"},
        ).one()
        assert row.greeting == "Hello, SQLAlchemy!"
        assert row._mapping["greeting"] == "Hello, SQLAlchemy!"

        statement = text(
            "SELECT :first AS greeting UNION ALL SELECT :second AS greeting"
        )
        greetings = (
            connection.execute(
                statement,
                {"first": "Hello", "second": "SQLAlchemy"},
            )
            .scalars()
            .all()
        )
        assert greetings == ["Hello", "SQLAlchemy"]
        print(greetings)

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1

    engine.dispose()


if __name__ == "__main__":
    main()
