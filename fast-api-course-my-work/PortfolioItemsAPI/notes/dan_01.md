# Pitanja i odgovori

## Pitanje 1

Imam jedno pitanje vezano za models.py. U fast-api-course-my-work/TodoApp/models.py koji nije dovršen je nullable=True prisutno u svim kolonama tabela osim ID koji je PK. Nije mi logično da npr prioritz kolona može da se izostavi. Da li je to namerno učinjeno u kursu koji pratim na Udemy-ju pa će se kasnije izmeniti ili je to normalno?

Završio sam fast-api-course-my-work/PortfolioItemsAPI/models.py minimalno .py skripti za kreiranje baze podataka. Pre nego sto kreiram bazu proveri skripte u fast-api-course-my-work/PortfolioItemsAPI i objasni mi koji pristup za nullable da iskoristim u fast-api-course-my-work/PortfolioItemsAPI/models.py kako bih pravilno definisao koje kolone mogu biti NULL, a koje ne.

---

## Odgovor 1

U izolovanoj memorijskoj bazi sam potvrdio da `nullable=False` za kolone koje moraju imati vrednost funkcioniše kako se očekuje: unos bez tih vrednosti izaziva grešku `NOT NULL constraint failed`. To znači da je preporučljivo jasno definisati koje kolone su obavezne, a koje mogu biti `NULL`, kako bi se izbegli problemi pri unosu podataka direktno u bazu ili kroz ORM.

Uočio sam važnu razliku: TodoApp API zahteva `priority`, ali njegova baza dozvoljava `NULL`. Sada proveravam novonapisane modele u izolovanoj SQLite bazi u memoriji, ne oslanjajući se na stvarnu bazu fajla, kako bih potvrdio da `nullable` pravila funkcionišu kako je očekivano.

Da, tvoja sumnja je opravdana: **ako svaki zadatak mora imati prioritet, baza ne bi trebalo da dozvoli `NULL` za `priority`.**

### Zašto je TodoApp drugačiji?

U `TodoApp/models.py` `priority` dozvoljava `NULL`, ali ga `CreateTodoRequest` zahteva i ograničava na vrednosti od 1 do 5.

To znači da API štiti unos **kroz taj endpoint**, ali direktan SQL unos ili drugi kod mogu zaobići Pydantic i upisati `NULL`. Takav red kasnije može praviti problem i pri formiranju API odgovora.

U lokalnom primerku kursa našao sam `priority = Column(Integer)` bez `nullable=False`, što takođe dozvoljava `NULL`. Kasnije će se sigurno dodati `nullable=False` kada se API implementira u skladu sa zahtevima, ali trenutno baza sama po sebi ne sprečava `NULL` vrednosti.

U suštini, `nullable` pravilo u SQLAlchemy definiše ograničenje na nivou baze, dok Pydantic modeli definišu pravila na nivou aplikacije. Idealno je da oba sloja budu usklađena kako bi se izbegli konflikti i neočekivano ponašanje.

Ako se desi da baza dozvoljava `NULL`, a Pydantic model ne, greške će se javljati pri unosu kroz API, ali direktni SQL unos može zaobići validaciju. Obrnuto, ako baza ne dozvoljava `NULL`, a Pydantic model ga ne zahteva, greške će se javljati pri pokušaju upisa `NULL` vrednosti u bazu. Stoga je najbolje da pravila budu konzistentna.

U praksi, to znači da za svako polje koje je obavezno u API-ju treba postaviti `nullable=False` u SQLAlchemy modelu, a za polja koja mogu biti opciona treba koristiti `nullable=True` i odgovarajuće Pydantic tipove sa `Optional` ili `None`. Na taj način se postiže konzistentnost između sloja baze i sloja aplikacije, smanjujući rizik od neočekivanih grešaka i problema pri unosu podataka.

---

### Preporuka za tvoj `PortfolioItemsAPI`

Tvoj pristup u `models.py` je dobar: **koristi `nullable=False` kada podatak mora postojati**, a `nullable=True` samo kada je odsustvo vrednosti smisleno.

Ovo pravilo pomaže da se izbegnu situacije gde API očekuje obavezne podatke, ali baza ih ne zahteva, što može dovesti do grešaka ili nekonzistentnih podataka. Uvek je dobro proveriti da li su `nullable` postavke u SQLAlchemy modelima u skladu sa zahtevima Pydantic modela koji definišu API unos. Na taj način se obezbeđuje da sloj baze i sloj aplikacije rade u harmoniji, smanjujući rizik od neočekivanih grešaka i problema pri unosu podataka.

| Polje                            | Preporuka        | Razlog                                                                                                |
| -------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------- |
| `users.name`, `users.email`      | `nullable=False` | Korisnik treba ime i email. Razmotri i `unique=True` za email.                                        |
| `categories.name`                | `nullable=False` | Kategorija treba ime. Razmotri i jedinstvenost imena.                                                 |
| `items.title`, `price`, `status` | `nullable=False` | Prema planu, stavka mora imati ove vrednosti.                                                         |
| `items.description`              | `nullable=False` | Trenutni plan je zahteva; ako opis može nedostajati, koristi `Mapped[str \| None]` i `nullable=True`. |
| `owner_id`, `category_id`        | `nullable=False` | Ako svaka stavka mora imati vlasnika i kategoriju.                                                    |
| `created_at`, `updated_at`       | `nullable=False` | Ima smisla ako svaka stavka mora imati datume — ali moraš i obezbediti njihove vrednosti.             |

