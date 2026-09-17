# Stage 2 - Setup Database

## Lekcija 04 - Queries Introduction (INSERT, SELECT, WHERE, UPDATE, DELETE)

## 0) Sta je cilj ove lekcije

Do sada si uradio:

- povezivanje sa bazom (`database.py`)
- definiciju tabela kroz ORM modele (`models.py`)
- kreiranje baze i tabela kroz `main.py`

Sada ulazis u prvi direktan rad sa podacima:

- kako ubacujes redove
- kako citas redove
- kako filtriras
- kako menjas postojeci red
- kako brises red

Ovo je SQL osnova za svaki CRUD sistem.

---

## 1) Sta transkript pokriva (verno lekciji)

Transkript prolazi 5 bazicnih SQL komandi:

1. `INSERT INTO` - kreiranje novih zapisa
2. `SELECT` - citanje podataka
3. `WHERE` - filtriranje podataka
4. `UPDATE` - izmena postojecih podataka
5. `DELETE` - brisanje podataka

I vrlo bitna poruka iz lekcije:

- kad god mozes, za update/delete koristi `id` (primary key)
- jer je jedinstven i bezbedniji od drugih kolona

---

## 2) Mentalni model za pocetnika

Tabela `todos` mozes zamisliti kao Excel sheet:

- kolone: id, title, description, priority, complete
- red: jedan konkretan todo

SQL upit je instrukcija "sta hocu od tabele".

Primer:

- `SELECT * FROM todos` = "daj mi sve redove i sve kolone"
- `WHERE priority = 5` = "daj mi samo one redove gde je prioritet 5"

---

## 3) INSERT - kako dodajes novi red

Primer iz lekcije:

```sql
INSERT INTO todos (title, description, priority, complete)
VALUES ('Go to the store', 'Pick up eggs', 4, 0);
```

Objasnjenje:

- navodis koje kolone popunjavas
- navodis koje vrednosti ulaze
- `id` ne navodis ako je auto-increment

Zasto ne unosis `id` rucno:

- baza automatski dodeljuje sledeci broj
- smanjujes rizik sudara duplikata

Dobra navika:

- uvek eksplicitno navedi kolone kod `INSERT`
- ne oslanjaj se na redosled svih kolona u tabeli

---

## 4) SELECT - kako citas podatke

## 4.1 Sve kolone i svi redovi

```sql
SELECT * FROM todos;
```

`*` znaci sve kolone.

## 4.2 Samo jedna kolona

```sql
SELECT title FROM todos;
```

Koristi se kad ti treba samo jedan deo podataka.

## 4.3 Vise kolona

```sql
SELECT title, description, priority FROM todos;
```

Ovo je cesto bolja praksa od `SELECT *` jer:

- vracas manje podataka
- response je cistiji
- upit moze biti efikasniji

---

## 5) WHERE - filtriranje rezultata

`WHERE` postavlja uslov.
Samo redovi koji ispunjavaju uslov ulaze u rezultat.

## 5.1 Filter po prioritetu

```sql
SELECT * FROM todos
WHERE priority = 5;
```

## 5.2 Filter po title

```sql
SELECT * FROM todos
WHERE title = 'Feed dog';
```

## 5.3 Najvazniji use-case: filter po id

```sql
SELECT * FROM todos
WHERE id = 2;
```

Zasto je `id` najbolji:

- jedinstven je
- vraca tacno jedan red (u normalnoj tabeli)
- stabilan je za API rute tipa GET /todos/{id}

---

## 6) UPDATE - izmena postojeceg reda

Primer iz lekcije:

```sql
UPDATE todos
SET complete = 1
WHERE id = 5;
```

Sta ovo radi:

- pronalazi red sa `id = 5`
- menja kolonu `complete` na true/1

Klasicna zamka:

```sql
UPDATE todos
SET complete = 1;
```

Bez `WHERE` menjas sve redove u tabeli.

Transkript navodi i update po title, ali to je rizicno:

```sql
UPDATE todos
SET complete = 1
WHERE title = 'Learn something new';
```

Ako postoje 2 reda sa istim naslovom, oba ce biti promenjena.

