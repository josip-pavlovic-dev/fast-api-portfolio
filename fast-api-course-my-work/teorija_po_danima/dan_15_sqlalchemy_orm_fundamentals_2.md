# Dan 15: SQLAlchemy ORM Fundamentals 2

## Cilj rada

Danas nastavljamo modelovanje tabela kroz lekcije 08–13. Cilj je da do samoreferencirajuće veze razumemo kako se nullable pravilo, podrazumevane vrednosti, jedinstvenost, primarni ključevi i strani ključevi nadovezuju jedan na drugi. Radimo postepeno: implementiramo samo obrađenu lekciju, proverimo modele, pa tek onda prelazimo dalje.

Kurski snapshot-i ostaju neizmenjeni. U praktičnom paketu koristimo SQLAlchemy 2.x stil (`Mapped[...]`, `mapped_column()`), srpske ASCII nazive i postojeći root `.venv`. Ako praktični model namerno odstupi od source primera, razlog beležimo ovde.

---

## Plan za danas

1. **Lekcija 08 – Obavezna polja:** uskladiti `Mapped` anotacije i `nullable=False`; razlikovati `NULL` od praznog teksta.
2. **Lekcija 09 – Default vrednosti:** proći Python/SQLAlchemy default i `server_default`; proveriti kada se vrednosti zaista dodeljuju.
3. **Lekcija 10 – Jedinstvene vrednosti:** dodati ograničenja `unique` prema pravilima kursa i razlikovati ih od `NOT NULL`.
4. **Lekcija 11 – Primarni ključevi:** povezati već postojeći tehnički `id` sa pravilima i dopuniti razumevanje PK-a bez ponovnog dodavanja kolona.
5. **Lekcija 12 – Strani ključevi:** povezati odgovarajuće modele i razdvojiti FK kolonu od ORM `relationship()` atributa.
6. **Lekcija 13 – Samoreferencirajući FK:** dodati vezu kategorije sa roditeljskom kategorijom i razrešiti zašto root kategorija zahteva nullable FK.

Redosled može da se pomeri ako neka provera pokaže da treba dodatno utvrditi prethodni pojam. Kriterijum za završetak nije samo da se kod učita: treba umeti objasniti koje pravilo sprovodi anotacija, koje SQLAlchemy metapodatak, a koje baza.

---

## Lekcija 08: Obaveznost i `NULL`

### Šta smo promenili

U `models/catalog.py` i `models/promotions.py` polja koja su u lekciji obavezna više ne koriste opcione anotacije poput `Mapped[str | None]`. Prešla su na `Mapped[str]`, `Mapped[date]`, `Mapped[int]`, `Mapped[bool]` ili `Mapped[datetime]`, a deklaracije navode i `nullable=False`. Time Python tip i ograničenje kolone opisuju isto pravilo.

U `catalog.py`:

- U klasi/tabeli `Kategorija` obavezni su `naziv` i `slug` kategorije, dok `aktivnost` i `nivo kategorije` ostaju `ne-nullable` i imaju početne vrednosti `default=False` i `0`.

- Klasa/tabela `Proizvod` sada zahteva `tekstualna polja` za `naziv` i `opis`, `boolean statuse` za `aktivan` i `digitalni`, `vremenske oznake` za `kreirano_u` i `izmenjeno_u` i `numerička polja` za `cenu`.

- U klasi/tabeli `StanjeZaliha` kolona `količina` ima default `0` i `nullable=False`, kao i `poslednja_provera` koja tako ima `nullable=False` i samim time kao i `količina` mora biti prosleđena. `poslednja_provera` za registrovanje vremena promene koristi `DateTime(timezone=True)` način definisanja kolone. Ovaj model osigurava da se svaka promena stanja zaliha beleži sa vremenskom oznakom.

U `models/promotions.py` imamo klasu/tabelu `PromotivniDogadjaj` gde su `naziv`, `datum_pocetka`, `datum_zavrsetka` i `umanjenja cene` promotivnog događaja postali obavezni.

Ne navodi se `Mapped[... | None]` za ova polja, već koristi `Mapped[...]` sa `nullable=False`. Napomena da `nullable=False` ne sprečava prazan string; to je samo ograničenje baze. Takođe, ne navođenje `None` u anotaciji automatski govori SQLAlchemy-ju da polje ne može biti `NULL` pa je `nullable=False` redundantno, i ne mora se eksplicitno navoditi osim radi jasnoće.

U početnom stanju pre lekcije 12, `VezaProizvodaIPromocije` je imala samo primarni ključ. Nakon implementacije lekcije 12 dobila je FK kolone `proizvod_id` i `promotivni_dogadjaj_id`, kao i složeni unique constraint da se isti par ne unese dvaput. Time se proizvod može povezati sa više promocija, a promocija sa više proizvoda. U Python-u tu mnogostruku vezu pratimo kroz asocijativni ORM model.

U `models/orders.py` imamo klasu/tabelu `Korisnik` i `Porudzbina` gde su korisnicko_ime, email, lozinka i količina stavke već bili ne-nullable, pa su ostali neizmenjeni. Vremena kreiranja i izmene porudžbine sada su tipizovana kao obavezna.

---

### Zašto postoje dva signala

SQLAlchemy 2.x može da zaključi nullability iz `Mapped[T]` i `Mapped[T | None]`. Ipak, ovde navodimo `nullable=False` eksplicitno zato što je lekcija upravo o ograničenju baze.

`Anotacija` pomaže da se Python kod i alati za tipove slažu sa ograničenjem

`nullable metapodatak` definiše SQL kolonu.

`None` nije dozvoljen za `Mapped[T]` obavezno polje, a `nullable=False` će sprečiti bazu da sačuva SQL vrednost `NULL`.

Ovo `ne` odbija `prazan string niti tekst sastavljen od razmaka`. To je posebna validacija. U ovoj lekciji još ne dodajemo `Pydantic` validatore niti `CHECK` ograničenja.

---

### Praktična korekcija za `izmenjeno_u`

Kurski source postavlja `updated_at` kao `nullable=False` uz `onupdate=func.now()`, ali nema početni default. Sam `onupdate` ne daje vrednost pri `INSERT`, pa bi zapis bez eksplicitnog `updated_at` pao na `NOT NULL` ograničenju.

