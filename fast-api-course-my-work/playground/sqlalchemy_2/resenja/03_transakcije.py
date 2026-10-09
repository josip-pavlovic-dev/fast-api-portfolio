"""Lekcija 03: uporedi close/rollback, commit i transakcijski blok."""

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select


def main() -> None:
    metadata = MetaData()
    note = Table(
        "note",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("text", String(100), nullable=False),
    )
    engine = create_engine("sqlite://", echo=True)
    metadata.create_all(engine)

    with engine.connect() as connection:
        connection.execute(note.insert().values(text="rolled back on close"))

    with engine.begin() as connection:
        connection.execute(note.insert().values(text="committed one"))
        connection.execute(note.insert().values(text="committed two"))

    try:
        with engine.begin() as connection:
            connection.execute(note.insert().values(text="rolled back on error"))
            raise RuntimeError("demonstrate transaction rollback")
    except RuntimeError:
        pass

    with engine.connect() as connection:
        saved = (
            connection.execute(select(note.c.text).order_by(note.c.id)).scalars().all()
        )
        assert saved == ["committed one", "committed two"]
        print(saved)

    engine.dispose()


if __name__ == "__main__":
    main()
