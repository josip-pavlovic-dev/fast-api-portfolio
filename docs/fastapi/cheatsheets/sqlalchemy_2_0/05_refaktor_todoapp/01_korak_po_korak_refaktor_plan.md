# 09 - Tvoj konkretan refaktor plan (TodoApp)

## Faza 1 - priprema

1. Napravi `snapshot` trenutnog stanja (`branch` + `backup baze`). Kako? Na primer, kreiraj novi `branch` i eksportuj trenutnu bazu u `.sql` fajl.
2. Potvrdi da app radi pre refaktora.
3. Potvrdi koje rute trenutno koristis (`auth`, `todos`).

---

## Faza 2 - modeli 2.0

1. Prebaci `Base` na 2.0 deklarativni stil (`DeclarativeBase`).
2. Refaktoriši `Users` i `Todos` na `Mapped` + `mapped_column`.
3. Pokreni app i potvrdi da se importi normalno učitavaju.

---

## Faza 3 - query refaktor

1. `core/security.py` -> `select(Users)`.
2. `api/routes/todos.py` -> svi `query/filter/all/first` u `select/where/execute/scalars`.
3. `api/routes/auth.py` -> user lookup i unique provere u 2.0 stilu.

---

## Faza 4 - users/admin (kada ih uvedes)

1. Primeni isti query obrazac.
2. Potvrdi ownership + role logiku.

---

## Faza 5 - stabilizacija

1. Proveri sve `auth` i `todos` endpointe kroz Swagger.
2. Proveri `login`, `create/read/update/delete` tok.
3. Tek tada pređi na `Alembic` workflow kao glavni izvor istine.