U praktičnim modelima sam zato postavio `default=func.now()` uz postojeći `onupdate=func.now()` za `Proizvod.izmenjeno_u` i `Porudzbina.izmenjeno_u`. Polje dobija početnu vrednost pri unosu, a kasniji SQLAlchemy `UPDATE` može da osveži vreme. Ovo je namerna praktična popravka, nije tvrdnja da je tako napisano u kurskom source-u. Kasnije ćemo kroz lekciju 09 detaljnije razdvojiti default ponašanja.

---

## Koraci implementacije

1. **Kategorija:** naziv i slug su postali `Mapped[str]` sa `nullable=False`; `aktivna` i `nivo` su obavezni, uz `default=False` i `default=0`.
2. **Proizvod:** naziv, slug, opis, digitalni status, aktivnost, vreme kreiranja, vreme izmene i cena su nenullable. Statusi imaju `False` default, vreme kreiranja `func.now()`, a vreme izmene i početni default i `onupdate`.
3. **Stanje zaliha:** količina je obavezna sa default-om `0`; vreme poslednje provere je obavezno i nema default, pa aplikacija mora da ga prosledi.
4. **Promotivni događaj:** naziv, početni i završni datum i iznos umanjenja cene su obavezni.
5. **Korisnik i stavka porudžbine:** njihova postojeća `nullable=False` pravila već su odgovarala lekciji; nisu menjana.
6. **Porudžbina:** `kreirano_u` je obavezno sa `default=func.now()`. `izmenjeno_u` je obavezno i dobija praktični početni default uz `onupdate`.
7. **README:** ažuriran je pregled implementiranih lekcija i zabeležena korekcija za `izmenjeno_u`.

U tadašnjem stanju projekta nisu još bili dodati `unique=True`, strani ključevi niti ORM relacije; te izmene su naknadno obrađene u lekcijama 10 i 12. `id` primarni ključevi su već postojali, zato lekcija 11 objašnjava njihovu ulogu bez dodavanja novih kolona. Samoreferencirajući `roditelj_id` za kategoriju i dalje čeka lekciju 13.

---

## Provera

Provereno je da se paket modela uvozi i da se mapiranje ispravno konfiguriše. Nakon lekcije 12 dodatno je testirana privremena memorijska SQLite baza sa uključenim FK enforcement-om: svih šest FK-ova je kreirano, ORM navigacija radi, nepostojeći roditeljski red i dupli par proizvoda/promocije bivaju odbijeni. Projekat i dalje nema trajni engine/session modul; provera koristi zaseban privremeni engine i ne menja trajnu bazu.

---

## Beleške i pitanja

Odgovore na pitanja iz lekcije 08 dodaćemo ovde nakon provere razumevanja. Sledeća tema je lekcija 09: kada SQLAlchemy primenjuje `default`, kada bazu koristi `server_default` i kako callable default utiče na vrednost.

---

## Lekcija 09: Podrazumevane vrednosti

### Šta smo naučili

Default određuje vrednost za INSERT koji ne navede vrednost kolone. `nullable=False` i dalje zasebno zabranjuje `NULL`; default ne zamenjuje to ograničenje niti predstavlja poslovno obrazloženje za izabranu vrednost.

- `default=False` i `default=0` prosleđuju Python vrednost kroz SQLAlchemy-generisani upit.
- `default=func.now()` je SQLAlchemy client-side default koji ubacuje SQL izraz u INSERT; bazni server izvršava `now()`.
- Python callable, na primer `default=lambda: str(uuid.uuid4())`, poziva se u Python-u kada SQLAlchemy-u zatreba vrednost. Prosleđuje se funkcija, ne rezultat njenog poziva pri učitavanju modula.
- `server_default=...` opisuje `DEFAULT` u DDL-u; baza ga koristi i za klijente koji ne koriste ovaj SQLAlchemy model, ako izostave kolonu.

SQLAlchemy `default` važi za SQLAlchemy ORM i Core iskaze, ali ne i za SQL koji direktno izvršava drugi klijent. `server_default` važi na nivou baze. Ako se šema već kreira, dodavanje ili promena serverskog default-a zahteva migraciju; promena modela sama ne prepravlja postojeću tabelu.

---

### Kako se to odnosi na naše modele

Default-i za ovu lekciju već su bili prisutni u modelima posle prethodne implementacije, pa nije bilo potrebno ponovo menjati njihove deklaracije. Sada smo proverili njihovo značenje i zabeležili ih uz odgovarajuće kursne primere:

| Praktično polje                                  | Default                              | Razlog                                                                                 |
| ------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------- |
| `Kategorija.aktivna`                             | `False`                              | nova kategorija počinje neaktivna                                                      |
| `Kategorija.nivo`                                | `0`                                  | početni nivo kategorije                                                                |
| `Proizvod.digitalni`, `Proizvod.aktivan`         | `False`                              | početni boolean statusi                                                                |
| `StanjeZaliha.kolicina`                          | `0`                                  | početno stanje je nula evidentiranih komada                                            |
| `Proizvod.kreirano_u`, `Porudzbina.kreirano_u`   | `func.now()`                         | vreme unosa računa baza kroz SQL izraz u SQLAlchemy INSERT-u                           |
| `Proizvod.izmenjeno_u`, `Porudzbina.izmenjeno_u` | `func.now()` i `onupdate=func.now()` | obavezno polje dobija početno vreme i može da se osveži pri narednoj SQLAlchemy izmeni |

Nismo dodali `server_default` modelima: ova lekcija/source koristi SQLAlchemy `default`, a server default bi promenio ugovor tako da direktni upisi drugih klijenata dobijaju vrednost iz šeme. Teorija sada prikazuje i SQLAlchemy 2.x `mapped_column()` oblik za obe opcije, ali primer server default-a ostaje objašnjavajući i ne menja praktični model.

### Provera ponašanja

U memorijskoj SQLite bazi proveravamo da se ORM objekti mogu upisati bez ručnog zadavanja polja koja imaju default, da se boolean/integer vrednosti popune i da `func.now()` obezbedi vreme. Ova provera pokriva ponašanje SQLAlchemy default-a u testnoj bazi; ne dokazuje da isti SQL literal ili tip radi identično u svakoj produkcionoj bazi.

Lekcija 10 o jedinstvenim vrednostima obrađena je u nastavku. Sledeća je lekcija 11: primarni ključevi, koje naši modeli već imaju kao tehnički preduslov.

