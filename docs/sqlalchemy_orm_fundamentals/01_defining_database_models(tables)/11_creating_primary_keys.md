# Lekcija 11: Primarni ključevi

## Važna napomena o priloženim materijalima

Priloženi transkript za lekciju 11 ponavlja sadržaj lekcije 10 o `unique=True`; ne objašnjava primarne ključeve. Priloženi `8_primary_key.py`, međutim, dodaje primarni ključ svakom modelu. Zato se objašnjenje ispod zasniva na tom source kodu i na potrebnom SQLAlchemy kontekstu; ne predstavlja parafrazu transkripta za lekciju 11. Ispravljen ili odgovarajući transkript bi omogućio da se teorija naknadno uskladi sa predavanjem.

## Cilj lekcije

Svaki ORM model treba da ima način da jednoznačno prepozna svaki red. U ovoj verziji modela dodaje se kolona `id` kao primarni ključ:

```python
id = Column(Integer, primary_key=True, autoincrement=True)
```

Ovo je numerički, automatski generisan identifikator koji baza dodeljuje novom redu. U source kodu isti obrazac se ponavlja za `Category`, `PromotionEvent`, `Product`, `ProductPromotionEvent`, `StockManagement`, `User`, `Order` i `OrderProduct`.

## Šta je primarni ključ

Primarni ključ (primary key, PK) je kolona ili skup kolona koji jednoznačno identifikuje svaki red u tabeli. Njegove osnovne osobine su:

- vrednost mora biti jedinstvena;
- vrednost ne može biti `NULL`;
- tabela ima jedno primarno-key ograničenje, koje može obuhvatiti jednu ili više kolona.

Uobičajeno je da se napravi posebna kolona `id`. Tada svaki red dobija tehnički identifikator nezavisan od poslovnih podataka kao što su naziv proizvoda ili email korisnika.

SQLAlchemy ORM koristi primarni ključ da prepozna identitet objekta u sesiji i da zna kom redu pripada učitan ili izmenjen objekat. Zato su prethodni source snapshot-ovi bili nepotpuni kao ORM modeli: klase su imale kolone, ali nisu imale PK.

## Deklaracija u priloženom kodu

Kurs koristi `Column(...)` stil:

```python
from sqlalchemy import Column, Integer, String


class Category(Base):
	__tablename__ = "category"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(50), nullable=False, unique=True)
```

Ovde:

- `Integer` je tip kolone;
- `primary_key=True` označava kolonu kao deo primarnog ključa;
- `autoincrement=True` traži automatsko generisanje narednog identifikatora za ovaj integer ključ, u skladu sa podrškom baze i dijalekta.

`primary_key=True` ujedno znači da je kolona obavezna i jedinstvena. Ne mora se dodatno navesti `nullable=False` ili `unique=True` za tu istu kolonu.

## Kako se vrednost generiše i kada je dostupna

Pri unosu novog reda aplikacija obično ne prosleđuje `id`; baza generiše vrednost prema mehanizmu koji koristi izabrani dijalekt. SQLAlchemy pribavlja generisani ključ nakon uspešnog `INSERT`-a, tako da je dostupan objektu nakon što je red upisan, na primer posle `flush()` ili `commit()`.

Automatski ID nije brojač redova i ne treba očekivati da su vrednosti bez praznina. Otkazani ili poništeni upisi mogu potrošiti vrednost, a ponašanje zavisi od baze. ID služi za identitet, ne za izračunavanje broja postojećih zapisa, redosleda poslovnih događaja ili datuma nastanka.

`autoincrement=True` nije isto što i `default=0`. Primarni ključ treba da dobije novu jedinstvenu vrednost; postavljanje iste konstante za svaki red bi prekršilo jedinstvenost.

## Primarni ključ i `unique=True` nisu isto

Primarni ključ je glavni identifikator reda i obavezno je jedinstven i nenull. `unique=True` dodaje jedinstvenost nekoj drugoj koloni, ali je ne čini primarnim ključem.

U source modelu, na primer, `Category` ima:

- `id` kao primarni ključ;
- `name` kao jedinstven poslovni naziv;
- `slug` kao jedinstvenu URL vrednost.

Naziv ili slug mogu se menjati u skladu sa poslovnim pravilima, ali `id` ostaje stabilan identifikator reda. Ograničenja `unique=True` na `name` i `slug` ostaju zasebna i ne treba ih uklanjati samo zato što je dodat PK.

