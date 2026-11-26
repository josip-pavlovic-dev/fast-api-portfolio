# Oblast 02 — Čitanje i manipulisanje podacima

Ova oblast obrađuje `SELECT` upite: izbor izvora i kolona, sortiranje i filtriranje rezultata, `NULL` vrednosti i osnovne osobine SQLite tipova. Svaka lekcija se oslanja na prethodne, pa ih je najbolje prolaziti po redosledu.

## Lekcije

1. [`SELECT`: čitanje podataka i izraza](./01_sqlite_select_statement.md)
2. [Čitanje svih kolona iz tabele](./02_querying_data_from_all_columns_in_a_table.md)
3. [Čitanje određenih kolona iz tabele](./03_querying_data_from_specific_columns_in_a_table.md)
4. [Sortiranje rezultata pomoću `ORDER BY`](./04_sorting_data_using_order_by_clause.md)
5. [Uklanjanje ponovljenih vrednosti pomoću `DISTINCT`](./05_removing_duplicate_records_using_distinct_clause.md)
6. [Filtriranje redova pomoću `WHERE`](./06_filtering_data_with_where_clause.md)
7. [Prepoznavanje `NULL` vrednosti](./07_identifying_null_values.md)
8. [Tipovi podataka i klase skladištenja u SQLite-u](./08_sqllite_data_types.md)
9. [Aliasi kolona i tabela](./09_sqlite_aliases.md)

## Na šta posebno da obratiš pažnju

U ovoj oblasti je najvažnije da sigurno čitaš podatke i razumeš kako upit oblikuje rezultat. Temeljno uvežbaj sledeće:

- **Osnove `SELECT` upita:** razlikuj izvor redova (`FROM`), izbor kolona (`SELECT`), filtriranje (`WHERE`), sortiranje (`ORDER BY`) i ograničavanje rezultata (`LIMIT`).
- **Predvidiv redosled:** bez `ORDER BY` redosled nije garantovan; ako više redova deli istu vrednost za sortiranje, dodaj jedinstveni tie-breaker, naročito uz `LIMIT` ili straničenje.
- **`DISTINCT`:** jedinstvenost se odnosi na celu izabranu kombinaciju, ne samo na prvu kolonu, i uklanjaju se duplikati samo iz rezultata — tabela se ne menja.
- **`NULL`:** koristi `IS NULL` / `IS NOT NULL`; `NULL` nije isto što i `''`. Zapamti i razliku između `COUNT(*)` i `COUNT(kolona)`.
- **Logički uslovi:** koristi zagrade kada kombinuješ `AND` i `OR`, i razumi da poređenje sa `NULL` ne daje običan `TRUE` ili `FALSE`.
- **SQLite tipovi:** razlikuj deklarisani tip kolone od klase konkretne sačuvane vrednosti (`typeof()`); obične SQLite tabele imaju afinitet tipa, dok je `STRICT` zasebna opcija.
- **Aliasi:** olakšavaju čitanje rezultata i upita, ali ne preimenuju trajno kolone ili tabele.

## Granični slučajevi u lekcijama i vežbama

Granični slučajevi su obrađeni u teoriji i proveravaju se u odgovarajućim SQL fajlovima u [playground/sql/02_retriving_data_and_manipulating_data/](../playground/sql/02_retriving_data_and_manipulating_data/):

- `ORDER BY`: jednaki ključevi sortiranja i stabilan tie-breaker; podrazumevani položaj `NULL`, `NULLS FIRST/LAST`, prazan tekst i ASCII ograničenja `NOCASE`.
- `DISTINCT`: poređenje cele izabrane kombinacije; ponovljeni `NULL`, prazan tekst i razlika između `BINARY` i `NOCASE`; `COUNT(DISTINCT kolona)` ne broji `NULL`.
- `WHERE` i `NULL`: `AND`/`OR` prioritet i zagrade; poređenje sa `NULL` daje `UNKNOWN`; `IS NULL` nije isto što i poređenje sa praznim tekstom; `LIKE` koristi `%` i `_`.
- SQLite tipovi: afinitet može konvertovati vrednosti, a obična `INTEGER` kolona može sadržati nekonvertibilan tekst. `STRICT` zahteva verziju 3.37.0+ i dozvoljava samo konverzije bez gubitka, ali sam ne dodaje `NOT NULL`.
- Aritmetika i predstavljanje vrednosti: celobrojno naspram realnog deljenja, približna `REAL` preciznost, Boolean vrednosti i datumi bez posebne SQLite storage klase.
- Aliasi: citiranje naziva sa razmacima, opseg aliasa i razlika između prenosivog aliasa u `ORDER BY` i nestandardne upotrebe aliasa u `WHERE`.

Svih devet SQL vežbi možeš ponovo pokrenuti nad `chinook_practice.db`; koristi `-readonly` za glavnu bazu. Vežba tipova pravi samo `TEMP` tabele, koje postoje u istoj konekciji i nestaju kada se ona zatvori. Za `STRICT` primere proveri verziju baš onog SQLite klijenta koji koristiš, jer CLI i SQLTools mogu koristiti različite biblioteke.

### Prenosivo znanje i SQLite specifičnosti

`SELECT`, izbor kolona, filtriranje, sortiranje, `DISTINCT` i pravilno rukovanje sa `NULL` predstavljaju temeljno SQL znanje koje će ti koristiti i u MySQL-u i PostgreSQL-u. SQLite storage klase, afinitet, `STRICT` i ugrađene kolacije treba praktično da razumeš, ali ne moraš sada pamtiti njihove interne detalje. Kada promeniš bazu, ponovo proveri konkretne razlike u tipovima, kolacijama i straničenju.

Ovaj prioritet prati [plan učenja](../plan_ucenja/sta_je_vazno.md): prvo savladaj prenosive SQL koncepte i ponašanje podataka; SQLite specifičnosti nauči dovoljno da prepoznaš njihov uticaj u praksi.

### Kako da radiš vežbe

Prođi lekciju, pokušaj da napišeš upite samostalno, pa ih proveri u odgovarajućem `.sql` fajlu i na `ChinookPractice` bazi. Detaljna uputstva, objašnjena rešenja i proveru razumevanja naći ćeš u [dnevniku vežbi za dan 06](../pitanja_i_odgovori/dan_06_retriving_data_and_manipulating_data_vezbe.md).

Primeri koriste Chinook bazu. U ovoj oblasti upoznaćeš i veze sa SQLAlchemy 2.0, uključujući izbor kolona, uslove upita i imena polja u rezultatu.

Nazad na [glavni README kursa](../README.md).
