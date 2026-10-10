# Priprema: Python klase i instance

Ovaj folder je osveženje Python OOP osnova koje su potrebne za SQLAlchemy 2.0 i FastAPI. Fokus je na klasama, instancama, atributima i tome kako SQLAlchemy deklarativna klasa opisuje tabelu, dok FastAPI/Pydantic klase opisuju i validiraju podatke razmene.

Primeri su usklađeni sa projektom: Python 3.12, SQLAlchemy 2.0 tipizovani ORM (`DeclarativeBase`, `Mapped`, `mapped_column`) i Pydantic 2 (`BaseModel`, `ConfigDict`). Ne uvodimo ovde SQL niti transakcije; to su sledeće pripremne oblasti.

## Redosled učenja

1. [Klase, instance i `self`](01_klase_i_instance.md)
2. [Atributi, metode i nasleđivanje](02_atributi_metode_i_nasledjivanje.md)
3. [SQLAlchemy model kao Python klasa i tabela](03_sqlalchemy_modeli_kao_klase.md)
4. [FastAPI, Pydantic šeme i ORM instance](04_fastapi_pydantic_i_orm.md)
5. [Vežbe](05_vezbe.md)
6. [Rešenja](06_resenja.md)

## Kako da koristiš materijal

Pročitaj jednu teorijsku celinu, prekrij rešenja, uradi odgovarajuće zadatke i tek onda uporedi pristup. Važno je da za svaki primer umeš da kažeš da li gledaš klasu ili instancu i gde se vrednost čuva.

Kratka mapa termina:

- `Item` je klasa; kod ORM modela opisuje i mapiranu tabelu.
- `item = Item(name="Knjiga")` pravi instancu sa konkretnim vrednostima atributa.
- `Item.name` je SQLAlchemy class-level atribut koji može predstavljati SQL kolonu/izraz.
- `item.name` je Python vrednost atributa konkretne instance.
- `ItemCreate` je Pydantic klasa za ulazne podatke; nije baza niti SQL tabela.

Dok čitaš primere, pitaj se: da li je ovo klasa koja opisuje oblik ili instanca koja trenutno nosi konkretne vrednosti?
