# Pitanja i odgovori o asinhronim i sinhronim rutama u FastAPI-ju

## Pitanje 1

Kod mene su rute u projektu koji sada ponavljam i koji nije dovršen sve funkcije sa async def. U kursu se spominje da FastApi radi i sa def ali se koristi async. Da li onda treba da koristim AsyncSession?

---

## Odgovor 1

Ne moraš da koristiš `AsyncSession` samo zato što je ruta `async def`. Ali postoji važna razlika: **`async def` ne pretvara sinhroni rad sa bazom u asinhroni.**

U tvom projektu trenutno:

- `database.py` koristi sinhroni `create_engine()` i `sessionmaker`.
- `session.py` daje običan `Session`.
- `todos.py` koristi `async def`, ali poziva sinhroni DB upit. Dok se taj upit izvršava, može da blokira event loop.

To **ne znači da kod neće raditi**. Za učenje i malu lokalnu bazu verovatno nećeš primetiti problem, ali pri većem broju istovremenih zahteva može uticati na odziv.

### Dva ispravna pristupa

**1. Sinhrona sesija + `def` ruta — moja preporuka za sada**

```python
@router.get("/")
def read_all(db: db_dependency):
    stmt = select(Todos)
    return list(db.scalars(stmt).all())
```

FastAPI običnu `def` rutu izvršava u thread pool-u, tako da sinhroni DB poziv ne blokira direktno event loop. Ovo je najjednostavnije za tvoju trenutnu fazu i ne zahteva promenu konfiguracije baze.

**2. `AsyncSession` + `async def` ruta — kasnija tema**

```python
@router.get("/")
async def read_all(db: async_db_dependency):
    stmt = select(Todos)
    result = await db.scalars(stmt)
    return list(result.all())
```

Ovde `async_db_dependency` tek treba definisati. Nije dovoljno samo zameniti `Session` sa `AsyncSession`: potrebni su i asinhroni engine, odgovarajući drajver (za SQLite npr. `aiosqlite`), drugačiji dependency i prilagođavanje DB poziva. SQLite pristup preko `aiosqlite` koristi pozadinske niti, pa async sam po sebi ne garantuje bržu bazu.

---

### Šta bih uradio u tvom slučaju?

Dok ponavljaš kurs, **ostao bih na običnom `Session` i koristio `def` za rute koje direktno rade sinhrone DB upite**. SQLAlchemy 2.0 stil (`select`) možeš učiti nezavisno od async pristupa.

Još jedna važna stvar: i `get_current_user` je `async def` i u sebi poziva sinhroni DB upit. Zato promena samo ruta u `def` ne rešava automatski sve sinhrone DB pozive u projektu. Nisam menjao kod.

Dakle, dok ne pređeš na asinhroni pristup sa `AsyncSession`, najbolje je da koristiš sinhrone rute (`def`) za sve direktne DB upite i da budeš svestan da asinhroni deo (`async def`) može blokirati event loop ako poziva sinhrone DB operacije.

U suštini, **sinhrone rute sa sinhronim DB pristupom su jednostavnije i sigurnije za početak**, dok se asinhroni pristup uvodi tek kada je potrebno rukovati velikim brojem istovremenih zahteva ili kada se koristi DB drajver koji podržava async.

---

## Pitanje 2

Objasni mi `Annotated` i kako se koristi u FastAPI-ju. Takođe, objasni šta znače parametri kod `Generator[Session, None, None]` anotacije kod funkcije `def get_db()`.

---

## Odgovor 2

U ovoj liniji iz tvog `TodoApp/db/session.py` nalaze se dva povezana koncepta: **`Annotated`** i **generator koji vraća sesiju**. Oni zajedno omogućavaju FastAPI-ju da pravilno upravlja životnim ciklusom DB sesije i prosleđuje je endpoint-ima:

```python
def get_db() -> Generator[Session, None, None]:
```

Funkcija daje SQLAlchemy sesiju, a `Annotated` i `Depends` govore FastAPI-ju da tu **sesiju prosledi endpoint-u**. Krenimo od `Annotated`, a zatim ćemo detaljno rastaviti generator.

---

### 1. Šta je anotacija tipa?

Anotacija tipa je informacija o očekivanom tipu vrednosti. Na primer:

```python
def pozdravi(ime: str) -> str:
    return f"Zdravo, {ime}!"
```

- `ime: str` kaže da se za `ime` očekuje string.
- `-> str` kaže da funkcija vraća string.

Python uobičajeno **ne proverava automatski** da li je prosleđena vrednost zaista tog tipa samo zbog anotacije. Anotacije koriste alati poput Pylance-a, a određene biblioteke, uključujući FastAPI i Pydantic, čitaju ih i koriste za svoje potrebe, kao što su validacija i dokumentacija.

---

### 2. Šta je `Annotated`?

`Annotated` dolazi iz Python modula `typing` i omogućava da uz neki tip priložiš dodatne informacije — **metapodatke**:

```python
from typing import Annotated

Primer = Annotated[str, "dodatna informacija"]
```

Ovde je osnovni tip `str`, a tekst nakon njega je metapodatak. Sam `Annotated` ne određuje šta taj metapodatak radi. Značenje mu daje alat ili biblioteka koja ga čita. Možeš navesti i više metapodataka:

```python
Primer = Annotated[str, "prva informacija", "druga informacija"]
```

