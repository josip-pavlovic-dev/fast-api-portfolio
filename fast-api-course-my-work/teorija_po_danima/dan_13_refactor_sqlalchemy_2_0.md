# Dan 13 - Refaktor TodoApp na SQLAlchemy 2.0

## Pitanje 1

PITANJE: Kako da uradim Fazu 2 refaktor plana: prebacivanje `Base`, `Users` i `Todos` na SQLAlchemy 2.0 deklarativni stil?

---

## Odgovor 1

ODGOVOR: U ovoj fazi promenjen je način na koji `SQLAlchemy` definiše `deklarativnu bazu` i `ORM modele`. Nazivi tabela i kolona, primarni ključevi, foreign key, indeksi, `nullable ponašanje` i default vrednosti su sačuvani. Nismo još menjali upite u routerima; to pripada Fazi 3.

`mapped_column` je novi način definisanja kolona u SQLAlchemy 2.0 deklarativnim modelima. Umesto da direktno koristimo `Column`, koristimo `mapped_column` unutar klase koja nasleđuje `Base`. Ovo omogućava bolju tipizaciju i integraciju sa modernim Python alatima za statičku analizu koda.

`nullable` ponašanje predstavlja da li kolona može da sadrži `NULL` vrednosti u bazi. U SQLAlchemy 2.0, ovo se eksplicitno navodi kroz `nullable=True` ili `nullable=False` u `mapped_column`.

`NULL` vrednost u bazi predstavlja odsustvo podataka u toj koloni. Kada je `nullable=True`, kolona može da sadrži `NULL` vrednosti (može biti prazna ili nepopunjena); kada je `nullable=False`, kolona mora da sadrži validne podatke (ne može biti prazna).

`Primary key` kolona mora da ima validnu vrednost i ne može da bude `NULL`. Ona je jedinstvena za svaki red u tabeli. Obično se koristi za identifikaciju i povezivanje redova između tabela. Najčešće je to `id` kolona jer je jedinstvena za svaki red i automatski se inkrementira (`auto-increment`). U SQLAlchemy 2.0, ovo se obično postiže kombinacijom `primary_key=True` i `nullable=False` (implicitno za primarni ključ i ne mora se eksplicitno navoditi ali se može navesti radi jasnoće). Ovo osigurava integritet podataka i omogućava efikasno indeksiranje primarnih ključeva.

`auto-increment` označava da se vrednost primarnog ključa automatski povećava za svaki novi red u tabeli. U SQLAlchemy 2.0, ovo se obično postiže korišćenjem `Integer` tipa sa `primary_key=True`, što automatski omogućava auto-inkrement.

PITANJE: Da li to znaci da ne moram praviti funkciju za generisanje ID-jeva ručno?

ODGOVOR: Tačno, `SQLAlchemy` će se pobrinuti za `automatsko inkrementiranje primarnog ključa`. Napomena da ovo važi samo za `Integer` primarne ključeve sa `primary_key=True`. Ovo nije vazilo u starom SQLAlchemy stilu, gde ječesto bilo potrebno eksplicitno definisati `Sequence` ili koristiti druge metode za automatsko generisanje ID-jeva.

`Foreign key` kolona referencira primarni ključ druge tabele, čime se uspostavlja veza između tabela, i može biti `nullable` ili `non-nullable` u zavisnosti od poslovne logike. U SQLAlchemy 2.0, ovo se definiše kroz `ForeignKey` u `mapped_column` i opcionalno `nullable=True` ili `nullable=False`.

`index` označava da li SQLAlchemy treba da kreira indeks za tu kolonu, što može poboljšati performanse pretrage po toj koloni. Indeksi su posebno korisni za kolone po kojima se često filtrira ili sortira. Primer: `id = Column(Integer, primary_key=True, index=True)` kreira indeks na `id` koloni. U SQLAlchemy 2.0, ovo se takođe navodi kroz `index=True` u `mapped_column`.

