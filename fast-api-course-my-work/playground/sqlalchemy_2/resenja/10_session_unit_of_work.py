"""Lekcija 10: Session, Unit of Work, flush, identity map i rollback."""

from datetime import datetime

from sqlalchemy import DateTime, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


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
    SessionFactory = sessionmaker(engine)

    with SessionFactory.begin() as session:
        user = User(name="spongebob", fullname="SpongeBob SquarePants")
        session.add(user)
        assert user in session.new
        assert user.id is None

        session.flush()
        assert user.id is not None
        assert user.created_at is not None
        user_id = user.id

        loaded_user = session.scalars(
            select(User).where(User.name == "spongebob")
        ).one()
        assert loaded_user is user
        print("Pending -> persistent:", user)

    try:
        with SessionFactory.begin() as session:
            user = session.get(User, user_id)
            assert user is not None
            user.fullname = "This change will roll back"
            assert user in session.dirty
            session.flush()
            raise RuntimeError("demonstrate rollback")
    except RuntimeError:
        pass

    with SessionFactory() as session:
        saved_user = session.get(User, user_id)
        assert saved_user is not None
        assert saved_user.fullname == "SpongeBob SquarePants"
        print("Rollback sačuvao prethodno commit-ovanu vrednost:", saved_user.fullname)

    engine.dispose()


if __name__ == "__main__":
    main()
