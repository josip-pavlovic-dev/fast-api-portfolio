# SQLAlchemy `relationship()` i `back_populates` — detaljno objašnjenje za početnike

Ovaj vodič objašnjava kako se redovi povezani stranim ključevima predstavljaju kao Python objekti u SQLAlchemy ORM-u i kako se povezane strane sinhronizuju pomoću `back_populates`. Primeri prate predloženu PortfolioItemsAPI šemu iz plana za 2026-11-17; to je nastavni primer, a ne potvrda da su ti modeli već implementirani u projektu.

## 1. Šta treba da razumemo pre `relationship()`

Portfolio aplikacija ima korisnike, stavke portfolija, kategorije, gradove i tagove. U relacionoj bazi te stvari predstavljamo tabelama, a veze među redovima predstavljamo primarnim i stranim ključevima.

Na primer, jedna stavka pripada jednom korisniku. Tabela `items` zato ima kolonu `owner_id`, čija vrednost pokazuje na `users.id`:

```text
users                              items
+----+--------+                    +----+----------------+----------+
| id | name   |                    | id | title          | owner_id |
+----+--------+                    +----+----------------+----------+
|  7 | Ana    | <----------------- | 31 | Portfolio sajt |        7 |
+----+--------+                    +----+----------------+----------+
                                      |
                                      +-- owner_id je strani ključ ka users.id
```

U SQL-u vezu između ta dva reda možemo napraviti pomoću `JOIN`-a. ORM nam dodatno omogućava da kroz Python objekte pristupamo povezanim podacima, na primer `item.owner` ili `user.items`. Ti atributi za navigaciju definišu se pomoću `relationship()`.

## 2. Najkraći odgovor: šta radi `relationship()`

`relationship()` definiše ORM atribut kojim se iz jednog Python objekta dolazi do povezanog Python objekta ili kolekcije povezanih objekata. Ona opisuje vezu ORM-u, ali sama po sebi ne pravi kolonu niti strani ključ u tabeli.

Najvažnije je razlikovati:

| SQLAlchemy konstrukcija          | Šta opisuje                             | Primer                        |
| -------------------------------- | --------------------------------------- | ----------------------------- |
| `mapped_column(ForeignKey(...))` | Kolonu i referencu u šemi baze          | `owner_id` u `items`          |
| `relationship(...)`              | Navigacioni atribut između ORM objekata | `item.owner` ili `user.items` |
| `back_populates="..."`           | Uparivanje dva navigaciona atributa     | `user.items` i `item.owner`   |

Dakle, u bazi su fizički važni `items.owner_id` i ograničenje stranog ključa. `item.owner` i `user.items` su atributi Python ORM modela; u tabelama ne postoje kolone koje se zovu `owner` ili `items`.

## 3. Šta znači `back_populates`

`back_populates` povezuje dva `relationship()` atributa koja predstavljaju suprotne strane iste veze. Vrednost mu je ime atributa na drugoj Python klasi, a ne ime tabele, kolone ili SQL izraza.

U ovom primeru postoje dva atributa:

```text
Users.items  <-------------------->  Items.owner
```

Na strani `Users` pišemo `back_populates="owner"`, jer se suprotni atribut na `Items` zove `owner`. Na strani `Items` pišemo `back_populates="items"`, jer se suprotni atribut na `Users` zove `items`.

```python
class Users(Base):
    # ...
    items: Mapped[list[Items]] = relationship(back_populates="owner")


class Items(Base):
    # ...
    owner: Mapped[Users] = relationship(back_populates="items")
```

Vrednosti moraju biti međusobno dosledne:

```text
Users.items  -> back_populates="owner" -> Items.owner
Items.owner  -> back_populates="items" -> Users.items
```

Ako napišemo `back_populates="owners"`, ali na drugoj klasi ne postoji relationship atribut pod imenom `owners`, konfiguracija nije ispravno uparena i SQLAlchemy prijavljuje grešku pri konfigurisanju mapper-a ili korišćenju modela. Imena su Python atributi i treba ih pisati tačno onako kako su deklarisana.

