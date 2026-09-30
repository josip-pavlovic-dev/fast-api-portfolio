# Oblast 03 - Authenticate Requests

## Lekcija 05 - DELETE Todo uz user_id ownership proveru

U ovoj lekciji zatvaramo ownership krug za CRUD: i delete endpoint mora da briše samo zapise koji pripadaju trenutno ulogovanom korisniku.

Authentication bez ownership provere nije dovoljan za bezbedan delete.

---

## 1) Šta je cilj lekcije

Cilj je da `DELETE /todos/{todo_id}` radi sledeće:

1. zahteva validan Bearer token,
2. proverava da je `todo_id` u vlasništvu current user-a,
3. briše zapis samo ako oba uslova važe,
4. vraća `204 No Content` kada je brisanje uspešno.

---

## 2) Usklađeno sa tvojim trenutnim kodom

U tvom `TodoApp/api/routes/todos.py` delete endpoint je već pravilno implementiran:

1. prima `current_user: current_user_dependency`,
2. query proverava i `Todos.id == todo_id` i `Todos.owner_id == current_user.id`,
3. ako nema rezultata, vraća `404`,
4. ako postoji, radi `db.delete(todo_model)` + `db.commit()`,
5. status je `204`.

To je tačno ownership ponašanje za delete operaciju.

---

## 3) Zašto je ownership filter obavezan kod delete-a

Ako endpoint briše samo po `todo_id`, korisnik može pokušati da obriše tuđi zapis pogađanjem ID-a.

Ownership filter (`owner_id == current_user.id`) sprečava to.

Ovo je direktna zaštita od IDOR klase problema i jedna od najvažnijih authorization provera.

---

## 4) Kako delete tok radi korak po korak

Kada klijent pozove `DELETE /todos/{todo_id}`:

1. FastAPI pokreće `get_current_user` dependency.
2. Bearer token se validira.
3. Dobija se `current_user` iz baze.
4. Query traži zapis koji istovremeno zadovoljava:
   - isti `todo_id`,
   - isti `owner_id` kao current user.
5. Ako takav zapis ne postoji, vraća se `404`.
6. Ako postoji, zapis se briše i radi se commit.
7. Endpoint završava sa `204` bez body-ja.

Sažetak:

```text
DELETE /todos/{todo_id}
	-> JWT validacija
		-> current_user
			-> filter(id + owner_id)
				-> delete + commit
					-> 204
```

---

## 5) Kursni stil vs tvoj trenutni stil

U transkriptu se pominje dodatno "duplo" filterisanje pre samog delete koraka.

Kod tebe je stil čistiji:

1. Jednom pronađeš `todo_model` sa ownership uslovom.
2. Ako postoji, direktno ga brišeš.

To je dovoljno i preglednije, bez suvišnog dupliranja query logike.

---

## 6) Zašto je 404 dobar izbor za nevažeći delete

`404` pokriva i slučaj:

1. resurs ne postoji,

i slučaj:

2. resurs postoji, ali nije u vlasništvu current user-a.

Na taj način API ne otkriva dodatne informacije o tuđim zapisima.

---

## 7) Test scenariji za ovu lekciju

### Scenario A - bez tokena

1. Pozovi `DELETE /todos/{todo_id}` bez Authorization header-a.
2. Očekuj `401`.

### Scenario B - validan korisnik, svoj todo

1. Login kao korisnik A.
2. Obriši `todo_id` koji pripada A.
3. Očekuj `204`.
4. `GET /todos/` više ne vraća taj zapis.

### Scenario C - validan korisnik, tuđ todo

1. Login kao korisnik B.
2. Pokušaj delete nad Todo zapisom korisnika A.
3. Očekuj `404` u tvojoj implementaciji.

### Scenario D - nepostojeći ID

1. Pozovi `DELETE /todos/999999` sa validnim tokenom.
2. Očekuj `404`.

---

## 8) Najčešće greške

1. Delete query koristi samo `todo_id`, bez `owner_id` provere.
2. Endpoint nije protected dependency-jem.
3. Zaboravljen `db.commit()` posle `db.delete(...)`.
4. Mešanje 401 i 404 semantike bez jasnog pravila.
5. Pretpostavka da "ulogovan" znači "sme da briše sve".

---

## 9) Veza sa prethodnim lekcijama

Ownership model sada pokriva sve glavne operacije:

1. create: server postavlja `owner_id` iz tokena,
2. read-all: lista filtrirana po `owner_id`,
3. read-by-id: proverava `id + owner_id`,
4. update: proverava `id + owner_id`,
5. delete: proverava `id + owner_id`.

To je kompletan osnovni authorization obrazac za user-scoped Todo API.

---

## 10) Kratak zaključak

Suština lekcije:

1. Delete endpoint mora biti autentifikovan.
2. Brisanje je dozvoljeno samo nad sopstvenim resursom.
3. `id + owner_id` je ključna kombinacija za bezbednost.

Posle ove lekcije svi ključni Todo endpoint-i u tvom projektu dosledno poštuju ownership pravilo.
