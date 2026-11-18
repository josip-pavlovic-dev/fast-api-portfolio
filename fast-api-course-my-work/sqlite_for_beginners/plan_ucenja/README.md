# Plan učenja po danima

Plan pokriva materijale koji su trenutno pripremljeni: uvodnu oblast, osnovne SQLite CLI komande i lekcije o čitanju i filtriranju podataka. Počinje u četvrtak, **19. novembra 2026.** i traje 12 dana. Svaki dan je planirano četiri sata fokusiranog rada; kratke pauze pravi između blokova i ne računaj ih u ta četiri sata.

Koristi [playground](../playground/README.md) za SQL skripte i lokalne baze. Radi na `playground/databases/chinook_practice.db`, a ne na originalnoj bazi. Vežbe koje koriste SQLite CLI komande pokreći u CLI-ju; one nisu obični SQL upiti.

## Ritam za svaki dan — 4 sata

| Vreme   | Aktivnost                                                                                                                  |
| ------- | -------------------------------------------------------------------------------------------------------------------------- |
| 30 min  | Priseti se prethodnog gradiva bez gledanja u beleške i postavi cilj dana. Prvog dana iskoristi vreme za proveru okruženja. |
| 60 min  | Pročitaj planirane lekcije i zapiši ključne pojmove i pitanja.                                                             |
| 120 min | Rešavaj vežbe iz lekcija u odgovarajućim fajlovima u `playground/`.                                                        |
| 30 min  | Pokreni rešenja, proveri rezultate i zapiši šta treba ponoviti.                                                            |

Kada su planirane dve lekcije, podeli teorijski i praktični blok između njih. Ne preskači vežbe da bi završio čitanje ranije; cilj je da samostalno napišeš i proveriš upite.

---

## Raspored

| Dan i datum                       | Fokus i materijali                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1 — četvrtak, 19. novembar**    | Upoznavanje sa SQLite-om i primer bazom: [Šta je SQLite](../00_intro/01_what_is_sqlite.md) i [Povezivanje primer baze sa SQLite-om](../00_intro/02_attaching_sample_database_to_sqlite.md). Otvori Chinook kopiju, pregledaj tabele i uporedi ih sa [ERD dijagramom](../chinook/ERD.drawio).                                                                                                                                                     |
| **2 — petak, 20. novembar**       | Konekcije i relacioni pojmovi: [Povezivanje sa SQLite bazom](../00_intro/03_how_to_connect_to_sqlite.md) i [Osnovni pojmovi baza podataka](../00_intro/04_database_concepts.md). Pronađi primere tabela, redova, kolona i veza u Chinook bazi.                                                                                                                                                                                                   |
| **3 — subota, 21. novembar**      | SQLite komandni alat: [Šta je `sqlite3` alat](../01_some_basic_sql_commands/01_what_is_sqlite3_tool.md). Vežbaj otvaranje baze, proveru putanje i razliku između trajne i privremene baze.                                                                                                                                                                                                                                                       |
| **4 — nedelja, 22. novembar**     | Pregled baze kroz CLI: [Često korišćene SQLite komande](../01_some_basic_sql_commands/02_some_commonly_used_sqlite3_commands.md). Vežbaj `.tables`, `.schema`, `.mode`, `.headers`, `.read`, `.once` i `.output`.                                                                                                                                                                                                                                |
| **5 — ponedeljak, 23. novembar**  | Izvoz i obnavljanje: [SQLite `.dump` komanda](../01_some_basic_sql_commands/03_sqlite_dump_command.md). Napravi dump, vrati ga u novu lokalnu bazu i uporedi dump sa kopijom baze. Ne prepisuj originalni Chinook fajl.                                                                                                                                                                                                                          |
| **6 — utorak, 24. novembar**      | Osnove `SELECT`: [SQLite `SELECT` naredba](../02_retriving_data_and_manipulating_data/01_sqlite_select_statement.md) i [Upit nad svim kolonama](../02_retriving_data_and_manipulating_data/02_querying_data_from_all_columns_in_a_table.md). Vežbaj čitanje rezultata i izbor tabele.                                                                                                                                                            |
| **7 — sreda, 25. novembar**       | Izbor i redosled kolona: [Odabir konkretnih kolona](../02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.md) i [Sortiranje pomoću `ORDER BY`](../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md). Napiši upite sa više ključeva sortiranja.                                                                                                                            |
| **8 — četvrtak, 26. novembar**    | Jedinstvene vrednosti i uslovi: [`DISTINCT`](../02_retriving_data_and_manipulating_data/05_removing_duplicate_records_using_distinct_clause.md) i [`WHERE`](../02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.md). Kombinuj poređenja i uslove, a rezultate proveri u bazi.                                                                                                                                         |
| **9 — petak, 27. novembar**       | Nedostajuće vrednosti: [Prepoznavanje `NULL` vrednosti](../02_retriving_data_and_manipulating_data/07_identifying_null_values.md). Uporedi `NULL`, prazan tekst i obične vrednosti; reši vežbe za `Company` i `Composer`.                                                                                                                                                                                                                        |
| **10 — subota, 28. novembar**     | SQLite tipovi: [SQLite tipovi podataka](../02_retriving_data_and_manipulating_data/08_sqllite_data_types.md). Proveri `typeof()`, afinitet tipova i razliku između običnih i `STRICT` tabela. Ponovi primere bez menjanja Chinook šeme.                                                                                                                                                                                                          |
| **11 — nedelja, 29. novembar**    | Čitljivi rezultati i reference na tabele: [SQLite aliasi](../02_retriving_data_and_manipulating_data/09_sqlite_aliases.md). Vežbaj alias kolone i tabele, pa ponovi teme koje su ti bile najteže.                                                                                                                                                                                                                                                |
| **12 — ponedeljak, 30. novembar** | Ponavljanje i završna vežba. U svojim fajlovima u `playground/sql/02_retriving_data_and_manipulating_data/` napiši samostalne upite koji kombinuju izbor kolona, `WHERE`, `DISTINCT`, `IS NULL`, `ORDER BY` i aliase. Koristi tabele `customers`, `tracks` i `albums`; ne koristi još nezavršene teme poput spajanja tabela. Na kraju objasni kako se tabela, kolona i rezultat upita povezuju sa pojmovima koje ćeš koristiti u SQLAlchemy 2.0. |

---

## Pravila napretka

- Reši vežbe pre nego što pogledaš primere ponovo; zatim proveri rezultat izvršavanjem upita.
- Ako ne završiš gradivo za četiri sata, nastavi ga sledećeg dana i pomeri datume. Razumevanje je važnije od praćenja kalendara.
- Sačuvaj upite u odgovarajućim fajlovima u playground-u i dodaj kratku napomenu o greškama koje si ispravio.
- Posle 12. dana zabeleži teme koje treba ponoviti pre nego što nastaviš na naredne oblasti kursa.
