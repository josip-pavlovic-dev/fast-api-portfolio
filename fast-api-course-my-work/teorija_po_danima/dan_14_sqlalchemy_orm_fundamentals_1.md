# Dan 14: SQLAlchemy ORM Fundamentals 1

## Cilj rada

Vraćamo se na početak SQLAlchemy ORM Fundamentals kursa i prolazimo prvu oblast postepeno. Ovaj dnevni dokument služi kao zajedničko mesto za odgovore na pitanja, kratka objašnjenja i beleške za kasnije ponavljanje.

Teorija pojedinačnih lekcija ostaje u `docs/sqlalchemy_orm_fundamentals/`, a praktični kod se razvija odvojeno u `fast-api-course-my-work/sqlalchemy_orm_fundamentals/`. Kada se koncept savlada, primenjujemo ga i u `TodoApp` projektu.

---

## Dogovor za učenje

- Za svaku lekciju koristimo njen transkript i pripadajući source kao osnovu; razlike i greške source primera označavamo, ne prepravljamo tiho.
- Kurske snapshot fajlove ostavljamo neizmenjene.
- U našem novom SQLAlchemy projektu koristimo SQLAlchemy 2.x stil sa `Mapped[...]` i `mapped_column()`, uz poređenje sa starim `Column` pristupom kada se pojavi u materijalu.
- Za sve projekte koristimo postojeći root `.venv`; ne pravimo zasebno okruženje u kurskom folderu.
- TodoApp se menja paralelno, tek kada je obrađeni koncept dovoljno jasan. Ne menjamo deo projekta koji još nije predmet trenutnog učenja.
- Ovaj dnevni fajl dopunjujemo stvarnim odgovorima i zaključcima tokom rada; teoriju i implementaciju ne dupliramo celu ovde.

---

## Trenutno stanje

- `TodoApp/db/base.py` je modernizovan i sadrži zajedničku SQLAlchemy 2.x `DeclarativeBase` klasu.
- `TodoApp/models.py` je modernizovan na tipizovani `Mapped`/`mapped_column` stil. Tu je trenutno stao praktični rad u TodoApp-u.
- Kreiran je zaseban kostur `fast-api-course-my-work/sqlalchemy_orm_fundamentals/` sa `db/base.py` i `models/` paketom. Njegovi modeli će se dodavati lekciju po lekciju.
- Root `.venv` sadrži SQLAlchemy `2.0.38` i PostgreSQL drajvere proverene tokom prethodnog rada.

---

## Odgovori i beleške

Odgovore na konkretna pitanja iz lekcija i vežbi dodavaćemo ovde po redosledu obrade. U ovom trenutku nisu navedena pitanja za odgovor; gornje stavke beleže radni dogovor i početno stanje, a ne proveru znanja.

---

## Sledeći korak

Početi od prve lekcije prve oblasti i uz svaku obrađenu temu dopunjavati ovaj dnevni dokument, a zatim primeniti savladani deo u radnom SQLAlchemy paketu i, kada je relevantno, u TodoApp-u.

---

## Pitanje 1

PITANJE: Hajde da nastavimo dalje. Kreirao sam `fast-api-course-my-work/sqlalchemy_orm_fundamentals/db/base.py`. Nisam znao da `__init__.py` može sadržati objašnjenje šta folder u kojem je **init**.py predstavlja.

Na redu je `docs/sqlalchemy_orm_fundamentals/01_defining_database_models(tables)/05_defining_the_database_tables_as_models.md`.

Pretpostavljam da modele kreiram u `fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/models.py`?

---

## Odgovor 1

ODGOVOR:

Ne moraš ručno da kopiraš moje odgovore. Ja ću ih direktno unositi u ovaj dnevni fajl kada ih zajedno razjasnimo. Ovde čuvamo odgovore i zaključke za ponavljanje; teorija lekcija ostaje u `docs/`, a izvršivi kod u radnom paketu.

`__init__.py` može da sadrži **module docstring**: kratak opis paketa kojem pripada. Taj tekst služi ljudima i alatima za dokumentovanje. Python ga ne koristi da automatski napravi modele ili strukturu foldera. Fajl može sadržati i `package-level importe` ili `javne izvoze`, ali ćemo to dodavati samo kada nam zatreba.

Za modele `NE` preporučujem putanju `models/models.py`, jer se ime `models` ponavlja: import bi izgledao kao `sqlalchemy_orm_fundamentals.models.models`. Umesto toga ćemo koristiti postojeći `models/` paket i fajlove grupisane po domenu.

