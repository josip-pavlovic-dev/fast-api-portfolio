# Lekcija 5: Kreiranje i uklanjanje tabela u bazi

## Cilj lekcije

U prethodnim lekcijama pripremili smo PostgreSQL server, SQLAlchemy engine i ORM sesije. Sada povezujemo modele iz prve oblasti sa stvarnom šemom baze pomoću `Base.metadata.create_all()` i `Base.metadata.drop_all()`.

Ove metode su korisne za početno kreiranje i uklanjanje tabela. Važno je da `drop_all()` briše tabele i njihove podatke, a `create_all()` nije migracioni alat za izmene postojećih tabela.

## `Base.metadata` i modeli

Deklarativna klasa `Base` obezbeđuje zajednički metadata registry. Kada se definišu klase koje nasleđuju `Base`, SQLAlchemy u njegov `metadata` objekat registruje opis njihovih tabela: kolone, primarne i strane ključeve, constraint-e, indekse i povezane informacije.

Da bi tabela ušla u taj metadata objekat, odgovarajući Python modul sa modelom mora biti učitan. U source primeru svi modeli su definisani u `models.py`; `from models import Base` izvršava taj modul i registruje njegove klase pre poziva `create_all()` ili `drop_all()`.

Metadata sadrži opise šeme iz Python modela. To nije isto što i živa šema PostgreSQL baze i ne predstavlja kopiju redova/podataka u bazi.

## Zašto se za šemu koristi engine

Kreiranje i uklanjanje tabela su DDL/schema operacije. SQLAlchemy koristi engine da pribavi konekciju i pošalje potrebne DDL naredbe direktno bazi. ORM sesija je namenjena radu sa ORM objektima i transakcijama u aplikaciji; za ove pozive nije potrebna.

To ne znači da engine sam zna koje tabele treba napraviti. Strukturu dobija iz `Base.metadata`, a engine obezbeđuje pristup konkretnoj bazi.

## Kreiranje tabela: `create_all()`

Osnovni poziv iz SQLAlchemy-ja je:

```python
Base.metadata.create_all(bind=engine)
```

SQLAlchemy pregleda tabele registrovane u metadata objektu, sastavi odgovarajuće DDL naredbe za aktivni dijalekt i pošalje ih bazi. Zavisnosti, kao što su strani ključevi, uzimaju se u obzir pri redosledu kreiranja.

Podrazumevano je `checkfirst=True`: SQLAlchemy proverava da li tabela već postoji i kreira one koje nedostaju. Ako tabela već postoji, `create_all()` je ne briše niti automatski usklađuje njene kolone sa novim modelom.

Zato izraz iz predavanja „migrirati modele u bazu“ treba razumeti kao kreiranje tabela iz modela u ovom početnom primeru. To nije isto što i kontrolisana migracija postojeće šeme.

## Uklanjanje tabela: `drop_all()`

Source funkcija za reset je:

```python
from db import engine
from models import Base


def reset_database():
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)
```

`drop_all()` uklanja tabele obuhvaćene tim metadata objektom koje postoje u ciljnoj bazi. SQLAlchemy obrađuje zavisnosti između tabela, uključujući strane ključeve. Metoda ne briše nasumično sve objekte u celoj PostgreSQL instanci niti tabele koje nisu deo tog metadata objekta.

Međutim, za sve obuhvaćene tabele brišu se i redovi/podaci. Drugi poziv zatim kreira prazne tabele ponovo. Zato `reset_database()` nije bezopasan način da se „osveže“ modeli.

`drop_all()` takođe podrazumevano proverava postojanje tabela pre pokušaja brisanja. To pomaže kada neka od deklarisanih tabela još ne postoji, ali ne štiti podatke od brisanja kada tabela postoji.

## `1_migration.py` i stvarni tok izvršavanja

Priloženi fajl `1_migration.py` sadrži:

```python
import reset_db

reset_db.reset_database()
```

Poziv je na najvišem nivou fajla, pa se `reset_database()` izvršava kada se skripta pokrene, na primer:

```bash
python 1_migration.py
```

Samo definisanje funkcije u `reset_db.py` ne pokreće je. U ovom source-u poziv iz `1_migration.py` pokreće reset. Transkript jednom kaže da će se funkcija pozivati „svaki put kada pokrenem query“; to nije tačno za prikazani kod. Funkcija se poziva kada se izvrši ovaj skript ili kada je drugi kod eksplicitno pozove, ne pri svakom SQL upitu.

Ime `1_migration.py` može da navede na pogrešan zaključak. Ovo nije Alembic migracija i nema verzionisanu istoriju promena. To je skripta za brisanje i ponovno kreiranje tabela. Ne pokretati je nad bazom sa podacima koje treba sačuvati; ne uvoziti je iz drugog modula koji se redovno koristi, jer se reset izvršava već pri import-u.

## Zašto `create_all()` ne zamenjuje migracije

`create_all()` kreira tabele koje nedostaju; ne menja postojeću tabelu da odgovara izmenjenom modelu. Na primer, ako se modelu doda kolona, ponovno pozivanje `create_all()` samo po sebi neće dodati tu kolonu već postojećoj tabeli.