`back_populates` je eksplicitan: oba atributa su vidljiva u kodu i oba navode ime svog para. To olakšava početniku da vidi celu vezu i omogućava alatima za tipove da razumeju oba atributa. Stariji pristup `backref` može automatski napraviti drugu stranu, ali u ovim primerima koristimo `back_populates` jer je jasniji i eksplicitno deklarisan.

## 4. Prvo razumevanje kardinalnosti

Kardinalnost govori koliko redova jedne tabele može biti povezano sa jednim redom druge tabele. Ona nam pomaže da odlučimo da li ORM atribut treba da predstavlja jedan objekat ili kolekciju objekata.

| Veza        | Primer iz projekta                                                | ORM atribut sa jedne strane        | ORM atribut sa druge strane      |
| ----------- | ----------------------------------------------------------------- | ---------------------------------- | -------------------------------- |
| 1:N         | Jedan korisnik ima više stavki                                    | `Users.items`: lista stavki        | `Items.owner`: jedan korisnik    |
| N:1         | Više stavki ima istu kategoriju                                   | `Items.category`: jedna kategorija | `Categories.items`: lista stavki |
| N:1 opciona | Više korisnika može imati isti grad; korisnik može biti bez grada | `Users.city`: grad ili `None`      | `Cities.users`: lista korisnika  |
| M:N         | Stavka može imati više tagova, a tag više stavki                  | `Items.tags`: lista tagova         | `Tags.items`: lista stavki       |

Imena „jedan-prema-više“ i „više-prema-jedan“ opisuju isti par gledan sa različitih strana. Na primer, `Users.items` je 1:N kada gledamo od korisnika ka stavkama, a `Items.owner` je N:1 kada gledamo od stavke ka korisniku.

## 5. Veza 1:N: jedan korisnik ima više stavki

### 5.1 Gde se čuva strani ključ?

Kod 1:N veze strani ključ se nalazi na strani N. Više redova `items` može upisati isti `owner_id`, dok svaki pojedinačni red stavke ima jednu vrednost `owner_id`.

```text
users.id       items.owner_id
---------      --------------
7       <----- 7     # Stavka 31 pripada korisniku 7.
7       <----- 7     # Stavka 32 takođe pripada korisniku 7.
```

Strani ključ pripada tabeli `items`, pa je `Items` ORM strana koja ima skalarni atribut `owner`. `Users` je roditeljska strana koja ima kolekciju `items`.

### 5.2 Model u SQLAlchemy 2.0 stilu

```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    items: Mapped[list[Items]] = relationship(back_populates="owner")


class Items(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped[Users] = relationship(back_populates="items")
```

`Mapped[...]` označava tip ORM atributa i SQLAlchemy ga koristi za konfiguraciju mapiranja. `Mapped[list[Items]]` kaže da je `items` kolekcija objekata `Items`; `Mapped[Users]` kaže da je `owner` jedan objekat `Users`.

`relationship()` može da utvrdi koji redovi pripadaju jedni drugima zato što postoji `ForeignKey("users.id")` na `Items.owner_id`. Kod standardnog slučaja ne moramo ručno da joj prosleđujemo uslov za `JOIN`.

### 5.3 Šta znači obavezna veza?

Ovaj primer sadrži:

```python
owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
owner: Mapped[Users] = relationship(back_populates="items")
```

`nullable=False` i Python tip `Mapped[int]` govore da red stavke mora imati vlasnika. Zbog toga je tip odnosa `Items.owner` običan `Users`, a ne `Users | None`. To pravilo se sprovodi na nivou baze tek kada je tabela definisana sa `NOT NULL` i kada se sprovode ograničenja baze.

`Users.items` je i dalje lista. Lista može biti prazna: korisnik može postojati bez ijedne stavke. `Mapped[list[Items]]` ne znači da korisnik mora imati bar jednu stavku.

### 5.4 Kreiranje i povezivanje objekata

```python
user = Users(name="Ana")
item = Items(title="Portfolio sajt", owner=user)

print(item.owner.name)  # Ana
print(item in user.items)  # True
```