`unique` označava da li kolona treba da ima jedinstvene vrednosti u tabeli. Ako je `unique=True`, SQLAlchemy će kreirati jedinstveni indeks na toj koloni, osiguravajući da se vrednosti ne ponavljaju. U SQLAlchemy 2.0, ovo se takođe navodi kroz `unique=True` u `mapped_column`.

Glavni ORM refaktor urađen je u:

1. `TodoApp/db/base.py`
2. `TodoApp/models.py`

Pylance provera je pokazala i jednu neophodnu prateću promenu u `TodoApp/api/routes/auth.py`, objašnjenu niže.

---

## Faza 2, korak 1 - novi `Base`

### Pre refaktora

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

Ovim se pozivala funkcija koja pravi `deklarativnu osnovu` za ORM modele.

---

### Posle refaktora: `TodoApp/db/base.py`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
	pass
```

---

### Šta se promenilo i zašto

1. `DeclarativeBase` se uvozi iz `sqlalchemy.orm`, koji je aktuelni ORM API.
2. Umesto da pozovemo `declarative_base()`, definišemo sopstvenu osnovnu klasu nasleđivanjem od `DeclarativeBase`.
3. `Users` i `Todos` nasleđuju tu klasu, pa SQLAlchemy registruje njihove tabele i čuva ih u `Base.metadata`.
4. `Base.metadata` i dalje može da se koristi za `pregled modela` i `create_all()`; organizacija metadata objekta nije promenjena.

`pass` znači da `Base` ne dodaje sopstvena polja ili metode. Njena uloga je da bude zajednička SQLAlchemy deklarativna osnova.

---

## 2) Faza 2, korak 2 - SQLAlchemy 2.0 tipizovani modeli

### Stari obrazac

Pre refaktora kolona se definisala direktno pomoću `Column`:

```python
id = Column(Integer, primary_key=True, index=True)
title = Column(String)
```

---

### Novi obrazac

U 2.0 stilu se koristi tipizovana deklaracija:

```python
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db.base import Base

