# Project 3 — beleške iz razgovora za 15.11.2026

Ove beleške sadrže ključne informacije o povezivanju FastAPI aplikacije sa SQLite bazom koristeći SQLAlchemy, uključujući strukturu projekta, URL baze, kreiranje tabela i rad sa relativnim putanjama.

---

## Osnovni delovi povezivanja sa bazom

U [db/database.py](./db/database.py) trenutno su definisani:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./Project_3/data/todosapp3.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

- **URL** govori SQLAlchemy-ju koju vrstu baze i koju lokaciju da koristi.
- **Engine** je centralni objekat koji upravlja povezivanjem sa bazom i
  konekcijama. Sam `create_engine()` obično ne otvara odmah konekciju; ona se
  koristi kada se izvrši operacija koja pristupa bazi.
- **`SessionLocal`** je fabrika sesija: `SessionLocal()` pravi novu `Session`
  instancu. Sesija je radni kontekst za ORM objekte i transakcije; ne treba je
  poistovetiti sa samim engine-om.
- **`Base`** iz [db/base.py](./db/base.py) je osnovna klasa ORM modela.
  Model `Todos` u [models.py](./models.py) nasleđuje `Base` i opisuje tabelu.
- `check_same_thread=False` isključuje SQLite proveru da se konekcija koristi
  samo u thread-u u kom je napravljena. To **ne čini sesiju ili konekciju
  automatski bezbednom za istovremenu upotrebu** u više thread-ova; sesije se
  ne dele nekontrolisano između paralelnih zahteva.

### Kako model postaje tabela?

U trenutnom [main1.py](./main1.py) tok je:

1. `from . import models` učitava ORM modele i registruje njihove tabele u
   `Base.metadata`.
2. `Base` i `engine` se uvoze iz `db` paketa.
3. `Base.metadata.create_all(bind=engine)` proverava registrovane tabele i
   kreira one koje nedostaju.

Model je opis strukture; sam import modela ne kreira tabelu. `create_all()` ne
menja strukturu već postojeće tabele da bi je uskladio sa novim modelom.
Za promenu postojeće šeme potrebna je odgovarajuća migracija ili druga
kontrolisana izmena baze. Ne briši postojeću bazu samo radi provere.

**Važno:** `main1.py` poziva `create_all()` već pri uvozu modula. Zato i
uvoz ili pokretanje preko Uvicorn-a može otvoriti bazu i kreirati nedostajuće
tabele.

---

## Šta znači SQLite URL?

Trenutna linija iz [db/database.py](./db/database.py):

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./Project_3/data/todosapp3.db"
```

može se pročitati kao:

- `sqlite` — koristi se SQLite.
- `sqlite:///` — SQLAlchemy oblik URL-a za relativnu putanju do SQLite fajla.
- `./Project_3/data/todosapp3.db` — relativna putanja do fajla baze.
- `todosapp3.db` — ime **fajla baze**, ne ime tabele. Tabela definisana
  modelom `Todos` zove se `todos`.

Relativna putanja se računa od **trenutnog radnog direktorijuma procesa**
(`cwd`), a ne od direktorijuma u kom se nalazi `database.py`. Ako aplikaciju
pokreneš iz `fast-api-course-my-work`, ciljni fajl je
`fast-api-course-my-work/Project_3/data/todosapp3.db`. Isti URL iz drugog
radnog direktorijuma može pokazivati na drugu lokaciju ili prijaviti grešku
ako odgovarajući folder ne postoji.

`data/` je praktično ime za podatke, dok `db/` ovde sadrži Python kod za
rad sa bazom. Ne postoji obavezno ime foldera.

### Da li URL kreira i folder?

Ne. SQLite može kreirati fajl baze kada se uspostavi konekcija, ali **ne
kreira nedostajuće roditeljske direktorijume**. Ako `Project_3/data/` ne
postoji, povezivanje može završiti greškom `unable to open database file`.

Iz `fast-api-course-my-work` folder možeš napraviti komandom:

```bash
mkdir -p Project_3/data
```

`-p` kreira potrebne roditeljske direktorijume i ne prijavljuje grešku ako
direktorijum već postoji. U trenutnom projektu `data/` i `todosapp3.db` već
postoje; nema potrebe ponovo ih praviti ili brisati.

Fajl baze može sadržati lične podatke i lozinke, pa ga obično ne treba
commit-ovati. Trenutni `.gitignore` ne isključuje automatski sve `.db`
fajlove: proveri `git status` pre commita.

---

## Linux putanje: `./`, `../` i `/`

