# Stage 2 Recap - Setup Database (Lekcije 01-05)

Ovaj recap povezuje sve lekcije iz oblasti setup baze u jedan praktican plan ucenja.
Cilj je da kroz par dana ucvrstis razumevanje i predjes iz teorije u sigurnu praksu.

## 1) Mapa oblasti

## Lekcija 01

Tema: konekcija aplikacije sa SQLite bazom kroz SQLAlchemy.
Ishod:

- razumes engine, SessionLocal i Base
- razumes zasto putanja baze zavisi od foldera pokretanja

Materijal:

- [docs/stage_2/01_setup_database/01_database_connection_with_orm_sqlAlchemy/01_database_connection_with_orm_sqlalchemy_detaljno.md](docs/stage_2/01_setup_database/01_database_connection_with_orm_sqlAlchemy/01_database_connection_with_orm_sqlalchemy_detaljno.md)

## Lekcija 02

Tema: modeli i tabele.
Ishod:

- razumes kako klasa postaje tabela
- razumes kolone, primarni kljuc, unique, foreign key

Materijal:

- [docs/stage_2/01_setup_database/02_database_tables_models/02_database_tables_models_detaljno.md](docs/stage_2/01_setup_database/02_database_tables_models/02_database_tables_models_detaljno.md)

## Lekcija 03

Tema: glavna ulazna tacka i automatsko kreiranje tabela.
Ishod:

- razumes create_all i kada se tabele stvarno kreiraju
- razumes import redosled i zasto je bitan

Materijal:

- [docs/stage_2/01_setup_database/03_main/03_main_detaljno.md](docs/stage_2/01_setup_database/03_main/03_main_detaljno.md)

## Lekcija 04

Tema: osnovni SQL upiti za CRUD logiku.
Ishod:

- znas INSERT, SELECT, WHERE, UPDATE, DELETE
- razumes zasto se update i delete rade po id

Materijal:

- [docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md](docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md)

## Lekcija 05

Tema: sqlite3 terminal praksa nad realnom bazom.
Ishod:

- znas da otvoris bazu, pogledas schema i menjas podatke
- razumes output modove i proveru rezultata

Materijal:

- [docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md](docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md)

---

## 2) Plan ucenja za 3 dana

## Dan 1 (oko 120 minuta)

- Procitaj lekcije 01 i 02 redom.
- Nacrtaj svoju mini mapu: engine, SessionLocal, Base, Users, Todos.
- U svojoj svesci napisi sta je razlika izmedju modela i tabele.
- Uradi samoproveru iz obe lekcije.

Exit kriterijum:

- mozes usmeno da objasnis kako SQLAlchemy zna koje tabele postoje.

## Dan 2 (oko 120 minuta)

- Procitaj lekciju 03.
- Pokreni aplikaciju na jedan stabilan nacin i potvrdi da postoji jedan db fajl.
- Proveri tabelu users i todos.
- Procitaj lekciju 04 i napisi 10 SQL upita na papiru ili u fajlu.

Exit kriterijum:

- mozes bez pomoci da napises SELECT i WHERE po id i po title.

## Dan 3 (oko 120 minuta)

- Procitaj lekciju 05.
- U sqlite3 uradi mini rutinu: insert 3 reda, select, update jednog, delete jednog.
- Posle svake operacije radi proveru rezultata.
- Napisi kratki report: 5 stvari koje su sada jasne i 2 koje jos nisu.

Exit kriterijum:

- sigurno manipulis podacima kroz sqlite3 bez straha da ces obrisati pogresne redove.

---

## 3) Minimalni prakticni zadatak za kraj oblasti

Napraviti startni skup podataka za todos i demonstrirati:

- unos vise redova
- citanje svih redova
- citanje po id
- update complete polja po id
- delete jednog reda po id

Definition of done:

- svaka operacija ima proveru posle izvrsenja
- nema update i delete bez preciznog where uslova
- mozes objasniti sta se desava na SQL strani i na ORM strani

---

## 4) Najvaznije lekcije koje treba zapamtiti

1. Putanja baze zavisi od mesta pokretanja aplikacije.
2. Model sam ne kreira tabelu dok se create_all ne izvrsi.
3. Primarni kljuc je najbezbedniji nacin za ciljanje jednog reda.
4. SQL i ORM nisu suparnici, ORM je alat iznad SQL-a.
5. Provera rezultata posle svake izmene je obavezna navika.

---

## 5) Spremnost za sledecu oblast

Spreman si za nastavak kada bez pomoci mozes:

- objasniti engine, session i base
- povezati model sa stvarnom tabelom
- napisati i izvrsiti osnovne SQL CRUD upite
- bezbedno uraditi update i delete po id

Ako ovo prolazi, prelaz u sledecu oblast ce biti znatno laksi.
