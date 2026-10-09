# SQLAlchemy ORM Fundamentals 3 - Unique Constraints, UniqueConstraint, PrimaryKey i ForeignKey

## Pitanje_1:

PITANJE: Nije mi baš jasna uloga `SQLAlchemyja` sada. Ja sam mislio da on preku `unique=True` govori bazi da je unikatna kolona u pitanju ali sada ispada da `unique` ograničenje pripada `bazi`. Molim te mi pojasni mi ovo.

---

## Odgovor_1:

ODGOVOR: `SQLAlchemy` je ORM (Object-Relational Mapper) koji omogućava rad sa bazom podataka koristeći Python objekte. Kada koristimo `unique=True` u definiciji kolone, mi zapravo govorimo `SQLAlchemyju` da generiše odgovarajući SQL kod koji će kreirati `unique` ograničenje u bazi podataka. Dakle, `unique` ograničenje tehnički pripada bazi, ali `SQLAlchemy` nam omogućava da ga definišemo kroz Python kod, što olakšava rad i održavanje modela.

### Detaljno objašnjenje:

Razumem zašto deluje kontradiktorno. Precizno rečeno: **`unique=True` pišemo u SQLAlchemy modelu, a SQLAlchemy na osnovu toga napravi UNIQUE ograničenje u bazi. Zatim sama baza sprovodi to pravilo.**

Tok izgleda ovako:

1. U modelu napišeš:

   ```python
   naziv: Mapped[str] = mapped_column(String(50), unique=True)
   ```

2. SQLAlchemy zabeleži to pravilo u metapodacima modela i, kada kreira šemu preko `Base.metadata.create_all(engine)`, prevede ga u `SQL upite` uz pomoć dijalekta (npr. PostgreSQL, SQLite) koji je definisan u `engine`-u i koji baza razume. Pojednostavljeno, baza dobije nešto poput:

   ```sql
   CREATE TABLE kategorija (
       naziv VARCHAR(50) UNIQUE
   );
   ```

3. Kada aplikacija pokuša da sačuva dupliran naziv, **baza odbije upis**. SQLAlchemy prenese grešku aplikaciji, obično kao `IntegrityError`.

Dakle, `unique=True` u SQLAlchemy modelu nije Python provera koja sama pregleda svaki unos i odbija duplikate. To je način na koji **deklaršeš pravilo u modelu kroz SQLAlchemy**, da bi to pravilo pri kreiranju šeme postalo **ograničenje koje čuva baza**. Zato ograničenje i dalje važi ako neko upisuje podatke direktnim `SQL`-om ili iz druge aplikacije.

Važna napomena: ako tabela već postoji, samo dodavanje `unique=True` u model ne menja automatski postojeću bazu. Potrebna je migracija koja će tamo dodati ograničenje.

---

## Pitanje_2:

PITANJE: Zar nismo rekli da ograničenja preko SQLAlchemy-ja ne važe ako se zaobiđe SQLAlchemy način generisanja upita za SQL bazu i koristi se upis podataka preko SQLite Terminala itd?

---

## Odgovor_2:

ODGOVOR: Nije tačno da ograničenja preko SQLAlchemy-ja ne važe ako se zaobiđe SQLAlchemy način generisanja upita. Kada definišeš `unique=True` u SQLAlchemy modelu i kreiraš šemu, SQLAlchemy generiše odgovarajuće SQL ograničenje u bazi. To ograničenje važi bez obzira na to kako se podaci upisuju u bazu, bilo preko `SQLAlchemy`-ja, direktnog `SQL`-a ili `drugog alata`.

Dakle, ako neko pokuša da unese duplikat direktno preko SQLite Terminala, baza će odbiti upis zbog `UNIQUE` ograničenja. Stoga, ograničenja definisana u SQLAlchemy modelu preko `unique=True` su zapravo ograničenja baze podataka i važe u svim slučajevima.