Pošto su dva atributa povezana sa `back_populates`, ORM sinhronizuje promenu među objektima u memoriji: dodela `item.owner = user` odražava se i kao dodavanje `item` u `user.items`. Isto važi i iz suprotnog smera:

```python
another_item = Items(title="API projekat")
user.items.append(another_item)

print(another_item.owner is user)  # True
```

To je sinhronizacija Python objekata; ne znači da je SQL već izvršen. Da bi promena bila poslata u bazu, objekti moraju biti deo odgovarajućeg `Session`-a, a SQLAlchemy šalje izmene pri `flush()`-u, često automatski pre `commit()`-a.

Nemojte zaključivati da je `item.owner_id` uvek odmah postavljen čim dodelite `item.owner`. Posebno kod novih objekata, vrednosti primarnih ključeva mogu biti dodeljene tek pri upisu. Za povezivanje novih objekata koristite relationship atribute (`item.owner = user` ili `user.items.append(item)`), a ne oslanjanje na to da ID već postoji.

## 6. Veza N:1 i `None`: korisnik i grad

Za `users.city_id` predloženo je da bude opcioni strani ključ. U bazi `NULL` znači da korisnik trenutno nema povezan grad. U Python tipu to treba prikazati kao mogućnost `None`:

```python
class Cities(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    users: Mapped[list[Users]] = relationship(back_populates="city")


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id"),
        nullable=True,
    )

    city: Mapped[Cities | None] = relationship(back_populates="users")
```

`Users.city` je jedan grad ili `None`; nije lista, jer korisnik u ovom modelu može imati najviše jedan grad. `Cities.users` je lista korisnika, jer više korisnika može pripadati istom gradu. `city_id` je nullable, pa je i `relationship` atribut opcionog tipa `Cities | None`.

Tri odluke treba da budu usklađene: nullable pravilo kolone, Python tip `Mapped[...]` i kardinalnost veze. Ako `city_id` postane obavezan (`nullable=False`), odnos sa strane korisnika treba da bude obavezni `Mapped[Cities]`, a ne `Mapped[Cities | None]`.

## 7. Veza M:N: stavke i tagovi

M:N znači da jedna stavka može biti povezana sa više tagova, a jedan tag može biti povezan sa više stavki. Relaciona tabela direktno ne čuva M:N vezu kao jednu FK kolonu, pa se u bazi ona razlaže pomoću spojne tabele:

```text
items 1:N item_tags N:1 tags
```

Za jednostavnu vezu bez sopstvenih podataka može se koristiti `Table` kao sekundarna tabela. `secondary=item_tags` govori `relationship()`-u da kroz tu tabelu poveže redove `items` i `tags`.

```python
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Items(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    tags: Mapped[list[Tags]] = relationship(
        secondary=item_tags,
        back_populates="items",
    )


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    items: Mapped[list[Items]] = relationship(
        secondary=item_tags,
        back_populates="tags",
    )
```

Ovaj kod je samostalan primer M:N veze: `Base`, spojna tabela i obe ORM klase definisani su zajedno. U stvarnom modulu `Base` se obično uvozi iz zajedničkog modula, a sve klase i `item_tags` moraju pripadati istom `Base.metadata`.

`item_tags` je prava tabela baze sa kolonama `item_id` i `tag_id`, dok su `Items.tags` i `Tags.items` ORM atributi za navigaciju. `secondary=item_tags` se navodi na obe strane, a `back_populates` upućuje na suprotni relationship atribut.

Složeni primarni ključ `(item_id, tag_id)` sprečava da se isti tag dva puta dodeli istoj stavci. Kada se preko ORM-a doda tag u `item.tags`, SQLAlchemy pri upisu dodaje odgovarajući red u `item_tags`. Nije potrebno ručno dodavati isti red u `item_tags` dok koristimo ovaj mapirani M:N obrazac.

```python
python_tag = Tags(name="python")
api_item = Items(title="Portfolio API")
api_item.tags.append(python_tag)

print(python_tag in api_item.tags)  # True
print(api_item in python_tag.items)  # True
```