class Todos(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complete: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
```

NAPOMENA: Koristimo `None` i `nullable=True` za sve kolone u bazi osim za primarni ključ (`id`). Iako nije logično da `pririty`, `complete`, ili `owner_id` budu `None`, ovo koristimo u početnoj fazi razvoja. Kada se aplikacija stabilizuje i pređemo na Alembic migracije, tada ćemo ažurirati kolone da budu striktno `NOT NULL` gde je to potrebno. Za sada ne obraćamo previše pažnje na ovo i stavljamo sve koline osim primarnog ključa kao nullable vrednosti (tj. dozvoljavamo `None` u Python kodu i `NULL` u bazi).

Kod primarnog ključa (`Primary Key`) ne koristimo `None` a `nullable` je implicitno `False` i ne mora se eksplicitno navoditi. To znači da možemo jednostavno definisati primarni ključ bez dodatnih parametara za nullable. Primer:

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
```

---

### Uloga `Mapped` i `mapped_column`

1. `Mapped[T]` označava Python tip atributa koji se koristi za ORM mapiranje na SQL kolonu.
2. `mapped_column(...)` opisuje SQL kolonu i njena pravila: `tip`, `primarni ključ`, `indeks`, `nullable`, `default` i slično.
3. `SQLAlchemy` koristi deklaraciju (`Base klasu`) da napravi `mapiranje ORM objekta` i `metadata` (Base.metadata) za tabelu.
4. Tipovi pomažu editoru i type checker-u da razumeju kakve vrednosti očekujemo na atributima modela.

`Mapped` nije SQL tip i ne kreira kolonu sam. On služi samo za tipizaciju u Python kodu. Jednostavno, leva strana anotacije (`id: Mapped[int]`) govori Pythonu i editoru kakav tip vrednosti očekujemo, dok `mapped_column(...)` definiše stvarnu SQL kolonu. Dakle, oba dela rade zajedno da bi se postigla `tipizacija` (`Mapped`) i mapiranje ORM modela (`mapped_column`).

NAPOMENA: Sam `mapped_column` nije zamena za Python tip anotaciju; u SQLAlchemy 2.0 koristi se zajedno sa `Mapped` koji služi kao Python tip anotacija za ORM atribute.

---

## 3) Šta je sačuvano u `Todos`

Novi model u `TodoApp/models.py` zadržava:

1. `__tablename__ = "todos"`
2. `id` kao primarni ključ sa indeksom
3. `title`, `description`, `priority` i `complete`
4. `complete` Python default vrednost `False`
5. `owner_id` foreign key ka `users.id`

Primeri novog mapiranja:

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
title: Mapped[str | None] = mapped_column(String, nullable=True)
complete: Mapped[bool | None] = mapped_column(
	Boolean, default=False, nullable=True
)
owner_id: Mapped[int | None] = mapped_column(
	ForeignKey("users.id"), nullable=True
)
```

`ForeignKey("users.id")` i dalje postavlja vezu na tabelu i kolonu baze. U ovoj fazi nismo dodavali ORM `relationship()`; za postojeće upite i ownership filtere foreign key je dovoljan, a ORM relacije nisu potrebne da bismo prešli na 2.0 mapiranje.

---

## 4) Šta je sačuvano u `Users`

Novi model zadržava:

1. `__tablename__ = "users"`
2. `id` kao primarni ključ sa indeksom
3. `email` i `username` kao unique kolone
4. lična polja `first_name` i `last_name`
5. `hashed_password`
6. `is_active` sa Python default vrednošću `True`
7. `role`

Primeri:

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
username: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
is_active: Mapped[bool | None] = mapped_column(
	Boolean, default=True, nullable=True
)
```

---

## 5) Zašto se koristi `str | None` i `nullable=True`?

U starom kodu većina `Column(...)` deklaracija nije navodila `nullable=False`. Za SQLAlchemy kolone je podrazumevano ponašanje zato nullable kolona, osim kada je kolona primarni ključ ili je nullable drugačije podešen.

U tipizovanom mapiranju SQLAlchemy koristi i Python anotaciju da zaključi nullable ponašanje:

1. `Mapped[str]` uglavnom znači da vrednost ne treba da bude `NULL`.
2. `Mapped[str | None]` označava da Python vrednost može biti `None`, pa odgovara nullable koloni.
3. U ovom refaktoru `nullable=True` je dodat eksplicitno da namera bude čitljiva i da se sačuva postojeća definicija baze.

Ovo je važno zato što je cilj ove faze promena ORM sintakse, a ne promena pravila baze. U budućnosti možemo svesno odlučiti da neka polja budu obavezna, ali takva promena seme treba da bude odvojena i vođena migracijom, ne sakrivena unutar sintaksnog refaktora.

---

## 6) Važna razlika: Python `default` i server-side default

Ostavljene su postojeće deklaracije:

```python
complete: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
```

Aplikacija se pokreće, a Swagger učitava rute,

Pošto smo čuvali trenutno ponašanje, nismo menjali `default` u `server_default`. To može biti buduća projektna odluka, ali nije deo ovog tipizovanog prelaza.

`server_default` se koristi kada želimo da baza sama postavi podrazumevanu vrednost za kolonu, nezavisno od Python koda. U ovom refaktoru smo zadržali Python `default`, a `server_default` nije dodavan. Primer:

```python
complete: Mapped[bool | None] = mapped_column(Boolean, server_default="false", nullable=True)
is_active: Mapped[bool | None] = mapped_column(Boolean, server_default="true", nullable=True)
```

U prvom primeru, `server_default="false"` omogućava bazi da automatski postavi vrednost kolone `complete` na `false` ako Python kod ne prosledi vrednost. Slično, u drugom primeru, `server_default="true"` osigurava da kolona `is_active` dobije podrazumevanu vrednost `true` od strane baze.

---

## 7) Zašto je postojeća baza ostala netaknuta?

U ovoj fazi promenili smo Python deklaracije modela, ali smo sačuvali postojeću strukturu tabela. Aplikacija u `main.py` poziva `Base.metadata.create_all(bind=engine)`, a `create_all()` kreira tabele koje nedostaju; ne radi automatski ALTER nad već postojećim tabelama.

`ALTER` komande su SQL naredbe (u SQL sintaksi) koje se koriste za menjanje postojeće strukture tabela, kao što su dodavanje novih kolona, menjanje tipova kolona ili postavljanje podrazumevanih vrednosti. One se ne izvršavaju automatski kada se promeni Python model; za to je potrebno koristiti migracije ili ručno izvršiti ALTER komande u terminalu uz pomoć `sqlite3` ili sličnog alata.

Posledica ne izvršavanja automatskog ALTER-a je:

1. Postojeća tabela se ne prepravlja automatski samo zato što smo promenili Python anotacije,
2. Imena tabela i kolona su ostala ista što znači da se postojeći upiti i dalje mogu koristiti bez promena
3. Postojeći podaci se ne brišu ovim refaktorom, ali je i dalje preporučljivo imati backup pre većih promena.
4. Promene strukture baze u budućnosti treba raditi kroz `Alembic` migracije.

Ovo nije zamena za backup. Pre većih DB promena i dalje čuvamo lokalni backup; SQL dump je ignorisan kroz `.gitignore` jer sadrži poverljive podatke.

---

## 8) Šta se namerno nije menjalo

Faza 2 se odnosi prvenstveno na declarative base i modele. Nismo menjali:

- `db/session.py` ni način kreiranja `Session`-a,
- `core/security.py` upit za pronalaženje korisnika,
- upite u `auth.py`, `todos.py`, `users.py` ili `admin.py`,
- `rute`, `status kodove` ili `API` ponašanje,
- `auth`, `ownership` ili `admin` pravila,
- `tabele` ručno niti `SQLAlchemy` upite.

U `auth.py` nije menjan upit. Promenjen je samo završni povratni izraz endpointa za registraciju: umesto direktnog vraćanja ORM modela sada se poziva `UserResponse.model_validate(create_user_model)`. Razlog je što `Mapped[str | None]` precizno označava da ORM atribut može biti `None`, dok `UserResponse` očekuje validiran response objekat. Eksplicitna konverzija usklađuje povratni tip i koristi postojeći `from_attributes=True` podešen na schema modelu.

`model_validate` metoda se koristi za konverziju ORM modela (njegovih atributa) u validiran Pydantic model (Response model). Ako ne pozovemo ovu metodu, Pydantic model neće biti pravilno inicijalizovan iz ORM instance. Kada promenimo da ORM atribut ne moze biti None (u kasnijoj fazi refaktora), ova metoda će osigurati da se ORM vrednosti pravilno mapiraju na Pydantic model.

U staroj verziji `UserResponse.model_validate(create_user_model)` je bio nepotreban jer su ORM atributi mogli biti `None`, dok sada eksplicitno koristimo ovu metodu da bismo osigurali pravilnu konverziju i validaciju.

Stari `db.query(...)` stil se i dalje može pojavljivati. Migracija tih upita pripada Fazi 3 i radiće se odvojeno, uz provere nakon svakog koraka.

---

## 9) Provere koje su izvršene

### Provera metadata modela u privremenoj bazi

Napravio sam privremeni SQLite engine samo u memoriji i pozvao `Base.metadata.create_all()` nad njim. Time nije menjana tvoja prava `todosapp.db` baza.

Provera je potvrdila:

1. postoje tabele `todos` i `users`,
2. nullable definicije su očuvane,
3. `todos.owner_id` i dalje referencira `users.id`,
4. `complete` i dalje ima Python default `False`,
5. `is_active` i dalje ima Python default `True`.

### Provera uvoza aplikacije

Iz direktorijuma `fast-api-course-my-work` pokrenuto je:

```bash
../.venv/bin/python -c 'from TodoApp.main import app; print("OK FastAPI app imported:", app.title)'
```

Rezultat je bio:

```text
OK FastAPI app imported: TodoApp API
```

To potvrđuje da aplikacija može da uveze `Base`, modele i FastAPI routere posle ove promene. To još nije pun test svih endpointa; CRUD/auth smoke testovi slede posle query refaktora.

---

## 10) Kratak rezime izmena po fajlu

### `TodoApp/db/base.py`

- Uklonjen je poziv `declarative_base()`.
- Dodata je klasa `Base(DeclarativeBase)`.
- `Base.metadata` ostaje centralni metadata objekat modela.

### `TodoApp/models.py`

- Uklonjen je `Column` import.
- Dodati su `Mapped` i `mapped_column`.
- Svaka kolona sada ima Python tip anotaciju.
- Zadržani su nazivi kolona/tabela, unique ograničenja, primarni ključevi, indeksi, foreign key, nullable ponašanje i default vrednosti.

### `TodoApp/api/routes/auth.py`

- Upit i registraciona logika nisu promenjeni.
- ORM objekat se eksplicitno pretvara u `UserResponse` pomoću `UserResponse.model_validate(...)`, da bi se povratni tip poklapao sa anotacijom endpointa.
- Ova izmena je pronađena tokom type-check provere nakon što su SQLAlchemy model atributi dobili precizne nullable anotacije.

---

## 11) Swagger smoke test posle Faze 2

Cilj testa je da proveriš da SQLAlchemy 2.0 modeli nisu pokvarili postojeći API. U ovoj fazi upiti u routerima još koriste `db.query(...)`; to je namerno, jer se query refaktor radi u Fazi 3.

### Pre pokretanja

Ovaj test koristi lokalnu SQLite bazu podešenu u `TodoApp/db/database.py`. Pokreći ga samo nad lokalnim razvojnim projektom, ne nad produkcionom bazom.

Iz korena repozitorijuma pokreni:

```bash
source .venv/bin/activate
cd fast-api-course-my-work
python -m uvicorn TodoApp.main:app --reload
```

Ostavi taj terminal otvoren dok testiraš. U browseru otvori:

```text
http://127.0.0.1:8000/docs
```

Ako port 8000 već koristi drugi proces, zaustavi ga ili pokreni TodoApp na drugom portu, na primer `--port 8001`, pa u browseru otvori odgovarajući URL.

---

### Korak 1 - proveri da je API dostupan

1. Otvori `/docs`.
2. Proveri da Swagger prikazuje grupe `auth`, `todos`, `users` i `admin`.
3. Ovo potvrđuje da se aplikacija pokrenula i da su routeri registrovani.

---

### Korak 2 - proveri da zaštićena ruta odbija zahtev bez tokena

1. Pronađi `GET /todos/`.
2. Klikni `Try it out`, pa `Execute`, bez prethodnog klika na `Authorize`.
3. Očekivani rezultat je `401`.

Ovim proveravaš da zaštićena ruta i dalje zahteva Bearer token.

---

### Korak 3 - registruj test korisnika

1. Pronađi `POST /auth/` i klikni `Try it out`.
2. Pošalji sledeći primer, uz zamenu username-a i email adrese jedinstvenim vrednostima ako si već ranije pokrenuo ovaj test:

```json
{
  "email": "sqlalchemy2-smoke-20261002@example.test",
  "username": "sqlalchemy2_smoke_20261002",
  "first_name": "SQLAlchemy",
  "last_name": "Smoke Test",
  "password": "TestPassword-2026",
  "role": "user"
}
```

3. Klikni `Execute`.
4. Očekuj `201 Created`.
5. Response treba da sadrži korisničke podatke, ali ne sme da sadrži `password` ni `hashed_password`.

Ako dobiješ `400` zbog duplikata, izaberi novu username i email vrednost. Test nalog ostaje u lokalnoj bazi; nemoj koristiti stvarnu lozinku.

---

### Bezbednosna napomena o `role`

Trenutni `CreateUserRequest` prima `role` od klijenta, a register endpoint upisuje tu vrednost. Zato u Swagger testu obavezno koristi samo `"role": "user"`. Nemoj javnim register endpointom praviti admin nalog. Dozvoljavanje klijentu da sam izabere `admin` ulogu je bezbednosni problem koji treba zasebno ispraviti.

---

### Korak 4 - prijavi se i autorizuj Swagger

1. Klikni `Authorize` pri vrhu Swagger stranice.
2. Unesi test korisnikov username i password.
3. Ako se prikaže polje `grant_type`, izaberi ili unesi `password`.
4. Potvrdi autorizaciju i zatvori prozor.

Swagger koristi OAuth2 token endpoint podešen u projektu (`/auth/token`). Ako Authorize forma ne uspe, proveri da si napravio korisnika i da unosiš username, ne email.

---

### Korak 5 - proveri current user endpoint

1. Pozovi `GET /users/me`.
2. Očekuj `200 OK`.
3. Potvrdi da response prikazuje podatke test korisnika.
4. Potvrdi da response ne sadrži `hashed_password`.

---

### Korak 6 - napravi Todo zapis

1. Pozovi `POST /todos/` sa telom:

```json
{
  "title": "Phase 2 Swagger test",
  "description": "Provera ORM modela posle SQLAlchemy 2.0 refaktora.",
  "priority": 1,
  "complete": false
}
```

2. Očekuj `201 Created` i zabeleži vraćeni `id`.
3. Request ne sadrži `owner_id`; server ga izvodi iz autorizovanog korisnika.

---

### Korak 7 - proveri read operacije

1. Pozovi `GET /todos/` i očekuj `200 OK` sa upravo kreiranim zapisom.
2. Pozovi `GET /todos/{todo_id}` koristeći `id` iz prethodnog odgovora.
3. Očekuj `200 OK` i isti Todo zapis.

---

### Korak 8 - proveri update

1. Pozovi `PUT /todos/{todo_id}` sa istim obaveznim poljima, uz promenjen naslov, na primer `Phase 2 Swagger test updated`.
2. Očekuj `204 No Content`.
3. Ponovo pozovi `GET /todos/{todo_id}` i potvrdi da je naslov promenjen.

`204` odgovor nema response body; zato je naredni GET način da potvrdiš da je izmena sačuvana.

---

### Korak 9 - proveri delete

1. Pozovi `DELETE /todos/{todo_id}` za test zapis.
2. Očekuj `204 No Content`.
3. Ponovo pozovi `GET /todos/{todo_id}`.
4. Očekuj `404 Not Found`.

---

### Korak 10 - opciono proveri promenu lozinke

1. Pozovi `PUT /users/password` sa telom:

```json
{
  "current_password": "TestPassword-2026",
  "new_password": "NewTestPassword-2026"
}
```

2. Očekuj `204 No Content`.
3. U `Authorize` prozoru se prijavi ponovo novom lozinkom. Očekuj uspešnu autorizaciju.
4. Nemoj koristiti lozinku iz ovog primera za bilo koji stvarni nalog.

---

### Korak 11 - opciono proveri ownership sa drugim korisnikom

Ovaj test je koristan za authorization, ali nije neophodan da potvrdiš samo ORM mapiranje.

1. Dok si autorizovan kao korisnik A, napravi Todo i zabeleži njegov ID.
2. Registruj drugog test korisnika B sa drugim username-om i email adresom, uz `"role": "user"`.
3. U Swagger `Authorize` prozoru autorizuj se kao korisnik B.
4. Pozovi `GET /todos/`; Todo korisnika A ne treba da bude u listi korisnika B.
5. Pozovi `GET /todos/{idA}` za ID korisnika A; očekuj `404`.

---

### Rezultat koji treba zabeležiti

Faza 2 smoke test je uspešan ako:

1. aplikacija se pokреће, a Swagger učitava rute,
2. zaštićene rute bez tokena vraćaju `401`,
3. registracija i login rade,
4. `/users/me` ne izlaže hash lozinke,
5. create/read/update/delete rade sa očekivanim status kodovima,
6. Todo zapis jednog korisnika nije dostupan drugom korisniku.

Ako neki korak padne, zabeleži endpoint, poslati zahtev, status kod i response `detail`; nemoj odmah menjati ORM modele. Prvo treba utvrditi da li je uzrok auth, validacija, postojeće stanje lokalne baze ili ORM izmena.

Kada završiš, zaustavi razvojni server sa `Ctrl+C` u njegovom terminalu.

---

## 12) Sledeći korak

Posle Swagger smoke testa Faza 2 je završena. Sledeća je Faza 3, korak 1: prevesti korisnički lookup u `core/security.py` sa `db.query(...).filter(...).first()` na `select(...)`, `db.execute(...)` i `scalars()`. Pre toga ćemo sačuvati ovaj stabilni checkpoint i menjati jedan upit po koraku.

---

## Pitanje 2

PITANJE: Zašto su `priority`, `complete` i `owner_id` deklarisani kao nullable i mogu li zaista biti `None`?

---

## Odgovor 2

ODGOVOR: U trenutnom modelu `None` je dozvoljen zato što smo tokom Faze 2 namerno sačuvali staro ponašanje baze. To ne znači da je `None` poželjna vrednost za ove kolone u TodoApp. Tvoja pretpostavka je naročito dobra za `complete`: poslovno gledano, zadatak treba da bude završen (`True`) ili nezavršen (`False`), a ne u nepoznatom stanju (`None`).

### 1) Zašto smo Fazi 2 zadržali `nullable=True`?

Pre refaktora kolone su bile napisane ovako:

```python
priority = Column(Integer)
complete = Column(Boolean, default=False)
owner_id = Column(Integer, ForeignKey("users.id"))
```

Pošto nije bilo `nullable=False`, SQLAlchemy je kolone tretirao kao nullable. Cilj Faze 2 bio je promeniti stil deklaracije (`Column` u `Mapped`/`mapped_column`), a ne istovremeno menjati pravila baze.

Zato smo eksplicitno preneli postojeće ponašanje:

```python
priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
complete: Mapped[bool | None] = mapped_column(
  Boolean, default=False, nullable=True
)
owner_id: Mapped[int | None] = mapped_column(
  ForeignKey("users.id"), nullable=True
)
```

Drugim rečima, nullable je zadržan radi kompatibilnosti sa starom definicijom, a ne zato što smo zaključili da aplikaciji treba dozvoliti nepotpun Todo zapis.

### 2) Šta tačno znači svaki deo deklaracije?

Uzmimo `complete`:

```python
complete: Mapped[bool | None] = mapped_column(
  Boolean, default=False, nullable=True
)
```

- `Mapped[bool | None]` kaže Python tipu i SQLAlchemy mapiranju da vrednost može biti `True`, `False` ili `None`.
- `Boolean` određuje SQL tip kolone.
- `default=False` postavlja SQLAlchemy default kada se vrednost ne prosledi pri upisu kroz SQLAlchemy.
- `nullable=True` dopušta bazi da u toj koloni sačuva SQL `NULL`.

`default=False` nije constraint. On ne zabranjuje `NULL` i ne znači da baza garantuje samo `True` ili `False`. Zato kombinacija `default=False` i `nullable=True` i dalje dozvoljava praznu/null vrednost u određenim načinima upisa.

U bazi postoje tri moguća stanja boolean kolone koja dopušta null:

1. `TRUE` - zadatak je završen.
2. `FALSE` - zadatak nije završen.
3. `NULL` - vrednost nije postavljena/nepoznata.

Za uobičajenu Todo logiku treće stanje nije korisno. Dakle, da: ciljna definicija za `complete` bi trebalo da dozvoli samo `True` ili `False`.

### 3) Šta govore request šeme i trenutna logika aplikacije?

U `CreateTodoRequest` polja `priority` i `complete` su obavezna, a `priority` dodatno ima validaciju opsega. Pydantic zato odbacuje zahtev u kome ta polja izostanu ili im se pošalje `null`.

`owner_id` klijent uopšte ne šalje. `POST /todos/` ga dobija iz `current_user.id`, pa u normalnom authenticated request toku treba da postoji vlasnik.

To znači da imamo razliku između dve granice:

1. **API validacija** određuje šta HTTP klijent sme da pošalje.
2. **Nullable constraint baze** određuje šta baza može da sačuva, bez obzira na putanju kojom se upis desio.

Trenutna API putanja već zahteva `priority` i `complete` i server određuje `owner_id`, ali sama nullable definicija baze je popustljivija od tih pravila.

### 4) Kako bi izgledala stroža ciljna Todo šema?

Kada budemo spremni da menjamo i pravila baze, smislenija definicija je:

```python
title: Mapped[str] = mapped_column(String, nullable=False)
description: Mapped[str] = mapped_column(String, nullable=False)
priority: Mapped[int] = mapped_column(Integer, nullable=False)
complete: Mapped[bool] = mapped_column(
  Boolean, default=False, nullable=False
)
owner_id: Mapped[int] = mapped_column(
  ForeignKey("users.id"), nullable=False
)
```

Ovde:

1. `Mapped[bool]` ne dopušta `None` u Python tipovima.
2. `nullable=False` zabranjuje SQL `NULL` u bazi.
3. `default=False` obezbeđuje početno `False` kada aplikacija ne zada vrednost, ali nije zamena za `nullable=False`.
4. `owner_id` je obavezan jer Todo u ovom projektu pripada korisniku.

Ovo je predlog ciljnog pravila za aplikaciju, a ne promena koju treba sakriveno ubaciti u trenutnu fazu. `title` i `description` su uključeni jer ih i request šema zahteva.

### 5) Zašto to nismo odmah promenili u Fazi 2?

Prelazak sa nullable na non-nullable je promena šeme baze, ne samo promena Python tipa. `Base.metadata.create_all()` ne prepravlja postojeće tabele; ako bi u bazi već postojao red sa `NULL` u nekoj od tih kolona, baza ne bi mogla jednostavno da zabrani nullable vrednosti dok se taj podatak ne očisti ili ispravi.

Zato je bezbedan redosled:

1. Faza 2: promeniti ORM sintaksu i sačuvati postojeću šemu.
2. Proveriti podatke i odlučiti koja polja zaista moraju biti obavezna.
3. Napraviti Alembic migraciju koja uklanja ili ispravlja postojeće `NULL` vrednosti i menja kolone na `NOT NULL`.
4. Promeniti modele da koriste `Mapped[T]` i `nullable=False`.
5. Testirati aplikaciju i migraciju na kopiji baze.

Možemo planirati tu šemu kao deo database/Alembic faze. Ne treba sada ručno menjati bazu niti računati da će promena anotacije sama izmeniti postojeću tabelu.

### Kratak zaključak

1. `complete` bi u poslovnom modelu trebalo da bude samo `True` ili `False`; `None` nije smislen status Todo zadatka.
2. `priority` je obavezan kroz postojeći request schema, a `owner_id` određuje server, pa su i oni kandidati za `nullable=False`.
3. Nullable vrednosti smo zadržali zato što smo u Fazi 2 čuvali staru šemu baze, ne zato što je to najbolji konačni dizajn.
4. `default=False` zadaje podrazumevanu vrednost, ali ne zabranjuje SQL `NULL`.
5. Zatezanje pravila na `NOT NULL` treba uraditi promišljeno, uz proveru podataka i Alembic migraciju.

---