Sa druge strane, ako tabela već postoji i nema `UNIQUE` ograničenja, samo dodavanje `unique=True` u model neće automatski promeniti postojeću bazu; potrebna je migracija. Ako ponovo kreiraš šemu sa `Base.metadata.create_all(engine)` nakon dodavanja `unique=True`, obrisaće se postojeće tabele i kreiraće nove sa odgovarajućim ograničenjima. Svi podaci iz baze će biti izgubljeni! Zbog toga se preporučuje koristiti migracije za promene u šemi baze podataka.

### Detaljno objašnjenje:

Ne baš. Razlika je između **zaobilaženja SQLAlchemy-ja** i **zaobilaženja ograničenja koje je već upisano u šemu baze** sa akcentom na **stvarna ograničenja u bazi podataka**.

`unique=True` u modelu je instrukcija `SQLAlchemy`-ju da, pri `kreiranju` ili `migraciji šeme`, napravi `UNIQUE` ograničenje u bazi. Kada je to ograničenje zaista prisutno u SQLite bazi i SQLite ga sprovodi bez obzira na to da li se upis radi kroz `ORM`, `direktan SQL` ili `SQLite Terminal`. Direktan upis ne zaobilazi ograničenje baze!

Ali ako je `unique=True` dodat samo u Python model, a postojeća baza nije ažurirana preko `Base.metadata.create_all(engine)` ili `Alembic`-a, SQLite Terminal ne zna ništa o toj izmeni. Tada direktan upis može napraviti duplikat, jer ograničenje još ne postoji u bazi. Isti slučaj važi ako terminal otvori drugi SQLite fajl umesto fajla koji koristi aplikacija.

Dakle:

- **ORM provera ili aplikaciona logika** može se zaobići direktnim SQL-om.
- **UNIQUE ograničenje u stvarnoj šemi baze** ne može se zaobići običnim direktnim upisom; baza će ga sprovesti.

Rečenica u belešci je tačna uz taj uslov. Preciznije bi glasila: „Zato UNIQUE ograničenje, **ako je kreirano u šemi baze**, i dalje važi pri direktnom SQL upisu ili upisu iz druge aplikacije.“

---

## Lekcija 14: Ponašanje pri brisanju referenciranog reda

### Cilj

Ovaj deo beleži kako lekciju 14 iz kurskog source-a prevodimo na praktični
projekat `fast-api-course-my-work/sqlalchemy_orm_fundamentals`. Kurski source
ostaje referenca za nameru lekcije; ne kopiramo njegov stariji `Column` kod
direktno u naše SQLAlchemy 2.x modele.

U kurskom source-u nameravana akcija je `RESTRICT` za tri FK veze:

1. roditeljska kategorija – potkategorija;
2. kategorija – proizvod;
3. korisnik – porudžbina.

U projektu su odgovarajući FK atributi `Kategorija.roditelj_id`,
`Proizvod.kategorija_id` i `Porudzbina.korisnik_id`. Četiri FK-a u
`StavkaPorudzbine` i `VezaProizvodaIPromocije` ostaju van obuhvata ove lekcije
i ne menjaju se.

---

### Korak 1: proveri početno stanje

1. Iz root-a repozitorijuma proveri `git status`; ne prepisuj postojeće izmene.
2. Otvori projektne modele `models/catalog.py` i `models/orders.py`.
3. Potvrdi da je `Kategorija.roditelj_id` nullable kako bi korenska kategorija
   mogla da ima `None`.
4. Ne menjaj course snapshot
   `docs/sqlalchemy_orm_fundamentals/01_defining_database_models(tables)/source_code/Models/11_on_delete.py`.

---

### Korak 2: razumi nameravano pravilo

`RESTRICT` znači da baza odbija brisanje roditelja dok postoji red koji ga
referencira:

| Roditelj koji pokušavamo da obrišemo | Postojeći zavisni red | Očekivanje           |
| ------------------------------------ | --------------------- | -------------------- |
| kategorija                           | potkategorija         | brisanje je odbijeno |
| kategorija                           | proizvod              | brisanje je odbijeno |
| korisnik                             | porudžbina            | brisanje je odbijeno |

