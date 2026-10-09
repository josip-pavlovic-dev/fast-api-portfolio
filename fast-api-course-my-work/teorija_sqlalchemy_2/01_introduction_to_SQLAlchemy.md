# Lekcija 01: Uvod u SQLAlchemy

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 0:04–4:46
**Napomena o obimu:** Ovaj deo je uvod u alat i strukturu predavanja. Još nema konkretnog programskog primera; tema `Engine` je samo najavljena na kraju.

## Cilj uvoda

Najvažnija poruka nije da je SQLAlchemy „biblioteka za ORM“, nego da je **alatni komplet za rad sa relacionim bazama**. ORM je jedan njegov deo. Možemo da koristimo SQLAlchemy za konekcije, SQL upite i upravljanje šemom i bez mapiranja Python klasa na tabele.

Predavanje zatim postavlja širu putanju učenja: prvo osnove povezivanja i transakcija, zatim opis šeme i sastavljanje SQL upita, pa tek onda ORM obrasci za čuvanje i učitavanje Python objekata.

## Šta SQLAlchemy obuhvata?

U uvodu se pominje nekoliko sposobnosti koje zajedno čine SQLAlchemy:

| Oblast                    | Šta rešava                                                                   | Primer pojma koji ćemo kasnije sresti |
| ------------------------- | ---------------------------------------------------------------------------- | ------------------------------------- |
| Rad sa DBAPI drajverom    | Pruža bogatiji i ujednačeniji sloj iznad Python interfejsa za drajvere baza. | `Engine`, `Connection`, transakcije   |
| Opis šeme                 | Opisuje tabele, kolone, tipove i ograničenja; može da generiše DDL za šemu.  | `MetaData`, `Table`, `Column`         |
| Izgradnja SQL upita       | Gradi SQL iskaze pomoću Python objekata i izraza.                            | `select()`, `insert()`, `where()`     |
| Inspekcija postojeće baze | Čita strukturu baze koja već postoji.                                        | tabele, kolone, tipovi, ograničenja   |
| ORM                       | Povezuje Python klase i objekte sa relacionim podacima.                      | deklarativni modeli, `Session`, veze  |

Ovo su povezani slojevi, ali nisu ista stvar. Na primer, ORM ne zamenjuje samu bazu niti ukida SQL; ORM koristi SQLAlchemy Core da bi sastavio i izvršio SQL potreban za rad sa mapiranim objektima.

## DBAPI i SQLAlchemy

**DBAPI** je uobičajeni naziv za Python Database API, definisan specifikacijom PEP 249. Specifikacija opisuje zajednički oblik kojim Python programi pristupaju drajverima baza. Konkretan drajver zatim komunicira sa određenom bazom, na primer SQLite-om ili PostgreSQL-om.

SQLAlchemy sedi iznad drajvera. Njegov dijalekt poznaje razlike u SQL sintaksi i tipovima određene baze, a `Engine` obezbeđuje SQLAlchemy-jevu ulaznu tačku za izvršavanje. Zato aplikacioni kod može da koristi dosledniji skup SQLAlchemy API-ja, dok dijalekt i drajver obavljaju posao prilagođavanja i komunikacije.

To ne znači da SQLAlchemy može da sakrije sve razlike između baza. Razlike u tipovima, ograničenjima, transakcijama i funkcijama baze i dalje mogu biti važne. SQLAlchemy olakšava rad sa njima; ne čini različite baze potpuno identičnim.

## Core i ORM

SQLAlchemy se često objašnjava kroz dva velika dela:

- **Core** je temeljni sloj za konekcije, šemu i SQL izraze. Njime radimo sa objektima koji predstavljaju tabele i SQL iskaze, čak i ako nemamo ORM klase.
- **ORM** je viši sloj koji mapira Python klase na tabele i Python objekte na redove. ORM je izgrađen na Core-u i koristi njegove mehanizme za izvršavanje upita.

Core nije samo „sirovi SQL“, a ORM nije „baza bez SQL-a“. U Core-u možemo SQL da gradimo kompoziciono, kroz Python objekte. ORM nam omogućava da radimo preko mapiranih klasa, ali ispod toga i dalje postoje SQL iskazi, konekcije i transakcije.