Zato tvrdnja „drugi parametar `Annotated` je dependency“ važi za **naš konkretni primer**, ali nije opšte pravilo. Drugi argument može biti i bilo koji drugi metapodatak koji neka biblioteka ili alat očekuje, a metapodataka može biti više.

---

### 3. Kako to izgleda u tvom projektu?

U `TodoApp/db/session.py` piše:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

db_dependency = Annotated[Session, Depends(get_db)]
```

Rastavimo ovaj izraz:

| Deo               | Značenje                                                        |
| ----------------- | --------------------------------------------------------------- |
| `Annotated`       | Omogućava da uz tip dodamo metapodatke.                         |
| `Session`         | Osnovni tip vrednosti koju endpoint očekuje: SQLAlchemy sesija. |
| `Depends(get_db)` | FastAPI metapodatak: koristi `get_db` kao dependency.           |
| `db_dependency`   | Ime pod kojim ponovo koristimo celu ovu anotaciju.              |

Tako endpoint može da napiše:

```python
def read_all(db: db_dependency):
    ...
```

Ovo čitaj: **„Parametar `db` je SQLAlchemy `Session`. FastAPI treba da dobije njegovu vrednost preko `get_db` dependency-ja.“**

`db_dependency` nije sama sesija i nije poziv funkcije. To je naziv anotacije. Stvarni objekat `Session` FastAPI prosleđuje u parametar `db` prilikom obrade zahteva.

---

### 4. Šta radi `Depends(get_db)`?

`Depends` je način da FastAPI-ju kažeš: „Za ovaj parametar potrebna mi je vrednost koju obezbeđuje ova dependency funkcija.“

```python
Depends(get_db)
```

Ovde prosleđuješ **funkciju** `get_db`, bez zagrada. FastAPI je poziva u odgovarajućem trenutku i upravlja njenim životnim ciklusom.

Nemoj mešati sa:

```python
Depends(get_db())  # pogrešno: ovde odmah pozivaš generatorsku funkciju
```

`get_db()` pravi generatorski objekat. To nije sama funkcija koju `Depends` treba da pozove kao dependency. Ona se koristi unutar FastAPI-ja da bi se upravljalo životnim ciklusom resursa koje generator obezbeđuje.

Kada ne koristiš skraćenicu, ista ideja može da se napiše direktno:

```python
def read_all(db: Annotated[Session, Depends(get_db)]):
    ...
```

Postoji i oblik bez `Annotated`:

```python
def read_all(db: Session = Depends(get_db)):
    ...
```

Oba oblika u FastAPI-ju služe za ubrizgavanje dependency-ja. U tvom projektu se koristi imenovana `Annotated` skraćenica, pa ne moraš da ponavljaš celu anotaciju u svakoj ruti.

FastAPI može koristiti `Annotated` i za druge metapodatke, ne samo `Depends`. Na primer, `Query(ge=1)` opisuje i validira query parametar:

```python
from typing import Annotated

from fastapi import Query


def primer(limit: Annotated[int, Query(ge=1)] = 10):
    return limit
```

Kada je ovo funkcija endpoint-a, `limit` je `int`, mora biti najmanje `1`, a podrazumevana vrednost je `10`. Ovde drugi argument **nije dependency**.

---

### 5. Šta je generator i čemu služi `yield`?

Obična funkcija sa `return` završava rad i vrati vrednost. Funkcija koja u svom telu sadrži `yield` je **generatorska funkcija**:

```python
def brojevi():
    yield 1
    yield 2
```

Poziv `brojevi()` ne izvršava odmah celo telo funkcije. On pravi **generator** — objekat koji može da nastavi izvršavanje i proizvodi vrednosti:

```python
generator = brojevi()

print(next(generator))  # 1
print(next(generator))  # 2
```

`next()` pokreće ili nastavlja izvršavanje do sledećeg `yield`. Generator se tada pauzira i pamti gde je stao. Kada nema više vrednosti, sledeći `next()` podiže `StopIteration`, što označava kraj iteracije.

U FastAPI DB dependency-ju obično se koristi **jedan yield**: pre njega pripremimo resurs, predamo ga endpoint-u, a posle njega ga oslobodimo sa `finally` blokom unutar generatorske funkcije.

---

### 6. Šta konkretno radi `get_db`?

Tvoj kod je:

```python
from collections.abc import Generator

from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Tok pojednostavljeno izgleda ovako:

1. FastAPI poziva `get_db()` i dobija generatorski objekat.
2. FastAPI pokreće generator: `SessionLocal()` pravi SQLAlchemy sesiju. To ne mora odmah otvoriti fizičku konekciju. Ona se obično pribavlja **lenjo**, tek kada nam je potrebna za rad sa bazom.
3. Na `yield db` generator se pauzira i FastAPI dobija vrednost `db` (jedna SQLAlchemy sesija).
4. FastAPI tu sesiju prosleđuje endpoint-u kao argument `db`.
5. Kada FastAPI završi upotrebu dependency-ja, upravlja nastavkom odnosno **završetkom** generatora. Izvršava se `finally` i poziva `db.close()`.

`finally` obezbeđuje cleanup i kada tokom obrade dođe do izuzetka.

`db.close()` zatvara sesiju i oslobađa njene resurse. Konekcija se obično vraća u pool (ako se koristi connection pool) i ne mora fizički da se zatvori.

