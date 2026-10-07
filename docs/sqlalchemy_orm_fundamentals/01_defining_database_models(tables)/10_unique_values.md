# Lekcija 10: Jedinstvene vrednosti

## Cilj lekcije

U ovoj lekciji dodajemo `unique=True` na kolone za koje poslovno pravilo zahteva da se ista vrednost ne pojavi u više redova iste tabele.

Primeri iz source koda su `nazivi` i `slugovi` `kategorija` i `proizvoda`, `nazivi promotivnih događaja`, `korisnička imena` i `email adrese`. Jedinstvenost zavisi od namene podatka: nije svaka kolona kandidat za ovo ograničenje.

---

## Šta znači jedinstvena vrednost

Ako je vrednost kolone jedinstvena, dva reda u istoj tabeli ne mogu imati istu vrednost u toj koloni. Na primer, kada kategorija sa `name="TV"` već postoji, baza odbija drugi red koji pokušava da sačuva isti naziv kategorije.

U klasičnom SQLAlchemy stilu iz kursa pravilo se navodi ovako:

```python
name = Column(String(50), nullable=False, unique=True)
```

U našem SQLAlchemy 2.x stilu isti atribut se zapisuje pomoću `Mapped[...]` i `mapped_column()`:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

naziv: Mapped[str] = mapped_column(
	String(50),
	nullable=False,
	unique=True,
)
```

`unique=True` traži od SQLAlchemy-ja da za kolonu napravi ograničenje jedinstvenosti u šemi baze. Baza proverava pravilo pri upisu ili izmeni reda. Aplikacija može ranije proveriti da li vrednost već postoji radi korisnije poruke, ali provera u aplikaciji ne zamenjuje ograničenje baze.

### Ograničenje nad više kolona u SQLAlchemy 2.x

Složeno (kompozitno) ograničenje jedinstvenosti proverava kombinaciju vrednosti iz više kolona. Ono ne zahteva da svaka kolona pojedinačno bude jedinstvena. Pravilo glasi: ista kombinacija ne sme da se pojavi u dva reda.

Projektni primer je tabela `VezaProizvodaIPromocije`. Kada u kasnijim lekcijama dodamo strane ključeve ka proizvodu i promotivnom događaju, isti proizvod može biti povezan sa više različitih promocija, a ista promocija sa više proizvoda. Ipak, isti par proizvoda i promocije ne bi trebalo uneti dvaput. Pravilo bi bilo:

| proizvod_id | promotivni_dogadjaj_id | Dozvoljeno?                                   |
| ----------- | ---------------------- | --------------------------------------------- |
| 4           | 9                      | da, prvi unos para (4, 9)                     |
| 4           | 12                     | da, proizvod 4 učestvuje i u drugoj promociji |
| 7           | 9                      | da, promocija 9 obuhvata i drugi proizvod     |
| 4           | 9                      | ne, par (4, 9) već postoji                    |

Dakle, vrednosti `proizvod_id` smeju da se ponavljaju i vrednosti `promotivni_dogadjaj_id` smeju da se ponavljaju. Zabranjeno je samo ponavljanje njihovog para. Kada bismo umesto toga postavili `unique=True` na obe kolone pojedinačno, ograničenje bi bilo mnogo strože: `proizvod` bi mogao biti u `samo jednoj promociji`, a `promocija` bi mogla da sadrži `samo jedan proizvod`. To nije pravilo mnogostruke veze!

Ilustracija kako bi budući model mogao izgledati nakon što uvedemo strane ključeve; ovo još nije implementirano u našem projektu:

```python
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class VezaProizvodaIPromocije(Base):
	__tablename__ = "veza_proizvoda_i_promocije"
	__table_args__ = (
		UniqueConstraint("proizvod_id", "promotivni_dogadjaj_id", name="uq_proizvod_promocija"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	proizvod_id: Mapped[int] = mapped_column(ForeignKey("proizvod.id"), nullable=False)
	promotivni_dogadjaj_id: Mapped[int] = mapped_column(
		ForeignKey("promotivni_dogadjaj.id"), nullable=False
	)
```

`UniqueConstraint` dobija `imena kolona iz SQLAlchemy metapodataka`, a `ne` njihove `Python vrednosti`. `name="uq_proizvod_promocija"` je opcion, ali eksplicitno i dosledno ime olakšava čitanje migracija i kasniju izmenu ili uklanjanje ograničenja. Veće aplikacije često postave `MetaData.naming_convention`; naš projekat to još nije uveo.

Isto poslovno pravilo bi moglo biti važno za buduću `StavkaPorudzbine`: ako svaka porudžbina sme da ima najviše jedan red za dati proizvod, onda bi par `(porudzbina_id, proizvod_id)` mogao biti unique. To zavisi od pravila aplikacije: ako se isti proizvod namerno prikazuje u više redova, takvo ograničenje ne treba dodati. U oba slučaja ove FK kolone još nisu deo našeg trenutnog modela.

---

## Zašto ograničenje treba da proverava baza

Sama provera pre upisa nije dovoljna za očuvanje integriteta. Dva zahteva mogu skoro istovremeno proveriti da vrednost ne postoji; oba zatim pokušaju da je upišu. Bez ograničenja u bazi oba upisa mogu uspeti.

Sa `unique=True`, baza je konačni autoritet: samo jedan od konfliktnih upisa može uspeti. Drugi će dobiti grešku integriteta. Aplikacija treba da uhvati odgovarajući `IntegrityError`, po potrebi uradi `rollback()` transakcije i korisniku vrati razumljivu poruku. Tačan način obrade pripada sloju `upisa/API`-ja, `ne deklaraciji` kolone.

---

## Polja iz priloženog modela

Source kod ove lekcije dodaje jedinstvenost na sledeće pojedinačne kolone:

| Model            | Kolona     | Razlog iz primera                                  |
| ---------------- | ---------- | -------------------------------------------------- |
| `Category`       | `name`     | naziv identifikuje kategoriju u domenu             |
| `Category`       | `slug`     | URL adresa treba da vodi do jedne kategorije       |
| `PromotionEvent` | `name`     | nazivi promotivnih događaja ne smeju se ponavljati |
| `Product`        | `name`     | svaki naziv proizvoda je jedinstven u ovom modelu  |
| `Product`        | `slug`     | URL slug identifikuje jedan proizvod               |
| `User`           | `username` | korisničko ime je jedinstveno                      |
| `User`           | `email`    | email adresa je jedinstvena                        |

U kodu su ova polja istovremeno `nullable=False` i `unique=True`. To su različita pravila:

- `nullable=False` zabranjuje SQL `NULL`;
- `unique=True` zabranjuje ponovljene vrednosti prema pravilima baze.

U source-u `password` nije jedinstven, što je ispravno: različiti korisnici mogu imati istu lozinku. Jedinstvenost treba dodati samo kada je ponavljanje zaista zabranjeno poslovnim pravilom.

---

## Jedinstvenost jedne kolone i kombinacije kolona

`unique=True` na koloni primenjuje se na tu kolonu samu. U našem praktičnom modelu `Kategorija.naziv` i `Kategorija.slug` su zasebno jedinstveni: ne mogu postojati dve kategorije sa istim nazivom, niti dve kategorije sa istim slug-om. To nije složeno pravilo nad parom `(naziv, slug)`.

Složeno pravilo se primenjuje na kombinaciju, kao budući par `(proizvod_id, promotivni_dogadjaj_id)` iz prethodnog primera. Pre izbora ograničenja pitamo se: „Koji tačno duplikat poslovno želimo da zabranimo?“ Ako je odgovor „ponavljanje jedne vrednosti u ovoj koloni“, koristimo `unique=True`; ako je odgovor „ponavljanje ove kombinacije“, koristimo `UniqueConstraint`.

U trenutnim modelima projekta nema složenog `UniqueConstraint`-a. To je teorijski, projektno motivisan primer za kasniju lekciju, a ne ograničenje koje sada postoji u bazi.

---

## Šta jedinstvenost (`unique=True`) ne garantuje

### Poređenje velikih i malih slova

`unique=True` ne znači automatski da se tekst normalizuje, niti da su `"Alice"` i `"alice"` uvek ista vrednost. Rezultat zavisi od tipa kolone, baze i njene collation postavke. Ako je potrebno neosetljivo poređenje, pravilo treba namerno definisati, na primer normalizacijom u aplikaciji ili odgovarajućim indeksom/kolacijom koju podržava baza.

Isto tako, jedinstvenost email adrese ne normalizuje automatski razmake, velika slova ili druge varijacije. Takvo pravilo treba definisati i dosledno primenjivati u sistemu.

---

### `NULL` vrednosti

Priloženi kod kombinuje `unique=True` sa `nullable=False`, pa za ove kolone `NULL` nije dozvoljen. Ako nullable kolona ima unique ograničenje (`unique=True`), broj dozvoljenih `NULL` vrednosti zavisi od `pravila konkretne baze`. Ne treba pretpostaviti da unique znači „najviše jedan `NULL`“; proveri ponašanje svog dijalekta!

---

### Ograničenje dužine i validacija

`unique=True` ne proverava da li je vrednost smislen naziv, da li je slug dobro formiran ili da li email ima ispravan format. Takođe, ne zamenjuje `nullable=False`. To su odvojena pravila i validacije.

---

## `unique=True` naspram `Index(unique=True)`

`Index` nije rezervisan za primarne ključeve. To je struktura koju baza može koristiti da brže pronađe redove, na primer pri `WHERE`, `JOIN` ili `ORDER BY`.

`Indeks` je najkorisniji kada `upiti često filtriraju ili spajaju tabele po indeksiranoj koloni`, ali `optimizator baze` odlučuje da li će ga koristiti. Indeks troši prostor i može usporiti `INSERT`, `UPDATE` i `DELETE`, jer treba održavati i njegov sadržaj.

VAŽNO: `Baza` obično `napravi indeks` ili odgovarajuću indeksnu strukturu `za primarni ključ`, pa se PK može brzo pronaći i proveriti. Zato `ne dodajemo još jedan` običan `indeks` na `id` bez posebnog razloga. To, međutim, ne znači da se indeksi koriste samo za primarne ključeve!

U našem projektu `Proizvod.slug` već ima `unique=True` i često bi se koristio za pronalaženje proizvoda.

VAŽNO: `Baza` obično koristi `indeksnu strukturu` za `unique` ograničenje, zato `ne` treba naslepo `dodavati` još jedan `Index` nad istim `slug`-om. Nasuprot tome, kada kasnije dodamo `porudzbina_id` u `StavkaPorudzbine`, indeks može biti koristan ako često učitavamo sve stavke jedne porudžbine:

```python
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

porudzbina_id: Mapped[int] = mapped_column(
	ForeignKey("porudzbina.id"),
	index=True,
	nullable=False,
)
```

Ovaj isečak je predlog za kasniju implementaciju, ne postojeće polje. `index=True` traži od SQLAlchemy-ja da doda običan indeks; ne čini vrednost jedinstvenom. Za jedinstvenost bi bilo potrebno zasebno unique pravilo.

`Složeni indeks` pokriva više kolona i može biti koristan za upite po njihovoj kombinaciji. `Redosled kolona` je važan: indeks nad `(porudzbina_id, proizvod_id)` najviše odgovara upitima koji filtriraju po koloni `porudzbina_id` ili po obe kolone.

NAPOMENA: Ne treba očekivati iste `performanse` za upit koji filtrira samo po koloni `proizvod_id`.

Složeni `UniqueConstraint` iz primera može već `dobiti indeksnu podršku od baze`, pa `ne dodajemo` paralelno još jedan `isti složeni indeks` bez merenja i konkretnog razloga.

Razlika u nameni je ključna:

- `UniqueConstraint` je pravilo `integriteta`: zabranjuje ponovljenu vrednost (`NULL` ili konkretne vrednosti) ili ponovljenu kombinaciju (`kolona1`, `kolona2`, ...).
- `Index` je pomoćna struktura za pristup podacima; `običan indeks` sam po sebi `dozvoljava duplikate`.
- `Index(..., unique=True)` istovremeno pravi indeks i sprovodi jedinstvenost, ali `unique indeks` i `UniqueConstraint` nisu potpuno zamenljivi u svim bazama i migracionim situacijama.

VAŽNO:

- `Indeks` biramo prema `stvarnim obrascima upita`

- Ograničenje (`UniqueConstraint` ili `unique=True`) prema `poslovnom pravilu` (npr. jedinstvenost korisničkog imena, email adrese, slug-a).

- `Baza` i `njen optimizator` (`query optimizer` npr. `PostgreSQL`, `MySQL`) određuju `fizičku implementaciju` u `bazi` i upotrebu `indeksa` i `unique ograničenja`, pa konkretan efekat treba proveriti na ciljnoj bazi.

- `unique=True` i `UniqueConstraint` opisuju šemu (`schema` npr. `CREATE TABLE` definicija, `INSERT` ograničenja, `ALTER TABLE` komande itd.) preko `SQLAlchemy metapodataka` (`Base.metadata.tables['tabela_ime']`u našem primeru).

- Ako tabela već postoji (`CREATE TABLE` je već izvršen preko SQLAlchemy metapodataka (`Base.metadata.create_all(engine)`) ili migracionog alata (npr. `Alembic`)), sama `izmena` Python klase `ne dodaje ograničenje u bazu`. Potrebna je `migracija`!

- Pre dodavanja `unique ograničenja` na postojeće podatke treba pronaći i razrešiti `duplikate`, inače migracija `neće` moći da se primeni.

---

## Razlike u source snapshot-ovima

- U `5_required.py` su `User.username` i `User.email` bili unique; u `6_default_values.py` to ograničenje je izostavljeno; `7_unique_column.py` ga ponovo postavlja.
- Ostala ograničenja iz ove lekcije su dodata na `Category.name`, `Category.slug`, `PromotionEvent.name`, `Product.name` i `Product.slug`.
- `updated_at` u `Product` i `Order` i dalje ima `nullable=False` i samo `onupdate`, bez početnog default-a. To je prethodno uočeni problem pri `INSERT`-u i nije posledica jedinstvenosti.
- Modeli još nemaju primarne ključeve, a `ProductPromotionEvent` je prazan; source fajl zato nije kompletan ORM primer za samostalno izvršavanje.

---

## Pitanja za proveru razumevanja

1. Šta sprečava `unique=True`?

- ODGOVOR: Sprečava da baza prihvati duplikate u koloni koja ima `unique=True`. Ako se pokuša uneti vrednost koja već postoji, baza će odbaciti upis i prijaviti grešku. To znači da aplikacija ne može sama garantovati jedinstvenost (`uniqueness`) bez podrške baze.

2. Zašto aplikaciona provera „da li slug postoji“ (`slug_exists`) ne zamenjuje `unique` ograničenje u bazi?

- ODGOVOR: Zato što konkurentni upisi iz više procesa ili niti mogu zaobići aplikacionu proveru i pokušati da unesu duplikat u bazu. Samo `unique` ograničenje u bazi garantuje jedinstvenost. Ovo je razlog zašto se oslanjanje isključivo na aplikacionu proveru ne smatra sigurnim.

3. Da li su `Category.name` i `Category.slug` unique samo kao par ili svaki zasebno?

- ODGOVOR: Svaka od kolona `Category.name` i `Category.slug` ima svoje `unique` ograničenje, što znači da svaka zasebno mora biti jedinstvena u tabeli.

4. Kako se razlikuje `UniqueConstraint` nad dve kolone?

- ODGOVOR: `UniqueConstraint` nad dve kolone garantuje da kombinacija vrednosti u tim kolonama bude jedinstvena, dok `unique=True` na pojedinačnoj koloni garantuje jedinstvenost samo te kolone.

5. Da li `unique=True` automatski pravi tekstualnu vrednost neosetljivu na velika i mala slova?

- ODGOVOR: Ne, `unique=True` ne pravi tekstualnu vrednost neosetljivu na velika i mala slova. Jedinstvenost se proverava prema pravilima poređenja baze, koja može biti osetljiva ili neosetljiva na velika i mala slova.

6. Koje pravilo dodatno obezbeđuje `nullable=False`?

- ODGOVOR: `nullable=False` dodatno obezbeđuje da kolona ne može imati `NULL` vrednost, što znači da svaki red mora imati validnu vrednost u toj koloni.

7. Zašto lozinka korisnika nije jedinstvena u source modelu?

- ODGOVOR: Lozinka korisnika nije jedinstvena jer različiti korisnici mogu imati istu lozinku. Jedinstvenost lozinke nije potrebna za funkcionalnost aplikacije, dok je jedinstvenost korisničkog imena i email-a kritična.

8. Šta spada u `aplikacione provere jedinstvenosti` a šta u `bazna ograničenja`?

- ODGOVOR:

- `Aplikacione provere jedinstvenosti` su provere koje aplikacija vrši pre nego što pokuša `INSERT` ili `UPDATE`, npr. funkcija `slug_exists` koja proverava da li slug već postoji. Funkcije poput `slug_exists`, `username_exists` ili `email_exists` definiše aplikacija; `SQLAlchemy` može da se koristi za izvršavanje upita u tim funkcijama, ali ih ne obezbeđuje automatski. Provera može dati raniju i jasniju poruku, ali konačnu garanciju jedinstvenosti pružaju `bazna ograničenja`.

- `Bazna ograničenja` su pravila definisana u samoj bazi, kao što su `unique=True` ili `UniqueConstraint`, koja `garantuju` jedinstvenost bez obzira na `konkurentne upise` (npr. prvi upis iz jednog session-a i drugi upis iz drugog session-a) iz `više procesa` ili niti što nije moguće obezbediti samo aplikacionim proverama.

- `Session` u SQLAlchemy-ju predstavlja `jedinicu rada sa bazom` i upravlja ORM operacijama i transakcijom. Sesija po potrebi automatski započinje transakciju (`autobegin`), a jedna transakcija može obuhvatiti više SQL upita. Transakcija se završava pozivom `commit()` ili `rollback()`; zato ne važi pravilo „jedan SQL upit = jedna transakcija“.

- `Session` nije bezbedno deliti između niti ili istovremenih asinhronih zadataka. Svaka nit ili zadatak treba da koristi svoju sesiju (`Session` za sinhroni, `AsyncSession` za asinhroni rad). Svaki proces takođe treba da napravi sopstvenu sesiju i konekciju; ne treba deliti sesiju ili konekciju nasleđenu iz drugog procesa.

- Kada više sesija istovremeno upisuje u istu bazu, aplikaciona provera može imati trku: više upisa može istovremeno utvrditi da vrednost još ne postoji. `unique` ograničenje ili `UniqueConstraint` u bazi sprečava da konfliktni duplikati budu sačuvani.

---

## Sažetak

- `unique=True` traži od baze da odbaci duplikate u jednoj koloni.
- Ograničenje baze je potrebno čak i kada aplikacija unapred proverava da li vrednost postoji, jer konkurentni upisi mogu zaobići takvu proveru.
- U ovoj skripti jedinstveni su nazivi i slug-ovi kategorija/proizvoda, naziv promocije, korisničko ime i email.
- `nullable=False` i `unique=True` rešavaju različite probleme; source ih kombinuje za sva navedena polja.
- Ponašanje poređenja teksta, uključujući velika i mala slova i nullable unique kolone, zavisi od baze i njenih podešavanja.
- `UniqueConstraint` može da ograniči kombinaciju kolona; `unique=True` na pojedinačnim kolonama ovde pravi odvojena pravila.
- Unique indeks može da sprovodi jedinstvenost, ali ga ne treba redundantno dodavati uz postojeće ograničenje.
- U postojećoj bazi unique pravilo se primenjuje migracijom, nakon provere da već upisani podaci nemaju duplikate.
