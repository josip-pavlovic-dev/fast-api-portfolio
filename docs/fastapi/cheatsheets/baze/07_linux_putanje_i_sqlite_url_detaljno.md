# Linux putanje u Bash-u i SQLite URL u SQLAlchemy-ju

Ovaj vodič razjašnjava razliku između Linux putanje kao što je `./todosapp.db` i SQLAlchemy URL-a kao što je `sqlite:///./todosapp.db`.

Primer koji ćemo pratiti nalazi se u [`Project_3/db/database.py`](../../../../fast-api-course-my-work/Project_3/db/database.py):

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

Najvažnije za početak:

- `./` znači trenutni direktorijum.
- `../` znači roditeljski direktorijum.
- `././` i dalje znači isti trenutni direktorijum, a ne roditeljski.
- U ovom primeru `./todosapp.db` se razrešava prema trenutnom radnom direktorijumu (`cwd`), a ne prema folderu u kom se nalazi `database.py`.
- Broj kosih crta u `sqlite:///...` tumači SQLAlchemy-jev SQLite URL format; to nije ista sintaksa kao Bash komanda `cd`.

U praksi, kada koristiš SQLite sa SQLAlchemy-jem, važno je razumeti da `sqlite:///./todosapp.db` znači: "koristi SQLite bazu koja se nalazi u fajlu `todosapp.db` u trenutnom radnom direktorijumu". Trenutni radni direktorijum (`cwd`) je direktorijum iz kojeg pokrećeš Python proces, a ne direktorijum u kojem se nalazi `database.py`. Ovo je čest izvor zabune, jer mnogi očekuju da će relativna putanja biti u odnosu na lokaciju fajla `database.py`, ali SQLAlchemy koristi `cwd` kao referencu za relativne putanje.

## 1. Linux filesystem: root, apsolutne i relativne putanje

Linux filesystem kreće od jednog početnog direktorijuma koji se zove **root**. Njegov zapis je jedna kosa crta:

```text
/
```

Primer apsolutne putanje:

```text
/home/alex/projects/my-api
```

Ona počinje sa `/`, pa opisuje lokaciju od root-a. Ne zavisi od toga u kom direktorijumu se trenutno nalaziš.

Relativna putanja ne počinje sa `/`. Ona se računa u odnosu na trenutni radni direktorijum. U Bash-u trenutni radni direktorijum vidiš komandom:

```bash
pwd
```

Na primer, ako je rezultat:

```text
/home/alex/projects/my-api
```

onda se relativne putanje računaju od `/home/alex/projects/my-api`.

---

## 2. Šta znače `.`, `..`, `./` i `../`

| Zapis    | Značenje                                             | Primer ako je `pwd` `/home/alex/projects/my-api`            |
| -------- | ---------------------------------------------------- | ----------------------------------------------------------- |
| `.`      | trenutni direktorijum                                | `/home/alex/projects/my-api`                                |
| `./`     | putanja koja počinje u trenutnom direktorijumu       | `./todosapp.db` je `/home/alex/projects/my-api/todosapp.db` |
| `..`     | roditeljski direktorijum, jedan nivo iznad           | `/home/alex/projects`                                       |
| `../`    | putanja koja počinje u roditeljskom direktorijumu    | `../todosapp.db` je `/home/alex/projects/todosapp.db`       |
| `././`   | trenutni direktorijum, pa opet trenutni direktorijum | isto kao `./`                                               |
| `../../` | dva nivoa iznad trenutnog direktorijuma              | `/home/alex`                                                |

Dakle:

```text
././todosapp.db
```

znači isto što i:

```text
./todosapp.db
```

Za kretanje jedan nivo nagore koristi se `..`, a ne `./.`:

```bash
cd ..
```

Tačke su specijalne komponente putanje. Kose crte `/` samo razdvajaju komponente putanje.

---

## 3. Kako da vidiš gde putanja vodi

Pretpostavimo da je trenutni direktorijum `/home/alex/projects/my-api`.

```bash
pwd
realpath -m ./todosapp.db
realpath -m ../todosapp.db
realpath -m ././todosapp.db
```

Očekivani rezultati putanja su:

```text
/home/alex/projects/my-api
/home/alex/projects/my-api/todosapp.db
/home/alex/projects/todosapp.db
/home/alex/projects/my-api/todosapp.db
```

