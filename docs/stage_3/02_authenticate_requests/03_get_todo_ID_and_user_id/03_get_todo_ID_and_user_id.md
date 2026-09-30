# Oblast 03 - Authenticate Requests

## Lekcija 03 - GET Todo po ID-u uz proveru user_id

U ovoj lekciji unapređujemo endpoint za čitanje jednog Todo zapisa tako da ne proverava samo `todo_id`, već i vlasništvo nad tim zapisom.

Drugim rečima, korisnik sme da pročita samo svoj Todo sa datim ID-em.

---

## 1) Šta je problem bez ownership provere

Ako endpoint radi samo:

```python
db.query(Todos).filter(Todos.id == todo_id).first()
```

onda je dovoljno pogoditi ID i korisnik može videti tuđ zapis.

To je klasičan IDOR problem (Insecure Direct Object Reference).

Bez ownership filtera:

1. URL ID postaje jedini uslov pristupa.
2. Privatni podaci mogu biti otkriveni drugim korisnicima.
3. Authentication postoji, ali authorization nad resursom ne postoji.

---

## 2) Ispravna logika u tvom trenutnom projektu

U tvom `TodoApp/api/routes/todos.py` `read_todo` već radi ispravno:

1. Endpoint je protected kroz `current_user_dependency`.
2. Query sadrži oba uslova:
   - `Todos.id == todo_id`
   - `Todos.owner_id == current_user.id`
3. Ako zapis ne postoji za tog korisnika, vraća se `404`.

To znači da korisnik ne može "pročitati tuđi ID" iako je autentifikovan.

---

## 3) Kako radi kombinovani filter

Suština ove lekcije je sledeća SQLAlchemy ideja:

```python
todo_model = (
	db.query(Todos)
	.filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
	.first()
)
```

Značenje:

1. Prvi uslov traži tačan resurs po ID-u.
2. Drugi uslov proverava da resurs pripada trenutnom korisniku.
3. Rezultat postoji samo ako su oba uslova tačna.

Praktično:

1. "Postoji li Todo sa ovim ID-em?"
2. "I da li je vlasnik baš current user?"

---

## 4) Tok zahteva od header-a do odgovora

Kada klijent pozove `GET /todos/{todo_id}`:

1. `Authorization: Bearer <token>` stiže na server.
2. `get_current_user` dependency validira token.
3. Dobija se `current_user` iz baze.
4. Query traži Todo po `todo_id` i `owner_id=current_user.id`.
5. Ako postoji, vraća se `200` i Todo.
6. Ako ne postoji, vraća se `404`.

Sažetak:

```text
GET /todos/{todo_id}
	-> JWT validacija
		-> current_user
			-> filter(id + owner_id)
				-> 200 ili 404
```

---

## 5) Zašto je u transkriptu bilo if user is None

U starijem kursnom stilu često se u svakom endpointu ponavlja:

```python
if user is None:
	raise HTTPException(status_code=401, detail="Authentication failed")
```

U tvom trenutnom kodu to nije potrebno u svakom endpointu, jer:

1. `get_current_user` centralno obrađuje auth greške.
2. Endpoint dobija već verifikovan `current_user` ili se izvršavanje prekida sa `401`.

To je čistiji i održiviji stil.

---

## 6) Zašto 404 kada ownership ne odgovara

Kod tebe je odluka:

1. Ako query ne vrati zapis, dobija se `404 Todo nije pronađen.`

To pokriva oba slučaja istom porukom:

1. ID stvarno ne postoji.
2. ID postoji, ali ne pripada tom korisniku.

Ovakav pristup često se koristi da ne otkriva informacije o tuđim resursima.

---

## 7) Veza sa prethodne dve lekcije

Logika sada čini konzistentan ownership lanac:

1. Lekcija 01: `POST /todos/` upisuje `owner_id=current_user.id`.
2. Lekcija 02: `GET /todos/` vraća listu filtriranu po `owner_id`.
3. Lekcija 03: `GET /todos/{todo_id}` proverava i `id` i `owner_id`.

To je tačan put od osnovne autentifikacije ka realnoj zaštiti podataka.

---

## 8) Test scenariji (prema transcript logici, usklađeni sa tvojim rutama)

### Scenario A - bez autorizacije

1. Pozovi `GET /todos/1` bez Bearer tokena.
2. Očekuj `401`.

### Scenario B - validan korisnik, svoj todo

1. Login kao korisnik A.
2. Pozovi `GET /todos/{id}` za Todo koji pripada A.
3. Očekuj `200`.

### Scenario C - validan korisnik, tuđ todo

1. Login kao korisnik B.
2. Pozovi `GET /todos/{id}` koji pripada korisniku A.
3. Očekuj `404` u tvojoj trenutnoj implementaciji.

### Scenario D - nepostojeći ID

1. Pozovi `GET /todos/999999` sa validnim tokenom.
2. Očekuj `404`.

---

## 9) Najčešće greške

1. Query proverava samo `todo_id`, bez `owner_id`.
2. Endpoint nije protected dependency-jem.
3. Ownership se proverava tek posle vraćanja modela, umesto u samom query uslovu.
4. Mešanje 401 i 404 semantike bez jasnog pravila.
5. Pretpostavka da "ulogovan korisnik" automatski znači "pravo na svaki resurs".

---

## 10) Kratak zaključak lekcije

Ova lekcija je praktičan authorization korak nad pojedinačnim resursom:

1. Authentication potvrđuje identitet.
2. Authorization proverava vlasništvo nad konkretnim `todo_id`.

Kombinacija `id + owner_id` u query-ju je ključ da API ostane bezbedan u višekorisničkom radu.
