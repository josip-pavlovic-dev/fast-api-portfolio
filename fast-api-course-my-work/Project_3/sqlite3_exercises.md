# SQLite3 vežbe — Project 3 `todos`

Ovaj dokument koristi postojeću bazu `Project_3/data/todosapp3.db` direktno.

## 1. Otvori pravu bazu

Komandu pokreni iz **root-a repozitorijuma**:

```bash
sqlite3 fast-api-course-my-work/Project_3/data/todosapp3.db
```

U SQLite prompt-u proveri da je otvoren pravi fajl i prikaži tabele:

```sql
.databases
.tables
.schema todos
```

U `.databases` treba da vidiš putanju `fast-api-course-my-work/Project_3/data/todosapp3.db`, a među tabelama treba da bude `todos`. Ako nešto nije tako, nemoj nastavljati sa izmenama.

Podesi prikaz rezultata:

```sql
.headers on
.mode table
```

Tabela `todos` u ovom projektu ima kolone `id`, `title`, `description`, `priority` i `complete`. Boolean vrednosti se u SQLite-u obično čuvaju kao `0` (false) i `1` (true).

---

## 2. Pregledaj postojeće redove — `SELECT`

1. Prikaži sve kolone i redove u tabeli `todos`:

   ```sql
   SELECT * FROM todos;
   ```

2. Prikaži samo odabrane kolone u tabeli `todos`:

   ```sql
   SELECT id, title, priority, complete
   FROM todos;
   ```

3. Pronađi zadatke određenog prioriteta u tabeli `todos`:

   ```sql
   SELECT id, title, priority
   FROM todos
   WHERE priority = 3;
   ```

4. Pronađi nedovršene zadatke u tabeli `todos`:

   ```sql
   SELECT id, title, complete
   FROM todos
   WHERE complete = 0;
   ```

5. Pronađi jedan red po ID-u u tabeli `todos`:

   ```sql
   SELECT id, title, description, priority, complete
   FROM todos
   WHERE id = 1;
   ```

   Ako ne postoji red sa `id = 1`, zameni ga ID-em koji si video u
   prethodnim rezultatima.

## 3. Dodaj vežbačke redove — `INSERT`

Započni transakciju da bi kasnije mogao da potvrdiš ceo niz vežbi sa `COMMIT` ili da ga poništiš sa `ROLLBACK`. Zatim dodaj tri probna zadatka. `id` se izostavlja da bi ga SQLite automatski dodelio:

```sql
BEGIN;

INSERT INTO todos (title, description, priority, complete)
VALUES
    ('SQLite practice A', 'INSERT primer A', 2, 0),
    ('SQLite practice B', 'INSERT primer B', 4, 1),
    ('SQLite practice C', 'INSERT primer C', 5, 0);
```

Pronađi samo ove redove i zapiši njihove ID-jeve:

```sql
SELECT id, title, description, priority, complete
FROM todos
WHERE title LIKE 'SQLite practice %'
ORDER BY id;
```

---

## 4. Promeni jedan vežbački red — `UPDATE`

Zameni `ID_REDA_A` ID-jem probnog reda A iz prethodnog rezultata:

```sql
UPDATE todos
SET complete = 1,
    priority = 3
WHERE id = ID_REDA_A;
```

Proveri tačno taj red i koliko je redova promenjeno:

```sql
SELECT id, title, priority, complete
FROM todos
WHERE id = ID_REDA_A;

SELECT changes();
```

Očekivano je da `changes()` vrati `1`. `UPDATE` bez `WHERE` uslova menja vrednosti u svim redovima tabele.

---

## 5. Ukloni jedan red u tabeli `todos` — `DELETE`

Zameni `ID_REDA_B` ID-jem probnog reda B iz prethodnog rezultata:

```sql
DELETE FROM todos
WHERE id = ID_REDA_B;
```

Proveri da li je red obrisan:

```sql
SELECT id, title
FROM todos
WHERE id = ID_REDA_B;

SELECT changes();
```

Prvi upit ne treba da vrati red, a `changes()` treba da vrati `1`.

---

## 6. Potvrdi vežbu

Pregledaj sva tri probna zapisa u tabeli `todos`. A je ažuriran, B obrisan, a C ostao
nepromenjen:

```sql
SELECT id, title, priority, complete
FROM todos
WHERE title LIKE 'SQLite practice %'
ORDER BY id;
```

U SQLite shell-u izmene se čuvaju u bazi; ovde ih eksplicitno potvrđujemo
transakcijom:

```sql
COMMIT;
```

Ako želiš da poništiš izmene pre potvrde, umesto `COMMIT`-a možeš izvršiti
`ROLLBACK`, ali to funkcioniše samo ako si pre izmena pokrenuo `BEGIN;`.
Za vežbu transakcije možeš ponoviti postupak: pokreni `BEGIN;`, dodaj
probni red, proveri ga, pa izvrši `ROLLBACK;`.

Izađi iz SQLite shell-a:

```sql
.quit
```

---

---

## Transakcije

Transakcija je sekvenca SQL upita koja se izvršava kao jedinstvena celina. Sve izmene unutar transakcije se ili trajno čuvaju pomoću `COMMIT`-a ili poništavaju pomoću `ROLLBACK`-a.

U SQLite-u, transakcije se obično započinju sa `BEGIN TRANSACTION;`, a zatim se izvršavaju potrebni upiti. Nakon toga se koristi `COMMIT;` za trajno čuvanje ili `ROLLBACK;` za poništavanje izmena.