Ako spojna tabela dobije sopstvene podatke, npr. `assigned_at`, `added_by_user_id` ili redosled taga, više nije samo skup parova. Tada je najčešće bolje mapirati `item_tags` kao ORM klasu (asocijacioni objekat) i napraviti dve 1:N veze: `Items` → `ItemTag` i `Tags` → `ItemTag`. Tako dodatni atributi imaju jasno mesto.

## 8. Kako SQLAlchemy zna da poveže dve tabele?

U najčešćem slučaju `relationship()` koristi `ForeignKey` veze koje su deklarisane u `Table` metapodacima da odredi JOIN uslov. Za `Items.owner` uslov je konceptualno:

```sql
items.owner_id = users.id
```

Za M:N `Items.tags`, putanja je konceptualno:

```sql
items.id = item_tags.item_id
AND item_tags.tag_id = tags.id
```

`relationship()` ne traži da napišemo ručno svaki `JOIN` za standardnu vezu. Međutim, ako postoji više stranih ključeva između istih tabela ili je veza nestandardna, SQLAlchemy može zahtevati dodatnu konfiguraciju kao `foreign_keys` ili `primaryjoin`. To su napredniji slučajevi i ne treba ih dodavati unapred kada je veza jednoznačna.

## 9. ORM veza nije isto što i `JOIN` upit

Relationship je definicija kako se objekti povezuju i kako se do njih može doći. To samo po sebi ne znači da su svi povezani redovi već pročitani iz baze.

Na primer:

```python
item = session.get(Items, 31)
```

Ovaj upit dohvata `Items` objekat. Ako zatim pristupimo `item.owner`, SQLAlchemy po podrazumevanoj strategiji može poslati još jedan upit za vlasnika. Ako pristupamo `item.tags`, može poslati upit koji prolazi kroz `item_tags`. Stvarni SQL zavisi od toga šta je već učitano u `Session`-u i koja je strategija učitavanja korišćena.

### 9.1 Lazy loading — učitavanje pri pristupu

Podrazumevani obrazac za običan `relationship()` je lazy loading: povezani podaci se učitavaju kada im se prvi put pristupi, ako već nisu dostupni. To je zgodno za jednostavan slučaj, ali petlja kroz mnogo objekata može izazvati mnogo dodatnih upita.

```python
from sqlalchemy import select

items = session.scalars(select(Items)).all()

for item in items:
    print(item.owner.name)
```

Ako svaki `item.owner` izazove dodatni upit, veći skup stavki može dovesti do problema poznatog kao N+1 queries: jedan upit za stavke i dodatni upiti za vlasnike. Tačan broj zavisi od identity map-a i već učitanih objekata, ali treba razmišljati o tome kako se relacije učitavaju kada pravimo API odgovor.

### 9.2 `selectinload()` za kolekcije

Kada unapred znamo da će nam trebati povezana kolekcija, često je dobar početni izbor `selectinload()`. SQLAlchemy učita glavne redove, pa zatim povezane redove za njih u dodatnom upitu koji koristi njihove ključeve:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = select(Users).options(selectinload(Users.items))
users = session.scalars(stmt).all()

for user in users:
    print([item.title for item in user.items])
```

Ovo ne uklanja potrebu da se podaci učitaju, već unapred kaže ORM-u koje veze će biti korišćene. Za učitavanje više nivoa može se ulančati, na primer `selectinload(Users.items).selectinload(Items.tags)`.

### 9.3 `joinedload()` za JOIN učitavanje

`joinedload()` koristi SQL JOIN da u istom SQL iskazu učita povezane objekte. To je često praktično za many-to-one relacije kao `Items.owner`, ali učitavanje kolekcija kroz JOIN može umnožiti broj rezultujućih redova. Zato strategiju biramo prema obliku podataka i upitu, a ne zato što `relationship()` postoji.

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

stmt = select(Items).options(joinedload(Items.owner))
items = session.scalars(stmt).all()
```

Nemojte mešati `relationship()` i `joinedload()`: `relationship()` deklariše vezu u mapiranju, dok je `joinedload()` opcija za to kako se veza učitava u konkretnom upitu. Isto tako, običan SQLAlchemy `select(...).join(...)` konstruiše JOIN za filtriranje ili projekciju upita; sam JOIN ne zamenjuje deklarisani relationship.

