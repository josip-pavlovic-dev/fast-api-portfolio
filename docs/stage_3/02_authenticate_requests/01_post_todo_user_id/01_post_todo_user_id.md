# Oblast 03 - Authenticate Requests

## Lekcija 01 - POST todo sa user identitetom iz tokena

Ova lekcija objašnjava kako da novi Todo zapis dobije `owner_id` iz trenutno ulogovanog korisnika, umesto da klijent šalje taj ID ručno.

To je suština bezbednog ownership modela.

---

## 1) Šta je cilj lekcije

Pre ove logike, endpoint za kreiranje Todo stavke može da sačuva podatke, ali nema pouzdan odgovor na pitanje:

1. Ko je vlasnik ovog Todo zapisa?
2. Kako sprečiti da klijent lažira tuđi user ID?

Cilj je:

1. Endpoint zahteva validan Bearer token.
2. Token se dekodira kroz `get_current_user` dependency.
3. Iz dekodiranog identiteta dobija se korisnik.
4. Novi Todo automatski dobija `owner_id=current_user.id`.

---

## 2) Kako je ovo rešeno u tvom trenutnom projektu

U tvom kodu je sve već postavljeno kroz tri ključna dela:

1. JWT encode/decode i `get_current_user` u `core/security.py`.
2. Dependency alias `current_user_dependency` u `api/routes/todos.py`.
3. Kreiranje Todo zapisa sa `owner_id=current_user.id` u `create_todo` endpointu.

Važno usklađenje sa tvojim projektom:

1. U kursnom transkriptu pominje se import iz auth fajla.
2. Kod tebe je ispravno: import iz `core/security.py`.
3. U kursnom primeru user često izgleda kao dict payload.
4. Kod tebe `get_current_user` vraća ORM `Users` objekat, što je čistije i robustnije.

---

## 3) Tok zahteva korak po korak

Kada klijent pošalje `POST /todos/`:

1. FastAPI vidi da endpoint traži `current_user: current_user_dependency`.
2. Pokreće se `get_current_user` dependency.
3. `OAuth2PasswordBearer` iz `Authorization` header-a uzima token.
4. `jwt.decode(...)` proverava potpis, algoritam i ostale JWT uslove.
5. Iz payload-a se čita `sub` i pretvara u `user_id`.
6. U bazi se traži korisnik po tom ID-u.
7. Ako korisnik ne postoji ili nije aktivan, vraća se `401`.
8. Ako je validan, endpoint dobija `current_user` objekat.
9. Kreira se `Todos(...)` i obavezno se dodaje `owner_id=current_user.id`.
10. Zapis se čuva u bazi.

Sažeto:

```text
Authorization: Bearer <token>
	-> get_current_user
		-> jwt.decode
			-> Users iz baze
				-> create_todo(owner_id=current_user.id)
```

---

## 4) Zašto klijent ne sme da šalje owner_id

Ako bi API primao `owner_id` direktno iz request body-ja:

1. Klijent bi mogao da upiše tuđi ID.
2. Time bi kreirao zapis „u ime“ drugog korisnika.
3. Cela ownership zaštita bi izgubila smisao.

Zato je pravilno:

1. Klijent šalje samo poslovna polja Todo zahteva.
2. Server određuje identitet iz tokena.
3. Server upisuje `owner_id` samostalno.

Ovo je jedan od najvažnijih security obrazaca u REST API dizajnu.

---

## 5) Razlika u odnosu na stariji kursni stil

U transkriptu se često radi dodatna provera:

```python
if user is None:
	raise HTTPException(status_code=401, detail="Authentication failed")
```

U tvom trenutnom kodu to uglavnom nije potrebno u samom endpointu zato što:

1. `get_current_user` već centralno baca `401` za nevalidan token.
2. Endpoint se izvršava tek kada dependency vrati validnog korisnika.

To je dobra praksa jer smanjuje dupliranje i drži auth logiku na jednom mestu.

---

## 6) Uloga Swagger Authorize dugmeta u ovoj lekciji

Kada endpoint koristi OAuth2 Bearer dependency, u Swagger UI-ju dobijaš zaštitu kroz lock mehanizam.

Praktično:

1. Bez autorizacije dobijaš `401 Not authenticated` ili ekvivalentan auth error.
2. Posle uspešne autorizacije, isti `POST /todos/` prolazi.
3. Kreirani zapis dobija `owner_id` trenutno autorizovanog korisnika.

Bitna napomena:

`tokenUrl="auth/token"` ne validira token sam po sebi, već govori OpenAPI/Swagger sloju gde se token dobija.

---

## 7) Povezivanje sa postojećim endpointima u projektu

Trenutno relevantne rute u tvom projektu:

```text
POST /auth/
POST /auth/token

POST /todos/
GET /todos/
GET /todos/{todo_id}
PUT /todos/{todo_id}
DELETE /todos/{todo_id}
```

U kontekstu ove lekcije fokus je na:

1. `POST /auth/token` da dobiješ access token.
2. `POST /todos/` da upišeš Todo za current user-a.

---

## 8) Minimalni test scenariji za ovu lekciju

### Scenario A - bez tokena

1. Pozovi `POST /todos/` bez Authorization header-a.
2. Očekuj `401`.

### Scenario B - sa validnim tokenom

1. Login kroz `POST /auth/token`.
2. Pošalji `POST /todos/` sa Bearer tokenom.
3. Očekuj `201` i uspešno kreiran zapis.

### Scenario C - provera ownership-a

1. Napravi Todo kao korisnik A.
2. Login kao korisnik B.
3. Proveri da B ne vidi ili ne menja A zapis kroz ownership filter.

---

## 9) Najčešće greške u ovoj fazi

1. Pogrešan `tokenUrl` koji ne prati realnu login rutu.
2. Dependency import iz pogrešnog fajla.
3. Prihvatanje `owner_id` iz request body-ja.
4. Dupliranje auth provera u svakom endpointu umesto centralnog dependency pristupa.
5. Mešanje pojmova: authentication (ko si) i authorization (šta smeš).

---

## 10) Kratak zaključak lekcije

Suština ove lekcije nije samo da endpoint „radi“, nego da ownership bude bezbedan i dosledan:

1. Identitet dolazi iz verifikovanog tokena.
2. `owner_id` određuje server, ne klijent.
3. Auth logika je centralizovana u `get_current_user`.

Ovim je postavljen temelj za sledeću lekciju: čitanje Todo stavki po konkretnom korisniku.
