# Stage 2 - Setup Database

## Lekcija 04 - Queries Introduction (INSERT, SELECT, WHERE, UPDATE, DELETE)

## 0) Šta je cilj ove lekcije

Do sada si uradio:

- povezivanje sa bazom (`database.py`)
- definiciju tabela kroz ORM modele (`models.py`)
- kreiranje baze i tabela kroz `main.py`

Sada ulaziš u prvi direktan rad sa podacima:

- kako ubacuješ redove
- kako čitaš redove
- kako filtriraš
- kako menjaš postojeći red
- kako brišeš red

Ovo je SQL osnova za svaki CRUD sistem.

---

## 1) Šta transkript pokriva (verno lekciji)

Transkript prolazi 5 bazičnih SQL komandi:

1. `INSERT INTO` - kreiranje novih zapisa
2. `SELECT` - čitanje podataka
3. `WHERE` - filtriranje podataka
4. `UPDATE` - izmena postojećih podataka
5. `DELETE` - brisanje podataka

I vrlo bitna poruka iz lekcije:

- kad god možeš, za `update/delete` koristi `id` (primary key)
- jer je jedinstven i bezbedniji od drugih kolona

---

## 2) Mentalni model za početnika

Tabela `todos` možeš zamisliti kao Excel sheet:

- kolone: id, title, description, priority, complete
- red: jedan konkretan todo

SQL upit je instrukcija "šta hocu od tabele".

Primer:

- `SELECT * FROM todos` = "daj mi sve redove i sve kolone"
- `WHERE priority = 5` = "daj mi samo one redove gde je prioritet 5"

---

## 3) INSERT - kako dodaješ novi red

Primer iz lekcije:

```sql
INSERT INTO todos (title, description, priority, complete)
VALUES ('Go to the store', 'Pick up eggs', 4, 0);
```

Objašnjenje:

- navodiš koje kolone popunjavaš
- navodiš koje vrednosti ulaze
- `id` ne navodiš ako je auto-increment

Zašto ne unosiš `id` ručno:

- baza automatski dodeljuje sledeći broj
- smanjuješ rizik sudara duplikata

Dobra navika:

- uvek eksplicitno navedi kolone kod `INSERT`
- ne oslanjaj se na redosled svih kolona u tabeli

---

## 4) SELECT - kako čitaš podatke

### 4.1 Sve kolone i svi redovi

```sql
SELECT * FROM todos;
```

`*` znači sve kolone.

---

### 4.2 Samo jedna kolona

```sql
SELECT title FROM todos;
```

Koristi se kada ti treba samo jedan deo podataka.

---

### 4.3 Više kolona

```sql
SELECT title, description, priority FROM todos;
```

Ovo je često bolja praksa od `SELECT *` jer:

- vraća manje podataka
- response je čistiji
- upit može biti efikasniji

---

## 5) WHERE - filtriranje rezultata

`WHERE` postavlja uslov.
Samo redovi koji ispunjavaju uslov ulaze u rezultat.

### 5.1 Filter po prioritetu

```sql
SELECT * FROM todos
WHERE priority = 5;
```

---

### 5.2 Filter po title

```sql
SELECT * FROM todos
WHERE title = 'Feed dog';
```

---

### 5.3 Najvažniji use-case: filter po id

```sql
SELECT * FROM todos
WHERE id = 2;
```

Zašto je `id` najbolji:

- jedinstven je
- vraća tačno jedan red (u normalnoj tabeli)
- stabilan je za API rute tipa GET /todos/{id}

---

## 6) UPDATE - izmena postojećeg reda

Primer iz lekcije:

```sql
UPDATE todos
SET complete = 1
WHERE id = 5;
```

Šta ovo radi:

- pronalazi red sa `id = 5`
- menja kolonu `complete` na true/1

Klasična zamka:

```sql
UPDATE todos
SET complete = 1;
```

Bez `WHERE` menjaš sve redove u tabeli.

Transkript navodi i `UPDATE` po title, ali to je rizično:

```sql
UPDATE todos
SET complete = 1
WHERE title = 'Learn something new';
```

Ako postoje 2 reda sa istim `title`, oba će biti promenjena.

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

Ako je većina redova incomplete, obrisao si skoro sve.

Najopasnija greška:

```sql
DELETE FROM todos;
```

