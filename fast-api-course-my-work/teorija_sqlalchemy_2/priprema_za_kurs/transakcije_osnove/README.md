# Priprema: osnove transakcija

Ovaj modul uvodi transakcije pre nastavka SQLAlchemy kursa. Cilj je da razumeš zašto više SQL naredbi često treba tretirati kao jednu celinu, šta rade `COMMIT` i `ROLLBACK`, i kako se te granice pišu u SQLite-u i SQLAlchemy-ju 2.0.

Primeri ne koriste korisničke ili projektne baze. Python primeri rade sa memorijskom SQLite bazom (`:memory:` ili `sqlite://`). Ne uvodimo ovde konkurentne transakcije, izolacione nivoe, lock-ove, savepoint-e niti migracije.

## Redosled učenja

1. [Pojam transakcije i ACID](01_pojam_i_acid.md)
2. [`COMMIT` i `ROLLBACK`](02_commit_i_rollback.md)
3. [Transakcije u SQLAlchemy-ju](03_transakcije_u_sqlalchemy.md)
4. [Vežbe](04_vezbe.md)
5. [Rešenja](05_resenja.md)

## Kako da koristiš materijal

Pročitaj po jednu celinu, zatim predvidi šta će ostati u bazi pre nego što pokreneš primer. Obrati pažnju na razliku između:

- SQL naredbe i transakcije;
- konekcije i transakcije;
- slanja SQL-a (`flush`) i potvrde promena (`commit`);
- uspešnog izlaska iz transakcionog bloka i izlaska sa greškom.

## Nastavak

Posle ove pripreme možemo pratiti SQLAlchemy primere koji koriste `engine.begin()`, `Connection.commit()` i ORM `Session` transakcije. Osnove ACID-a će biti dovoljne za početak; detaljna konkurentnost i izolacioni nivoi ostaju za napredniju oblast.
