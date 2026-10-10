# Priprema za SQLAlchemy 2.0

Ovaj folder je pripremni most ka glavnom SQLAlchemy kursu. Redosled je nameran: prvo obnavljamo Python klase i instance, zatim osnovni SQL, pa transakcije. Posle toga možeš da pratiš glavne beleške kursa bez preskakanja pojmova na kojima se kasnije zasnivaju primeri.

Glavni kurs je Mike Bayer, _Tutorial: SQLAlchemy 2.0_ sa Python Web Conf 2023. Beleške glavnog kursa nalaze se u roditeljskom folderu `teorija_sqlalchemy_2/` i prate predavanje kroz lekcije 01–10. Folder `transcripts/` čuva transkripte kurseva koji su korišćeni uz skripte iz REPO-a kursa. Na primer prva skripta [kursa](../../../scratch/sqlalchemy_2_course/python_web_conf_2023-main/python_web_conf_2023-main/slides/00_talking.py).

---

## Preporučeni redosled

Završavaj jednu celinu pre nego što pređeš na sledeću. Svaki pripremni modul ima svoj README sa unutrašnjim redosledom, teorijom, vežbama i rešenjima.

1. **Python klase i instance** — [otvori modul](python_klase_i_instance/README.md). Obnovi klase, instance, `self`, atribute, metode i nasleđivanje. Zatim poveži Python klasu sa SQLAlchemy ORM modelom i Pydantic šemom. Fajlovi idu od `01_klase_i_instance.md` do `04_fastapi_pydantic_i_orm.md`, zatim slede `05_vezbe.md` i `06_resenja.md`.
2. **Osnovni SQL** — [otvori modul](basic_sql_SELECT_INSERT_CREATE_TABLE/README.md). Uči tabele i `CREATE TABLE`, `INSERT`, pa `SELECT`, filtriranje, sortiranje i osnovni `JOIN`. Fajlovi idu od `01_tabele_i_create_table.md` do `03_select_filtriranje_i_join.md`, zatim slede `04_vezbe.md` i `05_resenja.md`.
3. **Transakcije** — [otvori modul](transakcije_osnove/README.md). Razumi pojam transakcije i ACID, zatim `COMMIT`/`ROLLBACK`, SQLAlchemy Core transakcije i ORM `Session`. Obrati posebnu pažnju na razliku između `flush()` i `commit()`. Fajlovi idu od `01_pojam_i_acid.md` do `03_transakcije_u_sqlalchemy.md`, zatim slede `04_vezbe.md` i `05_resenja.md`.
4. **Glavni kurs, lekcije 01–10** — prati tabelu ispod. Već poznaješ deo predznanja, ali i dalje čitaj lekcije redom; pojmovi se nadograđuju.

---

## Glavne lekcije kursa

| Redosled | Lekcija                                                                   |
| -------- | ------------------------------------------------------------------------- |
| 01       | [Uvod u SQLAlchemy](../01_introduction_to_SQLAlchemy.md)                  |
| 02       | [Rad sa `Engine`-om](../02_working_with_the_engine.md)                    |
| 03       | [Upravljanje konekcijama i transakcijama](../03_connection_management.md) |
| 04       | [Model tabele i `MetaData`](../04_table_metadata_model.md)                |
| 05       | [Kreiranje šeme baze](../05_create_database_schema.md)                    |
| 06       | [Unos podataka](../06_insert_data.md)                                     |
| 07       | [Grupni unos podataka](../07_bulk_data_insertion.md)                      |
| 08       | [Čitanje podataka](../08_selecting_data.md)                               |
| 09       | [Filtriranje i sortiranje](../09_filtering_and_ordering.md)               |
| 10       | [ORM `Session` i Unit of Work](../10_ORM_session_and_work_unit.md)        |

---

## Kako da radiš

- U svakom modulu prati njegov `README.md`; on određuje redosled teorije, vežbi i rešenja.
- Prođi jednu teorijsku celinu, prekucaj ili pokreni primere i pokušaj da predvidiš rezultat pre izvršavanja.
- Uradi vežbe bez gledanja rešenja. Otvori rešenja tek kada završiš pokušaj ili jasno znaš gde si zapeo.
- Ako primer ne radi, sačuvaj tačnu grešku i najmanji kod koji je reprodukuje. Rešavaj jednu nejasnoću odjednom.
- Ne moraš unapred da znaš napredni SQL niti svaki detalj ORM-a. Cilj pripreme je da prepoznaš osnovne koncepte i možeš da pratiš kurs.

