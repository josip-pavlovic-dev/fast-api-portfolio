# Stage 2 - API Request Methods

## Lekcija 01 - GET all todos from database

## 0) Gde se nalazimo u progresiji

Posle podešavanja baze, modela i upoznavanja SQLite-a, sledeći korak je čitanje zapisa kroz API. U ovoj lekciji pravimo osnovni `GET` za sve zadatke, objašnjavamo DB sesiju po zahtevu i zatim prikazujemo kako se upit ograničava na prijavljenog korisnika, tako da svaki korisnik vidi samo svoje zadatke.

Primeri su napisani u **SQLAlchemy 2.0 stilu**: `select()` i `Session.scalars()` zamenjuju stariji `Session.query()` obrazac. Stari obrazac i dalje postoji u SQLAlchemy 2.x kao legacy API i nije neispravan samo zato što koristi 2.x.
Transkript kursa i postojeći kod projekta mogu koristiti stariji stil SQLAlchemy-ja. Izmena ove lekcije ne menja automatski njegovu implementaciju.

---

## 1) Cilj lekcije

Povezujemo tri stvari:

1. `get_db()` pravi sesiju i obezbeđuje njeno zatvaranje.
2. FastAPI `Depends` prosleđuje tu sesiju endpoint-u.
3. `select(Todos)` formira upit, a `db.scalars(stmt).all()` vraća listu ORM objekata.

U ovoj lekciji koristimo **sinhroni** SQLAlchemy `Session`, pa su primeri endpoint-a obične `def` funkcije ali se i dalje oslanjaju na FastAPI dependency sistem za upravljanje sesijom.

---

## 2) Šta pokriva lekcija iz kursa

- `create_all()` kreira nedostajuće tabele, ne migrira postojeće.
- `get_db()` i `yield` omogućavaju rad sa sesijom i njeno zatvaranje.
- `Depends` i `Annotated` povezuju sesiju sa endpoint-om.
- `read_all` vraća zadatke iz baze.
- Skraćenica `db_dependency` smanjuje ponavljanje tipa i dependency-ja.

Kursni upit je ovde prikazan novijim stilom, ali cilj lekcije ostaje isti.

---

## 3) `get_db`: sesija i `yield`

U postojećem TodoApp-u `SessionLocal` je `sessionmaker` definisan u `TodoApp/db/database.py`, a `get_db` i `db_dependency` nalaze se u `TodoApp/db/session.py`. Pojednostavljeno:

```python
from collections.abc import Generator

# Može i from collections.abc import Iterator
# U tom slučaju bi definicija bila:
# def get_db() -> Iterator[Session]:

from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

1. `SessionLocal()` pravi novu SQLAlchemy sesiju, **ne nužno i odmah fizičku konekciju**: ona se obično preuzima iz pool-a kada zatreba.
2. `yield db` predaje sesiju FastAPI-ju za korišćenje u endpoint-u.
3. Kod u `finally` zatvara sesiju i ako obrada uspe i ako se desi izuzetak. Konekcija se oslobađa i, ako se koristi pool, obično vraća u pool; to ne mora značiti da je fizička konekcija odmah zatvorena.
4. `close()` ne radi `commit()`. Za upis je potrebna posebna kontrola transakcije; ova lekcija čita podatke i ne poziva `commit`.

FastAPI izvršava završni deo dependency-ja u skladu sa njegovim životnim ciklusom. Tačan trenutak u odnosu na slanje odgovora može zavisiti od verzije FastAPI-ja i podešavanja scope-a. Nemoj računati da se `finally` uvek izvršava tek nakon slanja odgovora.

Jedna sesija nije zamišljena kao globalni objekat koji istovremeno dele konkurentni zahtevi. `yield` pomaže da svaki zahtev dobije odgovarajuću sesiju i da se resurs oslobodi nakon upotrebe.

Pravilo je da svaka HTTP zahtev dobija svoju instancu sesije, koja se zatim oslobađa nakon upotrebe, čime se izbegava deljenje sesije između konkurentnih zahteva. Jedinstvena sesija po zahtevu omogućava sigurnu i izolovanu obradu podataka.

---

## 4) `Annotated` i `Depends`

U istom `db/session.py` može se definisati skraćenica:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

db_dependency = Annotated[Session, Depends(get_db)]
```