`drop_all()` pa `create_all()` može privremeno da napravi novu praznu šemu, ali uz cenu gubitka podataka. Za razvoj šeme kroz vreme koristi se migracioni alat, u ovom kursu kasnije Alembic, koji čuva kontrolisane i verzionisane promene.

## Trigger iz prethodne oblasti

Source `models.py` registruje PostgreSQL DDL listener na `Category.__table__` za `after_create`. Ako se tabela `category` zaista kreira pozivom SQLAlchemy schema API-ja, listener izvršava DDL koji kreira funkciju i trigger za normalizaciju `name` i `slug`.

Ako tabela već postoji i `create_all()` je preskoči, `after_create` događaj se ne emituje za nju i taj poziv neće naknadno dodati trigger. To je još jedan primer zašto `create_all()` nije alat za izmene postojeće šeme.

Kada `drop_all()` ukloni tabelu `category`, trigger vezan za tu tabelu uklanja se zajedno s njom. Trigger funkcija je zaseban objekat u PostgreSQL-u; source je ponovo definiše sa `CREATE OR REPLACE FUNCTION` pri narednom kreiranju tabele.

## Provera šeme u `psql`

Nakon pokretanja kreiranja tabela, `psql` može da proveri rezultat. U Compose kontejneru primer konekcije je:

```bash
docker compose exec postgres psql -U postgres -d inventory
```

U `psql` konzoli:

```text
\l
```

`\l` prikazuje baze u PostgreSQL serveru. `inventory` je **baza podataka**, ne tabela.

```text
\dt
```

`\dt` prikazuje tabele u trenutno izabranoj bazi i šemi. Očekuju se tabele iz modela, na primer `category`, `product`, `promotion_event` i druge.

```text
\d category
```

`\d category` prikazuje detalje konkretne tabele, uključujući kolone, indekse, strane ključeve i trigger-e koji su na nju vezani. `\d` bez imena objekta i `\dt` nisu ista komanda; za pregled tabela koristi se `\dt`.

PostgreSQL može prikazivati i sekvence koje služe za generisanje vrednosti primarnih ključeva. Sekvenca je zaseban schema objekat, nije tabela i neće se pojaviti kao tabela u `\dt` izlazu.

## Važna nepodudarnost u source modelima

U `models.py` se `CheckConstraint` deklaracije sa imenima `check_category_...` nalaze unutar klase `Product`. Zato se primenjuju na `product`, a ne na `category`. Trigger listener je, s druge strane, registrovan za `Category` tabelu. Prilikom pregleda `\d category` treba očekivati category kolone i trigger, ali ne product check constraint-e.

Imena constraint-a ne određuju tabelu; određuje je model/table objekat u čijem se metadata opisu constraint nalazi. Ova nepodudarnost je deo dostavljenog source snapshot-a i ovde ga ne menjamo.

## Povezivanje koraka iz oblasti

- Docker Compose pokreće PostgreSQL server i početnu bazu.
- Engine iz `db.py` zna kako da se poveže sa tim serverom.
- ORM sesija služi za rad sa podacima i transakcijama aplikacije.
- `Base.metadata` sadrži definicije modela, a schema metode koriste engine da kreiraju ili uklone odgovarajuće tabele.

Sesija zato nije potrebna za ovu operaciju schema kreiranja. Podaci koji se kasnije upisuju kroz sesiju predstavljaju zaseban rad nad već postojećom šemom.

## Pitanja za proveru razumevanja

1. Šta `Base.metadata` zna o modelima?
2. Zašto se za `create_all()` i `drop_all()` prosleđuje engine, a ne ORM sesija?
3. Šta se dešava ako tabela već postoji pa pozovemo `create_all()`?
4. Koje podatke uklanja `drop_all()` u `reset_database()`?
5. Zašto `1_migration.py` nije prava Alembic migracija?
6. Kada se izvršava `reset_database()` prema prikazanom kodu?
7. Zašto izmena modela nije automatski preneta na postojeću tabelu?
8. Koja je razlika između `\l`, `\dt` i `\d category`?
9. Zašto se product check constraint-i ne vide kao constraint-i tabele `category`?

## Sažetak

- Modeli nasleđuju `Base` i registruju opise tabela u `Base.metadata`.
- `Base.metadata.create_all(bind=engine)` kreira nedostajuće tabele; ne menja postojeće tabele i ne čuva migracionu istoriju.
- `Base.metadata.drop_all(bind=engine)` uklanja metadata tabele i njihove podatke.
- Source reset skripta briše tabele pa ih pravi ponovo; `1_migration.py` poziva reset pri pokretanju i nije Alembic migracija.
- Schema operacije koriste engine direktno, bez ORM sesije.
- `\dt` prikazuje tabele, `\d category` detalje tabele, a `\l` baze.
- Ovo je peta i poslednja lekcija oblasti: sada su modeli, PostgreSQL, engine, sesije i početno kreiranje šeme povezani u jedan tok.