## Lekcija 10: Jedinstvene vrednosti

### Šta znači `unique=True`

Unique ograničenje sprečava bazu da sačuva ponovljenu vrednost u koloni. To je pravilo integriteta koje baza proverava pri INSERT-u i UPDATE-u. Aplikaciona provera može ranije da pronađe zauzet slug ili email i prikaže bolju poruku, ali ne zamenjuje ograničenje: dva paralelna zahteva mogu istovremeno proći proveru, dok baza garantuje da samo jedan može da sačuva istu vrednost.

`unique=True` na jednoj koloni pravi pravilo za tu kolonu. Ako su dve kolone svaka zasebno unique, kao `naziv` i `slug`, njihove vrednosti se proveravaju odvojeno; ne radi se o jedinstvenosti samo njihovog para. Za jedinstvenu kombinaciju više kolona koristi se `UniqueConstraint`.

### Izmene u praktičnim modelima

1. `Kategorija.naziv` i `Kategorija.slug` su dobili `unique=True` jer naziv i URL slug kategorije treba pojedinačno da identifikuju jednu kategoriju.
2. `Proizvod.naziv` i `Proizvod.slug` su dobili `unique=True` prema pravilima priloženog source primera.
3. `PromotivniDogadjaj.naziv` je dobio `unique=True` da bi nazivi promocija bili jedinstveni.
4. `Korisnik.korisnicko_ime` i `Korisnik.email` već su bili unique i ostali su takvi. Lozinka nije unique: različiti korisnici smeju imati istu lozinku.
5. Nismo dodali unique ograničenja na druge kolone, složeni `UniqueConstraint` ili poseban unique indeks; source ove lekcije ne traži takva pravila.

Sva navedena polja su već `nullable=False`, pa sada istovremeno važe dva nezavisna pravila: vrednost mora postojati i ne sme se ponoviti. Jedinstvenost ne normalizuje tekst. Da li su, na primer, `"TV"` i `"tv"` jednaki zavisi od baze i kolacije; normalizaciju slug-a/email-a treba definisati odvojeno.

### Ograničenje naspram indeksa i migracije

`unique=True` izražava pravilo integriteta. Unique indeks takođe može da sprovodi jedinstvenost i koristiti se za pretragu, ali ga ne treba dodavati redundantno uz već postojeće ograničenje. Za poslovno pravilo nad više kolona koristi se `UniqueConstraint`; u teoriji je prikazan imenovan SQLAlchemy 2.x primer.

Pošto se modeli trenutno ne koriste za održavanje postojeće baze kroz migracije, menjali smo samo SQLAlchemy metapodatke. Kada uvedemo migracije, unique ograničenje moraće da se primeni na šemu, a postojeći duplikati moraju prvo da se razreše. Samo promenjen Python model ne menja već kreiranu tabelu.

### Provera ponašanja

U privremenoj SQLite bazi proveriću da li duplikate odbijaju sva nova unique polja, kao i već postojeći `Korisnik.korisnicko_ime` i `Korisnik.email`. Takva provera potvrđuje ograničenja u tom testnom dijalektu; poređenje velikih/malih slova i kolacije ostaje zavisno od produkcione baze.

---

## Kako da razmišljamo o SQLAlchemy-ju: klijent ili server?

Da, kao početni mentalni model možeš da kažeš da se `SQLAlchemy nalazi na strani aplikacije i ponaša se kao deo klijentskog sloja koji pristupa bazi`. SQLAlchemy nije sam server baze i obično nije zaseban proces: to je Python biblioteka koju koristi naša aplikacija.

Preciznije, SQLAlchemy ORM/Core pravi i prati rad sa SQL iskazima. `Engine` povezuje SQLAlchemy sa konkretnom bazom: koristi dijalekt da SQL i vrednosti prilagodi bazi, a DBAPI drajver obavlja konkretno izvršavanje kroz odgovarajući interfejs (npr. `psycopg2` za PostgreSQL, `mysqlclient` za MySQL, `sqlite3` za SQLite). Kod PostgreSQL-a ili MySQL-a drajver komunicira sa odvojenim serverom baze. Kod SQLite-a baza je obično ugrađena u aplikacioni proces, pa nema nužno odvojenog serverskog procesa.

Pojednostavljen tok upisa:

1. Python aplikacija napravi ORM objekat i doda ga u `Session`.
2. Pri `flush()` ili `commit()`, ORM pripremi potrebne INSERT/UPDATE iskaze.
3. `Engine` i njegov dijalekt kompajliraju iskaz za izabranu bazu, a DBAPI drajver ga izvršava.
4. Baza izvršava SQL i sprovodi ograničenja kao što su `NOT NULL` i `UNIQUE`.
5. SQLAlchemy preuzima vraćene vrednosti i sinhronizuje stanje objekta u sesiji.

### Client-side i server-side default

U ovom primeru:

```python
aktivna: Mapped[bool] = mapped_column(
	Boolean,
	default=False,
	nullable=False,
)
```

- `aktivna` je ime Python atributa u ORM klasi.
- `Mapped[bool]` označava da se atribut mapira kao ORM polje sa Python vrednošću tipa `bool`; SQLAlchemy može iz anotacije da zaključi tip i nullable pravilo.
- `mapped_column(...)` zadaje SQLAlchemy konfiguraciju kolone.
- `Boolean` je tip kolone.
- `default=False` je SQLAlchemy client-side default podešavanje: SQLAlchemy ga primenjuje pri svom INSERT-u kada upis ne navede vrednost.
- `nullable=False` je pravilo kolone u šemi baze; bazu treba migrirati ili kreirati iz ažuriranih metapodataka da bi se pravilo stvarno sprovelo.

Zato se ne kaže da je cela desna strana „client-side default“. Konkretno, `default=False` jeste client-side default, dok `Boolean` i `nullable=False` opisuju druge osobine kolone.

Client-side govori gde je default definisan i ko ga primenjuje; ne mora da govori gde se vrednost izračunava. Na primer, `default=func.now()` je podešen kao SQLAlchemy default, ali SQLAlchemy ubacuje SQL izraz `now()` u INSERT, a bazni server izvršava tu funkciju. Nasuprot tome, `default=False` je obična Python vrednost koju SQLAlchemy prosleđuje u upitu.