To ne znači da se dete automatski briše. `CASCADE` bi bilo drugačije pravilo i
moglo bi da ukloni čitavo podstablo ili povezane podatke. U ovom projektu
biramo `RESTRICT` da bismo sačuvali zavisne redove i istoriju.

---

### Korak 3: dodaj `ondelete` u `catalog.py`

`ondelete` pripada `ForeignKey(...)`; `nullable` ostaje argument
`mapped_column(...)`. U postojećem `Kategorija.roditelj_id` dodaj
`ondelete="RESTRICT"` i sačuvaj `nullable=True`:

```python
# Lekcija 14: baza odbija brisanje kategorije dok postoje potkategorije.
roditelj_id: Mapped[int | None] = mapped_column(
    ForeignKey("kategorija.id", ondelete="RESTRICT"),
    nullable=True,
)
```

Na `Proizvod.kategorija_id` dodaj isto pravilo, ali zadrži obaveznost postojeće
veze:

```python
# Lekcija 14: kategorija koju koriste proizvodi ne može da se obriše.
kategorija_id: Mapped[int] = mapped_column(
    ForeignKey("kategorija.id", ondelete="RESTRICT"),
    nullable=False,
)
```

`roditelj_id` i dalje dozvoljava `NULL` za koren. `kategorija_id` i dalje
zahteva kategoriju za svaki proizvod. Lekcija 14 menja ponašanje pri brisanju,
ne kardinalnost ili nullable pravila.

### Korak 4: prepusti ORM brisanje bazi

`ForeignKey(ondelete="RESTRICT")` opisuje ponašanje baze, ali ORM može tokom
`Session.delete(parent)` prvo da pokuša da postavi povezane FK vrednosti na
`NULL`. To je posebno važno za `Kategorija.roditelj_id`: pošto je nullable,
bez dodatnog podešavanja ORM bi mogao da odvoji potkategoriju od roditelja i
zatim obriše roditelja. Tada baza ne bi dobila `DELETE` dok FK još
referencira roditelja.

Na roditeljskoj kolekciji `Kategorija.deca` dodaj `passive_deletes="all"`:

```python
# Lekcija 14: ORM ne poništava roditeljski FK pre provere u bazi.
deca: Mapped[list[Kategorija]] = relationship(
    back_populates="roditelj",
    passive_deletes="all",
)
```

Dodaj isto podešavanje na `Kategorija.proizvodi` i
`Korisnik.porudzbine`, jer su i to roditeljske kolekcije za ova pravila:

```python
# Lekcija 14: ORM prepušta proveru kategorije sa proizvodima bazi.
proizvodi: Mapped[list[Proizvod]] = relationship(
    back_populates="kategorija",
    passive_deletes="all",
)

# Lekcija 14: ORM prepušta proveru korisnika sa porudžbinama bazi.
porudzbine: Mapped[list[Porudzbina]] = relationship(
    back_populates="korisnik",
    passive_deletes="all",
)
```

`passive_deletes="all"` nije `CASCADE` i ne briše zavisne objekte. Ono
sprečava ORM da menja FK pre nego što baza proveri `RESTRICT`. Ne kombinujemo
ga sa ORM `delete` ili `delete-orphan` cascade pravilima. Ovaj dodatak je
potreban da izabrano ponašanje bude isto i pri `Session.delete()`, a ne samo
pri direktnom SQL `DELETE` iskazu.

### Korak 5: dodaj `ondelete` u `orders.py`

Na `Porudzbina.korisnik_id` postavi `RESTRICT` na FK, a `nullable=False`
ostavi na koloni:

```python
# Lekcija 14: korisnik sa porudžbinama ne može da se obriše.
korisnik_id: Mapped[int] = mapped_column(
    ForeignKey("korisnik.id", ondelete="RESTRICT"),
    nullable=False,
)
```

Odgovarajući `passive_deletes="all"` već je dodat na
`Korisnik.porudzbine`. Ne menjaj `StavkaPorudzbine` ili
`VezaProizvodaIPromocije`: njihovi FK-ovi nisu među vezama koje kurski source
menja u ovoj lekciji.

