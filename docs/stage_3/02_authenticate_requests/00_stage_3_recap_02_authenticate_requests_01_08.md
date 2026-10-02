# Stage 3 Recap - Authenticate Requests (Lekcije 01-08)

Ovaj recap povezuje lekcije 01-08 iz oblasti **Authenticate Requests** u jednu mapu razumevanja i implementacije.

U prethodnoj oblasti postavljen je auth temelj:

- registracija korisnika
- login i JWT token
- `get_current_user` dependency
- protected endpoint osnovna logika

Oblast 02 sada taj temelj pretvara u dosledna pravila pristupa podacima:

```text
Pre:
ulogovan korisnik -> može da pozove endpoint

Sada:
ulogovan korisnik -> proveri ownership/ulogu -> tek onda CRUD nad podacima
```

Glavni cilj ove oblasti nije samo da endpointi budu "zaključani" tokenom, već da API jasno zna:

- kome resurs pripada
- da li korisnik sme da čita/menja/briše bas taj resurs
- kada je potrebna user-level, a kada admin-level dozvola
- kako da auth i authorization ostanu pregledni i odvojeni po routerima

---

## 0) Trenutno stanje projekta (usklađeno sa kodom)

Aktivne rute u `TodoApp/main.py` su:

```text
POST /auth/
POST /auth/token

GET /todos/
GET /todos/{todo_id}
POST /todos/
PUT /todos/{todo_id}
DELETE /todos/{todo_id}

GET /users/me
PUT /users/password

GET /admin/todos
DELETE /admin/todos/{todo_id}
```

Ključne potvrde iz aktivnog koda:

1. Ownership CRUD u `todos.py` je implementiran kroz `owner_id == current_user.id` filter.
2. `get_current_user()` u `core/security.py` vraća ORM `Users` instancu nakon JWT decode + DB lookup.
3. `users.py` sadrzi self-service tok (`/users/me`, promena lozinke).
4. `admin.py` koristi role proveru (`current_user.role == "admin"`) za admin-only endpoint-e.
5. U `auth.py` create-user endpoint koristi alias `CreateUserPayload` (umesto direktnog imena schema klase) radi stabilnijeg type-check ponašanja u editoru.

---

## 1) Mapa oblasti

## Lekcija 01 - POST todo sa user identitetom iz tokena

Tema: server sam postavlja `owner_id` pri kreiranju Todo zapisa.

Ishod:

- klijent ne salje `owner_id`
- identitet dolazi iz JWT-a
- ownership se upisuje na serveru

Ključno pravilo:

```text
owner_id dolazi iz current_user.id
nikada iz request body-ja
```

Materijal:

- [01_post_todo_user_id/01_post_todo_user_id.md](01_post_todo_user_id/01_post_todo_user_id.md)

## Lekcija 02 - GET svi Todo zapisi po user_id

Tema: lista Todo zapisa mora biti filtrirana po trenutno ulogovanom korisniku.

Ishod:

- endpoint ne vraca sve zapise iz baze
- korisnik vidi samo svoje zapise
- authentication se dopunjuje authorization filterom nad podacima

Koncept:

```text
GET /todos/
-> filter(owner_id == current_user.id)
```

Materijal:

- [02_get_all_todos_user_id/02_get_all_todos_user_id.md](02_get_all_todos_user_id/02_get_all_todos_user_id.md)

## Lekcija 03 - GET Todo po ID-u uz ownership proveru

Tema: read-by-id mora proveriti i `todo_id` i vlasnika.

Ishod:

- sprecava se IDOR scenario
- korisnik ne moze citati tudj Todo pogadjanjem ID-a
- endpoint vraca `404` kada resurs nije dostupan tom korisniku

Koncept:

```text
filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
```

Materijal:

- [03_get_todo_ID_and_user_id/03_get_todo_ID_and_user_id.md](03_get_todo_ID_and_user_id/03_get_todo_ID_and_user_id.md)

## Lekcija 04 - PUT Todo uz ownership proveru

Tema: update radi samo nad korisnikovim zapisom.

Ishod:

- ownership provera pre izmene
- `owner_id` ostaje pod kontrolom servera
- update ne menja API ugovor ka klijentu

Materijal:

- [04_put_todo_user_id/04_put_todo_user_id.md](04_put_todo_user_id/04_put_todo_user_id.md)

## Lekcija 05 - DELETE Todo uz ownership proveru