`server_default=...` definiše `DEFAULT` u DDL-u baze. Tada bazni server obezbeđuje vrednost i klijentima koji ne koriste SQLAlchemy, pod uslovom da izostave kolonu ili navedu `DEFAULT`. Ako upit eksplicitno pošalje `NULL`, default se ne koristi; odlučujuće je da li kolona dozvoljava `NULL`.

---

### Python tip u `Mapped[...]` i SQL tip kolone

U deklaraciji:

```python
aktivna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

`Mapped[bool]` opisuje Python vrednost atributa. SQLAlchemy može iz `bool` da zaključi SQLAlchemy tip `Boolean`, pa je u ovom primeru eksplicitni `Boolean` delom radi jasnoće. `mapped_column(...) zadaje kolonu i njene postavke`, kao što su `tip`, `default`, `nullability`, `primary key` i `unique` ograničenja.

U anotiranom declarative modelu kolona se u mnogim slučajevima može zaključiti i samo iz `Mapped[...]`, ali `mapped_column()` nam omogućava da njenu SQLAlchemy konfiguraciju navedemo neposredno.

Razlika je važnija kod celih brojeva:

```python
nivo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
```

Python vrednost je i dalje `int`; Python nema poseban ugrađeni tip `SmallInteger`. SQLAlchemy `SmallInteger` precizira SQL tip kolone, dok bi `Mapped[int]` bez eksplicitnog SQL tipa obično vodio do SQLAlchemy `Integer` tipa. Dijalekt zatim prevodi SQLAlchemy tip u odgovarajući DDL tip za izabranu bazu.

Ukratko: `Mapped[T]` govori koji Python tip vrednosti očekujemo i mapiramo; `mapped_column(SQLAlchemyType, ...)` eksplicitno zadaje tip i pravila SQL kolone. Nisu suvišni jedan drugom, iako SQLAlchemy često može da zaključi deo konfiguracije iz anotacije.

---

## Dodatak: `DateTime(timezone=True)` i `DateTime()`

Ova razlika je važna zato što Python, SQLAlchemy i baza imaju odvojene uloge. Python predstavlja datum i vreme kao `datetime` objekat; SQLAlchemy tipom opisuje kakvu kolonu želimo; dijalekt prevodi taj tip u oblik koji konkretna baza razume. Zato `timezone=True` nije obećanje da će svaka baza sačuvati vremensku zonu na isti način.

### Naivni i timezone-aware Python `datetime`

Python `datetime` može biti naivan ili timezone-aware:

```python
from datetime import datetime, timezone, timedelta

naive = datetime(2025, 1, 15, 12, 0, 0)
aware = datetime(
	2025, 1, 15, 12, 0, 0,
	tzinfo=timezone(timedelta(hours=2)),
)

print(naive, naive.tzinfo)
print(aware, aware.tzinfo)
```

Izlaz:

```text
2025-01-15 12:00:00 None
2025-01-15 12:00:00+02:00 UTC+02:00
```

Naivni objekat nema podatak koji kaže kojoj zoni ili UTC offset-u pripada `12:00`. To nije automatski „lokalno vreme“: on samo nema informaciju o zoni. Aware objekat ima offset i zato predstavlja određeni trenutak u vremenu. Za stvarne civilne zone, koje imaju pravila za letnje i zimsko računanje vremena, Python nudi `zoneinfo.ZoneInfo`, na primer `ZoneInfo("Europe/Belgrade")`.

### Šta podešava SQLAlchemy tip

```python
DateTime()
```

isto je što i:

```python
DateTime(timezone=False)
```

To traži tip kolone bez podrške za vremensku zonu. Python vrednosti namenjene toj koloni uobičajeno treba da budu naivni `datetime` objekti.

```python
DateTime(timezone=True)
```

traži tip kolone koji podržava vremensku zonu, ako takav tip postoji u ciljnoj bazi i njenom SQLAlchemy dijalektu. To samo po sebi ne dodaje zonu na naivnu Python vrednost, ne pretvara automatski svaku vrednost u UTC i ne čuva nužno naziv zone kao `Europe/Belgrade`. Aplikacija treba da odluči kako pravi i normalizuje vrednosti, a rezultat čuvanja zavisi od baze i drajvera.

### Šta je dijalekt i zašto je bitan?

SQLAlchemy koristi generičke tipove kao `DateTime`, `String` i `Integer`; svaka baza ima svoj SQL jezik i skup tipova. Dijalekt je deo SQLAlchemy-ja koji zna kako da te generičke tipove i iskaze prilagodi izabranoj bazi. Njega određuju URL i drajver u konfiguraciji engine-a. Isti Python model zato može da proizvede različit DDL za SQLite i PostgreSQL.

Za SQLAlchemy 2.0.38, kompajlirani tipovi su:

| SQLAlchemy deklaracija    | SQLite DDL tip | PostgreSQL DDL tip            |
| ------------------------- | -------------- | ----------------------------- |
| `DateTime()`              | `DATETIME`     | `TIMESTAMP WITHOUT TIME ZONE` |
| `DateTime(timezone=True)` | `DATETIME`     | `TIMESTAMP WITH TIME ZONE`    |

SQLite-ov `DATETIME` nema ugrađenu PostgreSQL-sličnu semantiku vremenske zone. U ovom dijalektu `timezone=True` ne stvara poseban tip kolone koji čuva offset. PostgreSQL ima odvojene tipove bez i sa podrškom za vremensku zonu, pa dijalekt može da prenese tu razliku u DDL.

---

### Proveren primer sa SQLite-om

Ovaj primer upisuje naivnu vrednost u `DateTime()` kolonu, a vrednost sa offset-om `+02:00` u `DateTime(timezone=True)` kolonu. Zatim ispisuje sirove vrednosti koje čuva SQLite i Python objekte koje SQLAlchemy vraća:

```python
from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, DateTime, MetaData, Table, create_engine, select

metadata = MetaData()
primer = Table(
	"datetime_primer",
	metadata,
	Column("bez_zone", DateTime()),
	Column("sa_zone", DateTime(timezone=True)),
)

engine = create_engine("sqlite://")
metadata.create_all(engine)

naivno_vreme = datetime(2025, 1, 15, 12, 0, 0)
vreme_sa_offsetom = datetime(
	2025, 1, 15, 12, 0, 0,
	tzinfo=timezone(timedelta(hours=2)),
)

