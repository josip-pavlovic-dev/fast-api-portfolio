"""Lesson 01 source-slide companion: Engine, Connection, Result and Row."""

from sqlalchemy import create_engine, text


def main() -> None:
    engine = create_engine("sqlite://", echo=True)
    statement = text("SELECT 'hello world' AS greeting")

    with engine.connect() as connection:
        driver_connection = connection.connection.driver_connection
        print("DBAPI connection:", type(driver_connection).__name__)

        first_row = connection.execute(statement).first()
        assert first_row is not None
        assert first_row[0] == "hello world"
        assert first_row.greeting == "hello world"
        assert first_row._mapping["greeting"] == "hello world"

        rows = connection.execute(statement).all()
        assert len(rows) == 1

        multiple_rows = text(
            "SELECT 1 AS item_id, 'hello' AS greeting "
            "UNION ALL SELECT 2, 'SQLAlchemy'"
        )
        tuple_rows = connection.execute(multiple_rows).all()
        scalar_values = connection.execute(multiple_rows).scalars().all()
        assert [row.greeting for row in tuple_rows] == ["hello", "SQLAlchemy"]
        assert scalar_values == [1, 2]

        print("First row:", first_row)
        print("All rows:", tuple_rows)
        print("First column from each row:", scalar_values)

    engine.dispose()


if __name__ == "__main__":
    main()
