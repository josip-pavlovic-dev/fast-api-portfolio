# 06 FastAPI sa bazom: database.py, models.py, schemas.py

## Cilj ove lekcije

Da razdvojis odgovornosti i dobijes cist backend skeleton.

Osnovna struktura:

- database.py: konekcija, engine, session, dependency
- models.py: SQLAlchemy ORM tabele
- schemas.py: Pydantic request/response modeli
- routes: endpoint logika

## database.py uloga

Tipican sadrzaj:

- DATABASE_URL
- create_engine
- SessionLocal
- Base = declarative_base()
- get_db dependency koja yield-uje sesiju

Kljuclno je da session bude kratkog veka po request-u.

## models.py uloga

Ovde su SQLAlchemy klase.
Svaka klasa mapira jednu tabelu.

Primer ideja polja:

- id primary key
- title string not null
- owner_id foreign key
- created_at timestamp

Ovde ne pises API validaciju poruka korisniku.
To je posao schemas sloja i endpoint logike.

## schemas.py uloga

Ovde pravis vise schema verzija:

- ItemCreate: sta klijent salje pri kreiranju
- ItemUpdate: sta klijent salje pri punom update
- ItemPatch: optional polja za parcijalni update
- ItemOut: sta vracas klijentu

Zasto vise schema:

- ulaz i izlaz retko imaju isti oblik
- bezbednije i jasnije API ponasanje

## Tok jednog POST zahteva

1. FastAPI validira telo kroz ItemCreate.
2. Route kreira Item ORM objekat.
3. add + commit + refresh kroz db session.
4. Vraca ItemOut response.

## Tok GET by id

1. Query po id.
2. Ako None -> HTTP 404.
3. Inace vrati ItemOut.

## Tok PATCH

1. Primis ItemPatch gde su polja optional.
2. Ucitas postojeci red.
3. Menjas samo polja koja su poslata.
4. commit + refresh.

## Gde je mesto za business pravila

Opcije:

- route fajl (ok za male projekte)
- service sloj (bolje za rast projekta)

Za tvoj nivo sada:

- route + helper funkcije je sasvim dobro
- kasnije uvod service/repository pattern

## Tipicne greske u ovoj arhitekturi

- direktno vracanje SQLAlchemy objekta bez response modela
- koriscenje jednog globalnog db objekta bez dependency
- mesanje schema naziva i namene
- izostavljen rollback u try/except granama

## Predlog naming pravila

- models: singular class names (Item, User)
- schemas: ItemCreate, ItemUpdate, ItemPatch, ItemOut
- tabele: plural names (items, users)

## Zadaci

1. Nacrtaj fajl po fajl sta ide u database.py, models.py, schemas.py.
2. Definisi ItemCreate i ItemOut sa realnim poljima.
3. Napisi korake za PATCH endpoint bez koda.
4. Opisi gde i zasto ide get_db dependency.

## Zakljucak

Kada ovo razumes, prelaz na puni SQL CRUD je prirodan.
Sledeca lekcija je bas to: CRUD implementacija i dobre prakse gresaka/validacije.