Za početak `lekcije 05`, prvu klasu možemo staviti u `models/catalog.py`; u našem paketu to su `Kategorija`, `Proizvod` i `StanjeZaliha` (kursni nazivi: `Category`, `Product` i `StockManagement`). Promocije i porudžbine imaju svoje module sa srpskim imenima modela; kursni nazivi ostaju u snapshot-ima.

Pošto je `SQLAlchemy ORM` modelu potreban primarni ključ (`Primary Key`) da bi se mapirao kao izvršiva klasa, naša praktična `Kategorija` klasa moraće da dobije minimalni `id` ranije nego što ga kurs formalno obrađuje. Označićemo ga kao tehnički preduslov, a lekciju o primarnim ključevima kasnije iskoristiti da ga detaljno obradimo. Kurski prazni modeli ostaju neizmenjeni kao snapshot-i.

---

## Pitanje 2

PITANJE: Kreirao sam prazan `models/category.py`. Napravi `Category` klasu sa minimalnim ID-jem i objasni koje kolone će model imati, zašto su izabranih tipova i šta znače `NULL`, prazan string i `nullable`.

---

## Odgovor 2

ODGOVOR:

Dogovorili smo se da koristimo `models/catalog.py`, pa je prazan `category.py` uklonjen. `models/__init__.py` izvozi modele iz paketa. Za lekciju 05 definisali smo osam klasa sa minimalnim ID-jem: `Kategorija`, `Proizvod` i `StanjeZaliha` u `catalog.py`; `PromotivniDogadjaj` i `VezaProizvodaIPromocije` u `promotions.py`; `Korisnik`, `Porudzbina` i `StavkaPorudzbine` u `orders.py`. Njihove tabele koriste srpska snake_case imena. Kursni snapshot-i ostaju na engleskom; potpuna veza između kursnih i naših imena nalazi se u lekciji 05.

### Zašto model trenutno ima samo `id`

Lekcija 05 uvodi vezu između Python klase i tabele; ne obrađuje još sve kolone. Ipak, ORM klasa koja se mapira na tabelu mora imati primarni ključ da SQLAlchemy može jednoznačno da prepozna svaki red. Zato u praktičnom modelu unapred dodajemo minimalni `id`, a ostatak kolona ćemo dodavati u lekcijama koje ih objašnjavaju.

```python
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

class Kategorija(Base):
	__tablename__ = "kategorija"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		autoincrement=True,
	)
```

- `Kategorija(Base)` čini klasu ORM modelom vezanim za zajednički `Base` i njegov `metadata`. Kursni source isti model naziva `Category` i njegovu tabelu `category`.
- `__tablename__` je eksplicitno ime tabele u bazi.
- `Mapped[int]` označava Python tip atributa za tipizovani SQLAlchemy 2.x ORM.
- `Integer` je tip kolone za celobrojne identifikatore.
- `primary_key=True` označava kolonu kao primarni ključ. Primarni ključ mora biti jedinstven i ne može biti `NULL`; zato ovde ne navodimo dodatne `nullable=False` i `unique=True` opcije.
- `autoincrement=True` traži od baze da generiše naredni celobrojni ID kada se napravi novi red bez eksplicitno zadate vrednosti.

`primary_key=True` i `autoincrement=True` imaju različite uloge: primarni ključ obezbeđuje identitet, jedinstvenost i zabranu `NULL` vrednosti; autoincrement generiše ID kada ga unos ne zada. Autoincrement sam po sebi ne zabranjuje `NULL`, a primarni ključ ne znači da svaka moguća strategija mora automatski generisati vrednost.

Kasnije ćemo detaljno obraditi vrste primarnih ključeva. Ovaj ID dodajemo sada kao tehnički uslov da klasa bude ispravan, izvršiv ORM model; izvorni kurski snapshot ostaje neizmenjen.

### Kolone koje ćemo dodavati po lekcijama

Prema kasnijim modelima u kurskom source-u, `Category` na kraju obuhvata sledeća polja. Ne dodajemo ih sve sada, jer bi to preskočilo plan lekcija.