Čitaj je ovako: „parametar je `Session`, a FastAPI ga dobija pozivom `get_db`“. Kada je modul sa endpoint-om na drugom mestu, uvezi tu skraćenicu iz odgovarajućeg paketa:

```python
def read_all(db: db_dependency):
    ...
```

`Depends` sam ne poziva bazu u trenutku definisanja funkcije. FastAPI razrešava dependency kada obrađuje zahtev.

---

## 5) SQLAlchemy 2.0: `select` i `scalars`

```python
from sqlalchemy import select
# Pretpostavlja se da postoji aktivna SQLAlchemy sesija `db` i model `Todos` definisan negde ranije.
stmt = select(Todos)
todos = db.scalars(stmt).all()
```

- `select(Todos)` pravi SQL izraz za izbor redova mapiranih na model `Todos`. Samo pravljenje izraza **ne izvršava** upit.
- `scalars()` je funkcija koja iz rezultata upita (kreiranog SQLAlchemy `select` izrazom) izdvaja samo prve kolone svakog reda, što je korisno kada se očekuje jedan ORM objekat po redu ili jedna kolona. Naprimer, ako se selektuje cela tabela `Todos`, prvi element svakog reda je ceo ORM objekat `Todos`. Isto važi i za pojedinačne kolone. Ako se selektuje više kolona, `scalars()` će izdvojiti samo prvu kolonu svakog reda. Primeri kroz kod:

```python
stmt = select(Todos)
todos = db.scalars(stmt).all()
# `todos` sada sadrži listu svih `Todos` objekata iz baze.
# Ako tabela `Todos` nema redova, `todos` će biti prazna lista `[]`.
```

Primer sa `select` izrazom koji vraća sve redove iz tabele `Todos` i koristi `scalars()` za izdvajanje ORM objekata.

Primer za pojedinačne kolone:

```python
stmt = select(Todos.title)
titles = db.scalars(stmt).all() # nemamo execute, direktno koristimo scalars() na sesiji
# `titles` sada sadrži listu svih naslova iz tabele `Todos`.
# Ako tabela `Todos` nema redova, `titles` će biti prazna lista `[]`.
```

Primer sa pojedinačnom kolonom pokazuje kako `scalars()` izdvaja samo prvu kolonu svakog reda.

- Direktno korišćenje `db.scalars(stmt).all()` je zgodno kada očekuješ listu rezultata i ne treba ti dodatna obrada rezultata pre nego što ih dobiješ. Kada se koristi `db.execute(stmt)` možeš dodatno manipulisati rezultatima pre nego što ih konvertuješ u listu, na primer filtrirati, mapirati ili kombinovati sa drugim upitima.

- `db.scalars(stmt)` izvršava izraz preko sesije i daje `ScalarResult`. Za ovaj upit pojedinačne vrednosti su `Todos` ORM objekti.
- `.all()` preuzima rezultate kao listu. Ako nema redova, rezultat je prazna lista `[]`, ne `None`.

Alternativni zapis koji daje istu listu za ovaj upit je:

```python
stmt = select(Todos)
todos = db.execute(stmt).scalars().all()
```

`execute()` prvo vraća rezultat sastavljen od redova; `.scalars()` izdvaja prvi element svakog reda. Kod `select(Todos)` taj prvi element je ORM objekat `Todos`.

Ako odabereš više kolona i trebaju ti sve, koristi `db.execute(stmt).all()` umesto `.scalars()`, jer `.scalars()` uzima samo prvu izabranu vrednost po redu.

SQL ekvivalent osnovne ideje je:

```sql
SELECT * FROM todos;
```

Redosled bez `ORDER BY` nije garantovan. SQL baza može da vrati redove u proizvoljnom redosledu. Za stabilan i predvidljiv redosled po ID-u, uvek koristi `order_by(Todos.id)` u svom `select` izrazu:

```python
stmt = select(Todos).order_by(Todos.id)
todos = db.scalars(stmt).all()
```

---

## 6) Osnovni endpoint: svi zadaci

Sledeći primer je **edukativni router** koji se može napisati unutar `TodoApp/api/routes/`. Relativni importi polaze od te lokacije. Koristi postojeći `db_dependency` i model `Todos`, ali definiše zasebnu response šemu za potrebe primera:

```python
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from ...db.session import db_dependency
from ...models import Todos

router = APIRouter(prefix="/todos", tags=["todos"])


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    description: str | None
    priority: int | None
    complete: bool | None
    owner_id: int | None


@router.get("/", response_model=list[TodoRead])
def read_all(db: db_dependency) -> list[Todos]:
    stmt = select(Todos).order_by(Todos.id)
    return list(db.scalars(stmt).all())
```

`response_model=list[TodoRead]` koristi **Pydantic šemu**, ne ORM klasu `Todos`. Sa `from_attributes=True` Pydantic može da čita vrednosti iz ORM objekata. Polja u primeru dozvoljavaju `None` tamo gde ih trenutni TodoApp ORM model dopušta kao `NULL`.

Primer namerno vraća sve zadatke i **nema autentikaciju**. Pogodan je za učenje nad lokalnom bazom, ali u aplikaciji sa privatnim podacima nije prikladan za javno izlaganje. Sam kod ne dodaje rutu u aplikaciju: router treba uključiti sa `app.include_router(router)`, uz izbegavanje dupliranja postojeće rute.

Postojeći `TodoResponse` u TodoApp-u, za razliku od ove edukativne šeme, zahteva nenulte `title`, `description`, `priority` i `complete`, i ne izlaže `owner_id`. Ako baza sadrži `NULL` u tim kolonama, njegova validacija odgovora može da ne uspe. Pravila šeme i baze treba uskladiti pre upotrebe te šeme. Ne pretpostavljaj da svaki postojeći red zadovoljava API šemu.

---

## 7) Filtriranje po prijavljenom korisniku

Kasnije, kada postoji pouzdana autentikacija, dodaje se `WHERE` uslov:

```python
stmt = (
    select(Todos)
    .where(Todos.owner_id == current_user.id)
    .order_by(Todos.id)
)
todos = db.scalars(stmt).all()
```

`current_user` ovde mora biti korisnik koji je već **proveren kroz autentikaciju**, a ne korisnički ID koji klijent slobodno navodi.

Na primer, postojeći TodoApp ima `get_current_user` dependency; njegova GET ruta u trenutnom kodu koristi legacy upit. Gornji izraz prikazuje kako se isti ownership filter piše u SQLAlchemy 2.0 stilu, bez tvrdnje da je ruta već prepravljena.

Ako korisnik nema zadataka, rezultat je `[]`. Filter obezbeđuje da se preuzimaju samo redovi tog vlasnika, ali ne zamenjuje autentikaciju ili druga pravila autorizacije.

SQL ideja:

```sql
SELECT *
FROM todos
WHERE owner_id = :user_id
ORDER BY id;
```

SQLAlchemy obrađuje vrednost ID-a kao vezani parametar; **uvek koristi vezane parametre** i nemoj praviti SQL konkatenacijom korisničkog unosa. Parametrizacija sprečava da se vrednost tumači kao deo SQL sintakse i pomaže zaštiti od SQL injection-a.

---

## 8) `create_all()` nije migracija

```python
Base.metadata.create_all(bind=engine)
```

Na osnovu registrovanih modela kreira tabele koje nedostaju. Ne dodaje automatski novu kolonu postojećoj tabeli i ne usklađuje postojeće constraint-e sa izmenjenim modelom. Za kontrolisane promene postojeće šeme
koriste se migracije, npr. Alembic.