with engine.begin() as connection:
	connection.execute(
		primer.insert().values(
			bez_zone=naivno_vreme,
			sa_zone=vreme_sa_offsetom,
		)
	)
	sirovo = connection.exec_driver_sql(
		"SELECT bez_zone, sa_zone FROM datetime_primer"
	).one()
	ucitano = connection.execute(select(primer)).one()

	print("SQLite raw:", sirovo)
	print("SQLite loaded:", ucitano)
	print(
		"SQLite tzinfo:",
		ucitano._mapping["bez_zone"].tzinfo,
		ucitano._mapping["sa_zone"].tzinfo,
	)
```

Izlaz na SQLite-u:

```text
SQLite raw: ('2025-01-15 12:00:00.000000', '2025-01-15 12:00:00.000000')
SQLite loaded: (datetime.datetime(2025, 1, 15, 12, 0), datetime.datetime(2025, 1, 15, 12, 0))
SQLite tzinfo: None None
```

Obrati pažnju: druga Python vrednost je pre INSERT-a imala `+02:00`, ali SQLite zapis nema taj offset, a učitani Python objekat nema `tzinfo`. Dakle, u ovoj kombinaciji SQLite-a i SQLAlchemy-ja oba polja su sačuvala isti zidni sat `12:00`, ne informaciju koja bi omogućila da se izračuna da aware vrednost predstavlja `10:00 UTC`. Sam naziv `timezone=True` nije dovoljan da spreči taj gubitak.

Isti primer može da se napiše deklarativnim ORM stilom SQLAlchemy-ja 2.0. Dodajemo `id` jer ORM model mora imati primarni ključ; vremenske kolone i dalje imaju ista podešavanja kao u prethodnom primeru.

```python
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
	pass


class DateTimePrimer(Base):
	__tablename__ = "datetime_primer"

	id: Mapped[int] = mapped_column(primary_key=True)
	bez_zone: Mapped[datetime] = mapped_column(DateTime())
	sa_zone: Mapped[datetime] = mapped_column(DateTime(timezone=True))


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

naivno_vreme = datetime(2025, 1, 15, 12, 0, 0)
vreme_sa_offsetom = datetime(
	2025, 1, 15, 12, 0, 0,
	tzinfo=timezone(timedelta(hours=2)),
)

with Session(engine) as session:
	session.add(
		DateTimePrimer(
			bez_zone=naivno_vreme,
			sa_zone=vreme_sa_offsetom,
		)
	)
	session.commit()

	ucitano = session.execute(select(DateTimePrimer)).scalar_one()
	sirovo = session.connection().exec_driver_sql(
		"SELECT bez_zone, sa_zone FROM datetime_primer"
	).one()

	print("SQLite raw:", sirovo)
	print("SQLite loaded:", (ucitano.bez_zone, ucitano.sa_zone))
	print("SQLite tzinfo:", ucitano.bez_zone.tzinfo, ucitano.sa_zone.tzinfo)
```

Očekivani izlaz:

```text
SQLite raw: ('2025-01-15 12:00:00.000000', '2025-01-15 12:00:00.000000')
SQLite loaded: (datetime.datetime(2025, 1, 15, 12, 0), datetime.datetime(2025, 1, 15, 12, 0))
SQLite tzinfo: None None
```

Ovde ORM klasa definiše tabelu, a `Session` dodaje objekat i izvršava upis. `select(DateTimePrimer)` vraća ORM objekat; sirovi SQL upit ostaje samo radi poređenja stvarnog SQLite zapisa sa vrednostima koje ORM učita.

---

### Poređenje sa PostgreSQL-om

PostgreSQL dijalekt generiše različite tipove:

```python
from sqlalchemy import DateTime
from sqlalchemy.dialects import postgresql, sqlite