| Kursna kolona | Planirana kolona kod nas    | Tip                      | Namena                                                                                                                                                                          |
| ------------- | --------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`          | `id`                        | `Integer`                | Primarni identifikator reda. Ovo je jedina kolona koju dodajemo sada da bi model mogao da se mapira.                                                                            |
| `name`        | `naziv`                     | `String(50)`             | Čitljiv naziv kategorije, do 50 karaktera. Biće obavezan i jedinstven prema kasnijem source-u.                                                                                  |
| `slug`        | `slug`                      | `String(55)`             | Tekstualni identifikator koji se koristi u URL-u; do 55 karaktera. Source kasnije traži da bude obavezan, jedinstven i ograničenog formata.                                     |
| `is_active`   | `aktivna`                   | `Boolean`                | Dvostanjski podatak: da li je kategorija aktivna. Source mu daje `False` kao podrazumevanu vrednost.                                                                            |
| `level`       | `nivo`                      | `SmallInteger`           | Ceo broj koji predstavlja nivo kategorije u hijerarhiji; mali integer odgovara malom opsegu nivoa. Source daje početnu vrednost `0`.                                            |
| `category_id` | `roditeljska_kategorija_id` | `Integer` + strani ključ | Veza kategorije ka roditeljskoj kategoriji u istoj tabeli. Dolazi u kasnijoj lekciji o samoreferentnim vezama; tada treba utvrditi da li root kategorija sme da nema roditelja. |

Prva kolona čuva nazive iz kursnog source-a, a druga beleži planirane srpske nazive za naš praktični model; ovo su dogovoreni nazivi za kasnije lekcije, ne kolone koje su već dodate. Tipovi opisuju prirodu vrednosti: naziv i slug su tekst, aktivnost je logička vrednost, nivo i ID su celi brojevi. Ograničenja dužine, obaveznost, podrazumevane vrednosti, jedinstvenost i strani ključevi obrađuju se posebno; tip sam po sebi ih ne zamenjuje.

U kasnijem source-u `category_id` je zamišljen kao strani ključ, ali jedna verzija pogrešno prosleđuje `nullable` u `ForeignKey`, umesto u `mapped_column`/`Column`. Pored toga, pravilo da li je roditeljska kategorija obavezna zavisi od toga da li model podržava root kategorije. Sačekaćemo lekciju o samoreferentnim vezama i tu razrešiti ovu razliku.

---

### `NULL`, `None` i prazan string

To su pojmovi iz različitih slojeva:

- SQL `NULL` u bazi znači da za kolonu nije upisana vrednost ili da je vrednost nepoznata.
- Python `None` je uobičajeni Python prikaz SQL `NULL` vrednosti kada se radi sa ORM-om.
- Prazan string `""` je stvarna tekstualna vrednost dužine nula; nije `NULL`.
- String razmaka, na primer `"   "`, takođe je tekstualna vrednost i nije prazan string.

| Vrednost          | Značenje                         | Da li je SQL `NULL`?                 |
| ----------------- | -------------------------------- | ------------------------------------ |
| `None` u Python-u | Nema vrednosti                   | Da, kada se sačuva u nullable kolonu |
| `""`              | Postoji string, ali nema znakova | Ne                                   |
| `"   "`           | String sadrži tri razmaka        | Ne                                   |
| `"TV"`            | String sadrži tekst              | Ne                                   |

`nullable=False` znači da baza odbija `NULL`. To **ne** znači automatski da odbija `""` ili samo razmake. Na primer, obavezni naziv koji ne sme biti prazan može zahtevati i `nullable=False` i dodatnu validaciju ili `CheckConstraint` koji odbija prazan string. Ako su dozvoljeni stringovi samo od razmaka, pravilo mora izričito da ih proveri ili ukloni razmake pre čuvanja.

U SQL upitima se `NULL` ne proverava pomoću `= NULL`; koristi se `IS NULL` ili `IS NOT NULL`, jer `NULL` nije obična vrednost koja se poredi kao broj ili tekst.

---

### Veza između Python tipa i `nullable`

SQLAlchemy 2.x tipizacija nam omogućava da tip atributa i pravilo nullabilnosti budu saglasni:

- Obavezna tekstualna vrednost: `Mapped[str]` uz `nullable=False`.
- Opciono tekstualno polje koje sme biti `NULL`: `Mapped[str | None]` uz `nullable=True`.
- Obavezni primarni ID: `Mapped[int]` uz `primary_key=True`.

`Mapped[str | None]` samo po sebi ne zabranjuje prazan string. `nullable=True` dopušta `NULL`, ali ne pretvara prazan string u `NULL`.
