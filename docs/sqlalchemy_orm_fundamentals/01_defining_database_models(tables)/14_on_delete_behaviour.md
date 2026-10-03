# Lekcija 14: Ponašanje pri brisanju referenciranog reda

## Cilj lekcije

Kada red u roditeljskoj tabeli referencira strani ključ u drugoj tabeli, baza mora da zna šta da uradi ako neko pokuša da obriše roditeljski red. SQLAlchemy prosleđuje ovo pravilo bazi kroz `ondelete` na `ForeignKey(...)`.

Primer je kategorija koju koriste proizvodi. Ako kategoriju referencira sto proizvoda, brisanje kategorije ne sme slučajno da ostavi nevažeće reference ili da obriše podatke bez namere. Izabrana akcija treba da prati poslovna pravila i politiku čuvanja podataka.

## Gde se navodi `ondelete`

Opcija pripada konstruktoru `ForeignKey`, jer je deo FK ograničenja u šemi baze:

```python
category_id = Column(
	Integer,
	ForeignKey("category.id", ondelete="RESTRICT"),
	nullable=False,
)
```

Ovde:

- `ForeignKey("category.id", ...)` definiše koju vrednost red referencira i ponašanje FK ograničenja;
- `ondelete="RESTRICT"` zadaje reakciju baze na brisanje referenciranog reda;
- `nullable=False` je zasebno pravilo na nivou kolone koje ne dozvoljava `NULL`.

`ondelete` ne briše redove sam SQLAlchemy ORM kodom. SQLAlchemy uključuje odgovarajuću klauzulu u DDL-u, a DBMS je sprovodi kada se izvrši brisanje.

## Moguće akcije

### `CASCADE`

```python
ForeignKey("category.id", ondelete="CASCADE")
```

Brisanje roditeljskog reda automatski briše redove koji ga referenciraju. Brisanje kategorije bi, na primer, obrisalo i sve povezane proizvode. Ovo može biti prikladno za zavisne podatke koji nemaju smisla bez roditelja, ali nosi rizik velikog i nepovratnog gubitka podataka. Koristiti ga samo kada je takvo ponašanje namerno.

### `SET NULL`

```python
category_id = Column(
	Integer,
	ForeignKey("category.id", ondelete="SET NULL"),
	nullable=True,
)
```

Baza zadržava zavisni red, ali postavlja njegov FK na `NULL`. FK kolona zato mora dozvoljavati `NULL`. Ovo ne radi sa `nullable=False`.

### `SET DEFAULT`

```python
from sqlalchemy import text

category_id = Column(
	Integer,
	ForeignKey("category.id", ondelete="SET DEFAULT"),
	nullable=False,
	server_default=text("1"),
)
```

Baza zadržava zavisni red i postavlja FK kolonu na njen **serverski default**. Ta vrednost i dalje mora da referencira postojeći red roditeljske tabele; u primeru bi kategorija sa ID-jem `1` morala postojati. Ako ne postoji, brisanje roditelja može pasti zbog FK ograničenja.

Python/SQLAlchemy `default=...` nije dovoljan za `ON DELETE SET DEFAULT`: ovu akciju izvršava baza, pa podrazumevana vrednost mora biti definisana u samoj šemi baze. Podršku i tačno ponašanje treba proveriti u dokumentaciji ciljnog DBMS-a.

### `RESTRICT`

```python
ForeignKey("category.id", ondelete="RESTRICT")
```

Zabranjuje brisanje roditeljskog reda dok postoje zavisni redovi. Pre brisanja kategorije, svaki proizvod mora biti obrisan ili prebačen u drugu kategoriju. To je akcija koju source kod ove lekcije pokušava da postavi na tri FK-a.

### `NO ACTION`

```python
ForeignKey("category.id", ondelete="NO ACTION")
```

Ovo je uobičajena podrazumevana FK akcija kada se ne navede drugačije, ali ne treba se oslanjati na pretpostavke umesto provere baze. Slično je `RESTRICT` jer ne dopušta da na kraju ostanu nevažeće reference. U nekim sistemima razlika je u trenutku provere: `NO ACTION` može dozvoliti odloženu proveru do kraja naredbe ili transakcije kada je ograničenje definisano kao deferrable, dok `RESTRICT` tipično blokira odmah. Detalji su specifični za DBMS.

## Ponašanje iz source koda

Source fajl namerava da koristi `RESTRICT` za:

| FK kolona              | Referencirani ključ | Očekivani efekat                                                 |
| ---------------------- | ------------------- | ---------------------------------------------------------------- |
| `Category.category_id` | `Category.id`       | ne može se obrisati roditeljska kategorija dok ima potkategorije |
| `Product.category_id`  | `Category.id`       | ne može se obrisati kategorija dok je koriste proizvodi          |
| `Order.user_id`        | `User.id`           | ne može se obrisati korisnik dok ima porudžbine                  |

To čuva redove i sprečava slučajno brisanje istorije. Source kod takođe predlaže soft delete: umesto uklanjanja kategorije iz baze, postaviti `is_active=False` i isključiti je iz uobičajenih upita. Soft delete je `UPDATE`, ne `DELETE`, pa `ondelete` akcija se tada ne aktivira.

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

## Baza mora stvarno da sprovodi ograničenje

Promena modela ne menja automatski već postojeću tabelu. `ondelete` mora biti prisutan u stvarnom FK ograničenju u bazi; izmena postojeće šeme obično zahteva migraciju ili kontrolisanu izmenu tabele.

Podrška i detalji akcija zavise od DBMS-a. SQLite, na primer, zahteva da FK enforcement bude uključen na konekciji; u suprotnom se FK akcije možda neće sprovoditi. PostgreSQL sprovodi kreirana ograničenja. Proveriti ponašanje izabrane baze, naročito za `RESTRICT` naspram `NO ACTION`, `SET DEFAULT` i odložena ograničenja.

## Pitanja za proveru razumevanja

1. Gde se u SQLAlchemy deklaraciji navodi `ondelete`?
2. Šta se dešava sa decom kada je akcija `CASCADE`?
3. Zašto `SET NULL` zahteva nullable FK kolonu?
4. Zašto `SET DEFAULT` zahteva serverski default koji pokazuje na postojeći roditeljski red?
5. Kako se razlikuju `RESTRICT` i `NO ACTION` u opštem slučaju?
6. Da li `ForeignKey.ondelete` i `relationship(cascade=...)` znače isto?
7. Da li postavljanje `is_active=False` pokreće `ON DELETE` akciju?
8. Koje greške u položaju argumenata sprečavaju učitavanje priloženog source fajla?

## Sažetak

- `ondelete` definiše šta baza radi sa zavisnim redovima kada se briše referencirani roditelj.
- SQLAlchemy ga prosleđuje bazi kroz `ForeignKey(..., ondelete=...)`; `nullable` pripada `Column(...)`.
- `CASCADE` briše decu, `SET NULL` zadržava ih bez reference, `SET DEFAULT` koristi serverski default, a `RESTRICT`/`NO ACTION` sprečavaju nevažeće reference.
- `SET NULL` zahteva nullable FK; `SET DEFAULT` zahteva validan serverski default koji referencira postojeći roditeljski red.
- `ForeignKey.ondelete` je ponašanje baze i razlikuje se od ORM `relationship(cascade=...)` podešavanja.
- Source fajl trenutno pada zbog argumenata prosleđenih pogrešnim konstruktorima; pogrešan položaj argumenata i izbor nullable za korensku kategoriju su eksplicitno zabeleženi.
