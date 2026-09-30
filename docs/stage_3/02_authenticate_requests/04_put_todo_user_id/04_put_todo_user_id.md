# Oblast 03 - Authenticate Requests

## Lekcija 04 - PUT Todo uz user_id ownership proveru

U ovoj lekciji fokus je na bezbednom ažuriranju Todo zapisa.

Nije dovoljno da korisnik bude samo ulogovan. Potrebno je i da server proveri da korisnik ažurira baš svoj zapis.

---

## 1) Problem koji rešavamo

Ako update endpoint traži samo `todo_id`:

```python
db.query(Todos).filter(Todos.id == todo_id).first()
```

ulogovan korisnik može da pokuša izmenu tuđeg zapisa ako pogodi ID.

Zato update mora da proveri dva uslova istovremeno:

1. da Todo sa tim ID-em postoji,
2. da pripada current user-u.

---

## 2) Usklađeno sa tvojim trenutnim kodom

U `TodoApp/api/routes/todos.py` `update_todo` endpoint je već dobro postavljen:

1. Endpoint je protected (`current_user_dependency`).
2. Query radi ownership proveru:
   - `Todos.id == todo_id`
   - `Todos.owner_id == current_user.id`
3. Ako zapis nije nađen, vraća se `404`.
4. Ako jeste, ažuriraju se polja i radi `db.commit()`.

To je tačno ponašanje koje transcript opisuje, ali u modernijem i čistijem obliku.

---

## 3) Zašto u update body-ju nema owner_id

U transcriptu je dobro naglašeno: ne šaljemo `owner_id` iz klijenta.

Razlog:

1. `owner_id` je security podatak.
2. Ako klijent može da ga menja, može pokušati preuzimanje tuđeg zapisa.
3. Vlasništvo se određuje na serveru iz verifikovanog tokena.

Zato klijent šalje samo poslovna polja (`title`, `description`, `priority`, `complete`), a ownership ostaje pod kontrolom servera.

---

## 4) Kako update tok radi korak po korak

Kada pozoveš `PUT /todos/{todo_id}`:

1. FastAPI traži validan Bearer token.
2. `get_current_user` vraća verifikovanog korisnika.
3. Query traži Todo koji zadovoljava oba uslova (`id` + `owner_id`).
4. Ako nema rezultata, endpoint vraća `404`.
5. Ako postoji, polja iz request body-ja se prepisuju u ORM model.
6. `db.commit()` snima izmene.
7. Vraća se `204 No Content`.

Sažetak:

```text
PUT /todos/{todo_id}
	-> JWT validacija
		-> current_user
			-> filter(id + owner_id)
				-> update polja
					-> commit
						-> 204
```

---

## 5) Zašto je status kod 204 dobar izbor

`204 No Content` znači:

1. Operacija je uspela.
2. Nema response body-ja.

To je standardan i veoma čest izbor za uspešan update kada ne vraćaš osvežen objekat u odgovoru.

---

## 6) Razlika u odnosu na stariji kursni stil

U starijim primerima često postoji eksplicitno:

```python
if user is None:
	raise HTTPException(status_code=401, detail="Authentication failed")
```

Kod tebe to nije potrebno u svakom endpointu jer:

1. `get_current_user` centralizovano rešava auth greške.
2. Endpoint dobija validnog korisnika ili se izvršavanje prekida ranije.

To smanjuje dupliranje i čini kod čistijim.

---

## 7) Test scenariji za ovu lekciju

### Scenario A - bez tokena

1. Pozovi `PUT /todos/{todo_id}` bez Authorization header-a.
2. Očekuj `401`.

### Scenario B - validan korisnik, svoj todo

1. Login kao korisnik A.
2. Pošalji validan body za Todo koji pripada A.
3. Očekuj `204`.
4. `GET /todos/` treba da pokaže izmenjene vrednosti.

### Scenario C - validan korisnik, tuđ todo

1. Login kao korisnik B.
2. Pokušaj update Todo zapisa korisnika A.
3. Očekuj `404` u trenutnoj implementaciji.

### Scenario D - nepostojeći ID

1. Pozovi `PUT /todos/999999` sa validnim tokenom.
2. Očekuj `404`.

---

## 8) Najčešće greške

1. Update query proverava samo `id`, bez `owner_id`.
2. Endpoint dopušta klijentu da pošalje `owner_id`.
3. Nema validacije `todo_id > 0` kroz `Path(gt=0)`.
4. Auth i ownership su pomešani ili duplirani po endpointima.
5. Posle izmene zaboravljen `db.commit()`.

---

## 9) Veza sa prethodnim lekcijama

1. Lekcija 01: Todo se kreira sa `owner_id` iz tokena.
2. Lekcija 02: Lista se filtrira po `owner_id`.
3. Lekcija 03: Read-by-id proverava `id + owner_id`.
4. Lekcija 04: Update sada prati isto ownership pravilo.

Tako dobijaš dosledan security model kroz ceo CRUD tok.

---

## 10) Kratak zaključak

Suština ove lekcije:

1. Ulogovan korisnik sme da ažurira samo svoje zapise.
2. Ownership se proverava u samom query-ju (`id + owner_id`).
3. `owner_id` nikada ne dolazi iz klijentskog body-ja.

Ovim je update endpoint bezbedno usklađen sa authentication/authorization pravilima projekta.