Korišćenje transakcija je ključno za očuvanje integriteta baze podataka, posebno kada se radi sa više povezanih operacija koje moraju biti izvršene zajedno. Važno je koristiti transakcije kada želimo da grupišemo više operacija nad bazom podataka i osiguramo da se sve izmene izvrše ili nijedna, čime se održava konzistentnost podataka.

Transakcije su posebno korisne kada radimo sa kritičnim podacima ili kada želimo da obezbedimo integritet baze u slučaju grešaka ili prekida u toku izvršavanja upita. Bez transakcija, delimično izvršeni upiti mogu ostaviti bazu u nekonzistentnom stanju, što može dovesti do gubitka podataka ili neispravnih rezultata. Korišćenje transakcija omogućava nam da kontrolišemo kada se izmene trajno čuvaju i da se u slučaju greške ili problema vratimo na prethodno stanje baze, čime se povećava sigurnost i pouzdanost rada sa podacima.

U praksi, transakcije su ključne za održavanje integriteta podataka u složenim aplikacijama gde više operacija zavisi jedna od druge, jer omogućavaju da se sve promene izvrše kao jedinstvena celina ili da se nijedna ne izvrši. Bez transakcija, greške u jednoj od operacija mogle bi dovesti do delimičnih promena koje narušavaju konzistentnost baze, što može imati ozbiljne posledice po pouzdanost i tačnost podataka.

Korišćenje transakcija omogućava nam da grupišemo operacije u logičke celine i da osiguramo da se sve izmene izvrše ili nijedna, čime se smanjuje rizik od gubitka podataka i održava integritet baze. Transakcije takođe omogućavaju lakše otkrivanje i rešavanje grešaka, jer možemo pratiti tačku u kojoj je došlo do problema i vratiti bazu u prethodno stanje bez posledica po ostatak podataka.

Primer transakcije u SQLite-u:

```sql
BEGIN TRANSACTION;

UPDATE tasks SET complete = 1 WHERE id = 1;
DELETE FROM tasks WHERE id = 2;

COMMIT;
```

U ovom primeru, transakcija započinje sa `BEGIN TRANSACTION;`. Zatim se izvršava `UPDATE` upit koji menja status zadatka sa `id = 1` i `DELETE` upit koji briše zadatak sa `id = 2`. Ako su oba upita uspešna, izmene se trajno čuvaju pomoću `COMMIT;`. Ako dođe do greške u bilo kom od upita, možemo koristiti `ROLLBACK;` da poništimo sve izmene i vratimo bazu u prethodno stanje. Ovaj pristup osigurava da baza podataka ostane konzistentna i da se delimične izmene ne primenjuju, čime se smanjuje rizik od gubitka podataka i održava integritet baze. Korišćenje transakcija je posebno važno u scenarijima gde više operacija zavisi jedna od druge, jer omogućava da se sve promene izvrše kao jedinstvena celina ili da se nijedna ne izvrši, čime se dodatno povećava pouzdanost i sigurnost rada sa podacima.

---

## Šta moraš da umeš objasniti

1. Zašto kod `INSERT`-a navodimo kolone?

- Navodimo kolone da bismo precizirali u koje kolone unosimo vrednosti i izbegli greške ako se struktura tabele promeni.

2. Zašto je `WHERE id = ...` dobar izbor za menjanje ili brisanje jednog reda?

- `WHERE id = ...` osigurava da se menja ili briše samo određeni red, čime se izbegava nenamerna promena ili brisanje svih redova u tabeli.

3. Šta bi se desilo kada bi iz `UPDATE` ili `DELETE` upita izostavio `WHERE`?

- Ako izostavimo `WHERE` uslov, `UPDATE` bi promenio sve redove u tabeli, a `DELETE` bi obrisao sve redove, što može dovesti do nenamerne gubitka podataka.

4. Zašto `complete = 0` označava nedovršen zadatak?

- `complete = 0` označava da zadatak nije završen, dok `complete = 1` označava da je zadatak dovršen.

5. Koja je razlika između `COMMIT`-a i `ROLLBACK`-a?

- `COMMIT` trajno čuva sve izmene izvršene u okviru trenutne transakcije, dok `ROLLBACK` poništava sve izmene izvršene u okviru te transakcije, vraćajući bazu u stanje pre početka transakcije.

### Transakcije u praksi

Transakcije su ključne kada radimo sa više povezanih upita koji moraju biti izvršeni kao celina. Na primer, prilikom prenosa sredstava između dva računa, potrebno je da se oba upita (`UPDATE` za smanjenje i povećanje stanja) izvrše zajedno. Ako jedan od upita ne uspe, transakcija omogućava da se svi prethodni upiti ponište, čime se sprečava nekonzistentno stanje baze. Bez transakcija, neuspešan upit bi mogao ostaviti bazu u delimično izmenjenom stanju, što može dovesti do gubitka sredstava ili drugih kritičnih problema. Zbog toga je praksa korišćenja transakcija u bazama podataka od suštinskog značaja za očuvanje integriteta i pouzdanosti podataka, posebno u aplikacijama koje zahtevaju visok nivo tačnosti i sigurnosti.

U sqlite3, transakcije se koriste na sličan način. Početak transakcije se označava sa `BEGIN TRANSACTION;`, a završetak sa `COMMIT;`. Ako dođe do greške, možemo koristiti `ROLLBACK;` da poništimo sve izmene izvršene u okviru te transakcije. Ovo omogućava da se više povezanih upita izvrši kao celina i osigurava konzistentnost baze podataka. Primer:

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

Ako dođe do greške u bilo kom od `UPDATE` upita, možemo izvršiti:

```sql
ROLLBACK;
```

Time se poništavaju sve izmene izvršene u okviru te transakcije i baza se vraća u prethodno stanje.