Bez `WHERE` briše celu tabelu podataka (sve redove).

---

## 8) Primary key i zašto je centralan

Primary key (`id`) je srce sigurnih CRUD operacija.

Za početnika pravilo:

- `SELECT` by id: najpreciznije
- `UPDATE` by id: najsigurnije
- `DELETE` by id: najsigurnije

Sve ostalo (po title, complete, priority) koristiš samo kada je namera da menjaš veću grupu redova.

---

## 9) Mapping na FastAPI CRUD koji već znaš

- `POST /todos` -> `INSERT`
- `GET /todos` -> `SELECT`
- `GET /todos/{todo_id}` -> `SELECT ... WHERE id = ...`
- `PUT/PATCH /todos/{todo_id}` -> `UPDATE ... WHERE id = ...`
- `DELETE /todos/{todo_id}` -> `DELETE ... WHERE id = ...`

Ovo je odlična tačka gde povezuješ HTTP i SQL razmišljanje.

---

## 10) SQLite specificnosti koje vredi znati sada

U SQLite:

- `0` se često koristi za `False`
- `1` se često koristi za `True`

Zato ćeš videti:

```sql
UPDATE todos SET complete = 1 WHERE id = 5;
```

I to je potpuno normalno.

---

## 11) SQLAlchemy veza sa ovom lekcijom

Transkript dobro napominje:

- u aplikaciji ćeš većinu ovih SQL komandi raditi indirektno kroz SQLAlchemy

Primer ideje:

- SQL `INSERT` <-> `db.add(obj)` + `db.commit()`
- SQL `SELECT` <-> `db.query(Model)...`
- SQL `UPDATE` <-> izmeni polja objekta + `commit`
- SQL `DELETE` <-> `db.delete(obj)` + `commit`

Dakle, SQL znanje i dalje treba, jer ORM samo prevodi tvoju nameru.

---

## 12) Česte greške početnika u ovoj fazi

1. Mehanički koriste `SELECT *` svuda
2. Zaborave `WHERE` kod `UPDATE`/`DELETE`
3. Filtriraju po ne-unique poljima pa slučajno promene više redova
4. Mešaju `id` iz URL-a sa drugim poljima
5. Ne proveravaju rezultat posle upita

---

## 13) Mini vežbe (od lakog ka srednjem)

### Vežba 1

Napiši 3 `INSERT` upita za todos sa različitim prioritetima.

```sql
INSERT INTO todos (title, complete, priority) VALUES ('Todo 1', 0, 1);
INSERT INTO todos (title, complete, priority) VALUES ('Todo 2', 0, 2);
INSERT INTO todos (title, complete, priority) VALUES ('Todo 3', 0, 3);
```

```python
# Primer kako bi ovo moglo da izgleda u SQLAlchemy
new_todo1 = Todo(title='Todo 1', complete=False, priority=1)
new_todo2 = Todo(title='Todo 2', complete=False, priority=2)
new_todo3 = Todo(title='Todo 3', complete=False, priority=3)
db.add(new_todo1)
db.add(new_todo2)
db.add(new_todo3)
db.commit()
```

---

### Vežba 2

Napiši upit koji vraća samo `title` i `priority` svih todos.

```sql
SELECT title, priority FROM todos;
```

```python
# Primer kako bi ovo moglo da izgleda u SQLAlchemy
todos = db.query(Todo.title, Todo.priority).all()
```

---

### Vežba 3

Napiši upit koji vraća sve incomplete todos (`complete = 0`).

`complete = 0` je isto što i `False`!

```sql
SELECT * FROM todos WHERE complete = 0;
```

```python
# Primer kako bi ovo moglo da izgleda u SQLAlchemy
incomplete_todos = db.query(Todo).filter(Todo.complete == False).all()
```

---

### Vežba 4

Napiši jedan bezbedan `UPDATE` po `id` i jedan rizičan po `title`.
Objasni razliku u jednom pasusu.

```sql
-- Bezbedan UPDATE po id
UPDATE todos SET complete = 1 WHERE id = 1;

-- Rizičan UPDATE po title
UPDATE todos SET complete = 1 WHERE title = 'Todo 1';
```