print(sqlite.dialect().type_compiler_instance.process(DateTime()))
print(sqlite.dialect().type_compiler_instance.process(DateTime(timezone=True)))
print(postgresql.dialect().type_compiler_instance.process(DateTime()))
print(postgresql.dialect().type_compiler_instance.process(DateTime(timezone=True)))
```

Izlaz:

```text
DATETIME
DATETIME
TIMESTAMP WITHOUT TIME ZONE
TIMESTAMP WITH TIME ZONE
```

U PostgreSQL-u `TIMESTAMP WITH TIME ZONE` se često naziva `timestamptz`. Baza koristi offset iz ulazne vrednosti da bi odredila trenutak, normalizuje ga interno i pri čitanju prikazuje taj trenutak u vremenskoj zoni tekuće PostgreSQL sesije. Na primer, `2025-01-15 12:00:00+02:00` predstavlja isti trenutak kao `2025-01-15 10:00:00+00:00`; uz sesiju podešenu na UTC, rezultat bi bio prikazan približno kao `2025-01-15 10:00:00+00:00`. Tačan prikaz zavisi od postavke zone sesije.

PostgreSQL ne čuva originalni naziv zone, poput `Europe/Belgrade`, niti garantuje da će vratiti isti tekstualni offset koji je poslat. Čuva trenutak, a prikaz prilagođava zoni sesije. Ako aplikaciji treba i originalni naziv zone, njega treba čuvati u posebnoj tekstualnoj koloni.

Nasuprot tome, `TIMESTAMP WITHOUT TIME ZONE` čuva datum i sat bez zone i bez konverzije u UTC. Vrednost `12:00` ostaje `12:00`, ali bez dodatnog pravila nije moguće znati na koji trenutak se odnosi. Zato ne treba mešati aware Python vrednosti sa kolonama bez zone: baza može zanemariti njihov offset, pa je bolje držati Python vrednosti i SQL kolonu semantički usklađenim.

### Praktično pravilo za izbor

- Za događaj koji predstavlja jedan stvarni trenutak, kao što je vreme kreiranja zapisa ili poslednja provera zaliha, najčešće koristimo aware Python vrednost, čuvamo je dosledno kao UTC i biramo bazni tip koji zaista podržava vremensku zonu. PostgreSQL `TIMESTAMP WITH TIME ZONE` je jedan takav tip.
- Za lokalni raspored koji je po nameri „svakog dana u 09:00“ nije uvek dovoljan jedan UTC trenutak. Čuvamo lokalni datum/vreme i, ako pravila letnjeg računanja vremena imaju značaj, zasebno čuvamo IANA naziv zone.
- Za SQLite testove ne treba zaključiti da timezone vrednosti rade isto kao u PostgreSQL-u. Primer iznad pokazuje da se offset gubi. Ako aplikacija mora da čuva timezone-aware trenutke u SQLite-u, treba izabrati i testirati eksplicitnu strategiju, na primer normalizaciju u UTC pre upisa i dosledno ponovno dodavanje UTC zone pri čitanju, ili namenski SQLAlchemy tip.
- `DateTime(timezone=True)` ne znači „sačuvaj lokalnu zonu“, a `DateTime()` ne znači „sačuvaj lokalno vreme“. Prvi traži podršku tipa sa zonom; drugi opisuje vrednost bez zone. Značenje lokalnog vremena mora doći iz pravila aplikacije.

U našem modelu `StanjeZaliha.poslednja_provera` je deklarisana kao `DateTime(timezone=True)`, ali projekat još nema engine ni produkcionu bazu. Zasad je to namera izražena u SQLAlchemy metapodacima; stvarno ponašanje moći ćemo da potvrdimo tek kada izaberemo dijalekt i proverimo njegov SQL tip i ponašanje bind/rezultat vrednosti.

---

## Samostalna implementacija: lekcije 11 i 12

Ovaj vodič je redosled za samostalno prekucavanje i razumevanje izmena u projektnim modelima. Kod u postojećim `.py` fajlovima služi kao referenca za poređenje tek nakon što pokušaš sam. Radimo od jednog odnosa do sledećeg i proveravamo svaku stranu veze. Nemoj ponovo dodavati kolone koje već postoje.

### Korak 1: pregledaj polazno stanje i nacrtaj veze

Pre koda otvori `db/base.py` i tri fajla u `models/`. Svaka od osam klasa već ima `id` sa `primary_key=True`; u lekciji 11 zato `ne praviš` još jedan `primarni ključ`. Zatim zapiši gde se nalazi FK. Pravilo je da se FK veze jedan-prema-više nalazi u tabeli „više“:

| Odnos                                   | Tabela koja čuva FK          | FK kolona                | Cilj                     |
| --------------------------------------- | ---------------------------- | ------------------------ | ------------------------ |
| kategorija 1:N proizvodi                | `proizvod`                   | `kategorija_id`          | `kategorija.id`          |
| korisnik 1:N porudžbine                 | `porudzbina`                 | `korisnik_id`            | `korisnik.id`            |
| porudžbina 1:N stavke                   | `stavka_porudzbine`          | `porudzbina_id`          | `porudzbina.id`          |
| proizvod 1:N stavke                     | `stavka_porudzbine`          | `proizvod_id`            | `proizvod.id`            |
| proizvod 1:N zapisi veze sa promocijom  | `veza_proizvoda_i_promocije` | `proizvod_id`            | `proizvod.id`            |
| promocija 1:N zapisi veze sa proizvodom | `veza_proizvoda_i_promocije` | `promotivni_dogadjaj_id` | `promotivni_dogadjaj.id` |

Poslednja dva odnosa zajedno predstavljaju logičku vezu više-prema-više između proizvoda i promocija. U fizičkoj šemi ona je razložena na dve veze jedan-prema-više preko `VezaProizvodaIPromocije`.

---

### Korak 2: potvrdi ciljna imena

`ForeignKey()` prima tekst oblika `"ime_tabele.ime_kolone"`, a ne ime Python klase. Pročitaj `__tablename__` u ciljnom modelu:

```python
class Kategorija(Base):
	__tablename__ = "kategorija"
```

Zato FK ka njenom ID-ju glasi `ForeignKey("kategorija.id")`. Česta greška je da se napiše ime klase (`"Kategorija.id"`) ili staro englesko ime tabele (`"category.id"`); obe vrednosti bi bile pogrešne za naš projekat.

---

### Korak 3: dodaj FK u tabelu na strani „više“

U `catalog.py`, unesi import `ForeignKey`, pa u `Proizvod` dodaj FK pored njegovih kolona:

```python
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
class Proizvod(Base):
	__tablename__ = "proizvod"
	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
	)
	kategorija_id: Mapped[int] = mapped_column(Integer,
		ForeignKey("kategorija.id"),
		nullable=False,
	)
```

`Mapped[int]` kaže da je Python vrednost integer; `ForeignKey(...)` daje SQLAlchemy-ju cilj referenciranja (tj. kojoj tabeli i koloni FK kolone `kategorija_id` pripada, u našem slučaju kolona kategorija_id referencira na kolonu `id` iz tabele `kategorija` -> model class `Kategorija`: `kategorija.id`); `nullable=False` zahteva da `svaki proizvod` iz tabele `proizvod` ima svoju kategoriju. `FK` sam po sebi ne znači da je obavezan. U ovom domenu smo odlučili da proizvod bez kategorije nije dozvoljen.

Dodaj odgovarajući komentar `Lekcija 12` uz novi FK prilikom vežbanja, kao što je urađeno u referentnom fajlu. Komentar treba da objasni pravilo, a ne samo da ponovi sintaksu!

---

### Korak 4: dodaj Python navigaciju na obe strane

U `Kategorija` dodaj kolekciju proizvoda, a u `Proizvod` atribut jedne kategorije:

```python
# U Kategorija:
proizvodi: Mapped[list[Proizvod]] = relationship(back_populates="kategorija")

# U Proizvod:
kategorija: Mapped[Kategorija] = relationship(back_populates="proizvodi")
```

Obe vrednosti `back_populates` moraju tačno da odgovaraju imenu atributa na suprotnoj klasi. `proizvodi` je kolekcija jer kategorija može imati više proizvoda; `kategorija` je jedan objekat jer svaki proizvod ima jednu obaveznu kategoriju. Nijedan od ovih `relationship()` atributa nije SQL kolona: kolona je `kategorija_id`.

`back_populates = "<ime_atributa>"` predstavlja atribut na suprotnoj strani veze (npr. `proizvodi` u `Kategorija` ili `kategorija` u `Proizvod`) i on je obavezan za dvosmernu navigaciju između povezanih modela i predviđa da promena na jednoj strani automatski ažurira drugu stranu, čime se održava konzistentnost ORM objekata (npr. dodavanje proizvoda u `Kategorija.proizvodi` automatski postavlja `Proizvod.kategorija`).

---

### Korak 5: obradi korisnika i porudžbinu

U `orders.py` dodaj `ForeignKey` i `relationship` importe. FK je na strani porudžbine, jer jedan korisnik može imati mnogo porudžbina:

```python
# U Porudzbina:
korisnik_id: Mapped[int] = mapped_column(
	ForeignKey("korisnik.id"),
	nullable=False,
)
korisnik: Mapped[Korisnik] = relationship(back_populates="porudzbine")

