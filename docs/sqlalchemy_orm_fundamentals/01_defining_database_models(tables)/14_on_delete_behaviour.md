# Lekcija 14: Ponašanje pri brisanju referenciranog reda

## Cilj lekcije

Kada red u roditeljskoj tabeli referencira strani ključ u drugoj tabeli, baza mora da zna šta da uradi ako neko pokuša da obriše roditeljski red. SQLAlchemy prosleđuje ovo pravilo bazi kroz `ondelete` na `ForeignKey(...)`.

Primer je kategorija koju koriste proizvodi. Ako kategoriju referencira sto proizvoda, brisanje kategorije ne sme slučajno da ostavi nevažeće reference ili da obriše podatke bez namere. Izabrana akcija treba da prati poslovna pravila i politiku čuvanja podataka.

---

## Gde se navodi `ondelete`

Opcija pripada konstruktoru `ForeignKey`, jer je deo FK ograničenja u šemi baze:

```python
kategorija_id: Mapped[int] = mapped_column(
    ForeignKey("kategorija.id", ondelete="RESTRICT"),
    nullable=False,
)
```

Ovde:

- `ForeignKey("kategorija.id", ...)` definiše koju vrednost red referencira i
  ponašanje FK ograničenja;
- `ondelete="RESTRICT"` zadaje reakciju baze na brisanje referenciranog reda;
- `nullable=False` je zasebno pravilo kolone koje ne dozvoljava `NULL`.

`ondelete` ne briše redove sam SQLAlchemy ORM kodom. SQLAlchemy uključuje odgovarajuću klauzulu u DDL-u, a DBMS je sprovodi kada se izvrši brisanje.

---

## Moguće akcije

### `CASCADE`

```python
ForeignKey("kategorija.id", ondelete="CASCADE")
```

Brisanje roditeljskog reda automatski briše redove koji ga referenciraju.
Brisanje kategorije bi, na primer, obrisalo i sve povezane proizvode. Za
samoreferentnu vezu kategorija–potkategorija, `CASCADE` može ukloniti i celo
podstablo. Ovo može biti prikladno za zavisne podatke koji nemaju smisla bez
roditelja, ali nosi rizik velikog i nepovratnog gubitka podataka. Koristiti ga
samo kada je takvo ponašanje namerno.

### `SET NULL`

```python
roditelj_id: Mapped[int | None] = mapped_column(
    ForeignKey("kategorija.id", ondelete="SET NULL"),
    nullable=True,
)
```

Baza zadržava zavisni red, ali postavlja njegov FK na `NULL`. U našem modelu
bi to na `roditelj_id` značilo da potkategorija postaje korenska kategorija.
FK kolona zato mora dozvoljavati `NULL`. Ovo ne radi sa `nullable=False`, kao
što su `Proizvod.kategorija_id` i `Porudzbina.korisnik_id`.

### `SET DEFAULT`

```python
from sqlalchemy import text

kategorija_id: Mapped[int] = mapped_column(
    ForeignKey("kategorija.id", ondelete="SET DEFAULT"),
    nullable=False,
    server_default=text("1"),
)
```

Baza zadržava zavisni red i postavlja FK kolonu na njen **serverski default**.
Ta vrednost i dalje mora da referencira postojeći red roditeljske tabele; u
primeru bi kategorija sa ID-jem `1` morala postojati. Ako ne postoji, brisanje
roditelja može pasti zbog FK ograničenja.

Python/SQLAlchemy `default=...` nije dovoljan za `ON DELETE SET DEFAULT`: ovu akciju izvršava baza, pa podrazumevana vrednost mora biti definisana u samoj šemi baze. Podršku i tačno ponašanje treba proveriti u dokumentaciji ciljnog DBMS-a.

---

### `RESTRICT`

```python
ForeignKey("kategorija.id", ondelete="RESTRICT")
```

Zabranjuje brisanje roditeljskog reda dok postoje zavisni redovi. Kategorija
sa potkategorijama ili proizvodima ne može da se obriše; korisnik sa
porudžbinama takođe ne može da se obriše. To je nameravana akcija kurskog
source koda za tri FK-a i izbor koji prenosimo na odgovarajuće veze u projektu.

