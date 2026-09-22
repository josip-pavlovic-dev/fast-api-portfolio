# Stage 2 - Setup Database

## Lekcija 05 - SQLite3 terminal rad: setup i manipulacija todos podacima

## 0) Cilj lekcije

Ovo je završna vežba u oblasti setup baze.
Cilj je da naučiš kako da direktno kroz sqlite3 terminal:

- Otvoriš bazu (npr. `sqlite3 todosapp.db`)
- Proveriš tabele i schema (`.tables` i `.schema`)
- Uneseš prve zapise (`INSERT INTO todos ...`)
- Obrišeš zapis bezbedno (`DELETE FROM todos WHERE id = ...`)
- Pročitaš podatke u preglednom formatu (`SELECT * FROM todos;`)
- Menjaš prikaz rezultata (`.mode ...`)

Ova vežba je veoma bitna jer ti gradi intuiciju kako tačno ORM radi "iza scene".

---

## 1) Šta transkript pokriva (verno lekciji)

Transkript prolazi sledeći tok:

1. Ulazak u TodoApp folder
2. Otvaranje baze komandnom linijom (`sqlite3 todosapp.db`)
3. Provera schema i tabela (`.schema` i `.tables`)
4. `INSERT` više todo redova
5. `SELECT * FROM todos;`
6. Menjanje prikaza preko `.mode` (column, markdown, box, table)
7. `DELETE` po `id`
8. Ponovna provera rezultata

Core poruka lekcije:

- za `update/delete` najbezbednije je koristiti primary key (`id`)

---

## 2) Pre starta: najvažnija priprema

Da bi `sqlite3` video tabele, baza mora biti prethodno kreirana kroz app startup (`create_all`).

To praktično znači:

1. pokreneš FastAPI aplikaciju barem jednom (npr. `uvicorn main:app --reload`)
2. proveriš da je nastao `todosapp.db`
3. tek onda ulaziš u sqlite3

Ako ne uradiš korak 1, `.schema` može biti prazan.

---

## 3) Otvaranje sqlite3 baze

Iz odgovarajućeg foldera pokreni:

```bash
sqlite3 todosapp.db
```

Ako je fajl na drugoj putanji, koristi apsolutnu putanju.

Kada uđeš u shell, videćeš sqlite prompt.

---

## 4) Komande koje moraš znati u sqlite3 shell-u

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

## 4.2 Pomoć

```sql
.help
```

Ako zaboraviš sqlite komandu, `.help` je prvi spas.

---

## 5) INSERT u praksi

Primer iz transkripta (forma):

```sql
INSERT INTO todos (title, description, priority, complete)
VALUES ('Go to the store', 'Pick up eggs', 5, 0);
```

Bitno za početnika:

- `id` se ne navodi jer ga baza dodeljuje automatski
- `0` znači `False`, `1` znači `True` (u SQLite `boolean` je numerički predstavljen)
- svaka SQL komanda treba da se završi sa `;`

Ako zaboraviš `;`, sqlite će čekati nastavak i videćeš nastavak prompta.

---

## 6) SELECT i čitanje podataka

Posle inserta:

```sql
SELECT * FROM todos;
```

Dobiješ sve kolone i sve redove.

Ako hoćeš samo deo:

```sql
SELECT id, title, priority, complete FROM todos;
```

Ovo je preglednije od `*` kada tabela poraste u broj redova.

---

## 7) Prikaz rezultata: .mode

Transkript je odličan ovde, jer pokazuje da sqlite output može biti čitljiviji.

Primeri:

```sql
.mode column
.mode markdown
.mode box
.mode table
```

Praktična preporuka:

- za svakodnevni terminal rad: `.mode table` ili `.mode box`
- za copy u dokumentaciju: `.mode markdown`

Dodatni trik:

```sql
.headers on
```

Uključuje imena kolona u outputu (korisno sa `column` i `table`).

```sqlite3
.mode column
.headers on
```

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

Zašto po id:

- `id` je jedinstven
- izbegavaš slučajno brisanje više redova

Rizičan primer:

```sql
DELETE FROM todos WHERE complete = 0;
```

Ako je većina redova incomplete, obrišaćeš skoro sve.

---

## 9) Napomena o id "ponovnoj upotrebi" (važna nijansa)

U transkriptu deluje kao da SQLite "ponovo koristi" obrisan id.
U praksi, kod `INTEGER PRIMARY KEY` bez `AUTOINCREMENT` pravilo je:

- sledeći id je obično `max(id) + 1`
- zbog toga može izgledati kao reuse kada obriseš poslednji red pa ponovo uneseš novi

Primer:

- imaš id 1,2,3,4
- obrišeš 4
- sledeći insert dobije 4 (jer je `max(id)` opet 3)

Ali to nije garancija da će SQLite "reciklirati" bilo koji obrisan `id` iz sredine.

Ako želiš striktno da se `id` nikad ne ponavlja, onda `schema` treba `AUTOINCREMENT` strategiju.

---

## 10) Najčešće greške u ovoj vežbi

1. Otvaraš pogrešan `todosapp.db` fajl
   Simptom: nema tabela i podataka u bazi

2. Zaboravljen `;`
   Simptom: `sqlite` prompt čeka nastavak unosa

3. `DELETE` bez preciznog `WHERE`
   Simptom: obrisano više redova nego što si hteo

4. Mešanje stringova i brojeva
   Primer: `priority` treba broj, ne tekst

5. Očekivanje da `sqlite shell` "sam čuva" greške
   Nema rollback discipline kao u app kodu bez eksplicitnog `transaction` rada

---

## 11) Veza sa FastAPI i SQLAlchemy

Sve što ovde radiš ručno, u app-u kasnije ide kroz SQLAlchemy:

- `INSERT` -> `db.add(model)` + `db.commit()`
- `SELECT` -> `db.query(Model)...`
- `DELETE` -> `db.delete(model)` + `db.commit()`

Zato je ova lekcija dragocena: daje ti baznu SQL intuiciju pre ORM sloja.

---

## 12) Praktična mini-rutina za samostalni rad

Uradi sledeće redom:

1. `.tables`
2. `.schema todos`
3. ubaci 3 nova todo reda u tabelu
4. prikaži `.mode table`
5. `SELECT id, title, priority, complete FROM todos;`
6. obriši jedan red po `id`
7. ponovo `SELECT` da potvrdiš

Ako ovo uradiš bez greške, spreman si za sledeći nivo CRUD rada.

---

## 13) Samoprovera razumevanja

1. Zašto je `id` bolji od `title` za delete/update?

Zato što je `id` jedinstven za svaki red u tabeli i ne menja se, dok `title` može biti duplikat ili se može promeniti. To znači da korišćenje `id` za `DELETE` ili `UPDATE` operacije smanjuje rizik od nenamernog brisanja ili ažuriranja više redova.

2. Kako proveravaš da li uopšte gledaš pravu bazu?

Tako što proverim da li su tabele i podaci koje očekujem prisutni u bazi. To uključuje korišćenje `.tables` i `.schema` komandi da se uverim da radim sa pravom bazom. Takođe, mogu proveriti putanju do fajla baze da budem siguran da gledam pravu bazu.

`.` ispred komandi (kao što su `.tables` i `.schema`) označava da su to specijalne SQLite komande, a ne SQL upiti. Razlika je u tome što SQL upiti rade sa podacima u tabelama (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), dok specijalne komande upravljaju samim SQLite okruženjem (npr. prikazuju tabele, šemu, putanju do baze itd.).

3. Čemu služi `.schema`, a čemu `.tables`?

`.schema` prikazuje strukturu tabele, tj. `SQL kod` koji definiše tabelu, dok `.tables` prikazuje listu svih tabela u bazi. Ovo je korisno za brzo proveravanje da li tabela postoji i kako je definisana.

4. Šta znači `complete = 0` u SQLite?

`complete = 0` znači da zadatak nije završen. U SQLite, `0` obično predstavlja `False`, dok `1` predstavlja `True`. Ovo je uobičajen način predstavljanja boolean vrednosti u SQLite. Boolean vrednosti se često koriste u tabelama koje prate status zadataka ili slične binarne informacije (npr. da li je zadatak završen ili ne).

5. Zašto je opasan `DELETE` koji ne cilja jedinstven zapis?

Takav `DELETE` može obrisati više redova nego što je namera, što može dovesti do gubitka podataka. Uvek je preporučljivo koristiti `WHERE` uslov koji cilja jedinstveni zapis, obično po `id`.

---

## 14) Zaključak

Ovom lekcijom zatvaraš setup fazu baze na praktičan način.

Sada ne samo da znaš kako se modeli i tabele kreiraju, nego i kako da direktno proveriš i manipulišeš podacima u samoj bazi.

To je odličan temelj za naredne lekcije gde SQLAlchemy i FastAPI preuzimaju operacije, a ti razumeš tačno šta se dešava ispod haube.
