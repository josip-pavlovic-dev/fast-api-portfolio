# 07 CRUD sa SQLAlchemy u FastAPI

## Cilj

Da povezes sve prethodno:

- SQL razmisljanje
- ORM modeli
- Pydantic schemas
- endpointi sa pravilnim status kodovima

## Create flow

1. Request telo ulazi kroz Create schema.
2. Validacija na API nivou.
3. ORM objekat se kreira i upisuje.
4. Vraca se Out schema.

Praksa:

- status kod 201
- vrati id i sva relevantna polja

## Read all flow

Tipicno dodajes:

- skip
- limit
- sortiranje

Zasto:

- izbegavas vracanje previse podataka
- spremas API za rast

## Read by id flow

- query po PK
- ako nema reda -> 404
- ako ima -> Out schema

## Update (PUT) flow

PUT znaci puna zamena resursa.

- klijent salje kompletan skup polja
- server menja sva predvidjena polja
- nepostojece polje nije implicitno sacuvano

Za pocetak:

- procitaj red
- ako ne postoji 404
- prekopiraj nova polja
- commit + refresh

## Partial update (PATCH) flow

PATCH menja samo poslata polja.

- patch schema ima optional polja
- menjas samo provided vrednosti
- pazis da ne prebrises postojece vrednosti sa None bez namere

## Delete flow

Opcije:

- hard delete
- soft delete

Ako radis hard delete:

- proveri postojanje
- delete + commit
- vrati 204 bez tela

## Error handling strategija

Razdvoji 2 nivoa gresaka:

- business/not found: HTTPException (404, 400)
- database greske (npr. unique): rollback + 409/400 zavisno od slucaja

## Primer defensive obrasca

- try blok oko commit
- except grana radi rollback
- vrati smislen API odgovor

## Response modeli

Uvek defini response_model da API ugovor bude jasan.
To pomaze i dokumentaciji i stabilnosti klijenata.

## Test scenariji koje obavezno pokriti

1. create success
2. create validation fail
3. read by id found
4. read by id not found
5. put success
6. patch success (menja 1 polje)
7. delete success
8. delete not found

## Performanse koje rano treba pratiti

- broj query-ja po request-u
- N+1 obrasci
- paginacija i limit

## Zadaci

1. Napisi check-listu za svaki CRUD endpoint.
2. Definisi kad vracas 200, 201, 204, 404, 409.
3. Osmisli 8 testova (nazivi + sta proveravaju).

## Zakljucak

Sa ovom lekcijom imas funkcionalnu SQL-backed API osnovu.
Ostaje profesionalizacija kroz migracije i napredne obrasce.