---

### `NO ACTION`

```python
ForeignKey("kategorija.id", ondelete="NO ACTION")
```

Ovo je uobičajena podrazumevana FK akcija kada se ne navede drugačije, ali ne treba se oslanjati na pretpostavke umesto provere baze. Slično je `RESTRICT` jer ne dopušta da na kraju ostanu nevažeće reference. U nekim sistemima razlika je u trenutku provere: `NO ACTION` može dozvoliti odloženu proveru do kraja naredbe ili transakcije kada je ograničenje definisano kao deferrable, dok `RESTRICT` tipično blokira odmah. Detalji su specifični za DBMS.

---

## Ponašanje iz source koda

Kursni source fajl namerava da koristi `RESTRICT` za:

| FK kolona              | Referencirani ključ | Očekivani efekat                                                 |
| ---------------------- | ------------------- | ---------------------------------------------------------------- |
| `Category.category_id` | `Category.id`       | ne može se obrisati roditeljska kategorija dok ima potkategorije |
| `Product.category_id`  | `Category.id`       | ne može se obrisati kategorija dok je koriste proizvodi          |
| `Order.user_id`        | `User.id`           | ne može se obrisati korisnik dok ima porudžbine                  |

To čuva redove i sprečava slučajno brisanje istorije. Source kod takođe predlaže soft delete: umesto uklanjanja kategorije iz baze, postaviti `is_active=False` i isključiti je iz uobičajenih upita. Soft delete je `UPDATE`, ne `DELETE`, pa `ondelete` akcija se tada ne aktivira.

### Prevod na modele našeg projekta

U mini projektu ista namera odnosi se na sledeće tri veze:

| FK kolona projekta       | Referencirani ključ | Akcija     | Rezultat                                                                                                       |
| ------------------------ | ------------------- | ---------- | -------------------------------------------------------------------------------------------------------------- |
| `Kategorija.roditelj_id` | `kategorija.id`     | `RESTRICT` | Kategorija sa potkategorijama ne može da se obriše; korenska kategorija i dalje sme da ima `roditelj_id=None`. |
| `Proizvod.kategorija_id` | `kategorija.id`     | `RESTRICT` | Kategorija koju koriste proizvodi ne može da se obriše.                                                        |
| `Porudzbina.korisnik_id` | `korisnik.id`       | `RESTRICT` | Korisnik koji ima porudžbine ne može da se obriše.                                                             |

Ostale četiri projektne FK kolone (`StavkaPorudzbine.porudzbina_id`, `StavkaPorudzbine.proizvod_id`, `VezaProizvodaIPromocije.proizvod_id` i `VezaProizvodaIPromocije.promotivni_dogadjaj_id`) ne menjamo u ovoj lekciji. One ostaju bez eksplicitnog `ondelete`; ne zaključujemo da ih treba brisati kaskadno samo zato što pripadaju veznim modelima.

U SQLAlchemy 2.x projektu promena na kategoriji izgleda ovako:

```python
# catalog.py
# Lekcija 14: brisanje kategorije sa potkategorijama odbija baza.
roditelj_id: Mapped[int | None] = mapped_column(
    ForeignKey("kategorija.id", ondelete="RESTRICT"),
    nullable=True,
)

# Lekcija 14: ORM ne poništava roditeljski FK pre provere u bazi.
deca: Mapped[list[Kategorija]] = relationship(
    back_populates="roditelj",
    passive_deletes="all",
)

# Lekcija 14: kategorija sa proizvodima ne može da se obriše.
kategorija_id: Mapped[int] = mapped_column(
    ForeignKey("kategorija.id", ondelete="RESTRICT"),
    nullable=False,
)

# Lekcija 14: ORM prepušta proveru kategorije sa proizvodima bazi.
proizvodi: Mapped[list[Proizvod]] = relationship(
    back_populates="kategorija",
    passive_deletes="all",
)
```

