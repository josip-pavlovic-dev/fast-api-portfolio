# Kako su source fajlovi raspoređeni po lekcijama

Source paket za drugu oblast okuplja primere iz više lekcija. Ne treba očekivati da svaki fajl pripada samo jednoj lekciji.

| Fajl                    | Lekcija / oblast                                     | Namena                                                                                                                   |
| ----------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `docker-compose.yml`    | Lekcija 02: Docker                                   | Definiše PostgreSQL i pgAdmin servise, portove i početna podešavanja baze.                                               |
| `_docs/db_commands.md`  | Lekcija 02: PostgreSQL u Docker-u                    | Podsetnik za `psql` komande kao što su `\l`, `\c` i `\dt`.                                                               |
| `db.py`                 | Lekcije 03 i 04                                      | `DATABASE_URL` i `create_engine()` pripadaju lekciji 03. `SessionLocal = sessionmaker(...)` je deo sesija iz lekcije 04. |
| `requirement.txt`       | Zajedničko podešavanje                               | Sadrži SQLAlchemy i `psycopg2-binary`, PostgreSQL drajver koji koristi primer engine-a. Nije Docker konfiguracija.       |
| `session.py`            | Lekcija 04: ORM sesije                               | Otvara sesiju i obrađuje commit, rollback i zatvaranje.                                                                  |
| `models.py`             | Modeli iz oblasti 01; koristi se ponovo u lekciji 05 | Opisuje tabele i relacije koje će se kasnije kreirati u bazi. Uključuje i event/trigger kod iz prethodne oblasti.        |
| `reset_db.py`           | Lekcija 05: kreiranje tabela                         | Briše pa ponovo kreira tabele iz modela. Destruktivno je za postojeće podatke.                                           |
| `1_migration.py`        | Lekcija 05                                           | Poziva `reset_database()`. Ime je varljivo: ovo nije Alembic migracija, već pokreće drop-and-recreate skriptu.           |
| `.vscode/settings.json` | Uređivačko podešavanje                               | Podešava VS Code formatter; ne utiče na Docker, PostgreSQL ili SQLAlchemy engine.                                        |

## Najvažnija razlika

Docker pokreće PostgreSQL server. SQLAlchemy engine povezuje Python aplikaciju sa serverom. Zato `docker-compose.yml` pripada lekciji 02, a `create_engine()` u `db.py` lekciji 03. Isti `db.py` sadrži i `sessionmaker()`, koji se obrađuje u lekciji 04.

## Dogovor za rad u ovom repozitorijumu

- Koristimo jedan postojeći `.venv` iz root-a repozitorijuma; ne pravimo environment unutar source paketa i ne instaliramo njegove zavisnosti zasebno.
- Za lekciju 03 fokus je na URL-u i engine-u. Sesije dolaze u lekciji 04, a kreiranje i reset tabela u lekciji 05.
- `reset_db.py` i `1_migration.py` ne pokretati nad bazom čiji podaci treba da se sačuvaju.
- Source fajlovi su kurski snapshot-i. Čuvamo ih neizmenjene; u sopstvenom praktičnom kodu ćemo kasnije koristiti `Mapped`/`mapped_column` i porediti ih sa starom `Column` sintaksom.
