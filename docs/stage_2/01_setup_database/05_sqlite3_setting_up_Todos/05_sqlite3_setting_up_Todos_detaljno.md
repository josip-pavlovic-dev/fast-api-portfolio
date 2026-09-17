# Stage 2 - Setup Database

## Lekcija 05 - SQLite3 terminal rad: setup i manipulacija todos podacima

## 0) Cilj lekcije

Ovo je zavrsna vezba u oblasti setup baze.
Cilj je da naucis kako da direktno kroz sqlite3 terminal:

- otvoris bazu
- proveris tabele i schema
- uneses prve zapise
- obrises zapis bezbedno
- citas podatke u preglednom formatu

Ova vezba je veoma bitna jer ti gradi intuiciju sta ORM radi "iza scene".

---

## 1) Sta transkript pokriva (verno lekciji)

Transkript prolazi sledeci tok:

1. Ulazak u TodoApp folder
2. Otvaranje baze komandnom linijom (`sqlite3 todosapp.db`)
3. Provera schema (`.schema`)
4. `INSERT` vise todo redova
5. `SELECT * FROM todos;`
6. Menjanje prikaza preko `.mode` (column, markdown, box, table)
7. `DELETE` po `id`
8. Ponovna provera rezultata

Core poruka lekcije:

- za update/delete najbezbednije je koristiti primary key (`id`)

---

## 2) Pre starta: najvaznija priprema

Da bi sqlite3 video tabele, baza mora biti prethodno kreirana kroz app startup (`create_all`).

To prakticno znaci:

1. pokrenes FastAPI aplikaciju barem jednom
2. proveris da je nastao `todosapp.db`
3. tek onda ulazis u sqlite3

Ako ne uradis korak 1, `.schema` moze biti prazan.

---

## 3) Otvaranje sqlite3 baze

Iz odgovarajuceg foldera pokreni:

```bash
sqlite3 todosapp.db
```

Ako je fajl na drugoj putanji, koristi apsolutnu putanju.

Kada udjes u shell, videces sqlite prompt.

---

## 4) Komande koje moras znati u sqlite3 shell-u

## 4.1 Pregled schema i tabela

```sql
.schema
.tables
```

- `.schema` ispisuje SQL definicije tabela
- `.tables` ispisuje samo imena tabela

Za konkretnu tabelu:

```sql
.schema todos
```

## 4.2 Pomoc

```sql
.help
```

Ako zaboravis sqlite komandu, `.help` je prvi spas.

---

## 5) INSERT u praksu

Primer iz transkripta (forma):

```sql
INSERT INTO todos (title, description, priority, complete)
VALUES ('Go to the store', 'Pick up eggs', 5, 0);
```

Bitno za pocetnika:

- `id` se ne navodi jer ga baza dodeljuje
- `0` znaci `False`, `1` znaci `True` (u SQLite boolean je numericki predstavljen)
- svaka SQL komanda treba da se zavrsi sa `;`

Ako zaboravis `;`, sqlite ce cekati nastavak i videces nastavak prompta.

---

## 6) SELECT i citanje podataka

Posle inserta:

```sql
SELECT * FROM todos;
```

Dobijes sve kolone i sve redove.

Ako hoces samo deo:

```sql
SELECT id, title, priority, complete FROM todos;
```

Ovo je preglednije od `*` kada tabela poraste.

---

## 7) Prikaz rezultata: .mode

Transkript je odlican ovde, jer pokazuje da sqlite output moze biti citljiviji.

Primeri:

```sql
.mode column
.mode markdown
.mode box
.mode table
```

Prakticna preporuka:

- za svakodnevni terminal rad: `.mode table` ili `.mode box`
- za copy u dokumentaciju: `.mode markdown`

Dodatni trik:

```sql
.headers on
```

Ukljucuje imena kolona u outputu (korisno sa `column` i `table`).

---

## 8) DELETE bezbedno: uvek po id

Bezbedan primer:

```sql
DELETE FROM todos WHERE id = 4;
```

Posle toga odmah proveri:

```sql
SELECT * FROM todos;
```

Zasto po id:

- `id` je jedinstven
- izbegavas slucajno brisanje vise redova

Rizican primer:

```sql
DELETE FROM todos WHERE complete = 0;
```

Ako je vecina redova incomplete, obrisaces skoro sve.

---

## 9) Napomena o id "ponovnoj upotrebi" (vazna nijansa)

U transkriptu deluje kao da SQLite "ponovo koristi" obrisan id.
U praksi, kod `INTEGER PRIMARY KEY` bez `AUTOINCREMENT` pravilo je:

- sledeci id je obicno `max(id) + 1`
- zbog toga moze izgledati kao reuse kada obrises poslednji red pa ponovo uneses novi

Primer:

- imas id 1,2,3,4
- obrises 4
- sledeci insert dobije 4 (jer je `max(id)` opet 3)

Ali to nije garancija da ce SQLite "reciklirati" bilo koji obrisan id iz sredine.

Ako zelis striktno da se id nikad ne ponavlja, onda schema treba `AUTOINCREMENT` strategiju.

---

## 10) Najcesce greske u ovoj vezbi

1. Otvaras pogresan `todosapp.db` fajl
   Simptom: nema tabela i podataka

2. Zaboravljen `;`
   Simptom: sqlite prompt ceka nastavak unosa

3. `DELETE` bez preciznog `WHERE`
   Simptom: obrisano vise redova nego sto si hteo

4. Mesanje stringova i brojeva
   Primer: `priority` treba broj, ne tekst

5. Ocekivanje da sqlite shell "sam cuva" greske
   Nema rollback discipline kao u app kodu bez eksplicitnog transaction rada

---

## 11) Veza sa FastAPI i SQLAlchemy

Sve sto ovde radis rucno, u app-u kasnije ide kroz SQLAlchemy:

- `INSERT` -> `db.add(model)` + `db.commit()`
- `SELECT` -> `db.query(Model)...`
- `DELETE` -> `db.delete(model)` + `db.commit()`

Zato je ova lekcija dragocena: daje ti baznu SQL intuiciju pre ORM sloja.

---

## 12) Prakticna mini-rutina za samostalni rad

Uradi sledece redom:

1. `.tables`
2. `.schema todos`
3. ubaci 3 nova todo reda
4. prikazi `.mode table`
5. `SELECT id, title, priority, complete FROM todos;`
6. obrisi jedan red po `id`
7. ponovo `SELECT` da potvrdis

Ako ovo uradis bez greske, spreman si za sledeci nivo CRUD rada.

---

## 13) Samoprovera razumevanja

1. Zasto je `id` bolji od `title` za delete/update?
2. Kako proveravas da li uopste gledas pravu bazu?
3. Cemu sluzi `.schema`, a cemu `.tables`?
4. Sta znaci `complete = 0` u SQLite?
5. Zasto je opasan `DELETE` koji ne cilja jedinstven zapis?

---

## 14) Zakljucak

Ovom lekcijom zatvaras setup fazu baze na praktican nacin.

Sada ne samo da znas kako se modeli i tabele kreiraju,
nego i kako da direktno proveris i manipulis podacima u samoj bazi.

To je odlican temelj za naredne lekcije gde SQLAlchemy i FastAPI preuzimaju operacije,
a ti razumes tacno sta se desava ispod haube.
