# Lekcija 05: Definisanje tabela kao ORM modela

## Cilj lekcije

U prethodnoj lekciji definisana je deklarativna baza `Base`. Sada se ona koristi kao zajednička osnova za Python klase koje predstavljaju entitete iz ERD-a. Te klase nazivamo **SQLAlchemy ORM modelima**.

Lekcija uvodi vezu između četiri pojma:

1. **Entitet** je pojam u dizajnu baze.
2. **Python klasa** je kodni opis tog pojma.
3. **ORM model** je Python klasa koju SQLAlchemy mapira na tabelu.
4. **Tabela** je objekat šeme u relacionoj bazi.

U ovoj fazi definišu se imena modela i tabela. Atributi, tipovi, ključevi i ostala pravila dodavaće se u narednim lekcijama.

## Entitet, klasa, model i tabela

### Entitet

Dok se dizajnira baza, ono o čemu sistem čuva podatke naziva se entitet. Entitet je konceptualna stavka u ERD-u, na primer kategorija proizvoda, korisnik ili porudžbina. U toj fazi još nije Python klasa niti tabela u bazi.

### Python klasa

Klasa je Python konstrukcija koja opisuje zajedničko ponašanje i strukturu objekata. Ime klase mora biti validan Python identifikator. Uobičajena konvencija je PascalCase: `Category`, `PromotionEvent`, `StockManagement`.

### SQLAlchemy model

ORM model je Python klasa koja je uključena u SQLAlchemy mapiranje. Za deklarativni stil, konkretni modeli nasleđuju kursnu bazu:

```python
class Category(Base):
	...
```

To nasleđivanje povezuje klasu sa registry i metadata sistemom deklarativne baze.

### Tabela

Tabela je struktura u konkretnoj relacionoj bazi. Njen naziv određuje se preko `__tablename__`. Ime Python klase i ime tabele ne moraju biti ista.

Klasa može da bude definisana u Python kodu, a da tabela još ne postoji u bazi. Za kreiranje tabele potreban je kasniji korak koji koristi engine i DDL operaciju.

## Kako se ERD entitet pretvara u model

Transkript pokazuje ovaj tok:

1. Izaberi entitet iz ERD-a, na primer `category`.
2. Definiši Python klasu sa čitljivim imenom, na primer `Category`.
3. Nasledi zajednički `Base`.
4. Postavi `__tablename__` na željeni naziv tabele.
5. U narednim koracima dodaj kolone, tipove, ključeve, ograničenja i odnose.
6. Kasnije primeni opis modela na izabranu bazu.

Primer za prvu tabelu:

```python
class Category(Base):
	__tablename__ = "category"
	pass
```

`Category` je Python naziv klase, dok je vrednost `__tablename__` (`"category"`) naziv tabele. Donje crte se obično koriste za nazive tabela koji imaju više reči, na primer `promotion_event`.

## Objašnjenje sintakse

### `class Category(Base):`

- `class` započinje definiciju Python klase.
- `Category` je ime klase. Uobičajeno se piše PascalCase i često je u jednini jer predstavlja jedan objekat, odnosno jedan red.
- `(Base)` označava nasleđivanje od deklarativne baze uvedene u prethodnoj lekciji.

### `__tablename__ = "category"`

`__tablename__` je poseban deklarativni atribut koji SQLAlchemy koristi kao eksplicitno ime tabele. Dve donje crte na početku i kraju deo su imena atributa; ne treba ih izostaviti.

Ime tabele je string i zato mora biti pod navodnicima. SQLAlchemy ne zaključuje uvek ime tabele iz imena klase. Eksplicitni naziv olakšava da se Python stil i konvencije baze razlikuju.

Primeri iz fajla povezuju:

| Python model            | Naziv tabele              |
| ----------------------- | ------------------------- |
| `Category`              | `category`                |
| `PromotionEvent`        | `promotion_event`         |
| `Product`               | `product`                 |
| `ProductPromotionEvent` | `product_promotion_event` |
| `StockManagement`       | `stock_management`        |
| `User`                  | `user`                    |
| `Order`                 | `order`                   |
| `OrderProduct`          | `order_product`           |

Ova imena prate strukturu kursnog ERD-a. Nazivi modela su PascalCase, a višerečni nazivi tabela snake_case.

### `pass`

`pass` je Python naredba koja ne radi ništa. Koristi se zato što telo klase ne može biti prazno u gramatici Pythona. U ovom primeru označava da model još nema dodatne atribute ili metode.

`pass` nije SQLAlchemy naredba i ne pravi kolone. Kada se dodaju `id`, `name` i druga polja, `pass` se uklanja jer telo klase više nije prazno.

## Šta sadrži skripta `2_defining_database_models.py`?

Skripta ponovo definiše `Base`, a zatim deklaracije za osam entiteta: `Category`, `PromotionEvent`, `Product`, `ProductPromotionEvent`, `StockManagement`, `User`, `Order` i `OrderProduct`. Svaka klasa nasleđuje `Base` i postavlja odgovarajući `__tablename__`.

Ponavljanje klase `Base` u tom fajlu omogućava da je izvorni primer samostalan. U većem projektu bi se `Base` obično definisao jednom u zajedničkom modulu, a modeli bi ga uvozili umesto da svaka datoteka pravi novu bazu.

Skripta ne definiše atribute tabela, kolone, veze niti engine. To je nameran međukorak u nizu izvora: sledeće lekcije dodaju vrste polja, obaveznost, podrazumevane vrednosti, jedinstvenost i ključeve.

## Važna napomena: dati snapshot nije izvršiv ORM model

Iako je priloženi fajl naveden kao završni kod lekcije, proverio sam ga sa SQLAlchemy 2.0.38 i njegovo izvršavanje pada pri definisanju prve konkretne klase:

```text
sqlalchemy.exc.ArgumentError: Mapper Mapper[Category(category)] could not assemble any primary key columns for mapped table 'category'
```

Razlog je što je klasa deklarisana kao mapirani ORM model sa `__tablename__`, ali nema nijednu kolonu, a time ni primarni ključ. SQLAlchemy ORM-u je potreban identifikator reda da bi mapirane instance mogao jednoznačno da prati u identity map-u.

Ovo ne znači da su `Base` ili `__tablename__` pogrešni. Znači da je ovaj snapshot **kostur za sledeće korake**, a ne samostalno pokretljiv kompletan model. Primarni ključevi se dodaju kasnije u kursu, u lekciji o `primary_key=True`. Neću menjati priloženi source fajl; teorija beleži njegovo stvarno ponašanje.

Relacione baze mogu imati tabele bez deklarisanog primarnog ključa, ali ORM mapiranje takve tabele zahteva da se SQLAlchemy-ju na drugi način označi skup kolona koji jednoznačno identifikuje red. To je napredniji slučaj i ne važi za ovaj kod.

## Mapiranje još nije kreiranje tabele

Kada je mapirani model ispravan, SQLAlchemy registruje njegov opis u metadata objektu. To samo po sebi ne šalje zahtev bazi i ne stvara fizičku tabelu.

Da bi tabela nastala u bazi, aplikacija mora da:

1. napravi engine sa URL-om za konkretnu bazu;
2. učita module sa svim modelima koje želi da uključi;
3. izvrši operaciju koja primenjuje metadata, na primer `Base.metadata.create_all(engine)`.

Zato „model predstavlja tabelu“ znači da postoji ORM mapiranje i opis šeme, a ne da je tabela sigurno već kreirana na serveru.

## Razvijanje baze postepeno

Transkript preporučuje da se, kada je moguće, radi tabela po tabela umesto da se sva šema i aplikacioni upiti grade odjednom. Početniku je to korisno jer omogućava da se:

- proveri osnovni model pre dodavanja mnogo veza;
- ranije otkrije greška u tipu, nazivu ili ograničenju;
- razdvoji problem nove tabele od problema već testiranih tabela;
- nauči tok od modela do tabele, unosa i upita u manjim koracima.

Primer toka za entitet `Category`:

1. Definiši model i njegov primarni ključ.
2. Dodaj kolone koje su poznate iz ERD-a.
3. Napravi tabelu u razvojnoj bazi.
4. Unesi nekoliko testnih kategorija i proveri čitanje i ograničenja.
5. Tek zatim dodaj povezane modele, kao što je `Product`.

To je nastavna strategija, a ne univerzalno pravilo da produkciona šema uvek mora da se isporučuje po jednoj tabeli. Povezane tabele često se planiraju i menjaju zajedno. Uz to, u modernom projektu se promene postojeće šeme obično uvode kontrolisanim migracijama, a ne ručnim brisanjem i ponovnim kreiranjem podataka.

### Terminološka dopuna: „migrate“ naspram migracija

Transkript neformalno kaže da tabelu treba „migrate“ u bazu. U ovom kontekstu verovatno misli na njeno kreiranje u bazi. To ne treba mešati sa verzionisanim migracijama šeme koje upravlja Alembic. `create_all()` može napraviti nedostajuće tabele, ali nije zamena za sistem migracija kada već postojeća šema treba da se menja.

## Povezivanje sa SQLAlchemy 2.0 i TodoApp-om

Kursni primer koristi deklarativni obrazac `class Model(Base)` i eksplicitni `__tablename__`, što i dalje važi u SQLAlchemy 2.0. U kasnijim primerima može koristiti stariju deklaraciju kolona sa `Column(...)`; to ne menja ovde predstavljeni odnos između modela, baze i tabele.

U novom tipizovanom kodu konkretna polja se često definišu preko `Mapped[...]` i `mapped_column(...)`. Taj oblik dopunjuje deklarativnu mapu; ne menja ulogu `Base` niti potrebu da se postavi ime tabele.

TodoApp već ima `Todos` i `Users` klase koje nasleđuju zajednički `Base`. To su puni modeli sa kolonama i primarnim ključevima, za razliku od praznih klasa u kursnom međukoraku. TodoApp zato može odmah da ih registruje u metadata sistemu i napravi tabele kada se pozove `create_all()`.

## Provera razumevanja

1. Koja je razlika između entiteta u ERD-u i ORM modela u Pythonu?
2. Zašto klasa `Category` nasleđuje `Base`?
3. Da li se ime klase automatski mora poklapati sa `__tablename__`?
4. Šta `pass` radi u praznoj klasi?
5. Da li samo definisanje modela pravi fizičku tabelu u PostgreSQL-u?
6. Zašto se dati fajl zaustavlja na definisanju `Category` modela?
7. Kako se razlikuje nastavna preporuka „radi jednu tabelu po jednu“ od Alembic migracije?

## Sažetak

- ERD entitet se u deklarativnom ORM stilu predstavlja Python klasom koja nasleđuje `Base`.
- `__tablename__` eksplicitno zadaje ime tabele i ne mora da prati ime klase.
- Uobičajeno je da imena klasa budu PascalCase, a višerečni nazivi tabela snake_case.
- `pass` samo popunjava prazno telo klase; ne dodaje mapiranje ni kolone.
- Prazan model sa `__tablename__`, ali bez primarnog ključa, pada pri ORM mapiranju; kursni source je u ovoj tački nedovršen kostur.
- ORM opis tabele i njeno kreiranje u bazi odvojeni su koraci.
- Postepena izrada olakšava učenje i dijagnostiku, dok se promene produkcione šeme kasnije vode kontrolisanim migracijama.