NAPOMENA: `close()` nije `commit()` — ne potvrđuje promene u bazi. Ako želiš da sačuvaš promene, moraš eksplicitno pozvati `db.commit()` pre `db.close()`. Primer:

```python
db.add(novi_objekat)
db.commit()  # potvrđuje promene u bazi
db.close()   # oslobađa resurse
```

Zamisli ovaj obrazac kao: **pripremi → predaj na korišćenje → očisti**. Tačan trenutak cleanup-a u odnosu na slanje HTTP odgovora može zavisiti od FastAPI verzije i scope-a dependency-ja, pa nije dobro uvek ga opisivati kao „nakon što je odgovor poslat“.

---

### 7. Kako se čita `Generator[Session, None, None]`?

`Generator` se ovde uvozi iz `collections.abc`. Anotacija ima tri tipa:

```text
Generator[YieldType, SendType, ReturnType]
          └─ 1 ──┘ └─ 2 ─┘ └── 3 ───┘
```

Za našu funkciju:

```text
Generator[Session, None, None]
          └── 1 ─┘ └─ 2 ┘ └─ 3 ┘
```

| Mesto           | Tip       | Značenje u `get_db`                                                     |
| --------------- | --------- | ----------------------------------------------------------------------- |
| 1. `YieldType`  | `Session` | Generator preko `yield` daje SQLAlchemy sesiju.                         |
| 2. `SendType`   | `None`    | Generator ne očekuje korisnu vrednost poslatu nazad preko `.send(...)`. |
| 3. `ReturnType` | `None`    | Generator po završetku ne vraća posebnu vrednost pomoću `return`.       |

Prvi tip odnosi se na **vrednost iza `yield`**, ne na to da `get_db()` direktno vraća `Session`. Direktan poziv `get_db()` vraća generator a kada se generator pokrene, on daje sesiju pa odatle potiče `YieldType` -> `Session`.

Drugi i treći `None` **ne znače** da je sesija `None`, niti da `yield db` vraća tri vrednosti. To su tri informacije o različitim osobinama jednog generatora.

---

### 8. Šta znači drugi parametar: `.send()`?

Generator može, osim da daje vrednosti, da primi vrednost kada se nastavi metodom `.send(...)`. To nije nešto što moraš da koristiš u svakodnevnom FastAPI DB dependency-ju. Demonstracija na zasebnom, jednostavnom primeru:

```python
from collections.abc import Generator


def primer() -> Generator[str, int, None]:
    broj = yield "Pošalji broj"
    print(f"Dobijen broj: {broj}")


g = primer()
print(next(g))  # Pošalji broj

try:
    g.send(5)  # Ispisuje: Dobijen broj: 5
except StopIteration:
    pass  # Generator je završio.
```

Ovde `Generator[str, int, None]` kaže: generator daje `str`, očekuje `int` poslat preko `.send()` i po završetku nema posebnu povratnu vrednost. Generator prvo mora da se pokrene do `yield`, kao u primeru sa `next(g)`.

Naš `get_db` ne koristi `.send()` za primanje poslovne vrednosti, zato je drugi tip `None`. To je ugovor tipa, a ne dodatna automatska runtime provera.

---

### 9. Šta znači treći parametar: `return` generatora?

Generator može na kraju imati `return` sa vrednošću. Ta vrednost nije još jedna vrednost iz `yield`. Nalazi se u `StopIteration.value` kada generator završi.

```python
from collections.abc import Generator


def primer() -> Generator[int, None, str]:
    yield 1
    return "gotovo"


g = primer()
print(next(g))  # 1

try:
    next(g)
except StopIteration as kraj:
    print(kraj.value)  # gotovo
```

Kod našeg `get_db` nema `return` sa posebnom vrednošću, pa je treći tip `None`. Sesija se predaje preko `yield db`, a ne preko `return db`.

---

### 10. Kako se sve povezuje?

```text
get_db()                         generatorski objekat
    └── yield db                 daje Session
          └── Depends(get_db)    FastAPI dobija Session iz dependency-ja
                └── Annotated[Session, ...]
                      └── db: db_dependency u endpoint-u
```

Zatim FastAPI završava dependency, a `finally` poziva `db.close()`. Endpoint radi sa `db` kao sa sesijom, ne sa generatorom.

`Generator[Session, None, None]` opisuje **generatorsku funkciju**;
`Annotated[Session, Depends(get_db)]` opisuje **parametar endpoint-a** koji prima vrednost iz njenog `yield`-a.

Zato je u prvom slučaju osnovni tip generator, a u drugom `Session`.

Za jednostavan generator koji se koristi samo kao iterator može se sresti i anotacija `Iterator[Session]`. Ona opisuje da se iz generatora dobijaju sesije, ali ne izražava posebno tipove za `.send()` i završni `return`.
Tvoj postojeći `Generator[Session, None, None]` eksplicitno prikazuje sve tri informacije i ispravan je za ovaj obrazac.

---

### Ukratko

- `Annotated` povezuje osnovni tip sa metapodacima; metapodatak nije uvek dependency.
- `Depends(get_db)` kaže FastAPI-ju da koristi `get_db` za dobijanje sesije.
- `yield db` daje sesiju endpoint-u i omogućava da se kasnije izvrši cleanup u `finally`.
- U `Generator[Session, None, None]`, redom se opisuju **yield**, **send** i završni **return** tip.
- Alternativno možemo koristiti `Iterator[Session]` ako nas zanima samo tip vrednosti koje generator daje, bez eksplicitnog navođenja tipa za `.send()` i završni `return`.