U trenutnom TodoApp `main.py` poziv se izvršava pri import-u. Zato pre pokretanja obrati pažnju na radni direktorijum i relativni SQLite URL: aplikacija može kreirati bazu ili nedostajuće tabele. Nemoj je pokretati samo da bi proverio tekst lekcije.

---

## 9) Sinhroni i asinhroni rad

`Session` u primerima je sinhron: poziv baze blokira nit u kojoj se izvršava. Zato za sinhronu DB logiku u FastAPI-ju koristimo `def` endpoint. FastAPI ga izvršava u thread pool-u.

Ako bi sinhroni poziv baze bio direktno unutar `async def`, mogao bi da blokira event loop. Pravi asinhroni rad zahteva odgovarajući async drajver, `AsyncSession` i `await`; samo pisanje `async def` ne pretvara sinhroni `Session` u asinhroni. To je posebna tema, ne moraš je uvoditi u ovoj lekciji.

---

## 10) Tok jednog GET zahteva

1. HTTP zahtev stiže na rutu.
2. FastAPI razrešava dependency-je i dobija sesiju iz `get_db`.
3. Endpoint formira `select(Todos)` izraz i izvršava ga sa `db.scalars`.
4. Baza vraća rezultate; SQLAlchemy ih mapira na ORM objekte.
5. FastAPI/Pydantic priprema odgovor koristeći response šemu.
6. FastAPI zatvara dependency u odgovarajućoj fazi njegovog životnog ciklusa; `finally` poziva `db.close()`.

Za velike tabele `.all()` učitava sve rezultate; kasnije treba razmotriti paginaciju. Za trenutnu lokalnu vežbu cilj je razumeti osnovni tok.

---

## 11) Praktične mini vežbe

1. U osnovnom endpoint-u iz odeljka 6 pronađi deo koji **pravi upit** i deo koji ga **izvršava**. Zameni `order_by(Todos.id)` sa `order_by(Todos.id.desc())` i objasni razliku u redosledu.
2. Sa podacima u lokalnoj bazi proveri da ruta vraća listu. Kada tabela nema redova, očekuj `[]`, ne grešku `404`.
3. Kao odvojenu vežbu dodaj ownership filter iz odeljka 7 tek kada postoji pouzdan `current_user` dependency. Uloguj se kao dva korisnika i potvrdi da svaki dobija samo svoje zadatke.
4. Uporedi ORM model sa response šemom. Koje kolone baze dozvoljavaju `NULL`, a koje šema dozvoljava kao `None`?

Ako si edukativni router iz odeljka 6 uključio u pokrenutu aplikaciju, primer poziva je:

```bash
curl -i http://127.0.0.1:8000/todos/
```

Taj primer **nema autentikaciju** i prikazuje sve redove. Ne može dokazati izolaciju korisnika. Za test ownership filtera potrebni su stvarni autentikovani zahtevi sa odgovarajućim tokenima za dva korisnika. Sam `/todos/{user_id}` ili filter po proizvoljnom `user_id` ne dokazuje da je pristup bezbedan.

---

## 12) Najčešće greške

1. **Globalna sesija:** ne deli jednu `Session` između konkurentnih zahteva.
2. **Bez zatvaranja sesije:** koristi dependency sa `yield` i `finally`.
3. **ORM klasa kao response model:** koristi Pydantic šemu sa
   `ConfigDict(from_attributes=True)`, ne `response_model=list[Todos]`.
4. **Nepodudaranje `NULL` pravila:** response validacija može da padne ako
   šema zahteva vrednost, a baza sadrži `NULL`.
5. **Neautorizovan filter:** ID iz URL-a nije dokaz identiteta korisnika.
6. **Sinhroni DB poziv u `async def`:** može blokirati event loop.
7. **Očekivanje migracija od `create_all()`:** postojeće tabele ne ažurira.
8. **Mešanje `.execute()` i `.scalars()`:** rezultat `execute()` sadrži redove, dok `scalars()` izdvaja prvu vrednost svakog reda.