U SQLAlchemy-ju 2.0 ova veza je naročito vidljiva u obrascu za upite: funkcija `select()` služi kao osnova za izgradnju iskaza, a način izvršavanja određuje da li dobijamo obične rezultate iz Core konekcije ili ORM objekte kroz `Session`.

### Pojednostavljen tok

```text
Python kod
   -> SQLAlchemy Core gradi ili izvršava SQL
   -> Engine i dijalekt prilagođavaju izvršavanje izabranoj bazi
   -> DBAPI drajver komunicira sa bazom
   -> baza izvršava SQL i vraća rezultat
   -> Core ili ORM predstavlja rezultat Python kodu
```

Ovo je mapa pojmova, ne detaljan redosled poziva. Sledeće lekcije razlažu `Engine`, konekcije i izvršavanje korak po korak.

## Zašto je poznavanje SQL-a važno?

Predavač preporučuje osnovno poznavanje SQL-a: `SELECT`, `INSERT` i pravljenja tabele. Razlog je što SQLAlchemy uglavnom automatizuje i strukturira rad sa SQL-om, ali ne menja relacionu logiku koja stoji iza njega.

Kada ORM upit ne vrati ono što očekujemo, korisno je umeti da razmišljamo o ekvivalentnom SQL-u: koje tabele se čitaju, koji uslov filtrira redove i koje kolone se vraćaju. Isto tako, razumevanje `INSERT`-a i ograničenja pomaže da se protumači zašto baza odbija upis.

Predavač pominje i transakcije kao korisno predznanje. **Transakcija** grupiše rad sa bazom tako da aplikacija može promene da potvrdi (`COMMIT`) ili poništi (`ROLLBACK`). To je važno jer SQLAlchemy upravlja izvršavanjem upita u kontekstu transakcija; transakcija nije samo još jedna sintaksa za INSERT.

## Predznanje za praćenje kursa

Prema predavanju, korisno je imati:

- osnovno iskustvo sa Python programiranjem;
- osnovno razumevanje klasa i instanci;
- početno poznavanje SQL-a: `SELECT`, `INSERT` i `CREATE TABLE`;
- makar početnu predstavu o tome šta je transakcija.

Nije potrebno unapred biti ekspert za ORM. Ipak, ako su SQL tabele i upiti potpuno novi pojmovi, vredi prvo utvrditi te osnove; SQLAlchemy ih koristi, ne zamenjuje ih.

## Struktura predavanja

Predavač kaže da izvorni materijal ima šest modula, ali da će na vremenski ograničenom predavanju proći većinu od prvih pet. Šesti modul obrađuje ORM veze, temu koja je dovoljno velika za zasebnu lekciju; izvorni GitHub materijal sadrži i taj modul.

Uvod najavljuje ovaj tok:

1. povezivanje sa bazom i transakcije;
2. opis tabela i metadata;
3. izgradnja SQL upita;
4. ORM obrasci za trajno čuvanje podataka;
5. ORM veze kao zasebna, šira tema u dodatnom modulu.

Zato nemoj očekivati da se sve o `relationship()` nauči iz uvodnog dela ili nužno iz vremenski ograničenog predavanja. Ako u transkriptu neke lekcije nedostaje konkretan primer ili objašnjenje sa slajda, možemo ga dopuniti kada pošalješ odgovarajući izvorni kod ili naredni deo materijala.

## Dokumentacija koju predavanje preporučuje

Predavač izdvaja tri mesta u zvaničnoj SQLAlchemy dokumentaciji:

- [SQLAlchemy 2.0 dokumentacija](https://docs.sqlalchemy.org/en/20/)
- [Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html), duži vodič koji povezuje osnovne koncepte;
- [ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html), kratak prikaz tipičnog ORM toka;
- [ORM Querying Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html), vodič za upite ORM stilom u verziji 2.0.

Za ovaj kurs treba čitati dokumentaciju za SQLAlchemy 2.0, a ne nasumične primere za 1.x. Stari primeri mogu da koriste obrasce koji su i dalje dostupni zbog kompatibilnosti, ali više nisu preporučeni kao novi 2.0 stil.

## Najava teme `Engine`

Na kraju dostavljenog transkripta počinje tema `Engine`. Predavač ga opisuje kao objekat koji upravlja skupom konekcija i izvršavanjem SQL-a prema bazi.

Za sada zapamti samo razliku između `Engine`-a i jedne konekcije:

- `Engine` je dugotrajniji objekat aplikacije koji zna kako da dođe do baze i upravlja pool-om konekcija;
- konekcija predstavlja konkretnu, privremeno korišćenu vezu sa bazom;
- jedna aplikacija obično deli `Engine`, a za pojedinačan posao uzima konekciju iz njegovog pool-a.

Detalji kao što su kada se stvarna konekcija otvara, kako se pozajmljuje iz pool-a, kada se vraća i kako se transakcija završava pripadaju narednim lekcijama. Ovde ih ne treba mešati u potpunu definiciju `Engine`-a.

## Verzijski okvir

Ovo je predavanje o SQLAlchemy-ju 2.0 iz 2023. godine. Playground u ovom repozitorijumu koristi SQLAlchemy `2.0.38`, pa buduće primere proveravamo u toj verziji.

Glavna praktična posledica za početak je da pratimo savremeni 2.0 stil, naročito `select()` za upite. Ako naiđemo na stariji obrazac, objasnićemo da li je samo drugačiji stil, kompatibilni legacy API ili ponašanje koje se promenilo.

## Sažetak za ponavljanje

- SQLAlchemy je alatni komplet za baze; ORM je samo jedan njegov deo.
- Core pruža temelj za konekcije, šemu i SQL izraze; ORM je sloj iznad njega.
- SQLAlchemy koristi DBAPI drajver, ali mu dodaje dijalekt, izvršavanje i druge alate.
- Python izrazi mogu da predstavljaju SQL iskaze; ne izvršavaju se kao obična Python logika nad celom bazom.
- Osnovni SQL i transakcije pomažu da se razume šta SQLAlchemy radi.
- Ovaj transkript je uvod i najava `Engine`-a; u njemu još nema konkretnog modela ni programskog primera.

---

## Dodatak: Core i ORM upit u SQLAlchemy 2.0

**Ovaj primer nije prikazan u dostavljenom transkriptu.** Služi samo da konkretnije prikaže razliku koju predavanje najavljuje. Oba iskaza ispod su SQLAlchemy izrazi; razlikuju se po tome da li su polja opisana kroz Core `Table` ili ORM klasu.

```python
from sqlalchemy import Column, Integer, MetaData, String, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Core opis tabele
metadata = MetaData()
autori_tabela = Table(
	"autori_core",
	metadata,
	Column("id", Integer, primary_key=True),
	Column("ime", String(100), nullable=False),
)

core_iskaz = select(autori_tabela.c.ime).where(
	autori_tabela.c.ime == "Pera"
)


# ORM opis tabele
class Base(DeclarativeBase):
	pass


class Autor(Base):
	__tablename__ = "autori_orm"

	id: Mapped[int] = mapped_column(primary_key=True)
	ime: Mapped[str] = mapped_column(String(100), nullable=False)


orm_iskaz = select(Autor).where(Autor.ime == "Pera")
```

### Kako čitati primer

- `autori_tabela.c.ime` označava kolonu `ime` u Core objektu tabele. `.c` je kolekcija kolona te tabele.
- `Autor.ime` označava mapirani ORM atribut klase `Autor`.
- `select(...)` gradi objekat koji predstavlja upit; linija koja ga napravi sama po sebi još ne šalje upit bazi.
- `.where(...)` dodaje uslov. SQLAlchemy vrednost `"Pera"` tretira kao bind parametar, umesto da je nebezbedno spaja u SQL tekst.
- `core_iskaz` bira vrednost kolone. Izvršavanje preko `Connection`-a daje rezultat na nivou kolona/redova.
- `orm_iskaz` bira ORM entitet `Autor`. Izvršavanje preko `Session`-a može da vrati `Autor` Python objekte.

Važan 2.0 obrazac je da je `select()` zajednički način izgradnje upita; Core ili ORM ponašanje proizlazi iz toga šta se bira i da li se iskaz izvršava preko `Connection`-a ili ORM `Session`-a. Kasnije ćemo ove iskaze zaista izvršiti i pratiti SQL koji baza dobija.