Tema: brisanje je dozvoljeno samo vlasniku zapisa.

Ishod:

- ownership check i kod delete-a
- `404` kada zapis nije pronadjen/dostupan
- kompletiran user-scoped CRUD bezbednosni obrazac

Materijal:

- [05_delete_todo_user_id/05_delete_todo_user_id.md](05_delete_todo_user_id/05_delete_todo_user_id.md)

## Lekcija 06 - Admin router i role-based pristup

Tema: uvodi se privilegovan nivo pristupa za admin korisnike.

Ishod:

- odvajanje user endpointa (`/todos`) i admin endpointa (`/admin`)
- role provera (`current_user.role`)
- admin moze globalan pregled i globalan delete

Materijal:

- [06_admin_router/06_admin_router.md](06_admin_router/06_admin_router.md)

## Lekcija 07 - Assignment: users ruta

Tema: current user profil i bezbedna promena lozinke.

Ishod:

- endpoint za current user podatke
- endpoint za promenu lozinke
- validacija stare lozinke pre upisa nove

Materijal:

- [07_assignment_problem/07_assignment_problem.md](07_assignment_problem/07_assignment_problem.md)

## Lekcija 08 - Assignment solution: users ruta

Tema: kompletna realizacija users samo-servis toka.

Ishod:

- `/users/me` vraca bezbedan response model
- `/users/password` menja hash nakon verifikacije stare lozinke
- nema vracanja `hashed_password` klijentu

Materijal:

- [08_assignement_solution_users_route/08_assignement_solution_users_route.md](08_assignement_solution_users_route/08_assignement_solution_users_route.md)

---

## 2) Ključna arhitektonska promena ove oblasti

U prethodnom auth delu glavni fokus je bio: "ko je korisnik".

U ovoj oblasti fokus prelazi na: "kojim podacima korisnik sme da pristupi".

To uvodi tri jasna sloja pravila:

1. **Authentication sloj** - validacija tokena i dobijanje `current_user`.
2. **Ownership sloj** - user vidi/menja samo svoje Todo zapise.
3. **Role sloj** - admin ima dodatne privilegije van ownership ogranicenja.

Konceptualno:

```text
JWT validacija
	-> current_user
		-> ownership check ili role check
			-> DB operacija
```

---

## 3) Pre oblasti 02 naspram posle oblasti 02

| Oblast                | Pre oblasti 02                 | Posle oblasti 02                        |
| --------------------- | ------------------------------ | --------------------------------------- |
| Create Todo ownership | mogao bi biti nejasan          | `owner_id` postavlja server             |
| Read all todos        | potencijalno svi zapisi        | samo zapisi current user-a              |
| Read by id            | rizik IDOR ako je samo po `id` | `id + owner_id` provera                 |
| Update/Delete         | samo auth nije dovoljan        | ownership obavezan pre izmene/brisanja  |
| Users self-service    | nije pokriven                  | `GET /users/me` i `PUT /users/password` |
| Admin pristup         | nije formalizovan              | odvojene `/admin` rute sa role proverom |
| Authorization model   | implicitno/rasuto              | eksplicitan i dosledan po endpointima   |

Najvaznija razlika:

```text
Ne proverava se samo da li je korisnik ulogovan,
vec i da li bas taj korisnik ima pravo nad tim resursom.
```

---

## 4) Tokovi zahteva u ovoj oblasti

### A) User-scoped create/read/update/delete

```text
Authorization: Bearer <jwt>
	-> get_current_user()
		-> ownership filter (owner_id == current_user.id)
			-> dozvoljena CRUD operacija
```

### B) Users self-service tok

```text
GET /users/me
	-> get_current_user()
		-> vrati bezbedan user response

PUT /users/password
	-> get_current_user()
		-> verify current_password
			-> hash new_password
				-> commit
```

### C) Admin tok

```text
GET /admin/todos ili DELETE /admin/todos/{todo_id}
	-> get_current_user()
		-> if role != admin: 403
			-> admin CRUD operacija
```

---

## 5) Gde su pravila implementirana u projektu

- Ownership CRUD: `TodoApp/api/routes/todos.py`
- Auth decode + current user: `TodoApp/core/security.py`
- Auth create/login i tip-stabilan create-user input (`CreateUserPayload`): `TodoApp/api/routes/auth.py`
- Users self-service: `TodoApp/api/routes/users.py`
- Admin role pravila: `TodoApp/api/routes/admin.py`
- Router composition: `TodoApp/main.py`