Opcija `-m` dozvoljava `realpath` komandi da prikaže putanju i kada fajl još ne postoji. Za pregled trenutnog direktorijuma možeš koristiti i:

```bash
ls -la
```

---

## 4. Apsolutna putanja u Linux-u

Apsolutna Linux putanja počinje od `/`. Na primer:

```text
/home/alex/data/todosapp.db
```

Ona ne znači „od trenutnog direktorijuma“. Uvek počinje od filesystem root-a.

Razlikuj ove primere:

```text
./data/todosapp.db       relativno: data/ je ispod trenutnog direktorijuma
../data/todosapp.db      relativno: kreni u roditeljski direktorijum, pa u data/
/home/alex/data/db.db    apsolutno: kreni od root-a
```

`~` je Bash prečica za tvoj home direktorijum, najčešće `/home/<korisnik>`. Shell je taj koji je proširuje:

```bash
cd ~/projects/my-api
```

Nemoj pretpostaviti da će svaki program automatski obraditi `~` u proizvoljnom tekstu ili konfiguracionom URL-u. Za SQLAlchemy putanju je jasnije koristiti apsolutnu putanju ili je napraviti u Python-u.

---

## 5. SQLite putanja nije Bash komanda

Ovaj string nije komanda za Bash:

```text
sqlite:///./todosapp.db
```

To je **URL koji SQLAlchemy parsira**. Njegov početak kaže koji database dialect da koristi, a ostatak daje SQLite fajl.

Za SQLite, uobičajeni oblici su:

```text
sqlite:///relative/path.db
sqlite:////absolute/path.db
```

### Relativna putanja

```text
sqlite:///./todosapp.db
```

SQLAlchemy SQLite format sa tri kose crte koristi se za relativnu putanju. Deo `./todosapp.db` kaže da je fajl u trenutnom radnom direktorijumu.

`./` može da se izostavi:

```text
sqlite:///todosapp.db
```

I ovaj zapis je relativan, pa se fajl i dalje traži u trenutnom radnom direktorijumu.

---

### Apsolutna putanja

```text
sqlite:////home/alex/data/todosapp.db
```

Posle `sqlite:` ovde se pojavljuju četiri kose crte: SQLAlchemy SQLite URL zapis koristi `sqlite:///` kao početni oblik, a apsolutna Linux putanja zatim počinje svojom kosom crtom (`/home/...`).

**Četiri kose crte su deo URL zapisa za SQLAlchemy.** Ne znače četiri direktorijuma i nisu instrukcija Bash-u da se pomeri četiri nivoa. Putanju na kraju parsira SQLAlchemy/SQLite, a ne `cd`.

U Bash-u se putanja piše bez SQLAlchemy prefiksa:

```bash
ls -l /home/alex/data/todosapp.db
```

U Bash-u možeš napisati i `////home/alex/data/todosapp.db`; to i dalje nije kretanje četiri direktorijuma nagore. To je putanja koja počinje sa kosim crtama, a na Linux-u se višestruke kose crte na početku uglavnom ponašaju kao jedna. Ipak, u Bash-u koristi uobičajen i jasan zapis sa jednom početnom crtom: `/home/alex/data/todosapp.db`.

U SQLAlchemy URL-u ista lokacija ima oblik:

```text
sqlite:////home/alex/data/todosapp.db
```

Nemoj mešati dva pravila:

- `../` u filesystem putanji znači „idi u roditeljski direktorijum“.
- `sqlite:////...` je zapis apsolutne SQLite putanje u SQLAlchemy URL-u.

## 6. Šta tačno znači URL iz projekta

URL iz [`database.py`](../../../../fast-api-course-my-work/Project_3/db/database.py):

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

možeš pročitati ovako:

1. `sqlite` — koristi se SQLite.
2. `///` — koristi se SQLAlchemy-jev oblik za SQLite URL.
3. `./todosapp.db` — fajl baze je relativan u odnosu na trenutni radni direktorijum.
4. `todosapp.db` — ime fajla baze. Ovo nije ime tabele.

Lokacija fajla zavisi od toga odakle je aplikacija pokrenuta:

| `pwd` pri pokretanju               | Lokacija koju cilja URL                        |
| ---------------------------------- | ---------------------------------------------- |
| `/home/alex/projects/Project_3`    | `/home/alex/projects/Project_3/todosapp.db`    |
| `/home/alex/projects/Project_3/db` | `/home/alex/projects/Project_3/db/todosapp.db` |
| `/home/alex/projects`              | `/home/alex/projects/todosapp.db`              |