`nullable=False` zabranjuje `NULL`, ali **ne proverava sve**: na primer, sam po sebi ne zabranjuje prazan tekst ili negativnu cenu. Pydantic validacija i, gde je potrebno, bazni `CHECK`/`UNIQUE` dodaju druga pravila.

---

### Važne stvari pre kreiranja baze

1. **Datumi nemaju podrazumevane vrednosti.** U izolovanoj memorijskoj bazi pokušaj unosa `Items` bez datuma završio se greškom `NOT NULL constraint failed: items.created_at`. Dakle, moraš ih proslediti pri unosu ili kasnije definisati odgovarajuće default/update ponašanje. `updated_at` se trenutno ne menja automatski.

2. **Tip za `status`:** u `models.py` koristiš `Mapped[Boolean]`; za Python vrednost koristi `Mapped[bool]`, dok `Boolean` ostaje SQLAlchemy tip kolone:

   ```python
   status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
   ```

   Ovo predstavlja dva stanja. Plan ih naziva `draft`/`published`, pa pre kreiranja odluči da li ti je razumljiviji boolean ili eksplicitni tekstualni status.

3. **SQLite strani ključevi:** u izolovanoj proveri `PRAGMA foreign_keys` je bio `0` i SQLite je prihvatio nepostojeće `owner_id` i `category_id`. Deklarisani `ForeignKey` i `nullable=False` nisu dovoljni dok se sprovođenje stranih ključeva ne uključi za SQLite konekcije a to planiramo za kasnije u aplikaciji.

4. **`create_all()` ne menja postojeće tabele.** Zato je dobro što ova pitanja razmatraš pre prvog kreiranja. Kasnije promene šeme zahtevaju migraciju ili drugi kontrolisan postupak.

---

## Pitanje 2

Objasni mi detaljno modul datetime u Pythonu i kako se koristi u kontekstu SQLAlchemy modela za polja `created_at` i `updated_at`.

---

## Odgovor 2

### 1. Šta je Python `datetime`?

`datetime` je standardni Python modul za predstavljanje datuma, vremena, njihove kombinacije i vremenskih zona. Ne treba ga instalirati dodatno. Naziv može biti zbunjujući zato što se modul i jedna njegova klasa zovu isto:

```python
import datetime

trenutak = datetime.datetime.now()
```

Ovde je prvo `datetime` naziv modula, a drugo `datetime` naziv klase. Često se zato koristi kraći uvoz:

```python
from datetime import datetime

trenutak = datetime.now()
```

U ovom drugom primeru `datetime` u kodu označava klasu, ne ceo modul.

Najvažnije klase i tipovi u modulu su:

| Tip                   | Šta predstavlja                                | Primer                |
| --------------------- | ---------------------------------------------- | --------------------- |
| `date`                | kalendarski datum bez vremena                  | `2026-11-16`          |
| `time`                | vreme u toku dana bez datuma                   | `14:30:00`            |
| `datetime`            | datum i vreme u jednoj vrednosti               | `2026-11-16 14:30:00` |
| `timedelta`           | trajanje ili razliku između dva datuma/vremena | 3 dana ili 2 sata     |
| `timezone` / `tzinfo` | podatke o vremenskoj zoni i pomeraju od UTC-a  | `UTC+01:00`           |

Na primer:

```python
from datetime import date, datetime, timedelta, timezone

danas = date.today()
trenutak = datetime.now()
rok = trenutak + timedelta(days=7)
trenutak_utc = datetime.now(timezone.utc)
```

`UTC` (Coordinated Universal Time) je vremenska zona koja se koristi kao referenca za sve druge vremenske zone. Vrednosti u UTC-u su nezavisne od lokalnog vremena i ne podležu letnjem računanju vremena, što ih čini pogodnim za čuvanje i razmenu vremenskih podataka u distribuiranim sistemima.

`datetime.now()` bez vremenske zone pravi **naivan** (`naive`) `datetime`: vrednost nema informaciju o tome u kojoj je vremenskoj zoni. Nasuprot tome, `datetime.now(timezone.utc)` pravi **svestan** (`aware`) `datetime` koji izričito označava UTC. Za sisteme koji rade u više vremenskih zona uobičajeno je čuvati i razmenjivati vreme u UTC-u, pa ga tek pri prikazu korisniku treba pretvoriti u lokalnu zonu. Naivne i svesne vrednosti ne treba mešati bez strogo definisanog i jasno dokumentovanog pravila i procedure, jer bi u suprotnom moglo doći do grešaka u računanju vremena i prikazu korisniku, što može dovesti do ozbiljnih problema u aplikacijama koje zavise od tačnog vremena, posebno u kontekstu finansijskih transakcija, zakazivanja događaja i logovanja aktivnosti.