---

## Pitanje 3

Šta je `thread pool` i zašto se koristi u kontekstu sinhronih funkcija u FastAPI-ju?

---

## Odgovor 3

### 1. Kratak odgovor

**Thread pool** je skup radnih niti koje aplikacija koristi za izvršavanje poslova. Umesto da za svaki posao stalno pravi novu nit, aplikacija može da dodeli posao jednoj od raspoloživih radnih niti i da je ponovo koristi za neki naredni posao.

FastAPI obične, sinhrone endpoint funkcije napisane sa `def` izvršava u thread pool-u. Tako se sinhroni poziv koji čeka bazu ili neki drugi I/O posao ne izvršava direktno na niti event loop-a i ne blokira je tokom tog čekanja.

Da bismo razumeli zašto je to važno, prvo razdvojimo nekoliko pojmova.

---

### 2. Proces, nit i zadatak

**Proces** je pokrenuti program sa sopstvenim resursima i memorijskim prostorom. Na primer, pokrenuti Python program radi u jednom procesu.

**Nit** (_thread_) je tok izvršavanja unutar procesa. Jedan proces može imati više niti. One dele memoriju tog procesa, ali svaka ima svoj tok izvršavanja.

**Zadatak** je posao koji treba obaviti. Na primer: obradi jedan HTTP zahtev ili izvrši funkciju koja čita podatke iz baze. Zadatak nije isto što i nit: više poslova može se tokom vremena izvršavati na istoj niti.

Pojednostavljena slika:

```text
Python proces
├── nit na kojoj radi event loop
└── radne niti thread pool-a
    ├── nit A: izvršava sinhronu funkciju
    ├── nit B: izvršava drugu sinhronu funkciju
    └── nit C: može preuzeti naredni posao
```

Ovo je mentalni model, ne obećanje o tačnom broju niti ili njihovom stvarnom rasporedu u svakoj aplikaciji.

---

### 3. Šta znači da je poziv blokirajući?

Poziv je **blokirajući** kada nit koja ga izvršava mora da sačeka da se poziv završi pre nego što nastavi dalje.

Kod sinhrone sesije:

```python
stmt = select(Todos)
todos = db.scalars(stmt).all()
```

Druga linija izvršava upit i čeka rezultat. Tokom čekanja ta nit ne može da nastavi narednu liniju te funkcije. To ne znači da je ceo računar zaustavljen: druge niti ili procesi mogu nastaviti sa svojim poslovima.

Primeri poslova koji često uključuju čekanje:

- čitanje ili upis podataka u bazu;
- pristup fajlu;
- čekanje odgovora udaljenog servera;
- pristup drugom spoljašnjem resursu.

Koliko će upit trajati zavisi od okolnosti; ne mora svaki upit trajati dugo.

Problem nastaje ako poziv koji čeka zauzme nit na kojoj je potrebno obrađivati i druge poslove.

---

### 4. Šta je event loop?

**Event loop** je mehanizam koji upravlja asinhronim zadacima. Kada asinhrona funkcija naiđe na `await` nad odgovarajućom asinhronom operacijom, može da prepusti kontrolu event loop-u dok čeka. Event loop tada može da napreduje sa drugim spremnim zadatkom.

Pojednostavljen primer:

```python
import asyncio


async def primer():
    print("Početak")
    await asyncio.sleep(1)
    print("Nastavak")
```

Za vreme `await asyncio.sleep(1)` event loop može da radi na drugim zadacima. `await` ne znači da funkcija završava; ona se nastavlja kada operacija bude spremna.

Važno: **`async def` samo po sebi ne čini sve pozive unutar funkcije asinhronim**. Ako u njoj direktno pozoveš blokirajuću sinhronu funkciju, ona se izvršava na niti koja trenutno pokreće tu asinhronu funkciju i može da blokira event loop.

---

### 5. Šta se dešava sa `async def` i sinhronim DB pozivom?

Pojednostavljen primer koji koristi običan SQLAlchemy `Session`:

```python
@router.get("/")
async def read_all(db: db_dependency):
    stmt = select(Todos)
    return list(db.scalars(stmt).all())
```

Ruta je `async def`, ali `db.scalars(stmt)` je ovde **sinhroni** DB poziv. Nema `await` koji bi ga pretvorio u neblokirajući poziv. Kada ruta direktno izvrši taj upit, event loop može biti blokiran dok on ne završi.

U [todos.py](../../../../fast-api-course-my-work/TodoApp/api/routes/todos.py) trenutne rute koriste `async def` sa sinhronom sesijom i legacy `db.query(...)` upitima. Isto pitanje blokiranja postoji i sa novijim `select()`/`scalars()` stilom ako se oni izvršavaju preko običnog sinhronog `Session` objekta. **SQLAlchemy 2.0 stil i async pristup nisu ista odluka.**

---

### 6. Šta FastAPI radi kada je ruta `def`?

Za sinhronu rutu FastAPI obično dodeljuje izvršavanje funkcije radnoj niti iz thread pool-a:

```python
@router.get("/")
def read_all(db: db_dependency):
    stmt = select(Todos)
    return list(db.scalars(stmt).all())
```

Pojednostavljeni tok je:

1. Stigne HTTP zahtev.
2. FastAPI razreši dependency-je potrebne endpoint-u.
3. Sinhroni endpoint `read_all` izvršava se u radnoj niti.
4. Ta radna nit čeka da sinhroni upit vrati rezultat.
5. Za to vreme event loop može da nastavi sa drugim spremnim poslovima.
6. Kada endpoint završi, FastAPI obrađuje njegov rezultat i priprema HTTP odgovor.

Radna nit je i dalje zauzeta dok čeka; čekanje nije nestalo. Posao je premešten sa niti event loop-a na radnu nit.

FastAPI takođe izvršava sinhrone dependency funkcije u odgovarajućem thread-pool kontekstu. Međutim, ako **sam pozoveš** običnu sinhronu pomoćnu funkciju direktno iz svoje `async def` funkcije, FastAPI ne može automatski premestiti taj unutrašnji poziv u thread pool. On se izvršava tamo gde si ga pozvao.

---

### 7. Poređenje tri pristupa

| Endpoint i DB pristup                        | Gde je čekanje?                                         | Zaključak                                                             |
| -------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- |
| `def` + sinhroni `Session`                   | Radna nit čeka sinhroni DB poziv.                       | Jednostavan obrazac za trenutni projekat.                             |
| `async def` + sinhroni `Session`             | Direktni DB poziv može blokirati event loop.            | Može raditi, ali `async` ne uklanja blokiranje.                       |
| `async def` + `AsyncSession` i async drajver | Kod koristi `await` za podržane asinhrone DB operacije. | Ne blokira event loop na isti način, ali zahteva async konfiguraciju. |

`AsyncSession` nije samo drugačija anotacija. Zahteva asinhroni engine, odgovarajući drajver i odgovarajući rad sa sesijom i `await`.

Na primer, SQLite sa `aiosqlite` koristi pozadinske niti za DB operacije; async sam po sebi ne garantuje da će jedan SQLite upit biti brži.

---

### 8. Kako se to povezuje sa tvojim `get_db`?

U [session.py](../../../../fast-api-course-my-work/TodoApp/db/session.py)
imaš:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`get_db` je sinhroni generatorski dependency: pravi sesiju, daje je endpoint-u i zatim je zatvara. Thread pool ne menja značenje `yield`, `Generator` ni `Session`; on se odnosi na to **gde se sinhroni posao izvršava**, dok dependency upravlja time **kako se sesija obezbeđuje i oslobađa**.

Sesiju treba koristiti za jedan tok rada, a ne deliti je istovremeno između više niti ili konkurentnih zadataka. `Session` je stanje koje se menja tokom rada i nije bezbedan za takvo istovremeno deljenje.

U [database.py](../../../../fast-api-course-my-work/TodoApp/db/database.py) već postoji SQLite postavka:

```python
connect_args={"check_same_thread": False}
```

Ona isključuje proveru SQLite drajvera koja inače zabranjuje upotrebu iste konekcije iz druge niti. **Ne čini sesiju ili konekciju automatski bezbednom za istovremenu upotrebu** i ne znači da više zahteva treba da deli jednu globalnu sesiju. Konekciju i dalje treba koristiti pravilno, a SQLite ima i svoja ograničenja pri konkurentnim upisima.

---

### 9. Thread pool nije isto što i connection pool

Nazivi liče, ali čuvaju različite resurse:

| Pool                | Šta organizuje?                                     | Primer                                       |
| ------------------- | --------------------------------------------------- | -------------------------------------------- |
| **Thread pool**     | Radne niti za izvršavanje sinhronih funkcija.       | Nit izvršava `def` endpoint.                 |
| **Connection pool** | Konekcije prema bazi koje se mogu ponovo koristiti. | SQLAlchemy sesija pribavi konekciju za upit. |

Jedan zahtev može koristiti radnu nit da izvrši funkciju, a zatim kroz sesiju pribaviti konekciju iz DB connection pool-a. Sesija i konekcija su resursi koji se pravilno upravljaju unutar thread pool-a, ali njihovo oslobađanje ne utiče na same radne niti. Zatvaranje sesije oslobađa njene DB resurse; to nije isto što i uništavanje radne niti.

---

### 10. Konkurentnost, paralelizam i GIL

- **Konkurentnost** znači da više poslova može napredovati tokom preklapajućeg perioda, na primer dok jedan čeka bazu, drugi obrađuje svoj zahtev.
- **Paralelizam** znači da se poslovi zaista izvršavaju istovremeno na različitim procesorskim jezgrima.

Thread pool je posebno koristan za blokirajući I/O: dok jedna nit čeka rezultat, druge mogu napredovati. To ne znači da će se svaki posao ubrzati.

U uobičajenoj CPython konfiguraciji **GIL** ograničava istovremeno izvršavanje Python bytecode-a na više niti, pa thread pool nije univerzalno rešenje za CPU-intenzivne Python proračune. Postoje izuzeci, kao što su neke native biblioteke koje oslobađaju GIL i free-threaded konfiguracije CPython-a.

Za duge CPU-intenzivne poslove često se razmatraju zasebni procesi ili posebni radnici, zavisno od aplikacije. To je druga tema od DB I/O-a.

---

### 11. Ograničenja i česte zabune

