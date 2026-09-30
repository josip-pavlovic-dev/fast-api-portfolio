# 07 - FastAPI + SQLAlchemy 2.0 integracija (Depends pattern)

## Tvoj get_db je vec dobar

`get_db()` sa `yield` i `finally: db.close()` je standardna FastAPI praksa.

To zadrzavas.

## Sta se menja zbog 2.0

Menja se:

1. stil modela,
2. stil upita.

Ne menja se:

1. endpoint dependency pattern,
2. session lifecycle po request-u.

## Preporuka

Uvedi refaktor redom:

1. modeli,
2. upiti u auth/todos,
3. users/admin kada ih implementiras,
4. tek onda Alembic migracioni tok.
