# 03: Transakcije u SQLAlchemy-ju

## Engine i Connection: Core transakcije

SQLAlchemy Core koristi `Engine` za upravljanje konekcijama i `Connection` za izvršavanje iskaza. Za transakcije su najvažnija tri obrasca.

## Obrazac 1: `engine.connect()` i eksplicitni `commit()`

Ovaj obrazac je poznat i kao `commit as you go`: izvršiš iskaze, pa eksplicitno potvrdiš posao kada odlučiš da je uspešan.

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://", echo=True)

with engine.connect() as connection:
    connection.execute(
        text("CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    )
    connection.commit()

    connection.execute(
        text("INSERT INTO note (text) VALUES (:text)"),
        {"text": "sačuvan zapis"},
    )
    connection.commit()
```

Poziv `execute()` tipično pokrene SQLAlchemy transakcijski kontekst (`autobegin`) ako ga već nema. `commit()` završava trenutnu transakciju. Naredni SQL rad na istoj konekciji može započeti novu transakciju.

Ako izađeš iz `with engine.connect()` bloka sa aktivnom nepotvrđenom transakcijom, zatvaranje konekcije je neće automatski commit-ovati; SQLAlchemy je obično rollback-uje pri vraćanju konekcije u pool.

## Obrazac 2: `engine.begin()` kao jedna transakcija

Za jednu logičku celinu često je najjednostavnije koristiti transakcijski kontekst:

```python
with engine.begin() as connection:
    connection.execute(
        text("INSERT INTO note (text) VALUES (:text)"),
        {"text": "prvi deo posla"},
    )
    connection.execute(
        text("INSERT INTO note (text) VALUES (:text)"),
        {"text": "drugi deo posla"},
    )
```

Pravila izlaska iz bloka:

- normalan izlazak: kontekstni menadžer radi `COMMIT`;
- izuzetak koji izađe iz bloka: kontekstni menadžer radi `ROLLBACK`, pa prosleđuje izuzetak dalje;
- konekcija se zatim vraća u pool ili zatvara, prema podešavanjima pool-a.

Ovo je dobar obrazac kada sve izmene treba da uspeju ili da se ponište zajedno.

### Važna zamka: ne progutaj grešku unutar bloka

Ako grešku uhvatiš unutar `engine.begin()` bloka i ne proslediš je dalje, kontekstni menadžer može videti normalan izlazak i commit-ovati preostali posao:

```python
with engine.begin() as connection:
    try:
        connection.execute(statement_that_fails)
    except SomeDatabaseError:
        pass  # Kontekst ne zna da želimo rollback.
```

Ako želiš rollback, pusti izuzetak da izađe iz bloka ili eksplicitno upravljaj transakcijom. Za početnički kod najjednostavnije je da izuzetak ne potiskuješ unutar transakcijskog konteksta.

## Obrazac 3: `connection.begin()`

Možeš najpre uzeti konekciju, pa zatim jasno otvoriti transakcijski blok:

```python
with engine.connect() as connection:
    with connection.begin():
        connection.execute(
            text("INSERT INTO note (text) VALUES (:text)"),
            {"text": "jedan transakcioni blok"},
        )
```

Unutrašnji `begin()` započinje transakciju na već otvorenoj konekciji. Normalan izlazak potvrđuje transakciju; izuzetak koji izađe iz unutrašnjeg bloka je poništava. Spoljašnji `with engine.connect()` i dalje upravlja životnim vekom konekcije.

Pozovi `connection.begin()` pre prvog upita ako SQLAlchemy već nije započeo `autobegin`. Ako je prethodni `execute()` već započeo transakciju, ne možeš da započneš drugu običnu transakciju preko nje. Savepoint/`begin_nested()` postoji, ali je naprednija tema.

## Poređenje Core obrazaca

| Obrazac                                             | Konekcija                      | Kada se potvrđuje?                      | Kada se radi rollback?                                           |
| --------------------------------------------------- | ------------------------------ | --------------------------------------- | ---------------------------------------------------------------- |
| `with engine.connect()`                             | `Engine` je daje               | Kod poziva `connection.commit()`        | Kod poziva `rollback()` ili pri zatvaranju nepotvrđene konekcije |
| `with engine.begin()`                               | Blok je uzima                  | Normalnim izlaskom iz bloka             | Kada izuzetak izađe iz bloka                                     |
| `with engine.connect()` + `with connection.begin()` | Spoljašnji blok daje konekciju | Normalnim izlaskom iz unutrašnjeg bloka | Kada izuzetak izađe iz unutrašnjeg bloka                         |

`Engine`/`Connection` predstavljaju Core putanju. Kada se pređe na ORM, sesija će upravljati sličnim transakcijskim granicama.

## ORM `Session` transakcije

ORM `Session` prati ORM objekte i koristi engine/konekciju kada treba da izvrši SQL. Za jednu jedinicu rada možeš koristiti `sessionmaker.begin()`:

```python
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker(engine)

with SessionFactory.begin() as session:
    session.add(User(name="sandy"))
    # normalan izlazak: flush, commit i zatvaranje sesije
```

Ako iz bloka izađe greška, transakcija se poništava, a sesija se zatvara. Za čitanje bez upisa koristi se sesija kao kontekstni menadžer:

```python
with SessionFactory() as session:
    users = session.scalars(select(User)).all()
```

Zatvaranje same sesije nije zamena za commit. Ako je upis ostao nepotvrđen, ne računaj da će zatvaranje da ga sačuva.

## `flush()` nije `commit()`

ORM uvodi dodatni korak jer prati promene objekata. Kada dodaš objekat:

```python
session.add(user)
```

sesija ga registruje kao pending. SQL možda još nije poslat. `flush()` šalje potrebne `INSERT`/`UPDATE`/`DELETE` naredbe u trenutnoj transakciji:

```python
session.add(user)
session.flush()
```

Posle flush-a baza može da dodeli primarni ključ ili server default, ali promene i dalje nisu potvrđene. Zatim:

- `session.commit()` obično prvo flush-uje pa potvrđuje transakciju;
- `session.rollback()` poništava nepotvrđene promene;
- `with SessionFactory.begin()` upravlja flush/commit/rollback granicom za blok.

Flush je „pošalji SQL u ovu transakciju“. Commit je „potvrdi transakciju“.

## Greške i rollback sesije

Ako ručno pozoveš `session.commit()` ili `session.flush()` i oni padnu zbog constraint-a, uradi rollback pre nastavka korišćenja te sesije:

```python
try:
    session.commit()
except IntegrityError:
    session.rollback()
    raise
```

U transakcijskom kontekstnom menadžeru izuzetak obično treba da izađe iz bloka, pa kontekst uradi rollback. Ne nastavljaj rad sa sesijom posle neuspešnog flush-a kao da se ništa nije desilo.

## Čest pogrešan mentalni model

Pogrešno: „Čim pozovem `execute()` ili `session.add()`, podaci su trajno sačuvani.“

Preciznije:

- `execute()` šalje iskaz, ali ne mora sam da ga commit-uje;
- `session.add()` samo registruje ORM objekat u sesiji;
- `flush()` šalje ORM promene u trenutnu transakciju;
- `commit()` potvrđuje transakciju;
- `rollback()` odbacuje njene nepotvrđene promene. Pravilo za pamćenje: flush šalje izmene bazi, a commit ih potvrđuje kao završenu transakciju.
