# Lekcija 19: Uvod u trigger-e na nivou baze

## Cilj lekcije

U prethodnoj lekciji korišćen je SQLAlchemy ORM event listener da `Category.name` i `Category.slug` pretvori u mala slova. Ova lekcija pravi sličnu transformaciju pomoću PostgreSQL trigger-a, tako da se ona izvršava u bazi pri unosu ili izmeni reda.

Glavna razlika je mesto izvršavanja: ORM listener radi kroz SQLAlchemy ORM u aplikaciji, dok trigger izvršava funkciju unutar baze. Trigger na taj način može da obuhvati upise iz različitih aplikacija i klijenata koji rade nad istom bazom.

Ovo je uvod u PostgreSQL trigger-e, ne potpuni vodič za njih niti prenosiv primer za sve DBMS-ove.

## Šta je trigger

Trigger je objekat baze koji pokreće funkciju kada se nad određenom tabelom dogodi neki događaj, najčešće `INSERT`, `UPDATE` ili `DELETE`. Trigger može da se podesi da radi pre ili posle operacije i za svaki red ili za celu naredbu, u zavisnosti od baze i definicije.

U ovoj lekciji trigger je:

- vezan za tabelu `category`;
- pokrenut pre `INSERT`-a ili `UPDATE`-a;
- izvršen za svaki red koji se menja;
- zadužen da `name` i `slug` pretvori u mala slova.

Trigger i funkcija koju trigger poziva su dva odvojena objekta baze. Funkcija sadrži logiku, a trigger određuje kada i nad kojom tabelom se ta logika poziva.

## PostgreSQL funkcija trigger-a

Source definiše sirovi SQL u promenljivoj `trigger_sql`:

```sql
CREATE OR REPLACE FUNCTION lowercase_category_fields()
RETURNS TRIGGER AS $$
BEGIN
	NEW.name := LOWER(NEW.name);
	NEW.slug := LOWER(NEW.slug);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Tumačenje delova funkcije:

- `CREATE OR REPLACE FUNCTION` kreira funkciju ili zamenjuje postojeću funkciju istog potpisa.
- `RETURNS TRIGGER` označava da je funkcija namenjena trigger-u i vraća trigger vrednost, a ne običan rezultat poput broja ili teksta.
- `NEW` je PostgreSQL zapis koji predstavlja novi red za `INSERT` ili novu verziju reda za `UPDATE`.
- `NEW.name := LOWER(NEW.name)` i analogna linija za `slug` menjaju vrednosti novog reda.
- `RETURN NEW` vraća izmenjeni red. Kod `BEFORE` trigger-a nad redom, to je verzija koja nastavlja obradu i može biti upisana.
- `LANGUAGE plpgsql` kaže da je telo funkcije napisano u PostgreSQL-ovom proceduralnom jeziku PL/pgSQL.

## Kreiranje trigger-a

Nakon funkcije source definiše trigger:

```sql
CREATE TRIGGER category_lowercase_trigger
BEFORE INSERT OR UPDATE ON category
FOR EACH ROW
EXECUTE FUNCTION lowercase_category_fields();
```

- `category_lowercase_trigger` je ime trigger objekta.
- `BEFORE INSERT OR UPDATE ON category` vezuje ga za unos i izmenu redova u tabeli `category`, pre nego što se promena primeni.
- `FOR EACH ROW` znači da se funkcija izvršava za svaki red koji operacija obrađuje. Ako jedna naredba izmeni više redova, trigger se izvršava za svaki od njih.
- `EXECUTE FUNCTION ...` navodi koju trigger funkciju PostgreSQL poziva.

Kada klijent upiše `name = 'TeleVizori'`, trigger izmeni `NEW.name` u `televizori` pre nego što se red sačuva. Isti postupak važi za `slug` i za izmene postojećih redova.

## Pokretanje DDL-a iz SQLAlchemy-ja

Definisanje stringa `trigger_sql` samo po sebi ne šalje SQL bazi. Source koristi SQLAlchemy DDL objekat i SQLAlchemy schema event da se taj SQL izvrši nakon kreiranja tabele:

```python
from sqlalchemy import DDL, event

