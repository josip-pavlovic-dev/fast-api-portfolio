# Lekcija 08: Obavezna polja, `NULL` i prazne vrednosti

## Cilj lekcije

Pri definisanju kolona ne određujemo samo njihov tip. Za svako polje treba odlučiti da li zapis sme da postoji bez vrednosti u tom polju. Ova lekcija uvodi `nullable=False` i objašnjava šta baza smatra nedostajućom vrednošću.

Glavna pravila:

- `nullable=False` zabranjuje SQL vrednost `NULL` u koloni;
- `nullable=True` dozvoljava da kolona bude `NULL`;
- dozvoljenost `NULL` vrednosti nije isto što i zabrana praznog teksta;
- odluka da li je polje obavezno najčešće je poslovno pravilo, a ne univerzalno pravilo za sve aplikacije.

---

## Šta znači „obavezno“

U kontekstu baze, obavezno polje znači da za red u toj koloni mora postojati vrednost koja nije `NULL`. Na primer, kategorija bez imena verovatno ne bi bila korisna u ovom sistemu. Zato kurs odlučuje da su `name`, `slug` i druga polja obavezna.

To je odluka o konkretnom domenu. Druga aplikacija može dozvoliti da kategorija privremeno nema slug ili da opis proizvoda bude nepoznat. ERD i poslovna pravila treba da obrazlože šta je obavezno.

Primarni ključ je poseban slučaj: vrednost primarnog ključa ne može biti `NULL`. Međutim, u ovoj verziji priložene skripte nijednom modelu još nije dodat primarni ključ; to je nedovršenost snapshot-a iz prethodnih lekcija.

---

## `nullable=False`

U kursnom stilu sa `Column(...)`, zabranu `NULL` vrednosti definišemo imenovanim argumentom:

```python
name = Column(String(50), nullable=False)
```

Ova postavka je deo SQLAlchemy metapodataka kolone. Kada se tabela kreira iz tih metapodataka (npr. pomoću `Base.metadata.create_all()`) ili izmeni migracijom (npr. pomoću `Alembic`-a), u šemi baze dobija se ograničenje `NOT NULL`. Ako se pri upisu u tako definisanu kolonu pokuša sačuvati `NULL`, baza odbija red. Naknadna promena Python modela ne menja automatski iz njega već kreiranu postojeću tabelu. Da bi se promena odrazila u bazi, potrebno je izvršiti odgovarajuću migraciju.

`ORM objekat` može postojati u Python-u sa nepostavljenim atributom (npr. `name` je `None`), ali se ograničenje proverava tek kada se promena pošalje bazi, tipično pri `flush()` ili `commit()`.

`flush()` je metoda koja šalje promene ORM objekata bazi, a `commit()` trajno čuva te promene.

Kod obične `Column` kolone koja nije primarni ključ, `nullable` je podrazumevano `True` ako nije drugačije navedeno.

`Primarni ključ` je izuzetak: baza zahteva da bude nenullable i jedinstven. Ne treba dodavati odvojena `nullable=False` i `unique=True` pravila na istu PK kolonu.

U ovom kursu se `nullable=False` navodi na kolonama za koje je autor odlučio da moraju imati vrednost.

Primer nullable kolone, kao što bi mogao biti opcion `parent_id`:

```python
parent_id = Column(Integer, nullable=True)
```

`nullable=True` dozvoljava `NULL`, ali ne zahteva da vrednost bude izostavljena. Može se proslediti i konkretan roditeljski ID.

---

## Tipizovani ORM u SQLAlchemy 2.x

U našem praktičnom kodu koristimo `Mapped[...]` i `mapped_column()`:

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

naziv: Mapped[str] = mapped_column(String(50), nullable=False)
opis: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Kada `nullable` nije naveden, `SQLAlchemy 2.x` ga po pravilu zaključuje iz `Mapped` anotacije: `Mapped[str]` označava `nullable=False` kolonu, a `Mapped[str | None]` `nullable=True` kolonu.

U nastavku lekcije navodimo `nullable=False` eksplicitno da bi ograničenje baze bilo jasno na mestu deklaracije. Ovo je više zbog nas samih kako bismo lakše razumeli i održavali kod.

Zaključak: `Anotacija` opisuje očekivanu Python vrednost koju atribut treba da ima i pomaže alatima (npr. mypy) za tipove dok `nullable` podešava SQL kolonu. Ta dva pravila treba držati usklađenim. Primarni ključ je ne-nullable zbog `primary_key=True`.

Za `opcionog roditelja`, SQLAlchemy 2.x zapis izgleda ovako:

