# 08 Migracije, Alembic i napredne teme

## Zasto migracije

Ako menjas tabele rucno, brzo gubis kontrolu verzija schema promene.
Migracije su istorija evolucije baze.

Alembic je standardan alat uz SQLAlchemy.

## Tipican ciklus migracija

1. promenis ORM model
2. generises migraciju
3. pregledas migraciju
4. primenis migraciju
5. po potrebi rollback

## Zasto je review migracija obavezan

Auto-generisanje nije magicno.
Mora se proveriti:

- da li su tipovi tacni
- da li su constraint-i dodati
- da li rename nije protumacen kao drop+create

## Strategije promene schema bez downtime rizika

Za vece sisteme se radi u koracima:

1. dodaj novu nullable kolonu
2. popuni podatke
3. prebaci kod da koristi novu kolonu
4. tek onda uvedi not null ili obrisi staru kolonu

## Seed podaci

Razlika:

- migration: schema promene
- seed: inicijalni ili demo podaci

Seed ne treba mesati sa kriticnim produkcionim podacima.

## Napredne SQLAlchemy teme za sledeci nivo

- relationship loading strategije
- transaction management po use-case-u
- optimistic locking
- bulk operacije
- repository/service sloj

## Bezbednost i stabilnost

- nikad ne trustuj klijenta za owner_id bez auth pravila
- validiraj poslovna pravila pre commit
- hvataj IntegrityError i vrati smislen HTTP odgovor

## Observability osnove

- loguj SQL greske uz context
- meri latency endpointa
- prepoznaj spore query-je

## Kada prelazis sa SQLite na PostgreSQL

Signal za prelaz:

- veci paralelizam
- kompleksniji query workload
- potreba za naprednim DB feature-ima

Dobra vest:

Ako je arhitektura cista, prelaz je znatno laksi.

## Zadaci

1. Opisi jednu realnu promenu schema kroz 2 migracije.
2. Nacrtaj plan rollback-a ako migracija krene lose.
3. Definisi koja 3 log signala bi odmah pratio u CRUD app.

## Zakljucak

Migracije su razlika izmedju "radi kod mene" i stabilnog backend procesa.
Time zatvaras pun ciklus: model -> implementacija -> evolucija.
