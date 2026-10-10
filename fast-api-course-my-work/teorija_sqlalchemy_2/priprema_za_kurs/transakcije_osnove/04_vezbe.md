# 04: Vežbe — transakcije

Pokušaj zadatke bez otvaranja [rešenja](05_resenja.md). Primeri su konceptualni ili koriste SQLite memorijsku bazu; nemoj koristiti postojeću bazu sa podacima koje želiš da sačuvaš.

## Vežba 1: prepoznaj granicu

Za svaku stavku napiši da li je SQL iskaz, konekcija ili transakcija:

- `INSERT INTO account ...`;
- `connection` dobijen iz `engine.connect()`;
- blok koji sadrži skidanje i dodavanje novca i završava se sa `COMMIT`.

## Vežba 2: COMMIT ili ROLLBACK

Napravi tabelu `note`, ubaci jedan red u transakciji i potvrdi ga. U drugoj transakciji ubaci drugi red pa uradi rollback. Na kraju pročitaj tabelu i predvidi koji red ostaje.

## Vežba 3: greška u sredini

U transakciji pokušaj dva INSERT-a sa istim primarnim ključem. Uhvatiti `IntegrityError`, pozvati rollback, pa proveri koliko redova te transakcije ostaje.

## Vežba 4: `engine.connect()` i eksplicitni commit

Koristi SQLAlchemy Core:

1. otvori `with engine.connect()`;
2. ubaci jedan red;
3. bez commit-a izađi iz bloka i proveri rezultat preko nove konekcije;
4. ponovi unos i eksplicitno pozovi `connection.commit()`;
5. uporedi šta je ostalo.

## Vežba 5: `engine.begin()`

U jednom `with engine.begin()` bloku ubaci dva reda i normalno izađi. Zatim ponovi u novoj transakciji, izazovi Python izuzetak posle prvog INSERT-a i pusti da izuzetak izađe iz bloka. Proveri koji redovi ostaju.

Dodatно: uhvati grešku unutar `engine.begin()` bloka i potisni je. Predvidi zašto blok tada može normalno da se završi i šta to znači za commit.

## Vežba 6: SQLAlchemy `Session`

Napravi `SessionFactory = sessionmaker(engine)`. Dodaj ORM objekat u `SessionFactory.begin()` bloku i potvrdi da ga druga sesija vidi posle normalnog izlaska.

## Vežba 7: `add`, `flush`, `commit`

U ORM sesiji proveri:

- pre `flush()`, objekat je u `session.new` i možda nema dodeljen ID;
- posle `flush()`, ID može biti dodeljen, ali transakcija još nije commit-ovana;
- rollback posle flush-a poništava nepotvrđeni INSERT;
- commit sačuva red.

## Završna provera razumevanja

Objasni svojim rečima:

1. Zašto `close()` nije isto što i `commit()`?
2. Može li rollback da poništi raniji commit?
3. Koja je razlika između `flush()` i `commit()`?
4. Šta radi `engine.begin()` pri normalnom izlasku, a šta kada izuzetak izađe iz bloka?
5. Zašto povezane izmene treba smestiti u jednu transakciju?
