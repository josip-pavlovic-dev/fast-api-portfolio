# SQLAlchemy ORM Fundamentals 3 - Unique Constraints, UniqueConstraint, PrimaryKey i ForeignKey

## Pitanje_1:

PITANJE: Nije mi baš jasna uloga `SQLAlchemyja` sada. Ja sam mislio da on preku `unique=True` govori bazi da je unikatna kolona u pitanju ali sada ispada da `unique` ograničenje pripada `bazi`. Molim te mi pojasni mi ovo.

---

## Odgovor_1:

ODGOVOR: `SQLAlchemy` je ORM (Object-Relational Mapper) koji omogućava rad sa bazom podataka koristeći Python objekte. Kada koristimo `unique=True` u definiciji kolone, mi zapravo govorimo `SQLAlchemyju` da generiše odgovarajući SQL kod koji će kreirati `unique` ograničenje u bazi podataka. Dakle, `unique` ograničenje tehnički pripada bazi, ali `SQLAlchemy` nam omogućava da ga definišemo kroz Python kod, što olakšava rad i održavanje modela.

### Detaljno objašnjenje:

Razumem zašto deluje kontradiktorno. Precizno rečeno: **`unique=True` pišemo u SQLAlchemy modelu, a SQLAlchemy na osnovu toga napravi UNIQUE ograničenje u bazi. Zatim sama baza sprovodi to pravilo.**

Tok izgleda ovako:

1. U modelu napišeš:

   ```python
   naziv: Mapped[str] = mapped_column(String(50), unique=True)
   ```

2. SQLAlchemy zabeleži to pravilo u metapodacima modela i, kada kreira šemu preko `Base.metadata.create_all(engine)`, prevede ga u `SQL upite` uz pomoć dijalekta (npr. PostgreSQL, SQLite) koji je definisan u `engine`-u i koji baza razume. Pojednostavljeno, baza dobije nešto poput:

   ```sql
   CREATE TABLE kategorija (
       naziv VARCHAR(50) UNIQUE
   );
   ```

3. Kada aplikacija pokuša da sačuva dupliran naziv, **baza odbije upis**. SQLAlchemy prenese grešku aplikaciji, obično kao `IntegrityError`.

Dakle, `unique=True` u SQLAlchemy modelu nije Python provera koja sama pregleda svaki unos i odbija duplikate. To je način na koji **deklaršeš pravilo u modelu kroz SQLAlchemy**, da bi to pravilo pri kreiranju šeme postalo **ograničenje koje čuva baza**. Zato ograničenje i dalje važi ako neko upisuje podatke direktnim `SQL`-om ili iz druge aplikacije.

Važna napomena: ako tabela već postoji, samo dodavanje `unique=True` u model ne menja automatski postojeću bazu. Potrebna je migracija koja će tamo dodati ograničenje.

---

## Pitanje_2:

PITANJE: Zar nismo rekli da ograničenja preko SQLAlchemy-ja ne važe ako se zaobiđe SQLAlchemy način generisanja upita za SQL bazu i koristi se upis podataka preko SQLite Terminala itd?

---

## Odgovor_2:

ODGOVOR: Nije tačno da ograničenja preko SQLAlchemy-ja ne važe ako se zaobiđe SQLAlchemy način generisanja upita. Kada definišeš `unique=True` u SQLAlchemy modelu i kreiraš šemu, SQLAlchemy generiše odgovarajuće SQL ograničenje u bazi. To ograničenje važi bez obzira na to kako se podaci upisuju u bazu, bilo preko SQLAlchemy-ja, direktnog SQL-a ili drugog alata. Dakle, ako neko pokuša da unese duplikat direktno preko SQLite Terminala, baza će odbiti upis zbog `UNIQUE` ograničenja. Stoga, ograničenja definisana u SQLAlchemy modelu preko `unique=True` su zapravo ograničenja baze podataka i važe u svim slučajevima. Sa druge strane, ako tabela već postoji i nema `UNIQUE` ograničenja, samo dodavanje `unique=True` u model neće automatski promeniti postojeću bazu; potrebna je migracija. Ako ponovo kreiraš šemu sa `Base.metadata.create_all(engine)` nakon dodavanja `unique=True`, obrisaće se postojeće tabele i kreiraće nove sa odgovarajućim ograničenjima. Svi podaci iz baze će biti izgubljeni! Zbog toga se preporučuje koristiti migracije za promene u šemi baze podataka.

### Detaljno objašnjenje:

Ne baš. Razlika je između **zaobilaženja SQLAlchemy-ja** i **zaobilaženja ograničenja koje je već upisano u šemu baze** sa akcentom na **stvarna ograničenja u bazi podataka**.

`unique=True` u modelu je instrukcija `SQLAlchemy`-ju da, pri `kreiranju` ili `migraciji šeme`, napravi `UNIQUE` ograničenje u bazi. Kada je to ograničenje zaista prisutno u SQLite bazi, SQLite ga sprovodi bez obzira na to da li se upis radi kroz ORM, direktan SQL ili SQLite Terminal. Direktan upis ne zaobilazi ograničenje baze.

Ali ako je `unique=True` dodat samo u Python model, a postojeća baza nije ažurirana, SQLite Terminal ne zna ništa o toj izmeni. Tada direktan upis može napraviti duplikat, jer ograničenje još ne postoji u bazi. Isti slučaj važi ako terminal otvori drugi SQLite fajl umesto fajla koji koristi aplikacija.

Dakle:

- **ORM provera ili aplikaciona logika** može se zaobići direktnim SQL-om.
- **UNIQUE ograničenje u stvarnoj šemi baze** ne može se zaobići običnim direktnim upisom; baza će ga sprovesti.

Rečenica u belešci je tačna uz taj uslov. Preciznije bi glasila: „Zato UNIQUE ograničenje, **ako je kreirano u šemi baze**, i dalje važi pri direktnom SQL upisu ili upisu iz druge aplikacije.“

---