---

## Provera predznanja

Pre glavnog kursa trebalo bi da možeš svojim rečima da objasniš:

- razliku između `Python klase` i `Python instance`, i šta predstavljaju `ORM klasa` i `ORM objekat`;
- šta `tabela`, `red`, `kolona`, `primarni ključ` i `strani ključ` predstavljaju;
- šta rade `CREATE TABLE`, `INSERT`, `SELECT`, `WHERE`, `ORDER BY` i osnovni `JOIN`;
- zašto više izmena može da pripada jednoj transakciji i šta rade `COMMIT` i `ROLLBACK`;
- da `flush()` pošalje ORM izmene u aktivnu transakciju, ali ih ne potvrđuje kao `commit()`.

Ako neka stavka nije jasna, vrati se samo na odgovarajući pripremni modul; ne moraš ponavljati sve od početka.

---

## Okruženje i bezbednost

Za ovaj repozitorijum koristi postojeći `.venv` u korenu projekta; ne pravi posebno virtuelno okruženje za svaki modul. Proverene verzije su Python 3.12.3 i SQLAlchemy 2.0.38, a zavisnosti su navedene u root fajlu `requirements.txt`.

Iz korena repozitorijuma možeš proveriti okruženje ovako:

```bash
source .venv/bin/activate
python --version
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Transakcioni primeri pripreme koriste memorijsku `SQLite` bazu. Pre pokretanja bilo kog drugog primera proveri njegov URL baze: `SQLite URL` koji sadrži fajl može da napravi ili izmeni trajnu bazu. Nemoj pokretati destruktivne `DROP`, `DELETE` ili `testne izmene` nad korisničkom ili projektnom bazom.

---

## Kratka mapa SQLAlchemy pojmova

- **Core** obezbeđuje rad sa `konekcijama`, `šemom` i `SQL izrazima`; nije ograničen na ručno pisanje sirovog SQL-a.
- **ORM** mapira `Python klase` i `objekte` na `tabele` i `redove` i oslanja se na Core.
- `Engine` je početna tačka za povezivanje i upravljanje `pool-om`;
- `Connection` izvršava Core iskaze i upravlja transakcijama.
- `Session` je objekat koji prati `ORM objekte` i njihove izmene
- `session.add()` registruje objekat čime postaje praćen od strane sesije
- `flush()` šalje izmene kroz aktivnu transakciju bez potvrđivanja.
- `commit()` potvrđuje izmene kroz aktivnu transakciju i završava je.
- `rollback()` odbacuje sve izmene kroz aktivnu transakciju i završava je.
- Zaključak: **Transakcija** određuje granicu potvrđivanja ili poništavanja rada. `commit()` je potvrđuje, `rollback()` odbacuje nepotvrđene izmene.

U SQLAlchemy 2.0 materijalu koristi se savremeni stil, uključujući `select()`, `DeclarativeBase`, `Mapped` i `mapped_column()`. Nemoj mešati primere sa `starijim SQLAlchemy 1.x obrascima` osim kada lekcija izričito poredi stilove.

---

## Orijentir za nastavak u novom chatu

- Objašnjenja i vežbe pripremaj na srpskom, korak po korak i za početnika; prednost imaju razumevanje i prekucavanje primera, ne brzo prelaženje sadržaja.
- Glavni izvor ostaje Mike Bayer PWC 2023 kurs i postojeće beleške/transkripti. Ako se dodaje korisno gradivo van izvora, jasno ga označi kao dodatak umesto da ga predstaviš kao sadržaj predavanja.
- Prisustvo fajla u folderu ne znači da je korisnik završio tu lekciju. Pre nastavka proveri šta je poslednje urađeno i nastavi od prve nezavršene celine.
- Rešenja služe za proveru posle samostalnog pokušaja. Ne prepisuj ih preko vežbi.
- Ne menjaj `fast-api-course-my-work/playground/sqlalchemy_2/resenja/` bez izričitog zahteva; taj folder sadrži korisnikova prethodna rešenja.
- Ne pokreći `git add`, commit ili druge promene Git indeksa/stanja bez izričitog zahteva.

**Sledeći korak:** započni prvim nezavršenim pripremnim modulom iz preporučenog redosleda. Ako su sva tri završena, počni glavni kurs od lekcije 01.
