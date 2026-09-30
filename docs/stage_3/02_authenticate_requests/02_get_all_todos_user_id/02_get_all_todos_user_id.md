# Oblast 03 - Authenticate Requests

## Lekcija 02 - GET svi Todo zapisi po user_id (ownership filter)

U ovoj lekciji cilj je da endpoint za čitanje svih Todo stavki više ne vraća sve zapise iz baze, već samo zapise trenutno ulogovanog korisnika.

To je prvi ozbiljan korak iz "samo authentication" ka praktičnom "authorization" ponašanju nad podacima.

---

## 1) Šta je problem bez ovog filtera

Ako endpoint radi ovako:

```python
db.query(Todos).all()
```

svaki korisnik može da vidi sve Todo zapise svih korisnika.

To znači:

1. Nema privatnosti podataka.
2. Nema vlasništva nad zapisom.
3. API je nebezbedan za višekorisnički scenario.

Zato uvodimo ownership filter.

---

## 2) Usklađeno sa tvojim trenutnim TodoApp kodom

U tvom projektu (`api/routes/todos.py`) endpoint je već ispravno postavljen:

1. Prima `current_user` kroz dependency.
2. Query koristi `filter(Todos.owner_id == current_user.id)`.
3. Vraća samo podatke tog korisnika.

To je tačno ponašanje koje transkript želi da postigne.

---

## 3) Kako tok radi korak po korak

Kada klijent pozove `GET /todos/`:

1. Endpoint traži `current_user: current_user_dependency`.
2. FastAPI pokreće `get_current_user`.
3. Bearer token se čita iz `Authorization` header-a.
4. JWT se dekodira i validira.
5. Iz token identiteta se nalazi korisnik u bazi.
6. Tek tada se izvršava Todo query.
7. Query vraća samo zapise gde je `owner_id` jednak `current_user.id`.

Sažetak toka:

```text
GET /todos/
	-> current_user dependency
		-> JWT validacija
			-> current_user
				-> filter po owner_id
					-> lista samo mojih todo stavki
```

---

## 4) Zašto je ovo authorization, a ne samo authentication

Authentication odgovara na pitanje:

1. Ko je korisnik?

Authorization odgovara na pitanje:

1. Kojim podacima taj korisnik sme da pristupi?

U ovoj lekciji:

1. `get_current_user` radi authentication.
2. `filter(Todos.owner_id == current_user.id)` radi authorization nad podacima.

Zato je ova lekcija veoma važna iako je kod kratak.

---

## 5) Poređenje: pre i posle ownership filtera

### Pre

```python
todo_models = db.query(Todos).all()
```

Efekat:

1. Svako vidi sve.

### Posle

```python
todo_models = db.query(Todos).filter(Todos.owner_id == current_user.id).all()
```

Efekat:

1. Svako vidi samo svoje.

---

## 6) Zašto ne filtrirati po username nego po owner_id

Iako token može sadržati i `username`, pravilnije je filtrirati po ID-u:

1. ID je stabilan primarni ključ.
2. Username može promeniti vrednost kroz vreme.
3. Relacija u bazi je definisana preko `owner_id -> Users.id`.

To čini query preciznim i doslednim modelu baze.

---

## 7) Swagger ponašanje koje vidiš u praksi

Transkript ispravno opisuje sledeće:

1. Bez `Authorize` dobijaš auth grešku (`401`).
2. Posle autorizacije vidiš samo zapise ulogovanog korisnika.

To je direktna posledica činjenice da je endpoint protected i da koristi ownership filter.

---

## 8) Veza sa prethodnom lekcijom

Lekcija 01 je obezbedila:

1. Da novi Todo dobije `owner_id=current_user.id` pri kreiranju.

Lekcija 02 koristi taj rezultat:

1. Čita sve Todo zapise, ali samo one koji pripadaju tom `owner_id`.

Drugim rečima:

1. Lekcija 01 pravilno upisuje vlasnika.
2. Lekcija 02 pravilno čita po vlasniku.

---

## 9) Minimalni test scenariji za ovu lekciju

### Scenario A - bez tokena

1. Pozovi `GET /todos/` bez `Authorization` header-a.
2. Očekuj `401`.

### Scenario B - korisnik A

1. Login kao korisnik A.
2. Pozovi `GET /todos/`.
3. Vidiš samo Todo stavke korisnika A.

### Scenario C - korisnik B

1. Login kao korisnik B.
2. Pozovi `GET /todos/`.
3. Vidiš samo Todo stavke korisnika B.
4. Ne vidiš podatke korisnika A.

---

## 10) Najčešće greške u ovoj fazi

1. Zaboravljen `current_user` parametar u endpointu.
2. Query bez `owner_id` filtera.
3. Filter po pogrešnom polju (npr. naslovu, a ne owner-u).
4. Pretpostavka da je auth dovoljan bez ownership provere.
5. Ručno čitanje tokena po endpointu umesto centralnog dependency mehanizma.

---

## 11) Kratak zaključak lekcije

Ova lekcija formalizuje pravilo:

1. "Mogu da čitam samo svoje podatke."

Tehnički, to je ostvareno kroz:

1. `current_user` dependency.
2. `Todos.owner_id == current_user.id` filter.

Ovo je osnova za sve naredne authorization korake (`read by id`, `update`, `delete`) gde isto pravilo mora da važi.