Python fajl u kom je URL definisan ne određuje automatski lokaciju baze. Ako se aplikacija pokrene iz drugog direktorijuma, isti URL može ciljati drugi `todosapp.db`.

---

## 7. Kada se SQLite fajl napravi

Ova linija samo dodeljuje string promenljivoj:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

Zatim se URL prosleđuje SQLAlchemy engine-u:

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
```

Samo kreiranje engine-a je uglavnom lenjo: stvarna konekcija se uspostavlja kada aplikacija prvi put obavi operaciju koja zahteva bazu. SQLite tada može napraviti fajl baze ako ne postoji. `check_same_thread=False` je zasebna SQLite opcija i ne menja putanju do fajla.

---

## 8. Kako da namerno izabereš lokaciju

### Opcija A: relativno, u odnosu na folder iz kog pokrećeš aplikaciju

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

Ovo je jednostavno za vežbe, ali pazi na `pwd`:

```bash
pwd
```

Pokreći aplikaciju dosledno iz istog direktorijuma ako želiš da uvek koristi isti fajl baze.

---

### Opcija B: apsolutna putanja direktno u URL-u

```python
SQLALCHEMY_DATABASE_URL = "sqlite:////home/alex/projects/Project_3/todosapp.db"
```

Ovo ne zavisi od trenutnog radnog direktorijuma, ali je putanja vezana za konkretnu mašinu i lokaciju projekta.

---

### Opcija C: napravi putanju u Python-u

Ako želiš putanju zasnovanu na lokaciji Python fajla, možeš je izračunati eksplicitno. Primer ispod stavlja bazu pored `database.py`:

```python
from pathlib import Path

from sqlalchemy import URL, create_engine

DATABASE_PATH = Path(__file__).resolve().with_name("todosapp.db")
database_url = URL.create("sqlite", database=str(DATABASE_PATH))
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False},
)
```

Ovde `Path(__file__).resolve()` kreće od lokacije samog Python fajla, a `URL.create(...)` napravi SQLAlchemy URL bez ručnog brojanja kosih crta. Ovo je drugačije ponašanje od relativnog `./todosapp.db`; nemoj ga uvoditi u projekat dok ne odlučiš da želiš takvu promenu.

---

## 9. Česte zabune

### „`./` znači trenutni folder, pa `././` mora značiti roditeljski.“

Ne. Svaki `.` označava trenutni direktorijum. Dva uzastopna `.` segmenta ne pomeraju putanju nagore. Roditeljski direktorijum označava se sa `..`.

---

### „Baza će biti pored `database.py`.“

Ne nužno. `./todosapp.db` je relativan prema trenutnom radnom direktorijumu procesa, a ne prema lokaciji `database.py`.

---

### „Četiri kose crte znače da idem četiri foldera naviše.“

Ne u ovom kontekstu. `////` se ovde pojavljuje unutar SQLAlchemy SQLite URL-a kao zapis apsolutne putanje. Za kretanje kroz direktorijume koristi `..` u filesystem putanji.

---

### „Ime URL-a kaže koja će tabela biti napravljena.“

Ne. `todosapp.db` je fajl baze. Tabele nastaju iz modela tek kada aplikacija izvrši odgovarajući SQLAlchemy kod, na primer `Base.metadata.create_all(...)`.

---

## 10. Kratka vežba

Pretpostavi da `pwd` prikazuje:

```text
/home/alex/Project_3
```

Odredi lokaciju svakog fajla:

```text
./todosapp.db
../todosapp.db
././todosapp.db
```

Odgovori:

```text
/home/alex/Project_3/todosapp.db
/home/alex/todosapp.db
/home/alex/Project_3/todosapp.db
```

Za SQLAlchemy URL:

```text
sqlite:////home/alex/Project_3/todosapp.db
```

Putanja do baze je apsolutna, pa promena `pwd` ne menja ciljni fajl.

---

## Zapamti

```text
./       trenutni direktorijum
../      roditeljski direktorijum
/home/…  apsolutna Linux putanja
sqlite:///./file.db     relativni SQLite URL
sqlite:////home/…/file.db  apsolutni SQLite URL
```

Kad nisi siguran koji fajl koristi aplikacija, prvo proveri `pwd`, a zatim razreši relativnu putanju u odnosu na taj direktorijum.