event.listen(Category.__table__, "after_create", DDL(trigger_sql))
```

Ovde:

- `Category.__table__` je cilj registracije, odnosno SQLAlchemy Table objekat za tabelu `category`.
- `after_create` je SQLAlchemy schema događaj koji se emituje nakon što se tabela kreira.
- `DDL(trigger_sql)` predstavlja sirovu DDL naredbu koju SQLAlchemy treba da izvrši u tom trenutku.

Dakle, SQLAlchemy event ovde služi kao okidač za kreiranje objekata šeme. Nakon izvršavanja, funkcija i trigger postoje u PostgreSQL-u i sama baza ih poziva pri budućim upisima. To je drugačije od listener-a iz prethodne lekcije, koji poziva Python funkciju tokom ORM flush-a.

## Ograničenje `after_create`

Ovaj pristup povezuje kreiranje trigger-a sa kreiranjem tabele. Ako tabela već postoji, uobičajeni `metadata.create_all()` ne menja postojeću tabelu i `after_create` se ne aktivira za nju. Zato ovaj kod nije zamena za migraciju i neće sam dodati trigger postojećoj bazi.

Za postojeću bazu, promenu treba primeniti migracijom ili drugim eksplicitnim DDL postupkom. Kreiranje, izmena i uklanjanje funkcije i trigger-a treba držati usklađenim sa verzijom šeme. U prikazanom SQL-u funkcija koristi `CREATE OR REPLACE`, ali trigger koristi `CREATE TRIGGER` bez uslova `IF NOT EXISTS`; ponovljeno izvršavanje DDL-a nad tabelom na kojoj trigger već postoji može zato pasti zbog duplog imena.

## ORM listener naspram trigger-a

| Osobina             | SQLAlchemy ORM listener                         | PostgreSQL trigger                                              |
| ------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| Gde se izvršava     | U Python aplikaciji, tokom ORM događaja         | U PostgreSQL bazi                                               |
| Koje upise obuhvata | Operacije kroz ORM koje registruju listener     | Upise na tabelu koji aktiviraju trigger, bez obzira na klijenta |
| U primeru           | Menja `target.name` i `target.slug`             | Menja `NEW.name` i `NEW.slug`                                   |
| Zavisnost           | Aplikacija mora učitati i registrovati listener | Baza mora imati funkciju i trigger                              |
| Prenosivost         | Vezan za SQLAlchemy ORM API                     | Konkretna sintaksa je vezana za DBMS                            |

Ova dva pristupa mogu da se dopunjuju. ORM listener može normalizovati Python objekat odmah u aplikaciji, dok trigger obezbeđuje da se ista transformacija sprovede za druge klijente. Ako se koriste zajedno, normalizacija se može desiti dvaput; `.lower()` je za ove vrednosti praktično idempotentna operacija, ali i dalje treba jasno dokumentovati gde se pravilo sprovodi.

## Važne posledice i rizici

- **Trigger nije isto što i `CHECK` constraint.** Trigger izvršava proceduru i može transformisati podatke; `CHECK` constraint proverava da li izraz važi. Izabrati mehanizam prema tome da li podatak treba odbiti ili preoblikovati.
- **Jedinstvenost se i dalje proverava.** Ako `Category.name` ili `Category.slug` imaju `UNIQUE` ograničenje, vrednost koja nakon `LOWER()` postane jednaka već postojećoj vrednosti može izazvati grešku i odbiti ceo upis.
- **Aplikacioni objekat možda ne odražava transformaciju odmah.** Trigger menja vrednost u bazi. Python ORM objekat može zadržati originalnu vrednost do osvežavanja iz baze, osim kada je vrednost vraćena/ponovo učitana odgovarajućim mehanizmom.
- **Efekti mogu biti manje vidljivi.** Aplikacioni kod ne prikazuje direktno da je baza promenila vrednost, pa trigger-e treba dokumentovati i testirati zajedno sa migracijama.
- **Trigger utiče na sve klijente**, što je prednost kada se pravilo mora dosledno primenjivati, ali i razlog da se izbegnu neočekivane ili spore operacije u trigger funkciji.

## Prenosivost

Transkript napominje da slične mogućnosti postoje u drugim tehnologijama baza, ali konkretan primer nije prenosiv. `LANGUAGE plpgsql`, `RETURNS TRIGGER`, promenljiva `NEW` i oblik `EXECUTE FUNCTION` pripadaju PostgreSQL-u. Druge baze imaju sopstvenu sintaksu, proceduralne jezike i pravila za trigger-e.

Pre korišćenja u drugom DBMS-u treba napisati odgovarajuću implementaciju za taj sistem. SQLAlchemy `DDL` prosleđuje zadati SQL bazi; ne prevodi PostgreSQL trigger sintaksu u ekvivalent za druge dijalekte.

## Napomene o source snapshot-u

- U `16_trigger.py`, `event.listen(Category.__table__, "after_create", DDL(trigger_sql))` je registrovan za tabelu `Category`, pa se DDL odnosi na `category`.
- U ovom source-u `category_id` prosleđuje `nullable=False` objektu `Column`, a ne konstruktoru `ForeignKey`; time je ispravljena greška koja je sprečavala učitavanje modela u prethodnom snapshot-u.
- Check constraint-i sa imenima `check_category_...` i dalje su deklarisani unutar klase `Product`, pa se odnose na tabelu `product`, ne na `category`. To je postojeća nepodudarnost u source-u, nevezana za trigger.
- Primer kreira trigger preko SQLAlchemy schema event-a, ali stvarni trigger kod je PostgreSQL DDL. Runtime ponašanje mora se proveriti nad PostgreSQL bazom i nakon što su tabela i DDL ispravno kreirani.

## Pitanja za proveru razumevanja

1. Koja je razlika između SQLAlchemy ORM listener-a i trigger-a koji izvršava baza?
2. Šta predstavljaju `NEW` i `RETURN NEW` u prikazanoj PostgreSQL funkciji?
3. Šta znači `FOR EACH ROW` kada jedna naredba menja više redova?
4. Koja je uloga `event.listen(..., "after_create", DDL(...))`?
5. Zašto `after_create` ne dodaje trigger tabeli koja je već postojala pre pokretanja aplikacije?
6. Zašto se prikazani PL/pgSQL kod ne može direktno preneti na SQLite?
7. Šta može da se dogodi ako `LOWER()` proizvede vrednost koja već postoji u jedinstvenoj koloni?

## Sažetak

- PostgreSQL trigger automatski poziva funkciju pri definisanom događaju nad tabelom.
- Primer koristi `BEFORE INSERT OR UPDATE`, `FOR EACH ROW` i `NEW` da normalizuje `category.name` i `category.slug` pre upisa.
- SQLAlchemy `DDL` i `after_create` povezuju kreiranje trigger-a sa kreiranjem `Category` tabele; postojeće tabele zahtevaju migraciju ili drugi DDL korak.
- Za razliku od ORM listener-a, trigger se izvršava u bazi i može obuhvatiti različite klijente.
- Trigger funkcija i sintaksa iz primera su PostgreSQL-specifični, iako druge baze imaju svoje ekvivalentne mehanizme.
- Ovo je završna lekcija prve oblasti: prethodne teme o modelima, ograničenjima i događajima povezuju se sa automatizacijom na nivou baze.