### 9.4 Session i serijalizacija

Lazy učitavanje zahteva da ORM ima pristup `Session`-u i konekciji. Ako objekat odvojimo od zatvorene sesije, pa tek onda pristupimo nekoj još neučitanoj vezi, SQLAlchemy ne može da je učita i može prijaviti `DetachedInstanceError`. Zato se u API-ju povezani podaci planirano učitavaju dok je sesija aktivna i zatim pretvaraju u Pydantic response model.

ORM veze su često ciklične: `user.items[0].owner` vraća istog korisnika. Direktna, neograničena rekurzivna serijalizacija celog ORM grafa može dovesti do beskonačnog kruženja ili do odgovora sa više podataka nego što API treba da izloži. Pydantic response modeli treba namerno da izaberu potrebna polja i smer prikaza; ne treba automatski ugnjezditi svaki relationship u oba smera.

## 10. `relationship()` ne određuje automatski pravilo brisanja

`relationship()` opisuje ORM vezu i navigaciju. Pravilo šta treba da se desi pri brisanju roditelja je zasebna odluka. Važno je razlikovati:

| Podešavanje                           | Gde se definiše          | Na šta utiče                                                                                    |
| ------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------- |
| `ForeignKey(..., ondelete="CASCADE")` | Šema baze / strani ključ | Šta baza radi kada se red roditelja obriše, ako baza sprovodi FK                                |
| `relationship(..., cascade="...")`    | ORM mapiranje            | Kako ORM `Session` obrađuje povezane ORM objekte pri operacijama                                |
| `delete-orphan`                       | ORM cascade pravilo      | Da li ORM briše zavisni objekat kada se ukloni iz roditeljske kolekcije, u odgovarajućem odnosu |

Ove opcije nisu sinonimi i ne treba ih dodavati samo da bi se izbegla greška pri brisanju. U predloženoj PortfolioItemsAPI šemi pravila brisanja korisnika, kategorije i taga ostavljena su za posebnu domensku odluku; ovaj vodič ih zato ne uključuje u primer modela.

## 11. Veza 1:1 ukratko

1:1 je veza u kojoj jedan red može biti povezan sa najviše jednim redom sa druge strane, na primer korisnik i profil kada svaki profil pripada jednom korisniku i svaki korisnik ima najviše jedan profil. U bazi se obično pravi strani ključ sa `UNIQUE` ograničenjem na strani zavisnog reda, a u anotiranom SQLAlchemy 2.0 mapiranju skalarni tip umesto `list[...]` signalizira da je odnos jedan-na-jedan.

Sama Python anotacija ili `relationship()` ne zamenjuje `UNIQUE` ograničenje u bazi. Baza mora sprečiti da dva reda profila pokažu na istog korisnika ako je to pravilo domena. 1:1 nije deo predložene šeme PortfolioItemsAPI; ovde ga navodimo samo da bismo razlikovali skalarni atribut od kolekcije.

## 12. Česti nesporazumi i greške

### „`relationship()` pravi kolonu stranog ključa“

Ne. Kolonu pravimo sa `mapped_column(ForeignKey(...))`; `relationship()` pravi ORM atribut za pristup povezanom objektu ili kolekciji.

### „`back_populates` upisuje podatke u bazu“

Ne odmah. On povezuje atribute i sinhronizuje promene u Python objektima. SQL se izvršava kada ORM pošalje promene iz `Session`-a, tipično pri `flush()` ili `commit()`.

### „Strani ključ treba da bude na obe strane“

Za jednu 1:N relaciju dovoljan je jedan strani ključ na N strani. Relationship atribut na roditelju je kolekcija koja se izvodi iz te veze, a ne druga FK kolona. Za M:N potrebna je spojna tabela sa dva strana ključa.

### „Vrednost `back_populates` je ime tabele“

Ne. To je ime relationship Python atributa na suprotnoj klasi. Na primer, `Items.owner` uparuje se sa `Users.items`, pa se koriste baš nizovi `"items"` i `"owner"`.

### „Kolekcija `user.items` znači da su stavke već učitane“

