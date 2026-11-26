# Oblast 00 — Uvod

Uvodne lekcije objašnjavaju šta su **SQLite i relaciona baza podataka**, kako da koristiš **Chinook primer** i kako su organizovani osnovni pojmovi baza podataka.

## Lekcije

1. [Šta je SQLite](./01_what_is_sqlite.md)
2. [Povezivanje primer baze sa SQLite-om](./02_attaching_sample_database_to_sqlite.md)
3. [Povezivanje sa SQLite bazom](./03_how_to_connect_to_sqlite.md)
4. [Osnovni pojmovi baza podataka](./04_database_concepts.md)

Po završetku oblasti trebalo bi da razlikuješ SQLite mehanizam, fajl baze i alat kojim pristupaš bazi, kao i tabele, kolone, redove i veze među tabelama.

## Važni koncepti i granični slučajevi

- SQLite biblioteka, fajl baze i `sqlite3` CLI su različite stvari. Ime ili nastavak fajla ne dokazuje da je otvorena prava baza; proveri putanju pomoću `.databases`.
- Relativne putanje zavise od radnog direktorijuma. Pogrešna putanja pri otvaranju ili običnom `ATTACH` može napraviti novu praznu bazu. Za postojeći fajl koji samo pregledaš proveri putanju i koristi read-only način rada.
- Otvaranje fajla kao glavne baze (`main`) nije isto što i `ATTACH`. Priključena baza važi samo u toj konekciji; `PRAGMA foreign_keys` je takođe podešavanje pojedinačne konekcije.
- Iste tekstualne vrednosti u dve tabele same ne uspostavljaju relaciju. Ključevi i odgovarajuća ograničenja definišu veze; povezničke tabele predstavljaju N:M relacije.
- Šema može dozvoliti nula povezanih redova iako poslovno pravilo očekuje najmanje jedan. Razlikuj ono što strani ključ proverava od dodatnih pravila aplikacije.

## Vežbe u Playground-u

SQL vežbe su u [playground/sql/00_intro/](../playground/sql/00_intro/). Pokreni `01_what_is_sqlite.sql` i `03_how_to_connect_to_sqlite.sql` nad radnom Chinook kopijom u read-only režimu. Pokreni `02_attaching_sample_database_to_sqlite.sql` i `04_database_concepts.sql` iz korena repozitorijuma u svežoj `sqlite3 :memory:` konekciji; druga skripta priključuje postojeće baze sa `mode=ro`, a četvrta pravi primere samo u memorijskoj bazi, ne u trajnom fajlu.

Nazad na [glavni README kursa](../README.md).
