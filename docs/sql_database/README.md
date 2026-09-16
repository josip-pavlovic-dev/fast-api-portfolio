# SQL Database putanja ucenja za FastAPI

Ovaj folder je nova etapa posle osnovnog FastAPI CRUD nivoa.
Cilj je prelaz sa in-memory liste na pravu SQL bazu uz cistu arhitekturu.

## Kako da koristis ovaj materijal

1. Uci redom, bez preskakanja.
2. Posle svake lekcije napravi mini implementaciju.
3. Testiraj i normalne i pogresne ulaze.
4. Vodi kratke beleske: sta je novo, sta je bilo tesko, sta je postalo jasno.

## Redosled lekcija

1. [01_uvod_u_baze_i_relacioni_model.md](01_uvod_u_baze_i_relacioni_model.md)
2. [02_sql_osnove_select_where_join.md](02_sql_osnove_select_where_join.md)
3. [03_modeliranje_baze_i_normalizacija.md](03_modeliranje_baze_i_normalizacija.md)
4. [04_sqlite_praksa_transakcije_i_indeksi.md](04_sqlite_praksa_transakcije_i_indeksi.md)
5. [05_sqlalchemy_osnove_core_i_orm.md](05_sqlalchemy_osnove_core_i_orm.md)
6. [06_fastapi_sa_bazom_database_models_schemas.md](06_fastapi_sa_bazom_database_models_schemas.md)
7. [07_crud_sa_sqlalchemy_u_fastapi.md](07_crud_sa_sqlalchemy_u_fastapi.md)
8. [08_migracije_alembic_i_napredne_teme.md](08_migracije_alembic_i_napredne_teme.md)
9. [09_plan_vezbe_i_mini_projekat.md](09_plan_vezbe_i_mini_projekat.md)

## Ocekivani ishod

Posle ove serije treba da mozes da:

- dizajniras tabele i odnose
- pises i citas SQL upite sa sigurnosnim navikama
- razumes transakcije i indeksiranje
- povezes FastAPI sa SQLite bazom
- organizujes kod kroz database.py, models.py, schemas.py
- napravis stabilan CRUD sa pravilnim status kodovima i greskama
- uvedes migracije i pripremis aplikaciju za rast