- Broj istovremenih radnih niti je ograničen. Ako su sve zauzete, dodatni poslovi mogu čekati; ne očekuj beskonačnu konkurentnost.
- Više niti ne znači automatski više DB konekcija ili bržu bazu. Ograničenja connection pool-a, baze i SQLite zaključavanja i dalje važe.
- Thread pool ne zamenjuje `db.close()`, `commit()` ni upravljanje transakcijama.
- `async def` ne prebacuje automatski svaki sinhroni poziv u thread pool.
- `check_same_thread=False` ne dozvoljava bezbedno istovremeno deljenje jedne `Session` između zahteva.
- Prekid čekanja na rezultat ne znači nužno da je sinhroni posao koji se već izvršava u drugoj niti trenutno zaustavljen.

U tvom projektu i `get_current_user` je `async def` sa sinhronim DB upitom. Ako kasnije menjaš rute u `def`, treba odvojeno razmotriti i taj dependency: promena samo endpoint-a ne uklanja blokiranje unutar drugih `async def` funkcija.

---

### Ukratko

Thread pool omogućava FastAPI-ju da sinhrone `def` funkcije izvršava u radnim nitima umesto direktno na event loop-u. To je korisno kada sinhroni SQLAlchemy poziv čeka bazu. Za tvoju trenutnu fazu učenja `def` ruta uz običan `Session` je jednostavan izbor; `AsyncSession` je zaseban pristup koji možeš učiti kasnije, kada budeš želeo da koristiš potpuno asinhrone DB operacije.

---

## Pitanje 4

Da li da u `session.py` u `finally bloku` koristim `add()` i `commit()` ili `close()` koja je razlika?

---

## Odgovor 4

### 1. Kratak odgovor

U tvom trenutnom `PortfolioItemsAPI/db/session.py` ostavi **db.close() u finally bloku**. To je mesto za oslobađanje sesije, bez obzira na to da li je obrada zahteva uspela ili je došlo do greške.

`add()`, `commit()` i `close()` ne rade isto:

| Metoda            | Svrha                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------- |
| `db.add(objekat)` | Dodaje objekat u sesiju da bi se njime upravljalo i da bi novi objekat mogao biti upisan. |
| `db.flush()`      | Šalje potrebne SQL izmene bazi unutar trenutne transakcije, ali ih još ne potvrđuje.      |
| `db.commit()`     | Potvrđuje transakciju; pre potvrde obavlja i potreban `flush`.                            |
| `db.rollback()`   | Poništava nepotvrđenu transakciju i vraća sesiju u stanje pogodno za dalji rad.           |
| `db.close()`      | Završava rad sa sesijom i oslobađa njene resurse; ne potvrđuje izmene.                    |

`add()` i `commit()` koristiš kada poslovna operacija zaista želi da upiše podatke u bazu. `close()` koristiš kada završavaš rad sa sesijom.

---

### 2. Šta sada radi tvoj `get_db`?

U `PortfolioItemsAPI/db/session.py` imaš:

```python
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Ovaj dependency ima jednu jasnu odgovornost: **obezbedi sesiju za obradu HTTP zahteva i zatvori je kada se završi njena upotreba**.

1. `SessionLocal()` pravi SQLAlchemy sesiju.
2. `yield db` predaje sesiju endpoint-u.
3. Endpoint po potrebi čita ili menja podatke.
4. `finally` poziva `db.close()`, uključujući i situacije u kojima nastane greška tokom obrade.

`finally` je pogodan za cleanup upravo zato što se izvršava i u slučaju greške. Zbog istog razloga **nije dobro mesto za bezuslovni `commit()`**: mogao bi pokušati da potvrdi izmene i kada operacija nije uspešno završena.

Tačan trenutak `cleanup`-a u odnosu na slanje `HTTP odgovora` zavisi od `FastAPI verzije` i `scope-a dependency-ja`, pa ga ne treba opisivati kao nešto što se uvek dešava posle poslatog odgovora.

---

### 3. Šta radi `db.add()`?

Na primer, napraviš Python objekat korisnika:

```python
user = Users(name="Ana", email="ana@example.test")
```

Ovo još ne šalje `INSERT` bazi. Sledeći korak je:

```python
db.add(user)
```

Sesija sada prati novi objekat i planira njegovo upisivanje. Sam `add()` **ne garantuje da je red već upisan u bazu** i ne potvrđuje transakciju.

`INSERT` se obično šalje tokom `flush()`-a, koji može biti eksplicitan ili se desiti kao deo `commit()`-a.

`add()` prima konkretan objekat koji želiš da sačuvaš. `get_db` ne zna da li se obrađuje korisnik, kategorija ili stavka, niti da li je zahtev uopšte upis. Zato `db.add(...)` pripada kodu koji pravi konkretnu promenu, a ne opštem `finally` bloku.

Za već učitan ORM objekat koji je vezan za istu sesiju, promena atributa se obično prati automatski i nije potreban novi `add()`:

```python
user.name = "Novo ime"
db.commit()
```

Ovde se pretpostavlja da je `user` prethodno učitan pomoću iste sesije.

---

### 4. Šta rade `flush()` i `commit()`?

Razmotrimo redosled:

```python
user = Users(name="Ana", email="ana@example.test")
db.add(user)
db.flush()
db.commit()
```

- Nakon `add()`, novi objekat je u sesiji i čeka upis.
- `flush()` šalje potreban `INSERT` bazi **unutar otvorene transakcije**. Na primer, tada može postati dostupan automatski generisani `user.id`.
- I posle uspešnog `flush()`-a transakcija još nije potvrđena. Ako se pre potvrde pozove `rollback()`, te nepotvrđene izmene se poništavaju.
- `commit()` najpre obavlja potreban `flush`, a zatim potvrđuje transakciju.

Zato ne moraš da pišeš eksplicitni `flush()` pre svakog `commit()`-a:

```python
db.add(user)
db.commit()  # uključuje potreban flush pre potvrde
```

U tvom `database.py` je `autoflush=False`. To znači da je automatski flush pre određenih upita isključen; **ne isključuje flush koji `commit()` mora da izvrši**. Ako ti ID ili provera ograničenja zatreba pre `commit()`-a, možeš namerno pozvati `db.flush()`.

Uspešan `commit()` potvrđuje transakciju u bazi, dok `flush()` sam po sebi to ne radi. Vidljivost nepotvrđenih promena drugim konekcijama zavisi od baze i izolacije transakcije; ne treba se oslanjati na to da će ih drugi odmah videti.

---

### 5. Šta radi `rollback()`?

`rollback()` poništava **trenutnu nepotvrđenu transakciju**:

```python
db.add(user)
db.flush()
db.rollback()
```

Čak i ako je `flush()` već poslao `INSERT`, `rollback()` može da poništi taj upis jer transakcija još nije potvrđena. Ali `rollback()` ne može da poništi prethodni uspešni `commit()` kao da se nije desio. Za poništavanje već potvrđene promene bila bi potrebna nova odgovarajuća promena.

Ako `flush()` ili `commit()` ne uspe, na primer zbog `UNIQUE` ograničenja, SQLAlchemy sesiju je potrebno vratiti u ispravno stanje pomoću `rollback()` pre ponovne upotrebe. Grešku ne treba prećutati: možeš je propustiti dalje ili je smisleno obraditi.

---

### 6. Šta radi `close()`?

```python
db.close()
```

`close()` završava rad sa sesijom: oslobađa njene resurse, odvaja ORM objekte od sesije i oslobađa korišćene DB konekcije. Ako je transakcija ostala otvorena, njene nepotvrđene izmene se poništavaju. Konekcija se, kada postoji pool, obično vraća u pool; to nije nužno fizičko zatvaranje konekcije.

**`close()` ne poziva `commit()` umesto tebe.** Ako si dodao objekat, a nisi potvrdio transakciju, ne treba očekivati da će `close()` sačuvati taj objekat.

Oslobađanje resursa i potvrda podataka su različite odgovornosti:

```text
commit()  → potvrdi transakciju
rollback() → poništi nepotvrđenu transakciju
close()   → oslobodi sesiju i njene resurse
```

---

### 7. Kako bi izgledao budući upis korisnika?

Ovo je **edukativni isečak**, ne već implementirana ruta. Pretpostavimo da `db` dolazi iz `get_db`, a `Users` je tvoj ORM model:

```python
from sqlalchemy.exc import SQLAlchemyError

user = Users(name="Ana", email="ana@example.test")

try:
    db.add(user)
    db.commit()
except SQLAlchemyError:
    db.rollback()
    raise

db.refresh(user)
```

- `add()` označava novi objekat za upis.

- `commit()` potvrđuje uspešnu operaciju.

- Ako SQLAlchemy prijavi grešku tokom upisa, `rollback()` čisti neuspelu transakciju, a `raise` prosleđuje grešku dalje umesto da se predstavi uspeh.

- `refresh(user)` ponovo učitava vrednosti iz baze kada su potrebne, na primer generisani ID. Greška pri `refresh()` nakon uspešnog `commit()`-a ne poništava već potvrđen upis.

- `get_db` na kraju zatvara sesiju pomoću `close()`. Ovaj isečak ne treba dodatno da zatvara sesiju koju je dobio od dependency-ja.

Ako kreiraš API endpoint, treba smisleno odlučiti kako se poznate greške predstavljaju klijentu. Na primer, duplikat email-a je drugačiji od neočekivane greške baze. Detaljna obrada grešaka je zaseban korak.

---

### 8. Da li se `commit()` ikada može centralizovati?

Postoje dizajni u kojima sloj koji upravlja transakcijom potvrđuje transakciju **samo nakon uspešnog rada**, a na grešku radi `rollback`. To je drugačije od bezuslovnog `commit()`-a u `finally`.

Takav pristup zahteva pažljivu odluku o životnom ciklusu FastAPI dependency-ja, trenutku potvrde i načinu prijavljivanja greške. Ne treba ga dodavati samo zato što koristiš `yield`. Za tvoju trenutnu fazu najjasnije je da operacija koja menja podatke eksplicitno odluči kada radi `commit()`, a `get_db` se pobrine za `close()`.

---

### Ukratko

- **Ostavi `db.close()` u `finally` bloku.**
- `add()` dodaje konkretan objekat u sesiju; samo po sebi ne potvrđuje upis.
- `flush()` šalje promene bazi, ali ih ne potvrđuje.
- `commit()` potvrđuje transakciju i prethodno radi potreban `flush`.
- `rollback()` poništava nepotvrđene promene; `close()` oslobađa sesiju.
- Nemoj stavljati bezuslovni `commit()` u `finally`, jer se `finally` izvršava i pri grešci.

---

## Pitanje 5

Zar se `.db` fajl neće kreirati u root-u repozitorijuma ako pokrenem `sqlite3` iz root-a? Zar ne treba da ga pokrenem iz `fast-api-course-my-work`? Kako se putanja određuje kada bazu koristim preko Uvicorn-a i FastAPI-ja?

---

## Odgovor 5

Ne moraš da pokreneš `sqlite3` iz istog direktorijuma kao aplikaciju. Važno je **koju putanju navodiš i iz kog je trenutnog direktorijuma računaš**.

### 1. `sqlite3` iz root-a repozitorijuma

Ako si u root-u repozitorijuma, komanda iz vežbi je:

```bash
mkdir -p fast-api-course-my-work/PortfolioItemsAPI/data
sqlite3 fast-api-course-my-work/PortfolioItemsAPI/data/portfolioitemsapp.db
```

Iako komandu pokrećeš iz root-a, SQLite dobija **putanju do fajla**, ne samo njegovo ime. Zato cilja:

```text
root-repozitorijuma/
└── fast-api-course-my-work/
    └── PortfolioItemsAPI/
        └── data/
            └── portfolioitemsapp.db