Za tekstualni prikaz i parsiranje postoje, između ostalog, `isoformat()`/`fromisoformat()` i `strftime()`/`strptime()`. ISO 8601 oblik, kao što je `2026-11-16T14:30:00+00:00`, koristan je za prenos datuma između API-ja i klijenata. FastAPI/Pydantic tipično predstavljaju Python `datetime` u JSON-u kao ISO 8601 tekst.

---

### 2. Python `datetime` i SQLAlchemy `DateTime` nisu isti tip

U ORM modelu rade zajedno, ali imaju različite uloge:

- Python `datetime` je tip objekta koji aplikacija koristi u memoriji.
- SQLAlchemy `DateTime` je tip kolone koji SQLAlchemy koristi da definiše kolonu u tabeli i pretvara DB vrednosti u Python vrednosti.

Zato je u modelu ispravno navesti `Mapped[datetime]` kao Python tip, a `DateTime` proslediti `mapped_column()`-u kao SQLAlchemy 2.0 kolone tip:

```python
created_at: Mapped[datetime] = mapped_column(DateTime, ...)
```

Kada se red učita ORM-om, aplikacija čita `item.created_at` kao Python `datetime` vrednost, a ne kao SQLAlchemy `DateTime` objekat. Ovo razdvajanje omogućava aplikaciji da radi sa standardnim Python tipovima dok SQLAlchemy brine o konverziji između baze i Pythona. Ta konverzija se obavlja automatski prilikom čitanja i upisivanja vrednosti u bazu, tako da aplikacija uglavnom ne mora da brine o detaljima SQL tipova. U našem primeru zahvaljujući `Mapped[datetime]` i `DateTime` koloni, sve funkcioniše automatski i konzistentno.

---

### 3. Kako model postavlja `created_at`

Trenutni model u `models.py` definiše:

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.now(),
)
```

- `nullable=False` znači da baza ne sme da sačuva `NULL` za ovu kolonu.
- `server_default=...` postavlja podrazumevanu vrednost na strani baze. Zato pri `INSERT`-u aplikacija može da izostavi `created_at`, a baza će upisati trenutni datum i vreme.
- `func.now()` je SQLAlchemy izraz koji se prevede u SQL funkciju baze. To nije poziv Python-ovom `datetime.now()` i ne vraća Python datum u trenutku definisanja modela.

`created_at` je vreme nastanka reda i po pravilu se postavlja jednom. Ne treba menjati ga pri svakom kasnijem ažuriranju.

---

### 4. Kako model postavlja `updated_at`

Model definiše:

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.now(),
    onupdate=func.now(),
)
```

- `server_default=func.now()` postavlja početnu vrednost prilikom kreiranja reda, tako da i novi red ima `updated_at`.
- `onupdate=func.now()` traži od SQLAlchemy-ja da uključi novu vrednost vremena kada SQLAlchemy generiše `UPDATE` za taj red.

Važno: `onupdate` **nije SQLite trigger** i sam po sebi ne menja šemu tako da bi svaka moguća SQL izmena u bazi ažurirala kolonu. Ako red promeniš direktno kroz `sqlite3` ili drugi alat, ova SQLAlchemy opcija se ne izvršava.

U direktnom SQL-u morao bi eksplicitno da napišeš:

```sql
UPDATE items
SET title = 'Novi naslov',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

Ako je potrebno da svaka izmena — bez obzira na to koji program je izvrši — automatski menja `updated_at`, to je pravilo za trigger na nivou baze.

Trenutni model takav trigger ne definiše.

---

### 5. Zašto ne koristiti `datetime.now()` umesto `func.now()`?

Ovo su dva različita pristupa:

```python
datetime.now()  # Python odmah izračunava vrednost
func.now()      # SQLAlchemy priprema SQL izraz za bazu
```

Za SQLAlchemy Python-side default može se proslediti funkcija, na primer `default=datetime.now` (bez zagrada), kako bi se pozvala prilikom unosa.

Pisanje `default=datetime.now()` nije isto: zagrade pozivaju funkciju odmah, pri učitavanju modula, pa bi model mogao da koristi već izračunatu vrednost umesto novog vremena za svaki red.

U ovom modelu izabran je `server_default=func.now()`: bazu se pita za vreme pri unosu, a ne Python proces. To je naročito korisno kada se podaci upisuju na više načina, jer podrazumevana vrednost dolazi sa DB strane. Vreme generisano na DB strani i vreme generisano u Python-u mogu se razlikovati ako serveri imaju različito podešene satove ili zone.

---

### 6. Vremenske zone i SQLite u ovom projektu

U modelu je upotrebljen `DateTime` bez `timezone=True`; to je SQLAlchemy kolona bez eksplicitne podrške za vremensku zonu. SQLite nema namenski datum/vreme tip kao neke druge baze: SQLAlchemy vrednosti datuma i vremena čuva i ponovo parsira kroz tekstualni prikaz.

SQLite `CURRENT_TIMESTAMP`, koji se koristi kao DB podrazumevana vrednost u ovom slučaju, predstavlja UTC vreme, ali njegov tekstualni prikaz nema eksplicitan `+00:00` pomeraj. Zato vrednost pročitana u Python-u može biti naivan `datetime` iako je konvencija za sačuvanu vrednost UTC. U ovom projektu je važno da svi delovi aplikacije dosledno tumače te vrednosti kao UTC i da ne mešaju naivne lokalne datume sa njima.

`DateTime(timezone=True)` može izraziti nameru da kolona koristi vremensku zonu, ali mogućnosti zavise od baze; samo dodavanje te opcije ne garantuje da će SQLite sačuvati i vratiti `tzinfo` (informaciju o vremenskoj zoni) na način na koji to radi baza sa pravim timezone tipom. Za sada treba razumeti postojeću šemu; ako projekat kasnije zahteva precizno timezone ponašanje, treba odabrati i proveriti jedinstvenu strategiju čuvanja UTC vrednosti.

---

### 7. Tok vrednosti kroz aplikaciju

Pojednostavljeno, za novi `Item` tok je:

1. SQLAlchemy generiše `INSERT` bez `created_at`/`updated_at`, jer ih baza obezbeđuje podrazumevanim vrednostima.
2. Baza upisuje red i izračunava početna vremena.
3. SQLAlchemy može da dobije te vrednosti iz baze tokom `flush`-a ili da ih učita kada su potrebne, u zavisnosti od mogućnosti baze i podešavanja.
4. Kada ORM izmeni red, `onupdate` dodaje novu vrednost `updated_at` u generisani `UPDATE`.
5. Ako se red ažurira direktnim SQL-om, korak 4 se ne dešava; SQL upit mora sam da menja `updated_at` ili baza mora imati trigger.

---

### Kratak pregled

| Pojam                 | Uloga u ovom projektu                                           |
| --------------------- | --------------------------------------------------------------- |
| Python `datetime`     | Tip vrednosti koju aplikacija koristi i čita                    |
| SQLAlchemy `DateTime` | Tip kolone u ORM modelu                                         |
| `func.now()`          | SQL izraz za vreme koje izračunava baza                         |
| `server_default`      | Vrednost koju baza postavlja pri unosu ako kolona nije navedena |
| `onupdate`            | Vreme koje SQLAlchemy dodaje svojim `UPDATE` upitima            |
| `created_at`          | Vreme kreiranja reda                                            |
| `updated_at`          | Vreme poslednje izmene kroz SQLAlchemy                          |

Ukratko, `datetime` je Python-ov način predstavljanja datuma i vremena, `DateTime` opisuje kolonu, `server_default` obezbeđuje početnu vrednost u bazi, a `onupdate` ažurira vreme pri izmenama koje prolaze kroz SQLAlchemy.

---

## Pitanje 3

Objasni mi detaljno `decimal.Decimal` u kontekstu Pythona i SQLAlchemy ORM-a.

---

## Odgovor 3

### 1. Šta je `decimal.Decimal`?

`decimal` je standardni Python modul za decimalnu aritmetiku, a `Decimal` je klasa iz tog modula:

```python
from decimal import Decimal

price = Decimal("19.99")
```

`Decimal` predstavlja decimalne brojeve na način koji je pogodan za iznose kao što su cene. Za razliku od binarnog tipa `float`, decimalni zapisi poput `0.1` mogu se predstaviti tačno:

```python
0.1 + 0.2
# 0.30000000000000004

Decimal("0.1") + Decimal("0.2")
# Decimal("0.3")
```

Ova razlika je važna kada se sabiraju, množe ili porede novčani iznosi: sitne greške zaokruživanja mogu se akumulirati kroz mnogo operacija.

---

### 2. Zašto se `Decimal` pravi iz teksta, a ne iz `float` vrednosti?

Koristi tekstualni zapis decimalnog broja:

```python
Decimal("0.10")
```

Izbegavaj ovo:

```python
Decimal(0.10)  # Ovo može dati nepreciznu vrednost zbog binarnog float-a. Bolje je koristiti string kao ulaz za Decimal.
```

`0.10` je prvo izračunato kao binarni `float`; `Decimal` zatim tačno predstavlja tu već približnu vrednost. Zato rezultat može biti veoma dugačak, na primer `0.10000000000000000555...`. Pretvaranje iz stringa čuva nameravani decimalni zapis.

Ako vrednost već dolazi kao `float`, `Decimal(str(value))` može da pretvori njegov kratki tekstualni prikaz, ali to ne vraća informaciju izgubljenu pre konverzije. Za API ulaz i novčane proračune bolje je izbeći nepotrebni `float` korak i proslediti decimalni tekst ili vrednost parsirati direktno kao `Decimal`.

---

### 3. `Decimal` ne znači automatski „uvek dve decimale“

`Decimal` može da predstavlja različit broj decimalnih mesta:

```python
Decimal("12.3")
Decimal("12.30")
Decimal("12.300")
```

Ti zapisi imaju jednaku numeričku vrednost, ali različit eksponent, odnosno različit prikaz preciznosti. Drugim rečima, `Decimal("12.3")` i `Decimal("12.30")` su numerički jednaki, ali prvi ima jednu decimalu, a drugi dve. Ako pravilo aplikacije zahteva dve decimale, može se eksplicitno kvantizovati:

```python
from decimal import Decimal, ROUND_HALF_UP

