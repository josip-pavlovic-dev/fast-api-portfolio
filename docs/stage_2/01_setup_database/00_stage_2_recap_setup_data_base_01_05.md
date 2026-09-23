# Stage 2 Recap - Setup Database (Lekcije 01-05)

Ovaj recap povezuje sve lekcije iz oblasti setup baze u jedan praktičan plan ucenja.
Cilj je da kroz par dana učvrstiš razumevanje i pređeš iz teorije u sigurnu praksu.

## 1) Mapa oblasti

## Lekcija 01

Tema: konekcija aplikacije sa SQLite bazom kroz SQLAlchemy.
Ishod:

- razumeš engine, SessionLocal i Base
- razumeš zašto putanja baze zavisi od foldera pokretanja

Materijal:

- [docs/stage_2/01_setup_database/01_database_connection_with_orm_sqlAlchemy/01_database_connection_with_orm_sqlalchemy_detaljno.md](docs/stage_2/01_setup_database/01_database_connection_with_orm_sqlAlchemy/01_database_connection_with_orm_sqlalchemy_detaljno.md)

## Lekcija 02

Tema: modeli i tabele.
Ishod:

- razumeš kako klasa postaje tabela
- razumeš kolone, primarni kljuc, unique, foreign key

Materijal:

- [docs/stage_2/01_setup_database/02_database_tables_models/02_database_tables_models_detaljno.md](docs/stage_2/01_setup_database/02_database_tables_models/02_database_tables_models_detaljno.md)

## Lekcija 03

Tema: glavna ulazna tacka i automatsko kreiranje tabela.
Ishod:

- razumeš create_all i kada se tabele stvarno kreiraju
- razumeš import redosled i zašto je bitan

Materijal:

- [docs/stage_2/01_setup_database/03_main/03_main_detaljno.md](docs/stage_2/01_setup_database/03_main/03_main_detaljno.md)

## Lekcija 04

Tema: osnovni SQL upiti za CRUD logiku.
Ishod:

- znaš INSERT, SELECT, WHERE, UPDATE, DELETE
- razumeš zašto se update i delete rade po id

Materijal:

- [docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md](docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md)

## Lekcija 05

Tema: sqlite3 terminal praksa nad realnom bazom.
Ishod:

- znaš da otvoriš bazu, pogledaš schema i menjaš podatke
- razumeš output modove i proveru rezultata

Materijal:

- [docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md](docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md)

---

## 2) Plan ucenja za 3 dana

## Dan 1 (oko 120 minuta)

- Pročitaj lekcije 01 i 02 redom.
- Nacrtaj svoju mini mapu: engine, SessionLocal, Base, Users, Todos.
- U svojoj svesci napisi sta je razlika izmedju modela i tabele.
- Uradi samoproveru iz obe lekcije.

Exit kriterijum:

- mozes usmeno da objasnis kako SQLAlchemy zna koje tabele postoje.

## Dan 2 (oko 120 minuta)

- Pročitaj lekciju 03.
- Pokreni aplikaciju na jedan stabilan nacin i potvrdi da postoji jedan db fajl.
- Proveri tabelu users i todos.
- Pročitaj lekciju 04 i napisi 10 SQL upita na papiru ili u fajlu.

Exit kriterijum:

- mozes bez pomoci da napises SELECT i WHERE po id i po title.

## Dan 3 (oko 120 minuta)

- Pročitaj lekciju 05.
- U sqlite3 uradi mini rutinu: insert 3 reda, select, update jednog, delete jednog.
- Posle svake operacije radi proveru rezultata.
- Napisi kratki report: 5 stvari koje su sada jasne i 2 koje jos nisu.

Exit kriterijum:

- sigurno manipulišeš podacima kroz sqlite3 bez straha da ćeš obrisati pogrešne redove.

---

## 3) Minimalni praktični zadatak za kraj oblasti

Napraviti startni skup podataka za todos i demonstrirati:

- unos više redova
- čitanje svih redova
- čitanje po id
- update complete polja po id-u
- delete jednog reda po id-u

Definition of done:

