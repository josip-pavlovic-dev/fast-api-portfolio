from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Deklarativna baza za SQLAlchemy 2.0 ORM modele.
    Koristi se kao osnovna klasa za sve ORM modele/tabele u aplikaciji.
    Svi ORM modeli u aplikaciji treba da nasleđuju ovu klasu.
    Ona ne vraća nikakve podatke sama po sebi.
    Base nasleđuje sve karakteristike SQLAlchemy DeclarativeBase klase.
    """

    pass