price = Decimal("19.995")
rounded_price = price.quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP,
)
# Decimal("20.00")
```

`quantize()` vraća novi `Decimal` sa željenim brojem decimala; originalni `Decimal` ostaje nepromenjen.

`quantize()` određuje broj decimala; `rounding` određuje pravilo zaokruživanja. `ROUND_HALF_UP` je često razumljiv primer, ali nije univerzalno ispravan za svaki finansijski domen — poslovna pravila treba da odaberu način zaokruživanja. Deljenje takođe može dati beskonačan decimalni zapis, pa se i tada preciznost i zaokruživanje moraju odrediti namerno.

---

### 4. Kako se `Decimal` koristi u ovom SQLAlchemy modelu?

U [models.py](../models.py) `Items.price` je definisan ovako:

```python
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

price: Mapped[Decimal] = mapped_column(
    Numeric(10, 2),
    nullable=False,
)
```

Ovde postoje dva povezana, ali različita opisa:

- `Mapped[Decimal]` označava da se u Python-u očekuje `Decimal` vrednost.
- `Numeric(10, 2)` je SQLAlchemy tip kolone za decimalne brojeve. Prvi broj (`10`) je ukupna preciznost, a drugi (`2`) broj cifara posle decimalne tačke. U bazi koja strogo sprovodi taj tip to znači do 8 cifara pre i 2 posle decimalne tačke, na primer `99999999.99`.
- `nullable=False` zabranjuje `NULL`; sam po sebi ne zabranjuje nulu, negativan iznos ili iznos izvan poslovnog opsega.

Python vrednost za objekat treba napraviti kao `Decimal`, najčešće iz stringa:

```python
item = Items(
    title="Portfolio landing page",
    price=Decimal("125.50"),
    owner_id=1,
    category_id=1,
)
```

Zatim se objekat dodaje i čuva u sesiji:

```python
session.add(item)
session.commit()
session.refresh(item)
```

Pri čitanju objekta kroz ORM, `item.price` je namenjen da bude Python `Decimal`, a ne `float`. SQLAlchemy povezuje Python tip sa `Numeric` kolonom i prosleđuje vrednosti kroz DBAPI parametre; ne treba ručno sastavljati SQL string konkatenacijom cene.

---

### 5. Šta garantuje `Numeric(10, 2)` — a šta ne?

SQLAlchemy `Numeric(10, 2)` opisuje željeni decimalni tip, preciznost i skalu kolone, ali konačno ponašanje zavisi i od baze i njenog DBAPI drajvera. Neke baze strože sprovode preciznost i skalu. SQLite koristi fleksibilan sistem tipova i numeric affinity; samo deklarisanje `NUMERIC(10, 2)` ne pruža istu strogu garanciju zaokruživanja i odbijanja nevažećih vrednosti kao stroža baza.

SQLAlchemy `Numeric` po podrazumevanom ponašanju cilja Python `Decimal`, ali način prenosa i konverzije zavisi od dijalekta i drajvera. Činjenica da aplikacija dobije `Decimal` objekat ne dokazuje sama po sebi da je baza sačuvala svaku operaciju sa neograničenom finansijskom preciznošću. Zato treba odvojeno razmišljati o:

1. Python tipu i načinu na koji se vrednosti računaju;
2. deklaraciji kolone u SQLAlchemy modelu;
3. stvarnim ograničenjima konkretne baze.

Ako aplikacija mora da odbije cenu sa više od dve decimale ili negativnu cenu, dodaj odgovarajuću validaciju na ulazu i, po potrebi, ograničenje i u bazi. `Numeric(10, 2)` i `nullable=False` sami po sebi ne izražavaju sva domenska pravila.

---

### 6. Gde zaokruživanje treba da se desi?

Zaokruživanje treba da bude namerna poslovna odluka, a ne slučajni efekat konverzije u `float` ili upisa u bazu. Na primer:

```python
from decimal import Decimal, ROUND_HALF_UP

