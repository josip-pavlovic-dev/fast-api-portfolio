# Priprema: osnovni SQL

Ovaj modul osvežava SQL koji ti treba da pratiš SQLAlchemy 2.0 kurs: relacione tabele, `CREATE TABLE`, `INSERT` i `SELECT` sa osnovnim filtriranjem i spajanjem tabela. Primeri koriste SQLite sintaksu, jer SQLite već koristiš u kursnim vežbama.

Cilj nije da naučiš svaki SQL detalj pre SQLAlchemy-ja. Cilj je da, kada vidiš SQL koji SQLAlchemy generiše, prepoznaš koje tabele i kolone koristi, koje redove bira i koje podatke upisuje.

## Redosled

1. [Tabele, kolone i `CREATE TABLE`](01_tabele_i_create_table.md)
2. [`INSERT` i unos vrednosti](02_insert.md)
3. [`SELECT`, filtriranje i JOIN](03_select_filtriranje_i_join.md)
4. [Vežbe](04_vezbe.md)
5. [Rešenja](05_resenja.md)

## Obuhvat i granica

Obrađujemo relacione tabele, tipove/ograničenja potrebna za SQLAlchemy modele, unos redova, čitanje izabranih kolona, `WHERE`, `ORDER BY` i osnovni JOIN preko stranog ključa. Transakcije, `COMMIT`/`ROLLBACK`, agregacije, indeksi, migracije i napredni SQL dolaze kasnije.

SQLite je stvarna SQL baza, ali se pojedinosti kao što su tipovi, automatsko generisanje ključeva, datumske vrednosti i podrška za pojedine izraze razlikuju među bazama. Kada napišemo nešto specifično za SQLite, to ćemo jasno označiti.

## Kako da koristiš materijal

Pročitaj teoriju, prekrij rešenja, prekucaj zadatke u SQLite okruženju koje koristiš za vežbu, pa uporedi rezultat. Obrati pažnju da SQL iskaz opisuje šta baza treba da uradi; SQLAlchemy kasnije može da ga sastavi za tebe, ali ne menja njegovu relacionu logiku.