Za korisnika i porudžbinu, ista promena se pravi u `orders.py`:

```python
# Lekcija 14: ORM prepušta bazi proveru korisnika sa porudžbinama.
porudzbine: Mapped[list[Porudzbina]] = relationship(
    back_populates="korisnik",
    passive_deletes="all",
)

# Lekcija 14: korisnik sa porudžbinama ne može da se obriše.
korisnik_id: Mapped[int] = mapped_column(
    ForeignKey("korisnik.id", ondelete="RESTRICT"),
    nullable=False,
)
```

`nullable=True` za `roditelj_id` i `nullable=False` za FK proizvoda i porudžbine
ostaju ista pravila kao pre lekcije 14. Menjamo politiku brisanja, ne
opcionalnost tih veza.

---

## Greške u deklaracijama priloženog source fajla

Pokretanje source-a u zajedničkom SQLAlchemy 2.0 okruženju pada prilikom deklarisanja `Category`, pre mapiranja modela. Uočene su dve vrste pogrešnog položaja argumenata:

```python
# U Category: nullable je prosleđen ForeignKey-u, gde ne pripada
ForeignKey("category.id", nullable=False, ondelete="RESTRICT")

# U Product i Order: ondelete je prosleđen Column-u, gde ne pripada
Column(ForeignKey("category.id"), nullable=False, ondelete="RESTRICT")
```

`ondelete` treba da bude na `ForeignKey`, a `nullable` na `Column`. SQLAlchemy je prijavio `TypeError` za argument `nullable` na `ForeignKey`. Ispravno postavljanje FK opcije je:

```python
category_id = Column(
	Integer,
	ForeignKey("category.id", ondelete="RESTRICT"),
	nullable=False,
)
```

Source fajl nisam menjao; primer iznad pokazuje ispravnu poziciju parametara.

Još jedna ranije uočena odluka ostaje važna za samoreferencirajuću kategoriju: ako korenske kategorije nemaju roditelja, `Category.category_id` mora biti nullable. Source koristi `nullable=False` u nameravanoj deklaraciji, što bi zabranilo korenski čvor. Odluku između obavezne roditeljske kategorije i dozvoljenih korena treba uskladiti sa pravilom hijerarhije.

## `ondelete` nije isto što i ORM cascade

Postoje dva povezana, ali različita mehanizma:

- `ForeignKey(..., ondelete="CASCADE")` definiše ponašanje baze i može se primeniti kada brisanje izvrši bilo koji klijent;
- `relationship(cascade="...")` definiše kako SQLAlchemy ORM sesija upravlja povezanim Python objektima.

Podešavanje jednog mehanizma ne treba automatski smatrati podešavanjem drugog. SQLAlchemy ORM može prilikom brisanja roditeljskog objekta slati dodatne `UPDATE` ili `DELETE` upite. Za koordinaciju sa brisanjem koje radi baza postoje relationship opcije kao `passive_deletes`; njih treba odabrati svesno i uskladiti sa `ForeignKey.ondelete` pravilom. Source ovog kursa podešava `ondelete`, ali ne prikazuje ORM cascade konfiguraciju.

---

### Zašto projektne kolekcije koriste `passive_deletes="all"`

U ovoj implementaciji `ondelete="RESTRICT"` treba da važi i kada brisanje
roditelja zatraži ORM `Session.delete()`. Podrazumevano, SQLAlchemy može da
učita povezanu kolekciju i pokuša da postavi FK kolone dece na `NULL` pre nego
što obriše roditelja. Kod nullable `roditelj_id` to bi odvojilo potkategorije
od roditelja i omogućilo brisanje kategorije, pa baza ne bi ni dobila priliku
da sprovede `RESTRICT`.

`passive_deletes="all"` na roditeljskoj kolekciji govori ORM-u da ne šalje te
`UPDATE` upite i da prepusti brisanje bazi. Zato je dodat na
`Kategorija.deca`, `Kategorija.proizvodi` i `Korisnik.porudzbine`. Opcija ne
znači `CASCADE` i ne briše povezane objekte. Ne sme se kombinovati sa ORM
`delete` ili `delete-orphan` cascade pravilima; takva pravila nisu dodata u
našem projektu.