# U Korisnik:
porudzbine: Mapped[list[Porudzbina]] = relationship(back_populates="korisnik")
```

Prati istu proveru kao u prethodnom koraku: stvarni FK je `korisnik_id`; `korisnik` i `porudzbine` su samo ORM putanje za rad sa objektima.

---

### Korak 6: poveži stavku sa porudžbinom i proizvodom

`StavkaPorudzbine` je na strani „više“ u oba odnosa: porudžbina ima više stavki, a proizvod može biti u stavkama različitih porudžbina. U `StavkaPorudzbine` dodaj oba obavezna FK-a:

```python
porudzbina_id: Mapped[int] = mapped_column(
	ForeignKey("porudzbina.id"),
	nullable=False,
)
proizvod_id: Mapped[int] = mapped_column(
	ForeignKey("proizvod.id"),
	nullable=False,
)
```

Zatim dodaj četiri ORM navigaciona atributa: `Porudzbina.stavke` ↔ `StavkaPorudzbine.porudzbina` i `Proizvod.stavke_porudzbine` ↔ `StavkaPorudzbine.proizvod`. Stavka čuva i svoju poslovnu kolonu `kolicina`, zato je modelujemo kao klasu, ne kao anonimnu direktnu many-to-many vezu.

---

### Korak 7: izgradi vezu proizvod–promocija preko asocijativnog modela

U `VezaProizvodaIPromocije` dodaj `proizvod_id` i `promotivni_dogadjaj_id` kao `ForeignKey` kolone sa `nullable=False`. Dodaj `Proizvod.veze_promocija` ↔ `VezaProizvodaIPromocije.proizvod` i `PromotivniDogadjaj.veze_proizvoda` ↔ `VezaProizvodaIPromocije.promotivni_dogadjaj`.

U `promotions.py` dodaj i `UniqueConstraint` nad parom kolona:

```python
__table_args__ = (
	UniqueConstraint(
		"proizvod_id",
		"promotivni_dogadjaj_id",
		name="uq_proizvod_promocija",
	),
)
```

Ovo sprečava samo da se isti proizvod i ista promocija povežu dvaput. Svaki FK zasebno sme da se ponavlja, inače bi proizvod mogao biti u samo jednoj promociji ili bi promocija mogla imati samo jedan proizvod. Constraint koristi SQL imena kolona, a ne Python atribute kroz tačku.

---

### Korak 8: razreši tipove između modula bez runtime ciklusa

Nakon što definišemo sve modele i njihove veze, potrebno je razrešiti tipove između modula bez izazivanja runtime ciklusa. Ovo se postiže kombinacijom `from __future__ import annotations` i `TYPE_CHECKING` bloka za uvoz tipova samo tokom statičke analize.

Pošto su `Proizvod`, `StavkaPorudzbine` i model promocione veze u različitim fajlovima, tipovi se međusobno pominju. U tim modulima koristi se:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .catalog import Proizvod
```

U svakom fajlu uvozi se samo klasa koja mu treba za anotaciju. `TYPE_CHECKING` blok služi statičkoj analizi i ne izvršava te importe tokom rada programa, čime izbegavamo runtime kružni import. `from __future__ import annotations` odlaže obradu anotacija, a SQLAlchemy zatim razrešava klase kada su modeli registrovani.

---

### Korak 9: ne dodaj još roditeljsku kategoriju ni kaskadno brisanje

Ovde namerno stajemo na odnosima iz lekcije 12. `Kategorija.parent_id`/`roditelj_id` je samoreferencirajući FK i pripada lekciji 13. Takođe nismo dodali `ondelete="CASCADE"`, `delete-orphan` niti pravila brisanja. To su odvojene odluke; običan FK ne znači da brisanje roditelja automatski briše decu.

---

### Korak 10: proveri mapiranje, šemu i ponašanje

Prvo pokreni konfiguraciju mappera iz root-a repozitorijuma:

```bash
PYTHONPATH=fast-api-course-my-work .venv/bin/python -c "from sqlalchemy.orm import configure_mappers; from sqlalchemy_orm_fundamentals import models; configure_mappers(); print('Mapperi su ispravni')"
```

Ovo hvata nepostojeće ciljne klase, pogrešan `back_populates` i greške u odnosima, ali samo po sebi ne proverava upis u bazu.

Za proveru ograničenja koristi se nova memorijska SQLite baza, ne korisnička/produkcijska baza. Napravi engine sa `sqlite://`, uključi SQLite FK enforcement na konekciji (`PRAGMA foreign_keys=ON`), pa pozovi `Base.metadata.create_all(engine)`. SQLite foreign key provera nije uvek uključena po podrazumevanom podešavanju; bez `PRAGMA` test ne dokazuje da FK baza stvarno sprovodi.

Proveri tri slučaja:

1. Napravi kategoriju i proizvod preko `Proizvod(kategorija=kategorija)`, potvrdi da INSERT-i prolaze i da su `proizvod.kategorija_id` i `kategorija.proizvodi` povezani.

```python
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy_orm_fundamentals import models
from sqlalchemy import create_engine

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
with engine.connect() as conn:
    conn.execute("PRAGMA foreign_keys=ON")
with Session(engine) as session:
    kategorija = models.Kategorija(naziv="Elektronika")
    proizvod = models.Proizvod(naziv="Laptop", kategorija=kategorija)
    session.add(proizvod)
    session.commit()
    assert proizvod.kategorija_id == kategorija.id
    assert proizvod in kategorija.proizvodi
```

2. Napravi korisnika, porudžbinu i stavku preko ORM atributa; proveri navigaciju `korisnik.porudzbine`, `porudzbina.stavke` i `stavka.proizvod`.