Ne nužno. Relationship definiše kako ih ORM može dobiti. Ako nisu već učitane, pristup može pokrenuti dodatni SQL upit; koristite odgovarajuću eager loading opciju kada znate da će vam povezani podaci trebati.

### „Ako je veza nullable, mogu da ostavim tip bez `None`“

Ne. Za opcioni `city_id` uskladite nullable kolonu i `Mapped[Cities | None]`. Python tip treba da odražava da `user.city` može biti `None`.

### „`back_populates` i `cascade` su isto“

Ne. `back_populates` povezuje obe strane odnosa. `cascade` definiše kako ORM operacije nad jednim objektom mogu uticati na povezane objekte. To su različita podešavanja.

## 13. Brz postupak za čitanje bilo koje veze

Kada naiđete na nepoznat `relationship()`, postavite sebi ova pitanja redom:

1. Koje su dve tabele ili klase povezane?
2. Gde je `ForeignKey` i na koju kolonu pokazuje?
3. Koja je kardinalnost: 1:N, N:1, 1:1 ili M:N?
4. Da li atribut predstavlja jedan objekat, opcioni objekat ili kolekciju?
5. Ako je veza dvosmerna, kako se zove relationship atribut na drugoj klasi i da li `back_populates` pokazuje na njega?
6. Kada će povezani podaci biti učitani: lazy pristupom ili loader opcijom kao `selectinload()`?
7. Postoji li domensko pravilo brisanja i da li je posebno razmotreno za ORM i bazu?

Za PortfolioItemsAPI možemo to primeniti ovako:

| FK u bazi                                                       | Navigacija sa FK strane      | Navigacija sa druge strane      | Tip odnosa                                 |
| --------------------------------------------------------------- | ---------------------------- | ------------------------------- | ------------------------------------------ |
| `items.owner_id -> users.id`                                    | `Items.owner: Users`         | `Users.items: list[Items]`      | Stavke 1:N po korisniku                    |
| `items.category_id -> categories.id`                            | `Items.category: Categories` | `Categories.items: list[Items]` | Stavke 1:N po kategoriji                   |
| `users.city_id -> cities.id`                                    | `Users.city: Cities \| None` | `Cities.users: list[Users]`     | Opcioni grad, jedan grad za više korisnika |
| `item_tags.item_id -> items.id` i `item_tags.tag_id -> tags.id` | `Items.tags: list[Tags]`     | `Tags.items: list[Items]`       | M:N preko `item_tags`                      |

## 14. Mini rečnik

| Pojam            | Jednostavno značenje                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| ORM              | Način da se redovi baze predstave Python objektima i da se tim objektima upravlja preko mapiranja      |
| `ForeignKey`     | Ograničenje kolone koje referencira ključ u drugoj tabeli                                              |
| `relationship()` | ORM atribut za pristup povezanom objektu ili kolekciji                                                 |
| `back_populates` | Veza između dva relationship atributa koji predstavljaju suprotne strane istog odnosa                  |
| Skalarni atribut | Relationship atribut koji predstavlja jedan povezani objekat ili `None` ako je opcioni                 |
| Kolekcija        | Atribut koji predstavlja više povezanih objekata, najčešće `list[...]`                                 |
| Lazy loading     | Učitavanje povezanih redova kada im se pristupi                                                        |
| Eager loading    | Učitavanje povezanih redova unapred, npr. pomoću `selectinload()` ili `joinedload()`                   |
| `Session`        | ORM jedinica rada koja prati objekte, transakciju i pristup bazi                                       |
| Identity map     | Mapa unutar `Session`-a koja omogućava da jedan red bude predstavljen jednim ORM objektom u toj sesiji |

## 15. Korisni zvanični izvori

- [SQLAlchemy 2.0 — Basic Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html): 1:N, N:1, 1:1 i M:N primeri sa `Mapped` anotacijama.
- [SQLAlchemy 2.0 — Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html): lazy, joined i select-in učitavanje.
- [SQLAlchemy 2.0 — Relationship Configuration](https://docs.sqlalchemy.org/en/20/orm/relationships.html): naprednija konfiguracija relationship odnosa.