Ovu razliku treba testirati sa uključenim FK enforcement-om. U izolovanom
SQLAlchemy/SQLite primeru `RESTRICT` bez `passive_deletes="all"` dozvolio je
da ORM postavi nullable parent FK na `NULL` i obriše roditelja; sa
`passive_deletes="all"` pokušaj brisanja je odbila baza. To je razlog zašto
projektna izmena uključuje oba sloja: FK `ondelete` i ORM podešavanje
pasivnog brisanja.

---

## Baza mora stvarno da sprovodi ograničenje

Promena modela ne menja automatski već postojeću tabelu. `ondelete` mora biti prisutan u stvarnom FK ograničenju u bazi; izmena postojeće šeme obično zahteva migraciju ili kontrolisanu izmenu tabele.

Podrška i detalji akcija zavise od DBMS-a. SQLite, na primer, zahteva da FK enforcement bude uključen na konekciji; u suprotnom se FK akcije možda neće sprovoditi. PostgreSQL sprovodi kreirana ograničenja. Proveriti ponašanje izabrane baze, naročito za `RESTRICT` naspram `NO ACTION`, `SET DEFAULT` i odložena ograničenja.

---

## Bezbedna provera u mini projektu

Paket trenutno ima modele i zajednički `Base`, ali još nema engine ni session
modul. Proveru zato treba raditi samo nad novim memorijskim SQLite engine-om,
ne nad korisničkom bazom. SQLite FK enforcement uključi se za svaku konekciju
pre kreiranja šeme:

```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite://")


@event.listens_for(engine, "connect")
def ukljuci_fk_enforcement(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")
```

Zatim pozvati `configure_mappers()` i `Base.metadata.create_all(engine)`.
Proveriti da `Session.delete()` i direktan SQL `DELETE` odbijaju:

1. kategoriju koja ima potkategoriju;
2. kategoriju koju koristi proizvod;
3. korisnika koji ima porudžbinu.

Svaki neuspeo `flush()`/`commit()` treba da se završi sa `session.rollback()`.
Proveriti i suprotne slučajeve: kategorija bez dece/proizvoda i korisnik bez
porudžbina mogu da se obrišu. Ako se koristi SQLite bez
`PRAGMA foreign_keys=ON`, test ne dokazuje da baza sprovodi FK pravila.

`ondelete` u Python metapodacima samo opisuje DDL koji treba da postoji u bazi.
Promena postojećeg FK-a zahteva migraciju ili kontrolisanu promenu šeme;
`create_all()` ne menja već postojeće ograničenje. Pošto praktični paket još
nema stalnu bazu, ne pokretati `drop_all()` niti reset skriptu radi ove provere.

---

## Pitanja za proveru razumevanja

1. Gde se u SQLAlchemy deklaraciji navodi `ondelete`?

- ODGOVOR: U deklaraciji `ForeignKey` unutar modela, npr. `ForeignKey("kategorija.id", ondelete="RESTRICT")`. Ostale opcije (`CASCADE`, `SET NULL`, `SET DEFAULT`, `NO ACTION`) se takođe navode ovde.

2. Šta se dešava sa decom kada je akcija `CASCADE`?

- ODGOVOR: Deca se automatski brišu kada se roditelj obriše. Ostale akcije (`SET NULL`, `SET DEFAULT`, `RESTRICT`, `NO ACTION`) imaju drugačije ponašanje.

3. Zašto `SET NULL` zahteva nullable FK kolonu?

- ODGOVOR: Ako FK kolona nije nullable, baza neće moći da postavi vrednost na NULL kada se roditelj obriše, što bi izazvalo grešku.

4. Zašto `SET DEFAULT` zahteva serverski default koji pokazuje na postojeći roditeljski red?

- ODGOVOR: Ako serverski default nije validan ili ne pokazuje na postojeći roditeljski red, baza neće moći da postavi vrednost kada se roditelj obriše, što bi izazvalo grešku.

