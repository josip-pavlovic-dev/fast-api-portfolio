from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Autor(Base):
    __tablename__ = "autor"

    id: Mapped[int] = mapped_column(primary_key=True)
    ime: Mapped[str] = mapped_column(String(100), nullable=False)


def main() -> None:
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Autor(ime="Pera Peric"))
        session.commit()

        autori = session.scalars(select(Autor)).all()
        for autor in autori:
            print(f"{autor.id}: {autor.ime}")


if __name__ == "__main__":
    main()
