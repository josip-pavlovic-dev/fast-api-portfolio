# Lekcija 08: Obavezna polja, `NULL` i prazne vrednosti

## Cilj lekcije

Pri definisanju kolona ne određujemo samo njihov tip. Za svako polje treba odlučiti da li zapis sme da postoji bez vrednosti u tom polju. Ova lekcija uvodi `nullable=False` i objašnjava šta baza smatra nedostajućom vrednošću.

Glavna pravila:

- `nullable=False` zabranjuje SQL vrednost `NULL` u koloni;
- `nullable=True` dozvoljava da kolona bude `NULL`;
- dozvoljenost `NULL` vrednosti nije isto što i zabrana praznog teksta;
- odluka da li je polje obavezno najčešće je poslovno pravilo, a ne univerzalno pravilo za sve aplikacije.

## Šta znači „obavezno“

U kontekstu baze, obavezno polje znači da za red u toj koloni mora postojati vrednost koja nije `NULL`. Na primer, kategorija bez imena verovatno ne bi bila korisna u ovom sistemu. Zato kurs odlučuje da su `name`, `slug` i druga polja obavezna.

To je odluka o konkretnom domenu. Druga aplikacija može dozvoliti da kategorija privremeno nema slug ili da opis proizvoda bude nepoznat. ERD i poslovna pravila treba da obrazlože šta je obavezno.

Primarni ključ je poseban slučaj: vrednost primarnog ključa ne može biti `NULL`. Međutim, u ovoj verziji priložene skripte nijednom modelu još nije dodat primarni ključ; to je nedovršenost snapshot-a iz prethodnih lekcija.

## `nullable=False`

U kursnom stilu sa `Column(...)`, zabranu `NULL` vrednosti definišemo imenovanim argumentom:

```python
name = Column(String(50), nullable=False)
```

SQLAlchemy će ovu postavku uključiti u definiciju kolone, a baza će dobiti ograničenje `NOT NULL`. Ako se pri upisu pokuša sačuvati `NULL`, baza odbija red. ORM objekat može postojati u Python-u sa nepostavljenim atributom, ali ograničenje se proverava kada se promena pošalje bazi, tipično pri `flush()` ili `commit()`.

Bez eksplicitne postavke, obična `Column` kolona je po pravilu nullable; primarni ključ je izuzetak. U ovom kursu se `nullable=False` navodi na kolonama za koje je autor odlučio da moraju imati vrednost.

Primer nullable kolone, kao što bi mogao biti opcion `parent_id`:

```python
parent_id = Column(Integer, nullable=True)
```

`nullable=True` dozvoljava `NULL`, ali ne zahteva da vrednost bude izostavljena. Može se proslediti i konkretan roditeljski ID.

### Tipizovani ORM u SQLAlchemy 2.x

U našem praktičnom kodu koristimo `Mapped[...]` i `mapped_column()`:

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

naziv: Mapped[str] = mapped_column(String(50), nullable=False)
opis: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Kada `nullable` nije naveden, SQLAlchemy 2.x ga po pravilu zaključuje iz `Mapped` anotacije: `Mapped[str]` označava nenullable kolonu, a `Mapped[str | None]` nullable kolonu. U nastavku lekcije navodimo `nullable=False` eksplicitno da bi ograničenje baze bilo jasno na mestu deklaracije. Anotacija opisuje očekivanu Python vrednost i pomaže alatima za tipove; `nullable` podešava SQL kolonu. Ta dva pravila treba držati usklađenim. Primarni ključ je nenullable zbog `primary_key=True`.

Za opcionog roditelja, SQLAlchemy 2.x zapis izgleda ovako:

```python
parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

## `NULL` nije isto što i prazan tekst

Za tekstualnu kolonu treba razlikovati nekoliko stanja:

| Vrednost    | Značenje                                                   |
| ----------- | ---------------------------------------------------------- |
| `NULL`      | nema vrednosti, vrednost je nepoznata ili nije dostavljena |
| `""`        | postoji tekstualna vrednost čija je dužina nula            |
| `"   "`     | postoji tekst sastavljen od razmaka                        |
| `"telefon"` | postoji tekstualna vrednost                                |

`nullable=False` odbija `NULL`, ali samo po sebi ne odbija `""` ili tekst od razmaka. Dakle, `name = Column(String(50), nullable=False)` ne garantuje da je naziv smislen ili da sadrži vidljive znakove.

U SQLAlchemy `Column` deklaraciji ne postoji opšti argument `blank=False` koji bi radio kao validacija forme. Provera da tekst nije prazan obično se radi na ulaznom sloju aplikacije, na primer Pydantic šemom. Ako isto pravilo mora da važi za sve klijente baze, može se dodati odgovarajuće `CHECK` ograničenje. Pravilo za prazan tekst je odvojeno od `NOT NULL` ograničenja.

## Obaveznost i default vrednosti

Polje može biti obavezno, a da aplikacija ipak ne mora svaki put eksplicitno da prosledi vrednost: SQLAlchemy ili baza mogu imati default koji je obezbeđuje pri unosu.

Skripta, na primer, navodi:

```python
is_active = Column(Boolean, nullable=False, default=False)
level = Column(SmallInteger, nullable=False, default=0)
quantity = Column(Integer, nullable=False, default=0)
```

U tipizovanom SQLAlchemy 2.x modelu ista pravila zapisujemo ovako:

```python
aktivna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
nivo: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
kolicina: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

Ako vrednost nije prosleđena, navedeni SQLAlchemy default-i obezbeđuju `False` ili `0` pri unosu preko SQLAlchemy-ja. U tabeli se i dalje ne dozvoljava `NULL`. U ovom stilu `default=False` je SQLAlchemy-jev podrazumevani izraz, a ne automatski serverski default koji baza primenjuje na upise svih mogućih klijenata. Za serverski default koristi se `server_default`.

Nasuprot tome, polje kao `name` nema default u source kodu, pa aplikacija mora da obezbedi vrednost pre uspešnog upisa. `nullable=False` ne izmišlja vrednost i ne pretvara `NULL` u prazan tekst.

## Pregled odluka u priloženoj skripti

Source kod ove lekcije eksplicitno postavlja `nullable=False` na svim deklarisanim kolonama:

| Model             | Kolone i pravilo                                                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `Category`        | `name`, `slug`, `is_active`, `level` su obavezni; `is_active` ima default `False`, a `level` default `0`                          |
| `PromotionEvent`  | `name`, `start_date`, `end_date`, `price_reduction` su obavezni i nemaju default u ovoj skripti                                   |
| `Product`         | tekstualna polja, statusi, datumi i `price` su `NOT NULL`; statusi imaju default `False`, a `created_at` ima `func.now()` default |
| `StockManagement` | `quantity` je obavezan sa default-om `0`; `last_checked_at` je obavezan bez default-a                                             |
| `User`            | `username`, `email` i `password` su `NOT NULL`; `username` i `email` dodatno imaju `unique=True`                                  |
| `Order`           | `created_at` i `updated_at` su `NOT NULL`; samo `created_at` ima default                                                          |
| `OrderProduct`    | `quantity` je obavezan bez default-a                                                                                              |

`unique=True` i `nullable=False` su odvojena ograničenja. Prvo zabranjuje duplikate prema pravilima baze, a drugo zabranjuje `NULL`. U ovom primeru su korisničko ime i email istovremeno jedinstveni i obavezni.

Transkript pominje opcioni `parent_id` na kategoriji, ali ga priloženi `5_required.py` još ne definiše. Zato u source kodu nema kolone niti ograničenja za to polje.

## Važna nedoslednost: `updated_at`

U prethodnoj lekciji `updated_at` je imao `onupdate=func.now()`, ali nije imao početni default. U ovoj skripti je dodat `nullable=False`, dok `onupdate` ostaje jedino pravilo za tu kolonu:

```python
updated_at = Column(DateTime, onupdate=func.now(), nullable=False)
```

`onupdate` važi pri odgovarajućem `UPDATE` upitu; ne obezbeđuje početnu vrednost pri `INSERT` upitu. Zbog toga insert koji ne prosledi `updated_at` nema vrednost za obaveznu kolonu i baza će ga odbiti zbog `NOT NULL` ograničenja. Isto važi za `Order.updated_at`.

Ako namera jeste da polje bude popunjeno i pri kreiranju, a zatim osveženo pri izmeni, modelu je potreban i početni default, na primer:

```python
updated_at = Column(
		DateTime,
		default=func.now(),
		onupdate=func.now(),
		nullable=False,
)
```

To bi bilo predloženo usklađivanje, a ne ono što trenutno radi priloženi source kod. Ovde ne menjamo source fajl, već beležimo posledicu njegovog trenutnog podešavanja.

Slično, `StockManagement.last_checked_at` je obavezno, ali nema default. Aplikacija zato mora da prosledi vrednost pri kreiranju reda.

## `NULL` i poslovna validacija na različitim slojevima

`nullable=False` je ograničenje baze. Ono je poslednja zaštita pri trajnom upisu, ali ne zamenjuje validaciju ulaza. API obično treba da proveri podatak pre nego što pokuša upis, kako bi korisnik dobio razumljivu poruku umesto sirove greške baze.

Za tekstualno polje validacija može proveriti da vrednost postoji, ukloniti spoljne razmake i odbiti prazan rezultat. Za broj ili datum može proveriti dozvoljen opseg ili pravila kao što je `end_date >= start_date`. Takva pravila ne nastaju automatski iz `nullable=False`.

Više slojeva može zato da dopunjuje jedno drugo:

1. API/šema proverava oblik i poslovno značenje ulaza.
2. SQLAlchemy model opisuje mapiranje i opcione ORM default-e.
3. Baza čuva trajna ograničenja kao što su `NOT NULL`, `UNIQUE` i `CHECK`.

## Napomene o prenosivosti

Osnovna razlika `NULL`/`NOT NULL` podržana je u relacijskim bazama, ali detalji ponašanja za prazne stringove i pojedina ograničenja mogu se razlikovati među bazama. Posebno ne treba zaključiti da je `""` isto što i `NULL` u svakom sistemu.

Kurski snapshot koristi klasični `Column(...)` stil, dok praktični paket koristi SQLAlchemy 2.x `Mapped[...]` i `mapped_column()`. Tipizovana anotacija može da utiče na zaključivanje nullable-a, ali ne menja osnovno značenje ograničenja. Pri prelasku između stilova proveriti i anotaciju i SQLAlchemy metapodatke kolone.

## Ograničenja priloženog snapshot-a

Modeli u skripti i dalje nemaju primarne ključeve, a `ProductPromotionEvent` je prazan. ORM mapiranje zato nije kompletno i fajl ne može samostalno da se izvrši kao gotov skup modela. Pored toga, `updated_at` kod proizvoda i porudžbine ima opisani problem pri unosu. To su ograničenja snapshot-a i ne treba ih mešati sa značenjem `nullable=False`.

## Pitanja za proveru razumevanja

1. Šta baza sprečava kada kolona ima `nullable=False`?
2. Da li `nullable=False` odbija prazan string `""`?
3. Koja je razlika između `NULL`, `""` i teksta sastavljenog od razmaka?
4. Kako `default=False` pomaže koloni koja je istovremeno `nullable=False`?
5. Da li `unique=True` zamenjuje `nullable=False`?
6. Zašto `updated_at` iz skripte može da izazove grešku pri prvom unosu?
7. Gde bi proverio da naziv ne sadrži samo razmake?
8. Koje polje iz transkripta, `parent_id`, nedostaje u priloženom source kodu?

## Sažetak

- `nullable=False` mapira se na `NOT NULL`: baza odbija `NULL` vrednost u koloni.
- `NOT NULL` ne znači automatski „tekst mora sadržati vidljive znakove“; `""` i razmaci su zaseban slučaj validacije.
- `default` može obezbediti vrednost za obavezno polje, ali ne uklanja samo po sebi potrebu za baznim ograničenjem.
- `unique=True` i `nullable=False` rešavaju različite zahteve.
- Source skripta postavlja sva postojeća polja kao obavezna, ali ta odluka dolazi iz pravila kursnog primera, ne iz univerzalnog pravila.
- `updated_at` i `Order.updated_at` imaju `nullable=False` i `onupdate`, ali nemaju default; pri unosu vrednost mora biti prosleđena ili se model mora dopuniti početnim default-om.
- `parent_id` se pominje u transkriptu, ali još ne postoji u priloženoj skripti.
- Source modeli nemaju primarne ključeve i zato nisu samostalno izvršiv ORM primer.
