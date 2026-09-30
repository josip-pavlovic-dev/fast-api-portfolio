# 10 - Kako povezati SQLAlchemy 2.0 refaktor i Alembic

## Redosled koji ima najmanje rizika

1. Stabilizuj SQLAlchemy 2.0 kod.
2. Tek onda inicijalizuj/ucvrsti Alembic u tom stanju.
3. Nakon toga svaka promena modela ide preko migracije.

## Zasto ovim redom

Ako menjas i ORM stil i migration alat istovremeno:

- tesko je izolovati gresku,
- duze traje debag,
- veci rizik za podatke.

## Prakticno za tvoj projekat

- Trenutno koristis `create_all()` i to je okej za fazu ucenja.
- Kada zavrsis refaktor na 2.0 i potvrdis stabilnost, postavi Alembic kao primarni tok promena seme.
- Posle toga izbegavaj "rucne" promene baze mimo migracija.