| Zapis             | Značenje                                          |
| ----------------- | ------------------------------------------------- |
| `.` ili `./`      | trenutni direktorijum                             |
| `..` ili `../`    | roditeljski direktorijum, jedan nivo iznad        |
| `././`            | i dalje trenutni direktorijum, **ne** roditeljski |
| `../../`          | dva nivoa iznad                                   |
| `/home/alex/data` | apsolutna putanja od filesystem root-a `/`        |

Na primer, ako je trenutni direktorijum `/home/alex/projects`, onda:

```text
./todosapp.db     -> /home/alex/projects/todosapp.db
././todosapp.db   -> /home/alex/projects/todosapp.db
../todosapp.db    -> /home/alex/todosapp.db
```

`pwd` prikazuje trenutni radni direktorijum. `cd ..` prelazi u roditeljski
direktorijum. `realpath -m ./todosapp.db` prikazuje razrešenu putanju i
kada delovi putanje još ne postoje.

### Zašto u SQLite URL-u postoje tri ili četiri kose crte?

SQLAlchemy URL nije isto što i obična Bash putanja. SQLAlchemy-jev oblik za
SQLite koristi `sqlite:///` ispred putanje do fajla:

```text
sqlite:///./todosapp.db            # relativna putanja: ./todosapp.db
sqlite:///todosapp.db              # takođe relativna: todosapp.db
sqlite:////home/alex/todosapp.db   # apsolutna putanja: /home/alex/todosapp.db
```

Kod apsolutnog oblika četvrta kosa crta je početni `/` Linux putanje. Ne
označava četiri foldera naviše. Za roditeljski folder u putanji koristi se
`..`, ne dodatne kose crte.

**Ispravka ranijeg objašnjenja:** treća kosa crta u `sqlite:///` sama po sebi
nije oznaka „relativne putanje“; deo je SQLAlchemy SQLite URL zapisa.
Relativnost ili apsolutnost određuje putanja baze koja sledi: `./todosapp.db`
je relativna, a `/home/alex/todosapp.db` apsolutna.

Više primera nalazi se u [vodiču za Linux putanje i SQLite URL](../../docs/fastapi/cheatsheets/baze/07_linux_putanje_i_sqlite_url_detaljno.md).

---

## Da li `-m` u `realpath` i Python-u znači isto?

Ne. Istu oznaku različiti programi mogu koristiti za različite opcije:

```bash
realpath -m ./todosapp.db
```

Kod GNU `realpath`, `-m` je kratki oblik za `--canonicalize-missing`: može
razrešiti putanju i ako neki njeni delovi ne postoje. Ne znači „make“ i ne
kreira fajl ili folder.

```bash
python -m uvicorn Project_3.main1:app
```

Kod Python-a, `-m` govori interpreteru da pronađe i pokrene imenovani **modul**
kao program. Ovde je to `uvicorn`; preostali argument `Project_3.main1:app`
koristi Uvicorn da pronađe aplikaciju. Kada pozivamo
`python -m Project_3.main1`, sam `Project_3.main1` se izvršava kao modul
paketa. To nije isto što i pokretanje FastAPI servera: za server se koristi
Uvicorn.

---

## `flush()`, `commit()` i `autoflush=False`

`SessionLocal` pravi sesije za rad sa ORM objektima. Kada menjaš podatke:

```python
db.add(novi_todo)  # objekat je pripremljen u sesiji
db.flush()         # SQL INSERT je poslat unutar otvorene transakcije
db.commit()        # transakcija je potvrđena
```

- **`add()`** stavlja objekat u sesiju; sam po sebi ne potvrđuje transakciju.
- **`flush()`** šalje potrebne SQL naredbe bazi u okviru tekuće transakcije.
  To još nije potvrda transakcije; pre `commit()` promene se mogu poništiti
  sa `db.rollback()`. Flush može, na primer, dodeliti ID koji je baza generisala.
- **`commit()`** potvrđuje transakciju. SQLAlchemy pre potvrde automatski
  izvršava potreban flush.
- **`rollback()`** poništava nepotvrđene promene u transakciji.

`autoflush=False` isključuje automatski flush pre određenih operacija, na
primer pre ORM upita. **Ne isključuje flush pri `commit()`** i ne sprečava
ručni `db.flush()`. `autocommit=False` ne znači da se SQL nikada ne šalje
bazi pre commit-a; znači da potvrdu transakcije kontrolišeš eksplicitno.

Posle rada sesiju treba zatvoriti. Primer dependency-ja koji to radi preko
`yield` i `finally` već postoji u [main11.py](./main11.py), ali današnja tema
bila je razlika između sesije, flush-a i commit-a.

---

## Greška: `attempted relative import with no known parent package`

U trenutnom [main1.py](./main1.py) nalazi se:

```python
from . import models
from .db.base import Base
from .db.database import engine
```