subtotal = Decimal("19.99") * 3
tax = (subtotal * Decimal("0.20")).quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP,
)
total = subtotal + tax
```

Konstante za decimalne iznose piši kao stringove (`Decimal("0.20")`), ne kao `Decimal(0.20)`. Tako se u kodu vidi precizno nameravana decimalna vrednost. Takođe vodi računa da se poređenje radi između kompatibilnih tipova — ne mešaj `Decimal` i `float` u istom računu.

---

### 7. Kako se ovo povezuje sa budućim FastAPI/Pydantic slojem?

Kada se implementiraju Pydantic šeme, polje za cenu treba predstavljati kao `Decimal`, tako da se ulaz validira kao decimalna vrednost pre nego što se dodeli ORM polju. Pydantic validacija može da ograniči, na primer, broj cifara, decimalnih mesta ili minimalnu cenu. ORM model i baza i dalje imaju svoju odgovornost — Pydantic ne štiti direktne SQL upite niti druge načine upisa u bazu već samo ulaz kroz Pydantic šeme (Python strana aplikacije).

Trenutni `schemas.py` još ne definiše te šeme, pa ograničenja ulazne validacije tek treba dodati. Pri JSON prenosu treba takođe odabrati dosledan format za cenu; API-ji često serijalizuju `Decimal` kao decimalni string da bi se izbeglo predstavljanje cene kao približnog binarnog `float`-a.

---

### 8. Alternativa: čuvanje najmanjih novčanih jedinica

Za neke finansijske sisteme jednostavnije je čuvati cenu kao ceo broj najmanjih jedinica — na primer, 125.50 kao 12550 centi. Tada se koristi Python `int` i SQL `INTEGER`, pa se izbegava decimalna aritmetika u bazi.

Ovaj pristup zahteva da valuta i broj manjih jedinica budu jasno definisani; ne važi svuda pravilo da svaka valuta ima tačno 100 manjih jedinica.

Za trenutni edukativni projekat `Decimal` uz `Numeric(10, 2)` je dobar način da se nauči decimalni tip u ORM-u. Za produkcionu finansijsku aplikaciju potrebno je dodatno definisati valutu, zaokruživanje, dozvoljeni opseg, validaciju i ponašanje konkretne baze.

---

### Ukratko

- Koristi `Decimal("19.99")`, a ne `Decimal(19.99)`.
- `Mapped[Decimal]` je Python tip, `Numeric(10, 2)` je SQLAlchemy tip kolone.
- `Decimal` smanjuje greške binarne `float` aritmetike, ali ne bira
  poslovno pravilo zaokruživanja umesto tebe.
- SQLite ne sprovodi `NUMERIC(10, 2)` kao strogu fiksno-decimalnu garanciju.
- Validacija ulaza, ograničenja baze i pravila računanja se dopunjuju. Nijedno samo ne zamenjuje ostala tri aspekta.

---

## Pitanje 4

Objasni mi `enum` u kontekstu `Pydantic` i `FastAPI`.

---

## Odgovor 4

### 1. Šta znači enum?

`Enum` je skraćeno od **enumeration** — nabrajanje. U programiranju je to tip koji predstavlja jednu vrednost iz unapred definisanog, ograničenog skupa mogućnosti.

Primer: ako portfolio stavka može biti samo nacrt ili objavljena, moguće vrednosti su:

- `draft`
- `published`

Enum imenuje te dozvoljene opcije i daje imena koja se koriste u Python kodu. Umesto da svuda ručno pišeš stringove poput `"draft"` i `"published"`, definišeš skup jednom:

```python
from enum import Enum


class ItemStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
```

Ovde:

- `ItemStatus` je naziv novog enum tipa enum-a.
- `DRAFT` i `PUBLISHED` su njegovi članovi (members) enum-a.
- `"draft"` i `"published"` su vrednosti tih članova enum-a.
- `ItemStatus.DRAFT` je enum član, a `ItemStatus.DRAFT.value` je njegov običan string (`"draft"`).

Možeš ga zamisliti kao skup unapred imenovanih, dozvoljenih opcija. Za razliku od slobodnog stringa, ne možeš slučajno dobiti novu validnu opciju kao što su `"publshed"` ili `"archived"` — one nisu članovi ovog enum-a.

---

### 2. Zašto `class ItemStatus(str, Enum)` nasleđuje od dve klase?

`Enum` omogućava definisanje ograničenog skupa članova. `str` označava da su vrednosti enum-a stringovi, što je zgodno za JSON API-je, baze koje čuvaju tekst i čitljiv prikaz:

```python
ItemStatus.DRAFT
ItemStatus.DRAFT.name   # "DRAFT"
ItemStatus.DRAFT.value  # "draft"
```

Član `enum`-a i `njegova vrednost` (`value`) nisu isti pojam:

| Izraz                    | Značenje                       |
| ------------------------ | ------------------------------ |
| `ItemStatus.DRAFT`       | Python enum član               |
| `ItemStatus.DRAFT.name`  | ime člana u kodu: `"DRAFT"`    |
| `ItemStatus.DRAFT.value` | pridružena vrednost: `"draft"` |

U ovom projektu su imena članova napisana velikim slovima, što je uobičajena konvencija za konstante u Python-u. Vrednosti koje se prenose kroz API i čuvaju u bazi su malim slovima.

---

### 3. Zašto ne koristiti obične stringove?

Običan string može sadržati bilo šta:

```python
status = "publshed"  # greška u kucanju, ali i dalje običan validan string
```

`Enum`, međutim, jasno ograničava dozvoljene izbore:

```python
status = ItemStatus.PUBLISHED
```

To smanjuje greške u kucanju, čini dozvoljene vrednosti vidljivim u kodu i omogućava alatima za tipove da lakše otkriju pogrešnu upotrebu.

`Enum` je koristan kada je skup opcija mali i kontrolisan kodom, kao što su:

- status stavke: `draft`, `published`;
- nivo logovanja: `debug`, `info`, `warning`;
- način isporuke: `standard`, `express`.

`Enum` nije dobar izbor za vrednosti koje korisnici često dodaju ili menjaju. Na primer, kategorije portfolio stavki su tabela `categories`, a ne enum: administrator može dodati kategoriju bez promene Python koda i nove verzije aplikacije.

---

### 4. Kako Pydantic koristi enum?

Pydantic koristi enum tip u šemi da validira podatke. Primer buduće ulazne šeme za stavku mogao bi izgledati ovako:

```python
from pydantic import BaseModel