## Jedna kolona ili složeni primarni ključ

Svi modeli u priloženom source kodu koriste jednu `Integer` kolonu `id`. Primarni ključ može, međutim, da se sastoji od više kolona; tada se svaka kolona označava sa `primary_key=True`:

```python
class Membership(Base):
	__tablename__ = "membership"

	organization_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, primary_key=True)
```

U tom primeru identitet reda je par `(organization_id, user_id)`. Svaka vrednost pojedinačne kolone može se ponoviti, ali kombinacija ne može. Složeni ključevi su korisni u nekim veznim tabelama, ali zahtevaju da se u odnosima i upitima koristi ceo ključ. Izvor ove lekcije bira jednostavniji, surogatni `id`.

## Surogatni i prirodni ključevi

- **Surogatni ključ** je tehnički identifikator koji nema poslovno značenje, na primer automatski `id`.
- **Prirodni ključ** koristi postojeći poslovni podatak koji bi mogao da identifikuje red, na primer serijski broj ili kod.

`name`, `slug`, `username` i `email` u ovoj skripti ostaju unique, ali ne postaju primarni ključevi. To zadržava stabilan tehnički identitet i istovremeno sprovodi poslovnu jedinstvenost.

## Pregled modela iz source koda

| Model                   | Primarni ključ                 |
| ----------------------- | ------------------------------ |
| `Category`              | `id`, `Integer`, autoincrement |
| `PromotionEvent`        | `id`, `Integer`, autoincrement |
| `Product`               | `id`, `Integer`, autoincrement |
| `ProductPromotionEvent` | `id`, `Integer`, autoincrement |
| `StockManagement`       | `id`, `Integer`, autoincrement |
| `User`                  | `id`, `Integer`, autoincrement |
| `Order`                 | `id`, `Integer`, autoincrement |
| `OrderProduct`          | `id`, `Integer`, autoincrement |

`ProductPromotionEvent` sada ima `id`, ali još nema kolone koje bi povezale proizvod i promotivni događaj. Sam primarni ključ ne uspostavlja relaciju; za to su potrebni strani ključevi i odgovarajuće relacione deklaracije, što pripada kasnijoj temi.

## Problemi u priloženom source fajlu

Ovo su zapažanja o dostavljenom kodu, bez izmene source fajla:

- Između `from sqlalchemy.orm import DeclarativeBase` i deklaracije `Base` nalazi se goli tekst `poslao sam ti materijal`. To nije validna Python naredba i izazvaće `SyntaxError` pri pokretanju fajla. U objašnjavajućem primeru iznad ta linija nije uključena.
- I nakon uklanjanja tog teksta, `Product.updated_at` i `Order.updated_at` su `nullable=False`, ali imaju samo `onupdate=func.now()` i nemaju početni default. Pri `INSERT`-u treba im proslediti vrednost ili dodati odgovarajući početni default; `onupdate` važi za kasnije izmene, ne za početno kreiranje.
- Transkript koji je priložen uz ovaj source zapravo ponavlja lekciju o unique kolonama i ne potvrđuje objašnjenje PK koda.

## Pitanja za proveru razumevanja

1. Koja svojstva dobija kolona kada joj se postavi `primary_key=True`?
2. Zašto SQLAlchemy ORM modelu treba primarni ključ?
3. Šta u primeru radi `autoincrement=True`?
4. Zašto generisani ID ne treba koristiti kao redni broj bez praznina?
5. Koja je razlika između `id` primarnog ključa i `name` kolone sa `unique=True`?
6. Kako se razlikuje složeni primarni ključ od dve nezavisne unique kolone?
7. Zašto `onupdate` ne obezbeđuje vrednost `updated_at` pri `INSERT`-u?

## Sažetak

- Primarni ključ jednoznačno identifikuje red; ne može biti `NULL` i mora biti jedinstven.
- SQLAlchemy ORM koristi PK za identitet objekta i mapiranje promena na red u bazi.
- Source kod dodaje `id = Column(Integer, primary_key=True, autoincrement=True)` u svih osam modela.
- Automatski generisani ID je tehnički identifikator; ne garantuje redosled bez praznina.
- `unique=True` na nazivu, slug-u, korisničkom imenu ili email-u ostaje odvojeno poslovno ograničenje.
- Priloženi transkript je duplikat lekcije 10, a source sadrži tekst koji izaziva `SyntaxError`; obe stvari su eksplicitno zabeležene, bez izmene source fajla.
