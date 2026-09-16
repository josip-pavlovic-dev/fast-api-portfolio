# Sprint 02 (Nedelje 3-4) - SQLAlchemy + SQLite osnove

Cilj: Prelaz sa in-memory CRUD na stabilan CRUD nad SQLite bazom uz jasnu podelu na datsabase.py, models.py i schemas.py.

## Checklist (uraditi redom)

- [ ] Potvrdi da app koristi SQLite konekciju
- [ ] Napravi i razumi database sloj (`engine`, `SessionLocal`, `get_db`)
- [ ] Definisi ORM model `Item` u `models.py`
- [ ] Definisi Pydantic sheme u `schemas.py`
- [ ] Prebaci sve `items` endpointe na SQLAlchemy session
- [ ] Dodaj startup inicijalizaciju tabela za lokalni rad
- [ ] Dodaj test setup sa testnom SQLite bazom
- [ ] Pokrij CRUD happy path + not found scenarije
- [ ] Dokumentuj status kodove i greske

## Dnevni fokus (120 min blok)

## Dan 1 - Baza i sesija

- 20 min: ponovi pojmove (PK, FK, transakcija, commit, rollback)
- 40 min: implementiraj `database.py`
- 40 min: proveri `get_db` dependency i lifecycle sesije
- 20 min: kratke beleske sta je bilo nejasno

Exit kriterijum:

- znas gde i zasto se kreira/zatvara sesija po request-u

## Dan 2 - Model i sheme

- 30 min: dizajn polja za `Item`
- 50 min: napravi `models.py` + `schemas.py`
- 20 min: proveri razliku ORM model vs Pydantic schema
- 20 min: mini recap

Exit kriterijum:

- jasno razdvojena uloga `models.py` i `schemas.py`

## Dan 3 - CRUD migracija sa memorije na bazu

- 20 min: procitaj stari route kod
- 70 min: prebaci POST/GET/GET by id/PUT/DELETE na DB
- 20 min: obrada 404 i osnovnih DB gresaka
- 10 min: manualna provera endpointa

Exit kriterijum:

- svi endpointi rade nad bazom, ne nad listom

## Dan 4 - Testovi i stabilnost

- 30 min: test dependency override za testnu bazu
- 60 min: napisi CRUD testove
- 20 min: dotegni not found slucajeve
- 10 min: finalni pregled

Exit kriterijum:

- testovi pokrivaju osnovni DB CRUD tok

## Definition of done

- `items` ruta koristi SQLAlchemy session dependency
- nema in-memory global liste za persistence
- testovi prolaze i proveravaju bazni CRUD tok
- status kodovi su dosledni (`201`, `200`, `204`, `404`)

## Rizici i sta pratiti

- pogresan session lifecycle
- zaboravljen `commit` ili `refresh`
- mesanje `models.py` i `schemas.py` odgovornosti
- testovi koji slucajno koriste produkcionu bazu