```python
from sqlalchemy.orm import Session
from sqlalchemy_orm_fundamentals import models
from sqlalchemy import create_engine

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
with engine.connect() as conn:
    conn.execute("PRAGMA foreign_keys=ON")
with Session(engine) as session:
    korisnik = models.Korisnik(ime="Pera", prezime="Peric")
    porudzbina = models.Porudzbina(korisnik=korisnik)
    stavka = models.Stavka(porudzbina=porudzbina, proizvod=models.Proizvod(naziv="Telefon", kategorija=models.Kategorija(naziv="Elektronika")))
    session.add(stavka)
    session.commit()
    assert porudzbina in korisnik.porudzbine
    assert stavka in porudzbina.stavke
    assert stavka.proizvod is not None
```

3. Dodaj istu kombinaciju proizvoda/promocije dva puta i očekuj `IntegrityError`; zatim probaj FK ka ID-ju koji ne postoji i očekuj isto odbijanje baze. Posle neuspešnog flush-a/commit-a pozovi `session.rollback()` pre nastavka korišćenja sesije.

```python
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy_orm_fundamentals import models
from sqlalchemy import create_engine

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
with engine.connect() as conn:
    conn.execute("PRAGMA foreign_keys=ON")
with Session(engine) as session:
    proizvod = models.Proizvod(naziv="Laptop", kategorija=models.Kategorija(naziv="Elektronika"))
    promocija = models.Promocija(naziv="Popust 10%")
    session.add(proizvod)
    session.add(promocija)
    session.commit()

    # Dodaj istu kombinaciju proizvoda/promocije dva puta
    try:
        session.add(models.ProizvodPromocija(proizvod=proizvod, promocija=promocija))
        session.add(models.ProizvodPromocija(proizvod=proizvod, promocija=promocija))
        session.commit()
    except IntegrityError:
        session.rollback()

    # Probaj FK ka ID-ju koji ne postoji
    try:
        session.add(models.ProizvodPromocija(proizvod_id=999, promocija_id=999))
        session.commit()
    except IntegrityError:
        session.rollback()
```

Na kraju pokreni test suite, proveri model dijagnostikama i `git diff --check`, pa osveži README i ERD. U Python fajlovima ostavi kratke komentare `Lekcija 12` uz FK, relationship i unique promene. Ne menjaš stare kurske snapshot-e. Koristi `session.rollback()` posle neuspešnog commit-a.

---

### Kriterijum završetka

- Svih osam postojećih ORM klasa i njihov po jedan `id` PK ostaju netaknuti.
- Postoje tačno šest FK kolona iz tabele na početku ovog vodiča; sve su `nullable=False`.
- Svaki `relationship()` ima odgovarajući `back_populates` na drugoj strani.
- Isti par proizvoda/promocije ne može se sačuvati dvaput.
- Mapper provera i SQLite provere prolaze; samoreferencirajući FK i pravila brisanja nisu dodati.

---

## Plan rada posle dana 15 (korak po korak)

Ovaj plan je nastavak tacno iz stanja koje sada imamo: lekcije 08-12 su implementirane, a lekcija 13 (samoreferencirajući FK kategorije) tek sledi.

### Korak 1: priprema i kontrola polaznog stanja

1. Iz root-a projekta potvrdi da je radno stablo cisto (`git status`).
2. Potvrdi da su modeli ucitljivi:

```bash
PYTHONPATH=fast-api-course-my-work .venv/bin/python -c "from sqlalchemy.orm import configure_mappers; from sqlalchemy_orm_fundamentals import models; configure_mappers(); print('Mapperi su ispravni')"
```

### Korak 2: implementiraj lekciju 13 u modelu `Kategorija`

1. U `models/catalog.py` dodaj kolonu `roditelj_id` kao `Mapped[int | None]` sa `ForeignKey("kategorija.id")` i `nullable=True`.
2. Dodaj relationship par:
   - `roditelj` (jedan roditelj ili `None`);
   - `deca` (lista podkategorija).
3. U `roditelj` relationship-u dodaj `remote_side` da SQLAlchemy zna referentnu stranu self-veze.
4. Ne menjaj postojeću vezu `proizvodi` prema modelu `Proizvod`.

### Korak 3: validacija mapiranja

1. Ponovo pokreni `configure_mappers()` komandu.
2. Ako prijavi gresku oko `back_populates` ili `remote_side`, ispravi pre bilo kakvog testnog unosa.

### Korak 4: proveri ponašanje na privremenoj SQLite bazi

1. Napravi privremeni engine (`sqlite://`) i kreiraj shemu iz `Base.metadata.create_all(engine)`.
2. Uključi FK enforcement (`PRAGMA foreign_keys=ON`) na konekciji.
3. Proveri tri upisa:
   - korenska kategorija (`roditelj_id=None`),
   - podkategorija koja pokazuje na koren,
   - pod-podkategorija koja pokazuje na podkategoriju.
4. Proveri ORM navigaciju u oba smera:
   - `dete.roditelj`,
   - `koren.deca`.
5. Proveri neuspeh za nepostojeci roditeljski ID i uradi `session.rollback()` nakon `IntegrityError`.

### Korak 5: dokumentacija i sinkronizacija artefakata

1. Azuriraj `13_self_referencing_relationships.md` da odgovara stvarnoj implementaciji i srpskim nazivima.
2. Azuriraj `README.md` prakticnog paketa (`fast-api-course-my-work/sqlalchemy_orm_fundamentals/README.md`) sa statusom lekcije 13.
3. Azuriraj `ERD_project_1.drawio` dodavanjem self-veze `kategorija.roditelj_id -> kategorija.id`.

### Korak 6: zavrsna provera pre commita

1. Proveri whitespace i format:

```bash
git diff --check -- 'fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/catalog.py' 'fast-api-course-my-work/sqlalchemy_orm_fundamentals/README.md' 'docs/sqlalchemy_orm_fundamentals/01_defining_database_models(tables)/13_self_referencing_relationships.md' 'fast-api-course-my-work/teorija_po_danima/dan_15_sqlalchemy_orm_fundamentals_2.md'
```

2. Ako je sve cisto, tek tada radi `git add`, `git commit`, pa `git push`.

### Kako da radiš svakog dana nadalje

1. Prvo mala teorija iz jedne lekcije.
2. Onda jedna ciljna izmena u modelima.
3. Odmah posle toga jedna tehnicka validacija (`configure_mappers` + kratka SQLite provera).
4. Na kraju azuriranje dokumentacije (README + teorija + ERD).

Ovim ritmom izbegavas velike skokove i mnogo lakse hvatas greske dok su male i lokalizovane.