```python
parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

`opcioni roditelj` (`parent_id`) je kolona koja preko stranog ključa čuva ID roditeljskog zapisa iz iste ili druge tabele. Može biti `NULL` ako zapis nema roditelja; ako roditelja ima, čuva njegov ID.

---

## `NULL` nije isto što i prazan tekst

Za tekstualnu kolonu treba razlikovati nekoliko stanja:

| Vrednost    | Značenje                                                   |
| ----------- | ---------------------------------------------------------- |
| `NULL`      | nema vrednosti, vrednost je nepoznata ili nije dostavljena |
| `""`        | postoji tekstualna vrednost čija je dužina nula            |
| `"   "`     | postoji tekst sastavljen od razmaka                        |
| `"telefon"` | postoji tekstualna vrednost                                |

`nullable=False` odbija `NULL`, ali samo po sebi ne odbija `""` ili tekst od razmaka. Dakle, `name = Column(String(50), nullable=False)` ne garantuje da je naziv smislen ili da sadrži vidljive znakove.

U SQLAlchemy `Column` deklaraciji ne postoji opšti argument `blank=False` (zabrana praznog teksta) koji bi radio kao `validacija forme`. Provera da tekst nije prazan obično se radi na `ulaznom sloju aplikacije`, na primer `Pydantic šemom`. Ako isto pravilo mora da važi za sve klijente baze, može se dodati odgovarajuće `CHECK` ograničenje.

ZAKLJUČAK: Pravilo za prazan tekst je odvojeno od `NOT NULL` ograničenja.

---

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

Ako vrednost nije prosleđena, navedeni SQLAlchemy default-i obezbeđuju `False` ili `0` pri unosu preko SQLAlchemy-ja. U tabeli se i dalje ne dozvoljava `NULL`.

Ovde je `default=False` SQLAlchemy client-side default podešavanje čija je vrednost običan Python `bool`; nije SQL izraz niti serverski default. SQLAlchemy koristi tu default vrednost pri pripremi INSERT-a kada upis preko SQLAlchemy-ja ne prosledi vrednost za kolonu.

Ako upis zaobiđe SQLAlchemy, SQLAlchemy client-side default nije dostupan; drugi klijent šalje vrednost koju je sam pripremio. Ako SQL iskaz eksplicitno prosledi `NULL`, client-side default se ne primenjuje: baza dobija `NULL` i prihvata ga samo ako kolona dozvoljava null vrednosti. Važna ORM nijansa: dodela Python `None` atributu nije uvek isto što i eksplicitno slanje SQL `NULL`. Za kolonu sa default-om ORM najčešće tretira `None` kao izostavljenu vrednost i izostavi kolonu iz INSERT-a, tako da SQLAlchemy default može da se primeni. Ako je namera da se zaista pošalje SQL `NULL`, to treba eksplicitno označiti, na primer SQLAlchemy izrazom `null()`; `nullable=False` će tada dovesti do odbijanja upisa u bazi.

Za serverski default koristi se `server_default`. On definiše vrednost u DDL šemi baze i može da je primeni na upis iz SQLAlchemy-ja, SQL konzole, skripte ili drugog klijenta, ali samo ako taj INSERT izostavi kolonu ili navede `DEFAULT`. Ako INSERT eksplicitno prosledi `NULL`, server default se ne koristi; `NOT NULL` ograničenje tada odbija upis.

Ovo pravilo opisuje SQL koji stiže do baze. Kod ORM objekta sa atributom postavljenim na `None`, ORM može izostaviti kolonu iz INSERT-a kada postoji server default, pa baza primeni taj default. Eksplicitni SQL `NULL` i ORM atribut `None` zato ne treba automatski smatrati istim slučajem.

`DDL` (Data Definition Language) šema baze definiše strukturu tabele, uključujući kolone, tipove podataka, ograničenja i default vrednosti. Serverski default se definiše u DDL šemi i primenjuje se na upise koji ne prosleđuju vrednost za kolonu.

Polje kao `name` nema default u source kodu, pa aplikacija treba da mu dodeli vrednost. Sama Python anotacija nije runtime validacija: obaveznost trajno sprovodi `NOT NULL` ograničenje u bazi.

### Šta se dešava od Python objekta do INSERT-a?

Primer u nastavku koristi `Product` kao ORM model. U našem praktičnom modelu sva obavezna polja bez default-a moraju biti prosleđena:

```python
product = Proizvod(
	naziv="Laptop",
	slug="laptop",
	opis="Prenosni računar",
	cena=Decimal("1000.00"),
)
session.add(product)
```

1. **Kreiranje objekta:** dobija se Python instanca mapirane ORM klase. Samo kreiranje instance ne šalje upit bazi. Python tipovi i `Mapped[...]` anotacije pomažu pri tipizaciji, ali sami po sebi ne validiraju obavezna polja u runtime-u.

2. **Praćenje sesije:** `session.add(product)` dodaje novi objekat u sesiju. Sesija prati njegove izmene; još uvek ne mora da bude izvršen INSERT. U deklarativnom stilu koji koristimo klasa nasleđuje zajednički `Base`, koji obezbeđuje ORM mapiranje i zajedničke metapodatke. Postoje i drugi načini mapiranja koji ne koriste baš ovaj obrazac nasleđivanja.

3. **Flush i priprema iskaza:** pri `session.flush()`, ORM Unit of Work utvrđuje koje objekte treba upisati i priprema i izvršava odgovarajuće iskaze, kao što su `INSERT`, `UPDATE` i `DELETE`. `session.commit()` automatski poziva flush pre nego što potvrdi transakciju, pa u uobičajenom slučaju nije potrebno ručno pozivati obe metode.

`flush()` se poziva zasebno kada želimo da se iskazi pošalju bazi pre završetka transakcije, na primer da bismo dobili generisani primarni ključ; sam flush ne potvrđuje transakciju i promene se i dalje mogu poništiti pozivom `session.rollback()`.

4. **Dijalekt i kompajliranje:** engine već ima dijalekt izabran prema URL-u i drajveru baze. SQLAlchemy koristi taj dijalekt dok kompajlira iskaz u odgovarajući SQL i prilagođava bind parametre i rezultate konkretnom DBAPI drajveru. Dijalekt nije nešto što se prvi put uključuje tek nakon generisanja SQL-a.

5. **Client-side default-i:** tokom pripreme/izvršavanja SQLAlchemy INSERT-a, SQLAlchemy primenjuje `default` za kolone za koje upis nije dao vrednost. `default=False` obezbeđuje Python vrednost `False`; `default=func.now()` ubacuje SQL izraz `now()` u INSERT, koji zatim izvršava baza. Python callable se poziva u Python-u. Ovi default-i se ne moraju pojaviti na atributu objekta odmah posle njegovog kreiranja.

6. **Izvršavanje i ograničenja baze:** SQLAlchemy šalje iskaz preko konekcije, a baza izvršava INSERT. Baza primenjuje `server_default` za izostavljenu kolonu ili `DEFAULT` i sprovodi ograničenja kao što su `NOT NULL`, `UNIQUE` i strani ključevi. SQLAlchemy ne proverava unapred svako `nullable=False` polje na instanci; ako INSERT pokuša da upiše `NULL`, baza odbija red i greška se obično prijavi tokom flush-a.

7. **Rezultat i ORM stanje:** nakon uspeha SQLAlchemy preuzima generisani primarni ključ i druge vrednosti koje podržani dijalekt može da vrati, na primer pomoću `RETURNING`. Vrednosti serverskih default-a mogu zahtevati vraćanje kroz `RETURNING` ili dodatno učitavanje; nije garantovano da će svaki dijalekt automatski vratiti svaku takvu vrednost. Sesija zatim usklađuje stanje mapiranog objekta sa rezultatom upisa.

ORM stanje ima preciznije nazive od `CREATED`, `UPDATED` i `DELETED`. Na primer, nov objekat je najpre `transient`, posle `session.add()` postaje `pending`, a posle uspešnog flush-a `persistent`. Izmenjeni persistent objekat sesija prati kao dirty; brisanje se takođe evidentira kroz sesiju. Ova stanja opisuju ORM objekat i njegov odnos sa sesijom, ne vrednosti kolona u tabeli.

Ako baza odbije flush zbog ograničenja integriteta, transakcija sesije ne može normalno da se nastavi dok aplikacija ne pozove `session.rollback()` ili ne zatvori sesiju.

---

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

---

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

---

## `NULL` i poslovna validacija na različitim slojevima

`nullable=False` je ograničenje baze. Ono je poslednja zaštita pri trajnom upisu, ali ne zamenjuje validaciju ulaza. API obično treba da proveri podatak pre nego što pokuša upis (npr. kroz Pydantic šemu ili ručnu proveru), kako bi korisnik dobio razumljivu poruku umesto sirove greške baze.

Za tekstualno polje validacija može proveriti da vrednost postoji, ukloniti spoljne razmake i odbiti prazan rezultat. Za broj ili datum može proveriti dozvoljen opseg ili pravila kao što je `end_date >= start_date`. Takva pravila ne nastaju automatski iz `nullable=False`.

Više slojeva može zato da dopunjuje jedno drugo:

1. `API/šema` proverava oblik i poslovno značenje ulaza.
2. `SQLAlchemy model` opisuje mapiranje i opcione ORM default-e.
3. `Baza` čuva trajna ograničenja kao što su `NOT NULL`, `UNIQUE` i `CHECK`.

---

## Napomene o prenosivosti

Osnovna razlika `NULL`/`NOT NULL` podržana je u relacijskim bazama, ali detalji ponašanja za prazne stringove i pojedina ograničenja mogu se razlikovati među bazama. Posebno ne treba zaključiti da je `""` isto što i `NULL` u svakom sistemu.

Kurski snapshot koristi klasični `Column(...)` stil, dok praktični paket koristi SQLAlchemy 2.x `Mapped[...]` i `mapped_column()`. Tipizovana anotacija može da utiče na zaključivanje nullable-a, ali ne menja osnovno značenje ograničenja. Pri prelasku između stilova proveriti i anotaciju i SQLAlchemy metapodatke kolone.

---

## Ograničenja priloženog snapshot-a

Modeli u skripti i dalje nemaju primarne ključeve, a `ProductPromotionEvent` je prazan. ORM mapiranje zato nije kompletno i fajl ne može samostalno da se izvrši kao gotov skup modela. Pored toga, `updated_at` kod proizvoda i porudžbine ima opisani problem pri unosu. To su ograničenja snapshot-a i ne treba ih mešati sa značenjem `nullable=False`.

---

## Pitanja za proveru razumevanja

1. Šta baza sprečava kada kolona ima `nullable=False`?

ODGOVOR: Baza sprečava unos `NULL` vrednosti u kolonu. Ostale provere, kao što su prazan string ili tekst od razmaka, moraju se obaviti na nivou aplikacije ili dodatnim ograničenjima u bazi.

2. Da li `nullable=False` odbija prazan string `""`?

ODGOVOR: Ne, `nullable=False` samo sprečava `NULL` vrednosti; prazan string `""` je validan. Ostale provere, kao što su dozvoljeni minimalni broj znakova ili tekst sastavljen samo od razmaka, moraju se obaviti na nivou aplikacije (npr. u Python kodu pre unosa u bazu) ili dodatnim ograničenjima u bazi (npr. `CHECK` ograničenje).

3. Koja je razlika između `NULL`, `""` i teksta sastavljenog od razmaka?

ODGOVOR: `NULL` označava odsustvo vrednosti, `""` je prazan string, a tekst od razmaka je ne-prazan string koji sadrži samo razmake.

4. Kako `default=False` pomaže koloni koja je istovremeno `nullable=False`?

ODGOVOR: `default=False` obezbeđuje početnu vrednost za kolonu, tako da baza ne odbija unos kada vrednost nije eksplicitno prosleđena preko aplikacije.

5. Da li `unique=True` zamenjuje `nullable=False`?

ODGOVOR: Ne, `unique=True` samo osigurava da vrednosti u koloni budu jedinstvene, ali ne sprečava `NULL` vrednosti.

6. Zašto `updated_at` iz skripte može da izazove grešku pri prvom unosu?

ODGOVOR: Zato što `updated_at` ima `nullable=False` i `onupdate`, ali nema default vrednost; pri prvom unosu baza očekuje eksplicitnu vrednost.

7. Gde bi proverio da naziv ne sadrži samo razmake?

ODGOVOR: Ovo se ne može osigurati samo pomoću `nullable=False`; potrebno je dodati dodatnu validaciju na nivou aplikacije ili koristiti `CHECK` ograničenje u bazi.

8. Koje polje iz transkripta nedostaje u priloženom source kodu za tabelu `Kategorija`?

ODGOVOR: Polje `parent_id` nedostaje u source kodu, iako se pominje u transkriptu i u `ERD-1.drawio` diagramu u tabeli `Kategorija`.

---

## Sažetak

- `nullable=False` mapira se na `NOT NULL`: baza odbija `NULL` vrednost u koloni.
- `NOT NULL` ne znači automatski „tekst mora sadržati vidljive znakove“; `""` i razmaci su zaseban slučaj validacije.
- `default` može obezbediti vrednost za obavezno polje, ali ne uklanja samo po sebi potrebu za baznim ograničenjem.
- `unique=True` i `nullable=False` rešavaju različite zahteve.
- Source skripta postavlja sva postojeća polja kao obavezna, ali ta odluka dolazi iz pravila kursnog primera, ne iz univerzalnog pravila.
- `updated_at` i `Order.updated_at` imaju `nullable=False` i `onupdate`, ali nemaju default; pri unosu vrednost mora biti prosleđena ili se model mora dopuniti početnim default-om.
- `parent_id` se pominje u transkriptu i u `ERD-1.drawio` diagramu u tabeli `Kategorija`. Ova tabela je kod nas smeštena u `catalog.py`, ali je `parent_id` kolona još uvek nedostajuće u source kodu pa je i mi nismo definisali u našem primeru.
- Source modeli nemaju primarne ključeve i zato nisu samostalno izvršiv ORM primer.
