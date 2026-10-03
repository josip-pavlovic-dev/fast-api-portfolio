# Lekcija 17: Uvod u ograničenja na nivou baze

## Cilj lekcije

Ograničenja na nivou baze su pravila zapisana u šemi koja DBMS proverava pri upisu ili izmeni podataka. Ona važe bez obzira na to da li podatke šalje FastAPI aplikacija, React klijent, skripta ili neki drugi program.

Ova lekcija je uvod, a ne sveobuhvatan pregled. Pored ograničenja, pred najavu sledeće teme pominju se event listener-i i trigger-i, ali se oni u ovom delu ne obrađuju. Lekcija uvodi `CheckConstraint` i povezuje ga sa prethodno obrađenim pravilima kao što su `NOT NULL`, `UNIQUE` i strani ključevi. Primeri proveravaju da tekstualna polja nisu prazna i da slug prati zadati format.

## Validacija u aplikaciji i ograničenja baze

Pravila se mogu proveravati na više slojeva:

- **Validacija u aplikaciji** daje brze, razumljive poruke pre slanja upita u bazu. Na primer, API šema može proveriti da naziv nije prazan.
- **Ograničenje baze** čuva integritet bez obzira na klijenta. Ako drugi program zaobiđe API validaciju, baza i dalje odbija nevažeće podatke.

Često su korisna oba sloja: aplikacija poboljšava korisničko iskustvo, a baza je konačna zaštita podataka. Validacija samo u jednoj aplikaciji nije dovoljna kada istoj bazi pristupa više programa ili direktni SQL.

Ograničenje baze ne zamenjuje API validaciju: greška baze može biti prekasna i teža za pretvaranje u jasnu poruku. Sa druge strane, API validacija ne zamenjuje bazno ograničenje integriteta.

## Zašto `nullable=False` nije dovoljno za tekst

`nullable=False` sprečava SQL vrednost `NULL`, ali prazan string `""` nije isto što i `NULL`. Zato tekstualna kolona može biti `NOT NULL`, a ipak sadržati nula znakova.

Razlikuj:

| Vrednost | Šta proverava `nullable=False`? | Šta proverava `name <> ''`?                               |
| -------- | ------------------------------- | --------------------------------------------------------- |
| `NULL`   | odbija                          | sama CHECK provera nije dovoljna; koristi se i `NOT NULL` |
| `""`     | dozvoljava                      | odbija                                                    |
| `"   "`  | dozvoljava                      | dozvoljava, jer vrednost nije prazan string               |
| `"TV"`   | dozvoljava                      | dozvoljava                                                |

Ako pravilo zahteva vidljive znakove, provera samo `<> ''` nije dovoljna: treba ukloniti ili proveriti razmake prema nameri aplikacije. I način na koji DBMS tretira prazan string može se razlikovati; na primer, Oracle ga tretira kao `NULL` u tekstualnom kontekstu.

## `CheckConstraint`

SQLAlchemy predstavlja SQL `CHECK` ograničenje klasom `CheckConstraint`. Ono dodaje SQL uslov koji vrednost ili skup vrednosti mora da zadovolji:

```python
from sqlalchemy import CheckConstraint

__table_args__ = (
	CheckConstraint("name <> ''", name="check_product_name_not_empty"),
)
```

Izraz je SQL, ne Python `if` uslov. DBMS ga proverava pri `INSERT`-u i `UPDATE`-u. Ako izraz nije zadovoljen, baza odbija izmenu i SQLAlchemy obično prijavljuje grešku integriteta.

### `__table_args__`

U source primeru više tabela/kolonskih ograničenja navedeno je kroz `__table_args__`:

```python
__table_args__ = (
	CheckConstraint("name <> ''", name="check_product_name_not_empty"),
	CheckConstraint("slug <> ''", name="check_product_slug_not_empty"),
)
```

To je deklarativno mesto za ograničenja i druge opcije cele tabele. Više ograničenja se navodi kao elementi tuple-a; završni zarez je važan i za tuple sa jednim elementom. `name=...` daje ograničenju prepoznatljivo ime u šemi i greškama.

`CheckConstraint` se može dodati i direktno koloni u nekim oblicima SQLAlchemy deklaracije; `__table_args__` je pogodan kada se pravila organizuju na nivou cele tabele ili proveravaju više kolona.

Pre ovog primera kurs podseća na `UNIQUE` ograničenje u međutabeli `product_promotion_event`: kombinacija `product_id` i `promotion_event_id` mora biti jedinstvena. To je primer ograničenja nad kombinacijom kolona, a ne `CHECK` uslova.

## Primeri iz source koda

Source definiše tri pravila:

```python
__table_args__ = (
	CheckConstraint("name <> ''", name="check_category_name_not_empty"),
	CheckConstraint("slug <> ''", name="check_category_slug_not_empty"),
	CheckConstraint(
		"slug ~ '^[a-z0-9_-]+$'",
		name="check_category_slug_format",
	),
)
```

Prva dva pravila zahtevaju da `name` i `slug` ne budu prazan string. Treće proverava slug prema regularnom izrazu:

- `^` označava početak teksta;
- `[a-z0-9_-]` dozvoljava mala slova `a`–`z`, cifre `0`–`9`, donju crtu `_` i crticu `-`;
- `+` zahteva jedan ili više dozvoljenih znakova;
- `$` označava kraj teksta.

Zato regex iz source-a dozvoljava i donju crtu. Transkript je u govornom opisu nabrojao slova, brojeve i crticu, ali nije pomenuo `_`; to je mala razlika između opisa i koda.