class ItemCreate(BaseModel):
    title: str
    status: ItemStatus = ItemStatus.DRAFT
```

Ako Pydantic dobije:

```python
ItemCreate(title="Portfolio site", status="published")
```

string `"published"` se proverava i pretvara u Python vrednost `ItemStatus.PUBLISHED`. U modelu zatim možeš koristiti enum član:

```python
item.status == ItemStatus.PUBLISHED
item.status.value  # "published"
```

Ako dobije nepoznatu vrednost:

```python
ItemCreate(title="Portfolio site", status="archived")
```

Validacija ne prolazi, jer `archived` nije među definisanim opcijama. Pydantic prijavljuje grešku umesto da tiho prihvati novu vrednost.

Kada se enum koristi za opcionalno polje, opcionalnost se navodi posebno:

```python
status: ItemStatus | None = None
```

To znači da je vrednost ili jedan od enum članova ili `None`. Sam enum ne znači da je polje opcionalno.

---

### 5. Kako se enum uklapa u FastAPI zahtev i odgovor?

FastAPI koristi Pydantic šeme za validaciju HTTP podataka. Ako endpoint prima `ItemCreate`, JSON zahtev može sadržati:

```json
{
  "title": "Portfolio site",
  "status": "published"
}
```

Pojednostavljen tok je:

1. Klijent pošalje tekst `"published"` u JSON-u.
2. FastAPI prosledi podatke Pydantic validaciji.
3. Pydantic proveri da li je tekst jedna od dozvoljenih enum vrednosti.
4. Ako jeste, Python kod dobija `ItemStatus.PUBLISHED`.
5. Ako nije, FastAPI vrati standardnu grešku validacije HTTP `422` umesto da pozove endpoint sa pogrešnom vrednošću.

Pri pravljenju odgovora FastAPI/Pydantic serijalizuje enum u njegovu javnu vrednost, dakle `"published"`, a ne u Python-ov interni prikaz člana.

Enum se može koristiti i kao query parametar ili path parametar, ne samo u
JSON telu. Na primer, parametar `status: ItemStatus` u endpoint-u bi prihvatao samo dozvoljene tekstualne vrednosti.

Pojednostavljen primer endpoint-a mogao bi da izgleda ovako:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ItemCreate(BaseModel):
    title: str
    status: ItemStatus = ItemStatus.DRAFT


@app.post("/items", response_model=ItemCreate)
def create_item(item: ItemCreate) -> ItemCreate:
    return item
```

Ovaj primer samo ilustruje FastAPI/Pydantic validaciju i serijalizaciju; trenutni `schemas.py` i API rute u projektu još nisu implementirani.

---

### 6. Šta dobijaš u OpenAPI dokumentaciji?

Kada enum pripada Pydantic šemi ili se koristi kao FastAPI parametar, FastAPI uključi dozvoljene vrednosti u OpenAPI šemu. Swagger UI (`/docs`) može ih prikazati kao unapred definisane opcije, umesto da korisnik mora sam da pogodi dozvoljen tekst.

Za trenutni enum šema je suštinski:

```json
{
  "type": "string",
  "enum": ["draft", "published"]
}
```

Time enum pomaže i serveru i korisniku API-ja: server validira vrednost, a OpenAPI dokumentacija objašnjava koje su vrednosti prihvaćene.

---

### 7. Kako je `ItemStatus` povezan sa SQLAlchemy modelom?

U `models.py` enum je definisan jednom:

```python
class ItemStatus(str, PythonEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
```

I koristi se za ORM polje:

```python
status: Mapped[ItemStatus] = mapped_column(
    SQLAlchemyEnum(
        ItemStatus,
        name="item_status",
        native_enum=False,
        create_constraint=True,
        values_callable=lambda enum_type: [
            member.value for member in enum_type
        ],
    ),
    default=ItemStatus.DRAFT,
    server_default=ItemStatus.DRAFT.value,
    nullable=False,
)
```

U ovom fajlu SQLAlchemy-jev `Enum` je uvezen kao `SQLAlchemyEnum`, a standardni Python `Enum` kao `PythonEnum`, da bi se njihova dva različita značenja mogla jasno razlikovati.