- svaka operacija ima proveru posle izvršenja
- nema UPDATE i DELETE bez preciznog WHERE uslova
- možeš objasniti tačno šta se dešava na SQL strani i na ORM strani

---

## 4) Najvažnije lekcije koje treba zapamtiti

1. Putanja baze zavisi od mesta pokretanja aplikacije.
2. Model sam ne kreira tabelu dok se create_all ne izvrsi.
3. Primarni ključ je najbezbedniji način za ciljanje jednog reda.
4. SQL i ORM nisu suparnici, ORM je alat iznad SQL-a.
5. Provera rezultata posle svake izmene je obavezna navika.

---

## 5) Spremnost za sledeću oblast

Spreman si za nastavak kada bez pomoći možeš:

- objasniti `engine`, `session` i `base`

`engine` - povezuje se sa stvarnom bazom podataka i omogućava izvršavanje SQL upita. Ključna je komponenta za komunikaciju sa bazom. On zna sve o vezi sa bazom i kako da izvrši SQL komande. Kroz `engine` se uspostavlja veza i šalju SQL upiti. Nije odmah aktivan dok se ne izvrši neka operacija koja zahteva vezu. Kreira se obično jednom i koristi tokom celog životnog ciklusa aplikacije.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///example.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
```

`session` - predstavlja radnu jedinicu za interakciju sa bazom podataka, omogućava izvršavanje upita i upravljanje transakcijama. Kreira se obično po potrebi i koristi za grupisanje operacija koje treba izvršiti u okviru jedne transakcije. Traje dok se eksplicitno ne zatvori uz `session.close()`. Na primer, možeš otvoriti sesiju, izvršiti nekoliko upita i zatim je zatvoriti.

```python
# Otvaranje sesije
session = Session()

# Izvršavanje upita
# ...

# Zatvaranje sesije
session.close()
```

`base` - služi kao osnovna klasa za definisanje modela koji se mapiraju na tabele u bazi.

Klasa `Base` pruža osnovnu funkcionalnost i metapodatke potrebne SQLAlchemy-ju za mapiranje modela na tabele. Svi modeli koje definišeš treba da naslede ovu klasu kako bi SQLAlchemy znao da ih treba mapirati na tabele. Na primer:

```python
from sqlalchemy import Column, Integer, String, Boolean
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    complete = Column(Boolean)
```

- povezati `model` sa stvarnom tabelom

```python
# Povezivanje modela sa stvarnom tabelom
Base.metadata.create_all(bind=engine)
```

`model` se povezuje sa stvarnom tabelom u bazi kada se izvrši `Base.metadata.create_all(bind=engine)`.

`Base` predstavlja osnovnu klasu za sve modele i sadrži metapodatke o tabelama koje nasleđuju ovu klasu.

`Base.metadata` sadrži informacije o svim tabelama, kolonama i vezama definisanim u modelima.

`Base.metadata.create_all` kreira sve tabele definisane u modelima koji nasleđuju `Base`.

`bind` predstavlja vezu sa bazom podataka koja se koristi prilikom kreiranja tabela sa `Base.metadata.create_all(bind=engine)`.

`engine` predstavlja instancu SQLAlchemy engine-a koja se koristi za povezivanje sa bazom podataka.

`bind=engine` predstavlja vezu sa bazom podataka koja se koristi prilikom kreiranja tabela sa `Base.metadata.create_all(bind=engine)`.

- napisati i izvršiti osnovne SQL CRUD upite (`SELECT`, `INSERT`, `UPDATE`, `DELETE`)

```sql
-- SELECT
SELECT * FROM todos;

-- INSERT
INSERT INTO todos (title, complete) VALUES ('Learn SQLAlchemy', 0);

-- UPDATE
UPDATE todos SET complete = 1 WHERE id = 1;

-- DELETE
DELETE FROM todos WHERE id = 1;
```

- bezbedno uraditi `UPDATE` i `DELETE` po `id`

```sql
-- Bezbedno uraditi UPDATE po id
UPDATE todos SET complete = 1 WHERE id = 1;

-- Bezbedno uraditi DELETE po id
DELETE FROM todos WHERE id = 1;
```

Ako ovo prolazi, prelaz u sledeću oblast će biti znatno lakši.