### Korak 6: proveri mapiranje

Iz root-a repozitorijuma proveri da svi modeli i `back_populates` atributi mogu
da se konfigurišu:

```bash
PYTHONPATH=fast-api-course-my-work .venv/bin/python -c "from sqlalchemy.orm import configure_mappers; from sqlalchemy_orm_fundamentals import models; configure_mappers(); print('Mapperi su ispravni')"
```

Ova provera ne kreira bazu i ne testira `ON DELETE`; ona samo proverava ORM
mapiranje.

### Korak 7: testiraj pravilo samo u privremenoj SQLite bazi

Paket još nema stalni engine ni session modul. Za ponašanje baze koristi novu
memorijsku bazu, uključi FK enforcement pre konekcije i kreiraj tabele iz
`Base.metadata`:

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import configure_mappers

from sqlalchemy_orm_fundamentals.db.base import Base
from sqlalchemy_orm_fundamentals import models

engine = create_engine("sqlite://")


@event.listens_for(engine, "connect")
def ukljuci_fk_enforcement(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


configure_mappers()
Base.metadata.create_all(engine)
```

Zatim, kroz `Session`, napravi tri odvojena slučaja i proveri da
`session.delete(parent)` pa `session.flush()` izazove `IntegrityError`:

1. kategorija koja ima potkategoriju;
2. kategorija koju koristi proizvod;
3. korisnik koji ima porudžbinu.

Posle svakog očekivanog `IntegrityError` pozovi `session.rollback()` pre
naredne provere. Proveri i da kategorija bez dece/proizvoda može da se obriše.
Direktan SQL `DELETE` nad roditeljskim redom treba da bude odbijen istim
ograničenjem baze.

Bez `PRAGMA foreign_keys=ON`, SQLite test ne dokazuje da se FK akcija sprovodi.
Ne koristi postojeću bazu i ne pokreći `drop_all()` radi ove provere.

### Korak 8: osveži prateću dokumentaciju

1. U `docs/sqlalchemy_orm_fundamentals/01_defining_database_models(tables)/14_on_delete_behaviour.md`
   zabeleži tri projektne veze, razliku `ondelete`/ORM cascade i razlog za
   `passive_deletes="all"`.
2. U projektnom `README.md` zabeleži implementaciju lekcije 14 i eksplicitno
   navedi da asocijativni FK-ovi ostaju nepromenjeni.
3. U `ERD_project_1.drawio` označi `ON DELETE RESTRICT` na tri FK-a i ažuriraj
   napomenu o obuhvatu.
4. Zadrži kratke komentare `Lekcija 14` direktno uz svaku izmenu u Python
   modelima.

### Šta ne treba da se kopira direktno iz kurskog source-a

Kurski source koristi stariji `Column(...)` stil i u snapshot-u ima greške:

- `nullable=False` je prosleđen `ForeignKey(...)`, iako pripada koloni;
- `ondelete="RESTRICT"` je na nekim mestima prosleđen `Column(...)`, iako
  pripada `ForeignKey(...)`;
- samoreferentni FK kategorije je označen kao `nullable=False`, što ne dozvoljava
  korensku kategoriju.

U projektu koristimo ispravan raspored argumenata u `mapped_column()` i čuvamo
već implementirano pravilo `roditelj_id: nullable=True`.

### Završna provera

- [ ] `configure_mappers()` prolazi.
- [ ] Postoje tačno tri nova `ondelete="RESTRICT"` podešavanja.
- [ ] `Kategorija.deca`, `Kategorija.proizvodi` i `Korisnik.porudzbine` imaju
      `passive_deletes="all"`.
- [ ] Korenska kategorija i dalje može da ima `roditelj_id=None`.
- [ ] Sve tri ORM probe brisanja padaju sa `IntegrityError`, a prazna kategorija
      može da se obriše.
- [ ] SQLite FK enforcement je uključen samo u memorijskoj testnoj bazi.
- [ ] Course snapshot-i nisu menjani.

---
