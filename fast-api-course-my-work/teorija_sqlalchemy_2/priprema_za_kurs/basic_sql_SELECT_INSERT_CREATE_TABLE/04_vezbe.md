# 04: Vežbe — CREATE TABLE, INSERT i SELECT

Pokušaj zadatke samostalno pre nego što otvoriš [rešenja](05_resenja.md). Koristi SQLite sintaksu. Za sada ne dodaj `COMMIT`, `ROLLBACK`, migracije ili SQLAlchemy kod.

## Vežba 1: protumači tabelu

Za SQL definiciju `user_account` objasni:

- šta identifikuje red;
- koje kolone obavezno moraju imati vrednost;
- koja kolona može ostati `NULL`;
- šta baza radi sa `created_at` kada je kolona izostavljena iz INSERT-a.

## Vežba 2: kreiraj dve povezane tabele

Napiši `CREATE TABLE` naredbe za:

1. `user_account`: `id`, jedinstveni i obavezni `name`, opcioni `fullname` i obavezni `created_at` sa `CURRENT_TIMESTAMP` default-om;
2. `address`: `id`, obavezni i jedinstveni `email_address`, obavezni `user_id` koji referencira `user_account.id`.

U SQLite-u uključi FK enforcement sa `PRAGMA foreign_keys=ON` na konekciji na kojoj ćeš testirati constraint.

## Vežba 3: unesi jednog korisnika

Napiši INSERT za korisnika `sandy`, puno ime `Sandy Cheeks`. Izostavi `id` i `created_at` da baza može da primeni njihova pravila.

## Vežba 4: unesi više korisnika

Jednim SQL INSERT iskazom dodaj `spongebob`, `patrick` i `squidward`. Za `squidward` neka `fullname` bude SQL `NULL`.

## Vežba 5: unesi povezane adrese

Dodaj dve adrese za Sandy i jednu za SpongeBob-a. Pretpostavi da su u sveže kreiranoj bazi Sandy dobila ID 1, SpongeBob ID 2. Objasni zašto je ovo samo pretpostavka vezana za konkretan seed redosled, a ne pravilo SQL-a.

## Vežba 6: izaberi samo potrebne kolone

Napiši SELECT koji vraća `name` i `fullname` svih korisnika, sortiranih po `name` uzlazno.

## Vežba 7: filtriraj redove

Napiši tri upita:

1. korisnik čije je `name` jednako `sandy`;
2. korisnici čiji `fullname` nije poznat;
3. korisnici čije ime počinje slovom `s`.

## Vežba 8: kombinuj uslove

Vrati korisnike sa `id > 1`, osim korisnika `patrick`. Sortiraj rezultat po ID-ju.

## Vežba 9: JOIN

Vrati korisničko ime i email za svaki povezani korisnik–adresa par. Koristi INNER JOIN i eksplicitan `ON` uslov.

## Vežba 10: LEFT JOIN

Vrati sve korisnike i njihove email adrese, uključujući korisnike koji nemaju adresu. Objasni zašto se za korisnika bez adrese u rezultatu pojavljuje `NULL` u email koloni.

## Vežba 11: parametar umesto konkatenacije

Zamisli da ime dolazi iz FastAPI zahteva. Napiši SQLAlchemy `text()` upit sa `:name` parametrom i prosledi vrednost posebno. Nemoj praviti SQL f-string.

## Završna provera

Bez gledanja beleški objasni razliku između:

- kolone i reda;
- `NULL` i praznog stringa;
- primarnog i stranog ključa;
- `INSERT` i `SELECT`;
- `WHERE` i `ORDER BY`;
- `JOIN` uslova i pukog navođenja dve tabele u `FROM`.