---

## 6) Najvažnija pravila koja ne smeju da se prekrše

1. `owner_id` se nikada ne uzima iz klijentskog body-ja.
2. Read/Update/Delete po ID-u u user ruteru mora da ima i ownership uslov.
3. `hashed_password` se nikada ne vraca klijentu.
4. Promena lozinke mora da verifikuje staru lozinku.
5. Admin privilegije moraju biti eksplicitno proverene.
6. Authentication i authorization greske moraju imati doslednu semantiku status kodova.

---

## 7) Status kodovi kroz oblast 02

1. Uspesan read list/single: `200` - trazeni podaci su vraceni.
2. Uspesan create: `201` - novi resurs je kreiran.
3. Uspesan update/delete/password change bez body-ja: `204` - operacija je uspesna bez response body-ja.
4. Nema token / nevalidan token: `401` - autentifikacija nije uspela.
5. Validan token, ali korisnik nije admin: `403` - autentifikacija jeste, ali dozvola nije.
6. Todo nije pronadjen ili nije dostupan: `404` - resurs ne postoji ili nije dostupan korisniku.
7. Los payload / validacija nije prosla: `422` - request podaci ne zadovoljavaju schema pravila.

---

## 8) Zavrsna checklist za teorijsko razumevanje

### Ownership

- [ ] Zasto `owner_id` dolazi sa servera, a ne od klijenta?
- [ ] Zasto je `id + owner_id` bolji od `id` samostalno?
- [ ] Kako ownership sprecava IDOR scenario?

### Users self-service

- [ ] Zasto je `GET /users/me` bolji od URL `user_id` pristupa za profil?
- [ ] Zasto `hashed_password` ne sme u response?
- [ ] Zasto promena lozinke mora da proveri staru lozinku?

### Admin pravila

- [ ] Koja je razlika izmedju `/todos` user ruta i `/admin` ruta?
- [ ] Kada vracas `403` umesto `401`?
- [ ] Zasto admin pravilo treba biti centralno i dosledno?

### Kvalitet implementacije

- [ ] Da li su ownership i role pravila ista u svim relevantnim endpointima?
- [ ] Da li je logika jasna i bez dupliranja auth provera po endpointima?

---

## 9) Minimalni prakticni zadatak za kraj oblasti

1. Login kao user A i napravi 2 todo zapisa.
2. Login kao user B i potvrdi da ne vidi zapise user-a A.
3. Pokušaj `GET/PUT/DELETE` nad todo ID-em user-a A dok si user B i potvrdi `404`.
4. Pozovi `GET /users/me` i potvrdi da nema `hashed_password` polja.
5. Promeni lozinku kroz `PUT /users/password` i potvrdi da stara lozinka vise ne radi.
6. Login kao admin i potvrdi da `GET /admin/todos` radi.
7. Kao user (ne admin) potvrdi da isti admin endpoint vraca `403`.

Definition of done:

- ownership radi kroz ceo user CRUD tok
- users self-service radi bez curenja osetljivih podataka
- admin privilegije rade i odbijaju neadmin korisnike
- endpointi imaju doslednu status semantiku

---

## 10) Kako ova oblast priprema prelaz na SQLAlchemy 2.0

Najvaznije je da su security i authorization pravila sada stabilna.

To znaci da u SQLAlchemy 2.0 prelazu menjas:

- stil modela (`Mapped`, `mapped_column`)
- stil upita (`select`, `execute`, `scalars`)

Ali ne smes promeniti:

- ownership logiku
- admin role granice
- API ugovor endpointa
- bezbednosnu semantiku status kodova

Drugim recima:

```text
Prvo stabilizuj pravila pristupa.
Onda promeni ORM sintaksu.
```

---

## 11) Zakljucak

Oblast 02 "Authenticate Requests" zavrsava najvazniji authorization deo za TodoApp:

1. svaki korisnik radi sa svojim podacima,
2. users sloj pokriva profil i bezbednu promenu lozinke,
3. admin sloj uvodi privilegovani pristup,
4. auth, ownership i role pravila su jasno odvojena i proverljiva.

Posle ove oblasti projekat vise nije "samo JWT login" aplikacija.
Postaje aplikacija sa realnim pravilima pristupa, spremna za kontrolisan prelaz na SQLAlchemy 2.0 i dalje rad sa migracijama.