---

## 7) DELETE - brisanje reda

Bezbedan primer:

```sql
DELETE FROM todos
WHERE id = 5;
```

Opasna varijanta:

```sql
DELETE FROM todos
WHERE complete = 0;
```

Ako je vecina redova incomplete, obrisao si skoro sve.

Najopasnija greska:

```sql
DELETE FROM todos;
```

Bez `WHERE` brises celu tabelu podataka (sve redove).

---

## 8) Primary key i zasto je centralan

Primary key (`id`) je srce sigurnih CRUD operacija.

Za pocetnika pravilo:

- `SELECT` by id: najpreciznije
- `UPDATE` by id: najsigurnije
- `DELETE` by id: najsigurnije

Sve ostalo (po title, complete, priority) koristis samo kada je namera da menjas vecu grupu redova.

---

## 9) Mapping na FastAPI CRUD koji vec znas

- `POST /todos` -> `INSERT`
- `GET /todos` -> `SELECT`
- `GET /todos/{todo_id}` -> `SELECT ... WHERE id = ...`
- `PUT/PATCH /todos/{todo_id}` -> `UPDATE ... WHERE id = ...`
- `DELETE /todos/{todo_id}` -> `DELETE ... WHERE id = ...`

Ovo je odlicna tacka gde povezujes HTTP i SQL razmisljanje.

---

## 10) SQLite specificnosti koje vredi znati sada

U SQLite:

- `0` se cesto koristi za `False`
- `1` se cesto koristi za `True`

Zato ces videti:

```sql
UPDATE todos SET complete = 1 WHERE id = 5;
```

I to je potpuno normalno.

---

## 11) SQLAlchemy veza sa ovom lekcijom

Transkript dobro napominje:

- u aplikaciji ces vecinu ovih SQL komandi raditi indirektno kroz SQLAlchemy

Primer ideje:

- SQL `INSERT` <-> `db.add(obj)` + `db.commit()`
- SQL `SELECT` <-> `db.query(Model)...`
- SQL `UPDATE` <-> izmeni polja objekta + `commit`
- SQL `DELETE` <-> `db.delete(obj)` + `commit`

Dakle, SQL znanje i dalje treba, jer ORM samo prevodi tvoju nameru.

---

## 12) Ceste greske pocetnika u ovoj fazi

1. Mehanicki koriste `SELECT *` svuda
2. Zaborave `WHERE` kod `UPDATE`/`DELETE`
3. Filtriraju po ne-unique poljima pa slucajno promene vise redova
4. Mesaju `id` iz URL-a sa drugim poljima
5. Ne proveravaju rezultat posle upita

---

## 13) Mini vezbe (od lakog ka srednjem)

## Vezba 1

Napisi 3 `INSERT` upita za todos sa razlicitim prioritetima.

## Vezba 2

Napisi upit koji vraca samo `title` i `priority` svih todos.

## Vezba 3

Napisi upit koji vraca sve incomplete todos (`complete = 0`).

## Vezba 4

Napisi jedan bezbedan `UPDATE` po `id` i jedan rizican po `title`.
Objasni razliku u jednom pasusu.

## Vezba 5

Napisi `DELETE` koji brise samo jedan red po `id`, pa zatim potvrdi da je red nestao preko `SELECT`.

---

## 14) Brza samoprovera

Ako mozes jasno da odgovoris, lekcija je usvojena:

1. Zasto ne treba unositi `id` rucno u `INSERT` (u ovom setup-u)?
2. Zasto je `WHERE id = ...` sigurnije od `WHERE title = ...`?
3. Sta je najveca opasnost kod `UPDATE` i `DELETE`?
4. Koja je razlika izmedju `SELECT *` i biranja kolona?
5. Kako se ove SQL komande mapiraju na FastAPI endpoint-e?

---

## 15) Zakljucak

Ova lekcija je prvi pravi kontakt sa manipulacijom podataka.

Ako savladas ovih 5 komandi i naviku da update/delete radis po `id`,
vec imas vrlo jaku bazu za sledeci korak: praktican rad u sqlite3 shell-u i kasnije ORM CRUD logiku kroz rute.