---

## 13) Samoprovera

1. Zašto se u `get_db` koristi `yield`, a ne samo `return`?

- `yield` omogućava da se sesija pravilno zatvori u `finally` bloku nakon što se završi sa korišćenjem. Ako bi se koristio samo `return`, sesija ne bi imala priliku da se zatvori, što može dovesti do curenja konekcija i problema sa konkurentnim pristupom bazi.

2. Da li `SessionLocal()` mora odmah otvoriti fizičku DB konekciju?

- Ne, `SessionLocal()` može odložiti otvaranje konekcije dok se zaista ne izvrši neki upit. Ovo omogućava efikasnije korišćenje resursa i smanjuje broj nepotrebno otvorenih konekcija. Fizička konekcija se otvara tek kada je zaista potrebna baza podataka za izvršavanje upita (npr. prilikom prvog `SELECT` ili `INSERT` upita).

3. Koja je razlika između `select(Todos)` i `db.scalars(stmt)`?

- `select(Todos)` gradi SQL izraz koji opisuje šta želimo da dohvatimo iz baze, dok `db.scalars(stmt)` izvršava taj izraz i vraća samo prve vrednosti iz svakog reda rezultata. Ovo je korisno kada nas zanima samo jedna kolona ili kada želimo da dobijemo listu objekata iz upita.

4. Šta vraća `.all()` kada nema nijednog reda?

- `.all()` vraća praznu listu kada upit ne pronađe nijedan red u bazi. Ovo omogućava jednostavno rukovanje situacijama kada nema rezultata, bez potrebe za dodatnom proverom `None` vrednosti.

5. Zašto `response_model` treba da bude Pydantic šema, a ne ORM klasa?

- Zato što Pydantic šema omogućava validaciju i serijalizaciju podataka koji se vraćaju iz API-ja, dok ORM klasa predstavlja strukturu baze podataka i ne pruža automatsku validaciju izlaza. Pored toga, Pydantic šema može definisati dodatna pravila i transformacije podataka koji se šalju klijentu, čime se osigurava konzistentan i siguran API izlaz.

6. Zašto `WHERE owner_id = ...` nije dovoljan ako je ID proizvoljan unos klijenta?

- Zato što klijent može da unese proizvoljan ID i pristupi tuđim podacima. Identitet korisnika mora se proveravati kroz autentikaciju, a ne samo kroz parametre URL-a. Na taj način se osigurava da korisnik može pristupiti samo svojim podacima, čime se štiti privatnost i integritet podataka.

7. Zašto je `def` prikladan za sinhronu sesiju u FastAPI-ju?

- Zato što sinhrona sesija blokira thread dok se izvršava, a FastAPI koristi thread pool za sinhrone rute. Korišćenje `def` omogućava da se sinhroni kod izvršava u thread pool-u bez blokiranja event loop-a. `thread pool` predstavlja mehanizam koji omogućava paralelno izvršavanje sinhronih funkcija u odvojenim thread-ovima. Funkcioniše tako što se sinhrone funkcije delegiraju na thread pool, dok glavni event loop ostaje slobodan za obradu drugih asinhronih zadataka.

8. Šta `create_all()` radi sa novom, a šta sa postojećom tabelom?

- `create_all()` kreira sve tabele koje ne postoje u bazi, ali ne menja postojeće tabele. Za migracije postojećih tabela potrebno je koristiti alatke kao što je Alembic.

---

## 14) Veza sa sledećim lekcijama

Ovaj obrazac sesije i dependency-ja koristi se i za `GET` po ID-u, kao i kasnije za `POST`, `PUT` i `DELETE`. Razlika je u upitu i radu sa transakcijom; promena podataka zahteva pažljivo upravljanje `commit` i `rollback` postupcima.