Važne postavke:

- `SQLAlchemyEnum(ItemStatus, ...)` kaže ORM-u da kolona koristi Python enum.

- `native_enum=False` traži tekstualnu kolonu umesto posebnog native enum tipa baze. To je praktično za SQLite, koji nema isti native enum tip kao neke druge baze.

- `create_constraint=True` traži ograničenje baze koje dopušta samo navedene vrednosti.

- `values_callable=...` kaže SQLAlchemy-ju da sačuva `.value` vrednosti (`draft`, `published`), a ne imena Python članova (`DRAFT`, `PUBLISHED`). Bez ove postavke SQLAlchemy Enum podrazumevano čuva imena članova.

- `default=ItemStatus.DRAFT` je SQLAlchemy/ORM podrazumevana vrednost pri unosu kroz ORM.

- `server_default=ItemStatus.DRAFT.value` daje bazi podrazumevanu vrednost `"draft"` kada `INSERT` ne navede status.

- `nullable=False` ne dozvoljava `NULL`.

Dakle, u Python-u se koristi `ItemStatus.DRAFT`, API-ju se šalje string `"draft"`, a SQLite kolona čuva tekst `draft` i ima ograničenje za dozvoljene vrednosti. To su različiti slojevi koji zajedno obezbeđuju konzistentan status.

---

### 8. Pydantic enum i SQLAlchemy enum nisu dve definicije skupa

Važno je razlikovati:

- **Python `Enum`** — definiše članove i vrednosti u aplikacionom kodu;
- **Pydantic** — koristi taj Python tip da validira API podatke;
- **SQLAlchemy `Enum`** — mapira taj tip na DB kolonu i, po postavkama,
  ograničava vrednosti u bazi.

U idealnom slučaju Pydantic šema i ORM model koriste isti Python `ItemStatus` tip. Tako se skup mogućih vrednosti ne prepisuje na više mesta i ne može lako doći do neslaganja, na primer Pydantic dopušta `"published"`, a ORM ili baza ne.

U ovom projektu `ItemStatus` je za sada u `models.py`, a `schemas.py` još nema implementirane Pydantic modele. Kada se šeme budu dodavale, treba ponovo koristiti isti enum, a ne praviti drugi, gotovo identičan enum.

Ako zajednički enum počne da stvara ciklične importe, može se izdvojiti u zaseban zajednički modul, na primer `enums.py`; za sada nema potrebe unapred menjati strukturu.

---

### 9. Podrazumevana vrednost nije isto što i dozvoljeni skup

Enum odgovara na pitanje: **koje su vrednosti dozvoljene?**

Podrazumevana vrednost odgovara na pitanje: **koju vrednost koristiti ako nije prosleđena?**

Za ovaj model:

- dozvoljeno: `draft` ili `published`;
- podrazumevano: `draft`.

`default=ItemStatus.DRAFT` i `server_default="draft"` postavljaju default u ORM-u i bazi, ali ne znače da enum ima samo jednu dozvoljenu vrednost.

Eksplicitni `"published"` je i dalje validan. Podrazumevana vrednost samo olakšava kreiranje novih zapisa bez eksplicitnog navođenja statusa, ali ne ograničava skup dozvoljenih vrednosti.

Ako se kasnije želi obavezno slanje statusa kroz API, uklanja se Pydantic šema default — to je odvojena odluka od ORM i baze default vrednosti.

---

### 10. Enum vrednosti su deo API ugovora

Kada se klijent oslanja na `"draft"` i `"published"`, te vrednosti postaju deo API ugovora. Promena `"published"` u `"public"` može da pokvari postojeće klijente i podatke u bazi. Dodavanje nove vrednosti takođe treba da bude pažljivo: aplikacija, OpenAPI šema i ograničenje baze moraju svi da je prihvate. Ako je baza već kreirana, promena DB ograničenja može zahtevati migraciju; menjanje Python enum klase samo po sebi ne menja postojeću šemu.

---

### Ukratko

- `enum` je ograničen skup imenovanih opcija.
- `ItemStatus.PUBLISHED` je Python enum član, a `.value` je `"published"`.

- `Pydantic` pretvara i validira API string prema enum-u. Nepoznata vrednost
  izaziva validacionu grešku.

- `FastAPI` koristi enum u zahtevima, odgovorima, query/path parametrima i
  OpenAPI dokumentaciji.

- `SQLAlchemy` mapira isti Python enum na kolonu. Postavke modela određuju
  format i ograničenja u bazi.

- `enum` je prikladan za male, kontrolisane skupove, ne za kategorije koje korisnici treba da dodaju dinamički.

- `default` vrednost ne menja skup dozvoljenih vrednosti; ona samo olakšava kreiranje novih zapisa.

- `server_default` postavlja podrazumevanu vrednost na nivou baze, ali takođe ne menja skup dozvoljenih vrednosti.

- Promena `enum` vrednosti u Python kodu ne menja automatski postojeće podatke u bazi. Za to je potrebna migracija ili ručna izmena.
