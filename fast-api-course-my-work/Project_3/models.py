from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db.base import Base


class Todos(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complete: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

# NAPOMENA: ID se automatski generiše i ne treba ga ručno postavljati prilikom kreiranja novog zadatka. Ovo je zbog toga što je ID primarni ključ i NOT NULL kolona u bazi podataka. Ovo omogućava da baza podataka sama upravlja jedinstvenim identifikatorima za svaki zadatak. U sqlite3 iz terminala možete koristiti komandu `.schema todos` da vidite strukturu tabele i primarni ključ. Tu se može videti da je ID kolona ID INTEGER NOT NULL definisana kao PRIMARY KEY i AUTOINCREMENT, što znači da će SQLite automatski dodeljivati jedinstvene vrednosti za svaki novi red automatski.

# Takođe, kada kreirate novi zadatak, možete jednostavno izostaviti ID i pustiti bazu da ga automatski generiše. Na primer:
# novi_zadatak = Todos(title="Novi zadatak", description="Opis zadatka", priority=1)
# db.add(novi_zadatak)
# db.commit()
# db.refresh(novi_zadatak)
# print(novi_zadatak.id)  # ID će biti automatski dodeljen od strane SQLite-a