5. Kako se razlikuju `RESTRICT` i `NO ACTION` u opštem slučaju?

- ODGOVOR: `RESTRICT` odmah sprečava brisanje roditelja ako postoje zavisni redovi, dok `NO ACTION` odlaže proveru do trenutka kada baza izvrši stvarnu proveru integriteta (obično na kraju transakcije). U praksi, za većinu baza, ponašanje je slično, ali `NO ACTION` može dozvoliti privremeno nevažeće reference unutar transakcije.

6. Da li `ForeignKey.ondelete` i `relationship(cascade=...)` znače isto?

- ODGOVOR: Ne, `ForeignKey.ondelete` definiše ponašanje baze kada se roditelj obriše, dok `relationship(cascade=...)` definiše ponašanje ORM-a pri brisanju objekata u Python kodu. Oni mogu biti usklađeni, ali nisu isto.

7. Da li postavljanje `is_active=False` pokreće `ON DELETE` akciju?

- ODGOVOR: Ne, postavljanje `is_active=False` samo menja atribut objekta u Python kodu i ne pokreće `ON DELETE` akciju u bazi. `ON DELETE` se aktivira samo kada se roditeljski red fizički obriše iz baze.

8. Koje greške u položaju argumenata sprečavaju učitavanje priloženog source fajla?

- ODGOVOR: Greške nastaju kada se argumenti prosleđuju pogrešnim konstruktorima ili kada se nullable postavlja na neodgovarajući način za korensku kategoriju.

9. Zašto `Kategorija.roditelj_id` ostaje nullable uz `ondelete="RESTRICT"`?

- ODGOVOR: `RESTRICT` samo sprečava brisanje roditelja ako postoje zavisni redovi, ali ne menja samu kolonu. Zato `Kategorija.roditelj_id` može ostati nullable, jer baza ne pokušava da postavi vrednost na NULL prilikom brisanja roditelja.

10. Zašto je `passive_deletes="all"` potrebno da ORM prepusti RESTRICT proveru bazi?

- ODGOVOR: `passive_deletes="all"` govori ORM-u da ne pokušava da automatski obriše decu kada se roditelj obriše, već da prepusti bazi da izvrši `ON DELETE` akciju. Ovo je važno za `RESTRICT`, jer ORM ne bi mogao da obavi brisanje ako bi pokušao da prvo obriše decu.

11. Koje projektne FK veze ostaju van obuhvata ove lekcije?

- ODGOVOR: Projektne FK veze koje ostaju van obuhvata ove lekcije uključuju sve one koje nisu direktno povezane sa `Kategorija`, `Proizvod` i `Porudzbina` modelima, ili koje koriste drugačije `ondelete` ponašanje koje nije detaljno obrađeno u ovoj lekciji.

---

## Sažetak

- `ondelete` definiše šta baza radi sa zavisnim redovima kada se briše referencirani roditelj.
- SQLAlchemy ga prosleđuje bazi kroz `ForeignKey(..., ondelete=...)`; `nullable` pripada `mapped_column(...)`.
- `CASCADE` briše decu, `SET NULL` zadržava ih bez reference, `SET DEFAULT` koristi serverski default, a `RESTRICT`/`NO ACTION` sprečavaju nevažeće reference.
- `SET NULL` zahteva nullable FK; `SET DEFAULT` zahteva validan serverski default koji referencira postojeći roditeljski red.
- U projektu se `RESTRICT` primenjuje na `Kategorija.roditelj_id`, `Proizvod.kategorija_id` i `Porudzbina.korisnik_id`; korenska kategorija ostaje dozvoljena.
- `passive_deletes="all"` prepušta ORM brisanje bazi za te roditeljske kolekcije; nije ORM cascade i ne briše decu.
- `ForeignKey.ondelete` je ponašanje baze i razlikuje se od ORM `relationship(cascade=...)` podešavanja.
- Source fajl trenutno pada zbog argumenata prosleđenih pogrešnim konstruktorima; pogrešan položaj argumenata i izbor nullable za korensku kategoriju su eksplicitno zabeleženi.