```python
# Primer kako bi ovo moglo da izgleda u SQLAlchemy
# Bezbedan UPDATE po id
todo = db.query(Todo).filter(Todo.id == 1).first()
if todo:
    todo.complete = True
    db.commit()

# Rizičan UPDATE po title
todos = db.query(Todo).filter(Todo.title == 'Todo 1').all()
for todo in todos:
    todo.complete = True
db.commit()
```

Razlika je u tome što je prvi upit bezbedan jer koristi jedinstveni identifikator `id`, dok je drugi rizičan jer može uticati na više redova sa istim `title`. Uvek je preporučljivo koristiti `id` kada je moguće kako bi se izbegle nenamerne promene u bazi.

---

### Vežba 5

Napiši `DELETE` koji briše samo jedan red po `id`, pa zatim potvrdi da je red nestao preko `SELECT`.

```sql
-- DELETE po id
DELETE FROM todos WHERE id = 1;

-- Provera da li je red obrisan
SELECT * FROM todos WHERE id = 1;
```

```python
# Primer kako bi ovo moglo da izgleda u SQLAlchemy
# DELETE po id
todo = db.query(Todo).filter(Todo.id == 1).first()
if todo:
    db.delete(todo)
    db.commit()

# Provera da li je red obrisan
deleted_todo = db.query(Todo).filter(Todo.id == 1).first()
print(deleted_todo)  # Trebalo bi da bude None
```

---

## 14) Brza samoprovera

Ako možeš jasno da odgovoriš, lekcija je usvojena:

1. Zašto ne treba unositi `id` ručno u `INSERT` (u ovom setup-u)?

`id` se automatski generiše, pa ga ne treba unositi ručno. Ovo smanjuje rizik od grešaka i kolizija u bazi.

U ovom setup-u, `id` je primarni ključ, što znači da je jedinstven za svaki red i automatski se inkrementira (po pravilu, za svaki novi red vrednost se povećava za 1). Ovo omogućava da se lako identifikuje i manipuliše pojedinačnim redovima bez rizika od kolizija ili grešaka.

2. Zašto je `WHERE id = ...` sigurnije od `WHERE title = ...`?

`id` je jedinstven za svaki red, dok `title` može biti isti za više redova. Korišćenje `id` smanjuje rizik od nenamernog ažuriranja ili brisanja više redova.

Ovo je posebno važno kada radimo sa tabelama koje imaju mnogo redova ili kada je tačnost podataka kritična. Treba uvek koristiti jedinstveni identifikator kada je moguće.

3. Šta je najveća opasnost kod `UPDATE` i `DELETE`?

Najveća opasnost je nenamerno ažuriranje ili brisanje više redova nego što je planirano, posebno ako se ne koristi jedinstveni identifikator kao što je `id`. Uvek je preporučljivo koristiti `WHERE id = ...` kako bi se izbegle neželjene promene.

Ovo je posebno važno u produkcionim okruženjima gde greške mogu imati ozbiljne posledice. Treba uvek biti pažljiv i dvaput proveriti upite pre izvršavanja.

4. Koja je razlika između `SELECT *` i biranja kolona?

`SELECT *` vraća sve kolone iz tabele, dok biranje kolona (`SELECT title, priority`) vraća samo specificirane kolone. Biranje kolona je efikasnije i smanjuje količinu prenetih podataka.

Ovo je posebno važno kada tabela ima mnogo kolona ili kada se radi sa velikim skupovima podataka. Takođe, biranje kolona može poboljšati čitljivost koda i olakšati održavanje.

5. Kako se ove SQL komande mapiraju na FastAPI endpoint-e?

`SELECT` se obično mapira na `GET` endpoint-e, `INSERT` na `POST`, `UPDATE` na `PUT` ili `PATCH`, a `DELETE` na `DELETE` endpoint-e. Na ovaj način, CRUD operacije u SQL-u odgovaraju RESTful operacijama u FastAPI-ju.

Ovo pomaže u održavanju konzistentnog i predvidivog API dizajna. Takođe olakšava razumevanje i održavanje koda, jer postoji jasna veza između SQL operacija i odgovarajućih API endpoint-a.

---

## 15) Zaključak

Ova lekcija je prvi pravi kontakt sa manipulacijom podataka.

Ako savladaš ovih 5 komandi i naviku da update/delete radiš po `id`, već imaš vrlo jaku bazu za sledeći korak: praktičan rad u sqlite3 shell-u i kasnije ORM CRUD logiku kroz rute.
