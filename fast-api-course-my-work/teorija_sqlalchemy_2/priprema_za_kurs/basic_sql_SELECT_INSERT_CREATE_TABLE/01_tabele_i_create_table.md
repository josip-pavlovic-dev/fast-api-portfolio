# 01: Relacione tabele i `CREATE TABLE`

## Šta je relaciona tabela?

Relacione podatke organizujemo u tabele. Tabela ima:

- **ime** koje opisuje vrstu stvari koju čuva;
- **kolone** koje opisuju osobine tih stvari;
- **redove** u kojima se nalaze konkretni podaci.

Na primer, tabela `user_account` može imati kolone `id`, `name` i `fullname`. Jedan red predstavlja jednog korisnika:

| id  | name        | fullname                |
| --- | ----------- | ----------------------- |
| 1   | `spongebob` | `SpongeBob SquarePants` |
| 2   | `sandy`     | `Sandy Cheeks`          |

Kolona odgovara jednoj vrsti podatka, a red jednom zapisu. U Python ORM modelu kasnije ćemo povezati takav red sa instancom `User`, a tabelu i kolone sa deklarativnom klasom i njenim mapiranim atributima.

## SQL naredba i konvencije

SQL se sastoji od naredbi kao što su `CREATE TABLE`, `INSERT` i `SELECT`. U primerima pišemo ključne reči velikim slovima radi čitljivosti; većina SQL baza ne razlikuje velika i mala slova za ključne reči. Imena tabela/kolona i osetljivost njihovih navodnika mogu zavisiti od baze.

Tekstualne vrednosti pišu se u jednostrukim navodnicima:

```sql
'Sandy Cheeks'
```

Identifikator kao što je ime kolone obično se piše bez navodnika. Navodnike za identifikatore koristimo kada je potrebno zbog rezervisane reči ili specijalnih znakova, ali je jednostavnije birati jasna imena kao `user_account` i `created_at`.

## Tipovi podataka

Kolona ima tip koji opisuje kakve vrednosti očekujemo. Česti SQL tipovi su:

| Tip                               | Primer upotrebe                                       |
| --------------------------------- | ----------------------------------------------------- |
| `INTEGER`                         | ID ili broj komada                                    |
| `VARCHAR(n)`                      | tekst ograničene dužine u bazama koje koriste taj tip |
| `TEXT`                            | duži tekst                                            |
| `NUMERIC(p, s)` / `DECIMAL(p, s)` | precizan decimalni broj, često cena                   |
| `REAL`                            | približan decimalni broj u SQLite-u                   |
| `DATE` / `DATETIME` / `TIMESTAMP` | datum ili datum i vreme; tačna podrška zavisi od baze |

SQLite je fleksibilniji u čuvanju tipova nego, na primer, PostgreSQL: deklarisani tip utiče na affinity i konverzije, ali ne predstavlja potpuno istu strogu garanciju tipa. U kursu će SQLAlchemy dijalekt prevoditi svoje tipove kao `String`, `Integer`, `Numeric` i `DateTime` u oblik koji izabrana baza razume.

Važno je razlikovati Python tip od SQL tipa. Python vrednost može biti `str`, a SQLAlchemy tip `String(120)` se prevodi u tip kolone za bazu. To su povezani, ali različiti slojevi.

## Ograničenja: pravila nad kolonama

Ograničenja (_constraints_) čuvaju osnovna pravila integriteta u samoj šemi baze.

### Primarni ključ

`PRIMARY KEY` jedinstveno identifikuje svaki red u tabeli. Jednostavan izbor je celobrojni `id`:

```sql
id INTEGER PRIMARY KEY
```

U SQLite-u `INTEGER PRIMARY KEY` je poseban slučaj vezan za `rowid`; ako se pri `INSERT` ID izostavi, SQLite obično dodeli sledeći ID. Reč `AUTOINCREMENT` nije potrebna za uobičajeno automatsko dodeljivanje i ima dodatnu semantiku, pa je ne dodajemo bez razloga.

Druge baze imaju svoje oblike za identity/auto-generated ključeve. SQLAlchemy `primary_key=True` izražava nameru u modelu, a dijalekt generiše odgovarajući DDL.

### `NOT NULL`

`NOT NULL` zabranjuje da kolona sadrži SQL `NULL`:

```sql
name TEXT NOT NULL
```

Ono ne zabranjuje prazan tekst `''` niti tekst sastavljen od razmaka. To bi zahtevalo dodatnu validaciju ili ograničenje.

### `UNIQUE`

`UNIQUE` zabranjuje ponovljene vrednosti u koloni:

```sql
email TEXT NOT NULL UNIQUE
```

`NOT NULL` i `UNIQUE` su nezavisna pravila: jedno zahteva vrednost, drugo sprečava duplikate.

### `DEFAULT`

`DEFAULT` obezbeđuje vrednost kada `INSERT` izostavi kolonu:

```sql
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Ako upit izričito pošalje `NULL`, default se obično ne primenjuje; `NOT NULL` bi takav unos odbio. SQLAlchemy `server_default` se pretvara u ovakvo pravilo u DDL-u.

### Strani ključ

Strani ključ povezuje redove dve tabele. Primer: svaka adresa čuva ID korisnika kome pripada:

```sql
user_id INTEGER NOT NULL REFERENCES user_account(id)
```

To je FK kolona na strani „više“: jedan korisnik može imati više adresa, a svaka adresa upućuje na jedan korisnički ID. `NOT NULL` je dodatno pravilo koje kaže da adresa mora imati korisnika; FK sam po sebi ne znači da je kolona obavezna.

SQLite zahteva da se FK enforcement uključi na svakoj konekciji pomoću `PRAGMA foreign_keys=ON`; bez toga constraint može biti naveden u tabeli, a da SQLite ipak ne odbija nevažeće reference. Druge baze uobičajeno sprovode FK constraint prema svojim pravilima.

## Kreiranje tabele: `CREATE TABLE`

Sledeći SQLite-kompatibilan primer opisuje tabelu korisnika:

```sql
CREATE TABLE user_account (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    fullname TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Čitaj ga redom:

1. `CREATE TABLE user_account` kaže da pravimo tabelu pod tim imenom.
2. Svaki sledeći red definiše jednu kolonu.
3. Posle tipa dolaze opciona ograničenja.
4. Zarez odvaja definicije kolona/ograničenja; poslednji element nema zarez.
5. Tačka-zarez završava SQL naredbu.

Primer druge tabele i FK-a:

```sql
CREATE TABLE address (
    id INTEGER PRIMARY KEY,
    email_address TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_account(id)
);
```

Tabele moraju biti definisane u skladu sa zavisnošću: `user_account` postoji pre nego što `address` referencira njen ključ.

`CREATE TABLE` pravi strukturu tabele, ne popunjava je redovima. U SQLAlchemy-ju Python model opisuje šemu u metadata-i, a `Base.metadata.create_all(...)` kasnije može poslati DDL za tabele koje nedostaju. Sama ORM klasa nije isto što i fizička tabela.

## Veza sa SQLAlchemy deklarativnom klasom

Slična struktura se u SQLAlchemy-ju 2.0 opisuje klasom:

```python
class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    fullname: Mapped[str | None] = mapped_column(String(100))
```

| SQL ideja                        | SQLAlchemy deklaracija                                   |
| -------------------------------- | -------------------------------------------------------- |
| tabela `user_account`            | `__tablename__ = "user_account"`                         |
| kolona sa mapiranim Python tipom | `name: Mapped[str]`                                      |
| SQL tip i dodatna pravila        | `mapped_column(String(50), nullable=False, unique=True)` |
| primarni ključ                   | `primary_key=True`                                       |
| strani ključ ka drugoj tabeli    | `ForeignKey("user_account.id")` na FK koloni             |

Ova paralela je priprema, ne znači da moramo sada već da koristimo SQLAlchemy. Najpre nauči da čitaš tabelu i ograničenja u SQL-u; kasnije ćeš videti kako ORM metadata predstavlja ista pravila.

## Šta ovde još ne obrađujemo?

- kako da popunimo tabelu (`INSERT` je sledeća celina);
- kako da čitamo i filtriramo redove (`SELECT` je posle toga);
- kada se promene potvrđuju (`COMMIT`) ili poništavaju (`ROLLBACK`), jer su transakcije zasebna pripremna oblast;
- kako se šema menja migracijom kada tabela već postoji.
