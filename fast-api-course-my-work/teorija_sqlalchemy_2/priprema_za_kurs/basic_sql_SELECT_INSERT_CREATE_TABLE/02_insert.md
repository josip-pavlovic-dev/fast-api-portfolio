# 02: `INSERT` i unos podataka

## Tabela i red

`CREATE TABLE` opiše gde i kakvi podaci mogu da se čuvaju. `INSERT` doda konkretan red u već postojeću tabelu.

Za tabelu `user_account` iz prethodne lekcije možemo dodati korisnika ovako:

```sql
INSERT INTO user_account (name, fullname)
VALUES ('sandy', 'Sandy Cheeks');
```

Čitaj naredbu delovima:

- `INSERT INTO user_account` bira ciljnu tabelu;
- `(name, fullname)` navodi kolone u koje se upisuje;
- `VALUES (...)` daje jednu vrednost za svaku navedenu kolonu, istim redosledom.

Imena kolona navedi eksplicitno. Tako upit ostaje razumljiviji i otporniji na promenu redosleda kolona u šemi.

## Izostavljena kolona i default

Primarni ključ `id` može biti izostavljen kada ga SQLite automatski generiše:

```sql
INSERT INTO user_account (name, fullname)
VALUES ('sandy', 'Sandy Cheeks');
```

`created_at` je takođe izostavljen; baza uzima `DEFAULT CURRENT_TIMESTAMP` iz definicije tabele.

Ako korisno polje dozvoljava `NULL`, možeš eksplicitno poslati `NULL`:

```sql
INSERT INTO user_account (name, fullname)
VALUES ('squidward', NULL);
```

`NULL` znači da vrednost nije poznata ili nije prisutna. Nije isto što i prazan tekst `''`, nula `0` ili string `'NULL'`.

Razlika između izostavljanja i eksplicitnog `NULL` važna je za default:

```sql
-- created_at je izostavljen, pa baza može da primeni DEFAULT
INSERT INTO user_account (name) VALUES ('sandy');

-- created_at je izričito NULL; DEFAULT se ne traži
INSERT INTO user_account (name, created_at) VALUES ('sandy', NULL);
```

Drugi unos bi pao zbog `NOT NULL` ograničenja.

## Unos više redova

SQL podržava unos više redova jednim `INSERT` iskazom:

```sql
INSERT INTO user_account (name, fullname)
VALUES
    ('spongebob', 'SpongeBob SquarePants'),
    ('sandy', 'Sandy Cheeks'),
    ('patrick', 'Patrick Star');
```

Svaka grupa u zagradama daje vrednosti za iste navedene kolone. Svaki red i dalje mora poštovati `NOT NULL`, `UNIQUE`, FK i druga ograničenja tabele.

Ovo nije isti mehanizam kao SQLAlchemy Core poziv `connection.execute(insert(User), lista_rečnika)`: SQLAlchemy API prosleđuje više skupova parametara, a dijalekt/drajver bira internu strategiju. Suštinski podaci koji se unose ostaju isti.

## Ime kolone i Python vrednost nisu SQL tekst

U SQL primeru vrednosti pišemo u navodnicima prema tipu:

```sql
VALUES ('sandy', 'Sandy Cheeks')
```

U aplikacionom kodu nemoj sastavljati SQL lepljenjem korisničkog unosa u string. Koristi bind parametre. Sa SQLAlchemy `text()` pišemo imenovani parametar:

```python
from sqlalchemy import text

statement = text(
    "INSERT INTO user_account (name, fullname) "
    "VALUES (:name, :fullname)"
)

connection.execute(
    statement,
    {"name": "sandy", "fullname": "Sandy Cheeks"},
)
```

`:name` i `:fullname` nisu vrednosti, већ mesta za parametre. Vrednosti prosleđujemo odvojeno kao dictionary. SQLAlchemy i DBAPI drajver ih bezbedno vezuju uz iskaz i prilagođavaju cilju.

Za sirovi SQLite DBAPI `sqlite3` koristi drugačiji placeholder, obično `?`; SQLAlchemy `text()` koristi svoj imenovani oblik i dijalekt ga prevodi. Nemoj ručno zamenjivati placeholder-e.

## Pravila koja baza proverava pri INSERT-u

Primeri grešaka koje baza može da odbije:

- nedostaje obavezna kolona bez default-a (`NOT NULL`);
- ponovljena vrednost u `UNIQUE` koloni;
- strani ključ upućuje na nepostojeći roditeljski red, ako se FK enforcement sprovodi;
- broj vrednosti ne odgovara broju kolona u SQL naredbi.

Validacija u Python/FastAPI sloju može dati korisniku bolju poruku, ali ograničenja baze štite podatke i od drugih aplikacija/upita.

## Unos adrese i strani ključ

Ako postoji tabela:

```sql
CREATE TABLE address (
    id INTEGER PRIMARY KEY,
    email_address TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_account(id)
);
```

unos adrese mora navesti postojeći `user_id`:

```sql
INSERT INTO address (email_address, user_id)
VALUES ('sandy@example.test', 2);
```

Vrednost `2` je ključ reda u `user_account`. FK nije Python objekat; u SQL-u unosimo vrednost ključa. Kasnije ORM `relationship()` može pružiti navigaciju između Python objekata, dok FK kolona ostaje deo šeme.

## Šta ovaj modul još ne pokriva?

`INSERT` naredba opisuje zahtev za upis, ali način na koji sesija/konekcija potvrđuje ili poništava upis pripada transakcijama. Za sada prepoznaj ciljnu tabelu, kolone i vrednosti; `COMMIT`/`ROLLBACK` obrađujemo u posebnoj pripremi.
