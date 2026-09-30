# Alembic migracije u FastAPI + SQLAlchemy projektu (detaljno)

Ovaj materijal objasnjava zasto `create_all()` nije dovoljan za realnu aplikaciju, sta Alembic tacno radi, i kako se koristi kroz ceo zivotni ciklus promene seme baze.

---

## 1) Problem koji Alembic resava

Do sada si koristio:

```python
Base.metadata.create_all(bind=engine)
```

Ovo:

- kreira tabele koje ne postoje
- ne menja postojece tabele

Simptom problema:

Zamisli da vec imas tabelu `users` sa podacima, i sada dodas novo polje u model:

```python
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    phone_number = Column(String)
```

Pokretanje `create_all()` ponovo:

- nece dodati kolonu `phone_number` u postojecu tabelu
- tabela `users` vec postoji, pa se `create_all` "ne dotice" nje

Ovo je razlog zasto ti treba pravi migration alat.

---

## 2) Sta je migracija (koncept)

Migracija je:

- eksplicitan, verzionisan opis promene seme baze
- ima "upgrade" (primeni promenu) i "downgrade" (vrati promenu nazad)
- cuva se kao Python fajl u `alembic/versions/`

Migracije ti omogucavaju da:

1. pratis istoriju promena seme kroz vreme
2. primenis iste promene na drugom okruzenju (test, staging, produkcija)
3. vratis bazu na prethodno stanje ako nesto krene po zlu

---

## 3) Instalacija i inicijalizacija (koncept, ne komanda po komanda)

Tipican tok:

```bash
pip install alembic
alembic init alembic
```

Ovo generise:

```text
alembic.ini
alembic/
  env.py
  README
  script.py.mako
  versions/
```

`alembic.ini` je glavni konfiguracioni fajl, `alembic/env.py` je "mozak" koji povezuje Alembic sa tvojim SQLAlchemy modelima.

---

## 4) alembic.ini - kljucni deo

Relevantan isecak:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
```

Znacenje:

- `script_location`: gde se nalaze migracije (folder `alembic/`)
- `prepend_sys_path`: dodaje trenutni direktorijum u `sys.path`, sto pomaze da importi (npr. `import models`) rade kad Alembic pokrece migracije

Ovde se obicno definise i:

```ini
sqlalchemy.url = sqlite:///./todosapp.db
```

Ovo je URL baze nad kojom Alembic radi. Bitno: mora da odgovara istoj bazi koju koristi tvoja aplikacija.

---

## 5) env.py - povezivanje Alembic-a sa tvojim modelima

Isecak iz kursa (Project 4):

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import models

config = context.config
fileConfig(config.config_file_name)
target_metadata = models.Base.metadata
```

Objasnjenje po delovima:

### `import models`

- ovo je isti princip kao i kod `create_all()`
- Alembic mora da "vidi" tvoje modele da bi znao koje tabele/kolone postoje u kodu

### `target_metadata = models.Base.metadata`

- ovo je most izmedju tvog Python koda (modeli) i Alembic autogenerate mehanizma
- Alembic poredi:
  - stanje baze (sta stvarno postoji)
  - stanje `target_metadata` (sta modeli kazu da treba da postoji)
- razlika izmedju ta dva postaje osnova za automatski generisanu migraciju

### `run_migrations_offline()` vs `run_migrations_online()`

- offline: generise SQL bez stvarne konekcije (koristi se u posebnim scenarijima)
- online: koristi pravi `engine` i konekciju da izvrsi migracije direktno nad bazom

Za standardan rad na razvoju, najcesce koristis online rezim (podrazumevano ponasanje kad pokreces obicne Alembic komande).

---

## 6) Migration fajl - anatomija

Primer stvarne migracije iz kursa:

```python
"""create phone number for user col

Revision ID: aeff25f89db0
Revises:
Create Date: 2023-08-28 19:59:25.616334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'aeff25f89db0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

### revision i down_revision

- `revision`: jedinstveni ID ove migracije
- `down_revision`: ID prethodne migracije (ovde `None` znaci da je ovo prva migracija u lancu)

Ovo pravi lanac (chain) migracija, slicno kao commit istorija u Git-u.

### upgrade()

- sadrzi operacije koje primenjuju promenu
- `op.add_column(...)` dodaje kolonu `phone_number` u tabelu `users`

### downgrade()

- sadrzi operacije koje ponistavaju promenu
- `op.drop_column(...)` uklanja kolonu ako se vratis na prethodnu verziju

---

## 7) Mentalni model: Alembic kao "Git za semu baze"

Analogija:

- Git prati promene u kodu kroz commit-e
- Alembic prati promene u semi baze kroz revizije

Svaka migracija:

- ima svoj "commit" (revision ID)
- zna svog prethodnika (down_revision)
- moze se primeniti unapred (upgrade) ili vratiti unazad (downgrade)

---

## 8) Tipican radni tok (workflow) sa Alembic-om

1. Izmenis model u `models.py` (npr. dodas novo polje)
2. Generises novu migraciju (autogenerate uporedi model sa bazom)
3. Pregledas generisani fajl u `alembic/versions/`
4. Primenis migraciju na bazu (upgrade)
5. Po potrebi, vratis promenu (downgrade) ako nesto ne valja

Konceptualno (bez ulaska u svaku CLI opciju):

```bash
alembic revision --autogenerate -m "create phone number for user col"
alembic upgrade head
```

`head` znaci "najnovija revizija u lancu".

---

## 9) Zasto se autogenerate ne sme slepo verovati

Autogenerate je koristan, ali:

- ne prepoznaje uvek preimenovanja kolona (moze videti "drop + add" umesto "rename")
- ne hvata sve tipove promena (npr. neke promene constraint-a)
- treba uvek rucno pregledati generisani fajl pre primene

Dobra praksa:

1. generisi migraciju
2. procitaj `upgrade()` i `downgrade()`
3. tek onda pokreni `alembic upgrade head`

---

## 10) Odnos Alembic-a i create_all u istom projektu

Cesto pitanje: da li treba i dalje koristiti `create_all()` kad koristis Alembic?

Praksa:

- U projektima sa Alembic-om, `create_all()` se obicno izbegava za "prave" promene seme
- Alembic postaje jedini izvor istine za strukturu baze

Ako mesas oba pristupa nekontrolisano:

- mozes dobiti "rasinhronizaciju" izmedju onoga sto baza stvarno ima i onoga sto Alembic misli da ima

---

## 11) Najcesce greske pocetnika

1. Menjanje modela bez generisanja migracije

- baza ostaje "stara", model u kodu je "nov", nastaje neslaganje

2. Rucno menjanje baze mimo Alembic-a

- npr. rucno dodata kolona kroz SQL, ali bez odgovarajuce migracije
- Alembic tada "ne zna" za tu promenu

3. Ne pregledavanje autogenerated migracije

- moze doci do neocekivanog brisanja kolona ili gubitka podataka

4. Mesanje vise izvora istine za URL baze

- razlicit URL u `alembic.ini` i u aplikaciji moze dovesti do migracija nad pogresnom bazom

5. Zaboravljen `import models` u `env.py`

- bez toga, `target_metadata` ne zna za tvoje tabele, pa autogenerate ne prepoznaje promene

---

## 12) Kako se ovo uklapa sa TodoApp projektom

U referentnom Project 4 vec postoji kompletna Alembic konfiguracija:

- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/aeff25f89db0_create_phone_number_for_user_col.py`

To je primer kako izgleda "vec zavrsen" deo puta. U tvom aktivnom projektu (`fast-api-course-my-work/TodoApp`) ovu temu uvodis tek kada:

- imas stabilne modele
- imas prve podatke u bazi koje ne zelis da izgubis
- prvi put menjas postojecu tabelu (npr. dodajes novo polje)

Do tada je sasvim ispravno koristiti `create_all()` za inicijalno kreiranje tabela.

---

## 13) Samoprovera razumevanja

1. Zasto `create_all()` nije dovoljan kada menjas postojecu tabelu?
2. Sta predstavlja `revision`, a sta `down_revision`?
3. Cemu sluzi `target_metadata = models.Base.metadata` u `env.py`?
4. Zasto treba rucno proveriti autogenerated migraciju pre primene?
5. Sta se desava ako rucno promenis semu baze mimo Alembic-a?

---

## 14) Zakljucak

Alembic resava tacno onaj problem koji `create_all()` ne moze da resi: kontrolisanu, verzionisanu promenu seme baze tokom vremena.

Kljucne ideje za pamcenje:

- migracija = verzionisana promena seme (upgrade/downgrade)
- `env.py` povezuje Alembic sa tvojim SQLAlchemy modelima preko `target_metadata`
- autogenerate je pomoc, ne zamena za pazljivu proveru
- Alembic postaje glavni izvor istine za strukturu baze, ne rucne izmene ili `create_all()`

Ovo je prirodan sledeci korak nakon sto imas stabilan CRUD i osnovne modele, i pre nego sto pocnes da menjas semu baze koja vec sadrzi podatke.