```

Ako baza postoji, otvara se postojeća baza. Ako ne postoji i putanja je ispravna, SQLite je može kreirati.

`mkdir -p` osigurava da direktorijum `data/` postoji. SQLite ne pravi nedostajuće roditeljske direktorijume.

Samo kada bi iz root-a naveo **isključivo ime fajla**, baza bi bila u root-u:

```bash
sqlite3 portfolioitemsapp.db
```

Ta komanda cilja drugi fajl, a ne bazu u `PortfolioItemsAPI/data/`.

---

### 2. `sqlite3` iz `fast-api-course-my-work`

Ako se prvo premestiš u `fast-api-course-my-work`, relativna putanja je kraća:

```bash
cd fast-api-course-my-work
sqlite3 PortfolioItemsAPI/data/portfolioitemsapp.db
```

Ova komanda cilja **isti fajl** kao prethodni primer, pod uslovom da je prva komanda pokrenuta iz root-a repozitorijuma, a druga iz `fast-api-course-my-work`.

Možeš proveriti gde se nalaziš pomoću `pwd`, a nakon ulaska u SQLite shell i koja je baza otvorena:

```sql
.databases
```

Ako putanja nije ona koju očekuješ, nemoj nastavljati sa izmenama. Pogrešna putanja može dovesti do otvaranja ili kreiranja **druge, prazne baze**.

---

### 3. Kako putanju određuje FastAPI aplikacija?

U `PortfolioItemsAPI/db/database.py` trenutno stoji:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./PortfolioItemsAPI/data/portfolioitemsapp.db"
```

Deo `sqlite:///` označava SQLAlchemy SQLite URL, a deo posle njega:

```text
./PortfolioItemsAPI/data/portfolioitemsapp.db
```

Predstavlja relativnu putanju. `.` označava **trenutni radni direktorijum procesa**, a ne automatski direktorijum u kome se nalazi `database.py`.

Zato pri trenutnoj konfiguraciji Uvicorn treba pokrenuti iz `fast-api-course-my-work` da bi URL pokazao na željeni fajl:

```bash
# Iz root-a repozitorijuma:
cd fast-api-course-my-work
../.venv/bin/uvicorn PortfolioItemsAPI.main:app --reload
```

Tada i aplikacija i prethodne `sqlite3` komande ciljaju **isti fajl**: `fast-api-course-my-work/PortfolioItemsAPI/data/portfolioitemsapp.db`. Direktorijum `data/` mora prethodno postojati.

Ako aplikaciju pokreneš iz drugog radnog direktorijuma, isti relativni URL pokazuje na drugu lokaciju. Ako tamo roditeljski direktorijum ne postoji, povezivanje može da prijavi grešku; ako postoji, može se otvoriti ili kreirati druga baza.

---

### 4. Ko zapravo kreira bazu i tabele?

- Komanda `sqlite3` otvara SQLite bazu na zadatoj putanji i može napraviti novi fajl ako ne postoji. Sama činjenica da postoji fajl ne znači da već ima tabele; njih praviš SQL komandama ili drugim alatom.

- Uvicorn pokreće i uvozi FastAPI aplikaciju. U ovom projektu `main.py` pri uvozu poziva `Base.metadata.create_all(bind=engine)`. Taj poziv traži konekciju preko SQLAlchemy engine-a, pa SQLite može kreirati nedostajući fajl, a SQLAlchemy kreira registrovane **nedostajuće tabele**.

- Sam `create_engine()` postavlja engine, ali obično ne otvara konekciju odmah. `create_all()` ne menja postojeće tabele da bi ih uskladio sa izmenjenim modelima. Za to su kasnije potrebne migracije.

U oba slučaja radiš nad fajlom koji je određen putanjom, ne nad posebnom „FastAPI bazom“ i posebnom „sqlite3 bazom“. Ako putanje vode do istog fajla, podaci su isti.

---

### Ukratko

- Relativna putanja računa se od **trenutnog radnog direktorijuma**.
- Iz root-a koristi `fast-api-course-my-work/PortfolioItemsAPI/data/...`.
- Iz `fast-api-course-my-work` koristi `PortfolioItemsAPI/data/...`.
- SQLAlchemy URL u ovom projektu podrazumeva pokretanje aplikacije iz `fast-api-course-my-work`.