Tačka u `from . import models` znači: „uvezi `models` iz istog **Python
paketa**“. Ne znači samo „pogledaj fizički roditeljski folder“.

Greška se javlja ako se fajl pokrene direktno, na primer:

```bash
# Iz root-a repozitorijuma — ovako relativni import ne radi:
./.venv/bin/python fast-api-course-my-work/Project_3/main1.py
```

Python tada pokreće fajl kao samostalnu skriptu i nema poznat roditeljski
paket za relativni import. Problem nije u tome što folder na disku ne postoji,
već u tome što pri takvom pokretanju modul nema potreban kontekst paketa.
Samo promena trenutnog direktorijuma ne popravlja direktno pokretanje fajla.

### Pokretanje FastAPI servera

Iz root-a repozitorijuma:

```bash
cd fast-api-course-my-work
../.venv/bin/python -m uvicorn Project_3.main1:app --reload
```

`Project_3` je paket, `main1` modul u paketu, a `app` FastAPI objekat u tom
modulu. Uvicorn ga uvozi kao `Project_3.main1`, pa Python zna da `.models`
znači `Project_3.models`. `--reload` je namenjen lokalnom razvoju i ponovo
učitava aplikaciju pri promenama.

Ovaj način je praktičan jer je `Project_3` dostupan iz roditeljskog
direktorijuma i trenutni relativni URL baze pokazuje na
`Project_3/data/todosapp3.db`. Nije jedini način: bitno je da paket bude na
Python import putanji, ali i da radni direktorijum odgovara relativnom URL-u.
Kada se modul uveze, `create_all()` može pristupiti postojećoj bazi i kreirati
nedostajuće tabele.

Ranije je potvrđeno da je direktno pokretanje tadašnjeg `main11.py` dalo
navedeni `ImportError`, dok je paketni uvoz uspeo kada je `create_all()`
zamenjen tokom provere da se baza ne bi menjala. Zbog kasnije zamene
sadržaja fajlova, ovaj primer se sada odnosi na `main1.py`.

---

## FastAPI ekstenzija za VS Code — lokalna upotreba

Ekstenzija **FastAPI** (`FastAPILabs.fastapi-vscode`) može pomoći pri
navigaciji kroz rute:

- **Path Operation Explorer** prikazuje pronađene rute i omogućava prelazak
  na njihovu definiciju.
- **FastAPI: Search Path Operations...** pronalazi rute po putanji, metodi
  ili imenu.
- **CodeLens** može povezati pozive test klijenta sa odgovarajućim rutama.

Ekstenzija ne pokreće automatski testove i njen prikaz ruta nije dokaz da
endpoint radi. Cloud integracija i telemetrija ekstenzije isključene su u
Windows korisničkom profilu; postojeća Python, Pylance i Ruff podešavanja nisu
menjana.

Prethodni CLI je prijavio uspešnu instalaciju, ali je u tvom aktivnom VS Code
prozoru prikazano dugme **Install**. Zato ta CLI poruka nije dokaz da je
ekstenzija dostupna u aktivnom profilu/prozoru. Ako je još potrebno, instaliraj
je kroz Extensions panel tog WSL prozora i proveri status posle instalacije.
Detalji su u [vodiču za FastAPI ekstenziju](../../docs/fastapi/cheatsheets/fastapi_extensions_vscode/fastapi_extension_vscode.md).

---

## Kratka samoprovera

1. Zašto `././todosapp3.db` ne vodi u roditeljski folder?
2. Od kog direktorijuma se računa trenutni relativni SQLite URL?
3. Da li SQLite kreira `data/` ako taj folder ne postoji?
4. Šta `flush()` radi, a šta dodatno radi `commit()`?
5. Zašto `autoflush=False` ne sprečava flush pri commit-u?
6. Zašto direktno pokretanje `main1.py` ne daje kontekst za `from . import models`?
7. Šta znače `Project_3`, `main1` i `app` u Uvicorn argumentu
   `Project_3.main1:app`?

## Provere i granice današnjeg rada

- Provereno je da je SQLAlchemy verzija u repozitorijumskom `.venv`-u bila
  **2.0.38** i da su u postojećem TodoApp-u u metadata-i registrovane tabele
  `todos` i `users`. To je odvojeno od trenutnog Project 3 modela `Todos`.
- SQLAlchemy URL parserom provereni su relativni `./todosapp.db` i apsolutni
  `/home/alex/data/todosapp.db` oblici, bez pristupa bazi.
- Primeri sa `create_all()` mogu menjati fajl baze; današnji pregled beleški
  nije pokretao aplikaciju niti menjao postojeće SQLite podatke.
- Ne treba tumačiti root `pytest` testove kao dokaz da je Project 3 testiran;
  root podešavanje cilja `tests/` za root aplikaciju.