Transkript zatim navodi da se slična pravila mogu razmotriti i za druge podatke iz ERD-a: za `Category` naziv i slug, za kategorijski nivo koji zavisi od toga da li kategorija ima roditelja, za datume promocije i za cenu umanjenu popustom. To su ideje za moguća pravila, ne dodatni constraint-i implementirani u prikazanom kodu. Posebno, pravilo koje zavisi od roditeljskog reda ne može se tek tako proveriti običnim `CHECK` uslovom u jednom redu; za takvu logiku treba razmotriti drugi mehanizam, poput aplikacione logike ili trigger-a.

## Važne razlike u priloženom source-u

### Imena constraint-a i tabela nisu usklađeni

U prikazanom source-u `__table_args__` se nalazi unutar klase `Product`, pa ograničenja važe za kolone `product.name` i `product.slug`. Njihova imena ipak počinju sa `check_category_`. Transkript tokom objašnjenja pominje category name i slug, ali pri zaključku izričito kaže da su tri uslova primenjena na product tabelu. Dakle, nedoslednost je u imenima constraint-a i promenljivom kontekstu objašnjenja; mesto deklaracije u modelu određuje stvarnu tabelu. Ako je cilj bila tabela `Category`, deklaracije treba premestiti u tu klasu; source nisam menjao.

### Regex operator je PostgreSQL-specifičan

Operator `~` u uslovu `slug ~ '...'` je PostgreSQL operator za regularne izraze. `CheckConstraint` prosleđuje SQL izraz bazi; SQLAlchemy ne prevodi proizvoljan SQL regex izraz u prenosivu implementaciju za svaki dijalekt.

Ovaj izraz zato nije prenosiv na SQLite i druge baze bez odgovarajuće sintakse ili dodatne podrške. Izvorni kurs koristi PostgreSQL; pre upotrebe istog constraint-a na drugom DBMS-u treba proveriti sintaksu i podržane funkcije. `name <> ''` je uobičajen SQL izraz, ali i prazni string ima razlike među bazama.

## `CheckConstraint` naspram aplikacione provere

Ako API proverava slug regularnim izrazom, a baza ne proverava isto pravilo, direktni SQL ili drugi klijent može upisati nevažeći slug. Ako baza proverava pravilo, API i dalje može unapred validirati ulaz i vratiti prijateljsku grešku.

Praktičan pristup je da pravila integriteta koja moraju važiti za sve upise obezbedi baza, a da ih aplikacija ponovi za bolji odgovor korisniku. Izrazi moraju predstavljati isto poslovno pravilo; u suprotnom bi validacija mogla da odbije vrednost koju baza prihvata ili obrnuto.

`CHECK` ograničenja su za pravila koja se mogu izraziti preko vrednosti reda/kolona. Za jedinstvenost se koristi `UNIQUE`, za obaveznost `NOT NULL`, a za reference ka drugoj tabeli `FOREIGN KEY`.

## Constraint modela nije automatska migracija

Dodavanje `CheckConstraint` u Python model opisuje željenu šemu, ali ne menja samo po sebi već postojeću bazu. Ograničenje mora biti kreirano kroz `create_all()` za novu tabelu ili migraciju/izmenu šeme za postojeću tabelu.

Zbog toga se tokom razvoja proverava i stvarna šema baze, a ne samo Python deklaracija. Promena modela i promena baze su povezani koraci, ali nisu ista operacija.

## Source snapshot ne može trenutno da se učita

Pokušaj uvoza `14_constraints.py` u zajedničkom SQLAlchemy 2.0 okruženju pada dok se definiše `Category`, pre nego što se primene check ograničenja. Uzrok je ranija deklaracija `ForeignKey("category.id", nullable=False, ...)`: `nullable` ne pripada konstruktoru `ForeignKey`, već `Column`.

U source-u postoje i druge greške iz prethodnih lekcija, uključujući pogrešno prosleđen `ondelete` u `Product.category_id` i `Order.user_id`. Zato nije moguće runtime proveriti `CheckConstraint` deklaracije učitavanjem celog fajla dok se prethodne greške ne isprave. Source fajl nisam menjao.

## Pitanja za proveru razumevanja

1. Zašto `nullable=False` dozvoljava `""`?
2. Koja je razlika između `CheckConstraint` i provere u API šemi?
3. Šta znače `^`, `+` i `$` u regex-u iz source-a?
4. Koji znak source regex dozvoljava, a transkript ga nije izričito naveo?
5. Na koju tabelu su ograničenja stvarno primenjena prema položaju `__table_args__`?
6. Zašto se operator `~` ne može smatrati prenosivim SQLAlchemy izrazom?
7. Da li promena Python modela automatski dodaje constraint postojećoj bazi?

## Sažetak

- Aplikaciona validacija daje bolje poruke; constraint baze dosledno štiti podatke od svih klijenata.
- `CheckConstraint` prosleđuje SQL uslov koji baza proverava pri unosu i izmeni.
- `nullable=False` odbija `NULL`, ali ne i prazan string; `name <> ''` odbija samo prazan string, ne i tekst od razmaka.
- Source regex dozvoljava mala slova, cifre, `_` i `-`, i koristi PostgreSQL operator `~`.
- Iako se constraint-i zovu `check_category_...`, u source-u su deklarisani u `Product` klasi i zato važe za tabelu `product`.
- Model opisuje constraint, ali postojeću bazu treba promeniti migracijom ili drugim DDL korakom.
- Source trenutno pada na ranijim pogrešno postavljenim FK argumentima pre nego što check constraint-i mogu biti učitani.
