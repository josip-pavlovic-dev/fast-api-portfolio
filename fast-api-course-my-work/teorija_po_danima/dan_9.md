# Dan 9 - Plan rada za JWT (Lekcije 12 i 13) + trenutno stanje projekta

Ovaj dokument je dnevni vodič za danasnji rad.

Cilj dokumenta:

1. Tačna retrospektiva dokle je stigao trenutni TodoApp kod.
2. Uskladjivanje teorije iz lekcija 12 i 13 sa stvarnim stanjem projekta.
3. Jedinstveno objašnjenje kako HTTP zahtev putuje do servera i kroz FastAPI.
4. Praktičan plan rada i raspodela vremena za danas.
5. Preporuka za dalje backend učenje (Udemy smernice).

Napomena:

- Ne dupliram celu teoriju iz lekcija 12 i 13.
- Fokus je na tome kako to mapirati na tvoj trenutni kod i šta radimo sledeće.

---

## 1) Gde smo trenutno sa kodom (realan snapshot)

### 1.1 Auth je stabilan za pre-JWT fazu

Trenutno ima:

- registraciju korisnika sa proverom duplikata po `email`-u ili `username`-u
- `bcrypt` hash lozinke pri registraciji
- `login endpoint` koji proverava username + password
- proveru da je korisnik aktivan
- odgovor sa `placeholder tokenom`

Konkretno, `login` sada vraća:

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

To znači:

- auth `token` postoji
- ali `JWT encode/decode` jos nije uveden

---

### 1.2 Modeli i DB sloj

- `Users` i `Todos` modeli su ORM i rade.
- `db_dependency` i `get_db()` su dobro postavljeni.
- `response_model` za auth create user radi kako treba.

---

### 1.3 API arhitektura sada

- `main.py` uključuje `auth` i `todos` routere.
- `users.py` je trenutno prazan (normalno za ovu fazu).
- `core/config.py` je placeholder i jos ne nosi JWT konfiguraciju.

---

### 1.4 Najvažniji status za danas

Za JWT fazu ti ne krećes od nule.

Imas već završeno:

1. validaciju korisnika (`authenticate_user(...)`)
2. login endpoint (`/auth/token`)
3. bazu i modele (`Users` i `Todos`)
4. dependency injection za DB (`get_db()`)

Nedostaje JWT sloj:

1. encode helper
2. token schema
3. decode/current user helper
4. protected ruta koja koristi current user

---

## 2) Usklađivanje sa Lekcijom 12 (encode JWT)

Lekcija 12 traži uvođenje:

1. JWT biblioteka
2. secret key + algorithm
3. create_access_token
4. exp claim
5. token response schema

Mapiranje na tvoj projekat:

### 2.1 Šta će ići gde

- `TodoApp/core/config.py`
  - JWT_SECRET_KEY
  - JWT_ALGORITHM
  - ACCESS_TOKEN_EXPIRE_MINUTES

- `TodoApp/core/security.py`
  - `create_access_token(...)`
  - password helperi (kasnije i decode helperi)

- `TodoApp/schemas.py`
  - `Token` schema (`access_token`, `token_type`)

- `TodoApp/api/routes/auth.py`
  - login ruta poziva `create_access_token`
  - umesto placeholder tokena vraća pravi JWT

---

### 2.2 Najbitnija razlika kurs vs tvoj kod

Kurs često drži sve u `auth.py`.

Tvoj profesionalniji smer:

- config odvojeno (`core/config.py`)
- security odvojeno (`core/security.py`)
- rute ostaju tanke (pozivaju se helperi iz `core/security.py`), npr. `auth.py` samo poziva `create_access_token` i `get_current_user`)

To je ispravan smer za produkcijski mindset.

---

## 3) Usklađivanje sa Lekcijom 13 (decode JWT)

Lekcija 13 traži:

1. `OAuth2PasswordBearer`
2. `jwt.decode` validaciju
3. `get_current_user` dependency
4. 401 tok za nevalidan token (`HTTPException`)

Mapiranje na tvoj projekat:

### 3.1 Planirana mesta

- `TodoApp/core/security.py`
  - `oauth2_bearer`
  - `get_current_user` dependency
  - decode helper

- `TodoApp/api/routes/todos.py`
  - protected endpoint(i) koji koriste current user dependency
  - filtriranje po owner identitetu

---

### 3.2 Ključna ideja

Encode i decode moraju deliti isti `claims ugovor`.

Ako encode piše `sub` i `id`, decode mora čitati isto to.

Ako kasnije pređeš na `sub = user_id`, i decode logic mora biti usklađen.

---

## 4) Kako HTTP zahtev putuje (kompletan tok na jednom mestu)

Ovo je najvažniji backend mental model za tebe.

### 4.1 Korisnik šalje request

Primer login zahteva:

```text
POST /auth/token
Body/Form: username, password, grant_type=password
```

---

### 4.2 Mreža i server sloj

1. Klijent šalje HTTP zahtev.
2. Uvicorn prima TCP/HTTP saobraćaj.
3. Uvicorn prosleđuje zahtev FastAPI (ASGI app).

---

### 4.3 FastAPI routing i dependency faza

1. FastAPI nalazi odgovarajuću rutu.
2. Rešava dependencies (`Depends(...)`) pre poziva funkcije.
3. Parsira i validira ulazne podatke (`Pydantic/FastAPI`).

Ako validacija padne:

- endpoint funkcija se i ne poziva
- FastAPI vraća 422

---

### 4.4 Endpoint logika

Za trenutni login tok:

1. `authenticate_user(...)` helper se poziva kako bi se proverio identitet korisnika.
2. SQLAlchemy query traži user-a u bazi pomoću ID-a ili username-a.
3. `bcrypt` proverava `hash` lozinke tako što upoređuje unesenu lozinku sa sačuvanim hash-om.
4. Provera `is_active` statusa korisnika preko atributa u bazi. (ako nije aktivan, vraća se odgovarajuća greška)
5. Ako sve prođe, vraća se token response (obično JSON sa JWT) klijentu.

NAPOMENA: Trenutno je token samo placeholder i služi za testiranje toka. Posle Lekcije 12 on postaje pravi JWT.

---

### 4.5 Response faza

1. Endpoint vrati Python objekat (npr. dict ili ORM model). ORM modeli su znači takođe python objekti ali ih FastAPI serializuje u JSON pre slanja klijentu. Serijalizacija se dešava automatski.

2. Dakle, FastAPI serializuje odgovor u JSON pre nego što ga pošalje klijentu.

3. Ako postoji `response_model`, FastAPI `filtrira/validira` izlaz. Pod response_model podrazumeva se da će izlaz biti u skladu sa definisanim `Pydantic` modelom.

4. `Uvicorn` šalje HTTP response klijentu.

---

### 4.6 Tok protected zahteva (posle Lekcije 13)

Primer:

```text
GET /todos/me
Authorization: Bearer <jwt>
```

Server tok:

1. FastAPI ruta matchuje zahtev sa odgovarajućom endpoint funkcijom.
2. `oauth2_bearer` izvuče token iz header-a `Authorization: Bearer <jwt>`
3. `get_current_user` dekodira i validira JWT token.
4. Endpoint dobija provereni current user.
5. `SQLAlchemy` vraća samo `user`-ove podatke iz baze.
6. Na kraju, `FastAPI` šalje response nazad klijentu.

Ako token ne valja:

- vraća se 401
- endpoint business logika se ne izvršava

To je srce backend sigurnosti: identitet se verifikuje pre pristupa resursu.

---

## 5) Najbitnije backend stvari koje treba da znaš sada

Ako zeliš profesionalno FastAPI, fokusiraj se na ovih 8 tačaka:

1. Jasna podela slojeva:
   - route (HTTP endpoints)
   - schema (Pydantic models)
   - service/security helper (business logic and security utilities)
   - persistence (db layer)

2. Authn i authz nisu isto
   - authentication: Ko si (identitet korisnika)
   - authorization: Šta smeš sa tim resursom da radiš (dozvole korisnika, role, ownership)

3. JWT nije enkripcija
   - payload je čitljiv i ne treba se oslanjati na tajnost podataka u njemu
   - ne stavljati tajne podatke u payload

4. Secret management
   - nikad hardcode (hardcoded znači da je vrednost direktno upisana u kod i dostupna je svuda u router-u).Uvek koristiti env/config sloj za čuvanje tajni.
   - env/config sloj za čuvanje tajni predstavlja preporučeni način upravljanja tajnama. U ovom smislu, sve tajne vrednosti (npr. JWT secret) treba čuvati u env/config sloju, a ne direktno u kodu.

5. Dosledan claim ugovor
   - encode i decode moraju biti usklađeni

6. 401/403 disciplina
   - 401: nevalidan identitet
   - 403: validan identitet, nema dozvolu

7. Ownership filter, omogućava da korisnik vidi samo svoje resurse i sprečava pristup tuđim podacima. Query treba filtrirati po `owner_id` zatim koristiti current user identitet.
   - current user identitet
   - query po owner_id

8. Test mindset za zaštićene endpoint-e
   - prvo happy path sa validnim tokenom (expect 200)
   - zatim invalid token sa očekivanim 401
   - expired token sa očekivanim 401
   - missing claim sa očekivanim 401

---

## 6) Plan rada za danas (Lekcija 12 + 13)

Predlog je napravljen za jednu ozbiljnu sesiju od oko 3 sata.

### Blok A - 40 min

Tema: Lekcija 12 mapiranje na kod, priprema za implementaciju auth flow-a

Zadatak:

1. Pročitaj svoje beleške iz lekcije 12.
2. Napravi mini mapu tačno šta ide u config, šta u security, šta u auth router.
3. Definisi claim ugovor koji ćeš koristiti (preporuka: stabilan `sub` sa user ID-jem, bez username i drugih promenljivih podataka).

Izlaz:

- papir/markdown odluka o claims i strukturi fajlova

---

### Blok B - 55 min

Tema: Praktična implementacija encode faze

Zadatak:

1. Uvedi `Token schema`, koja će predstavljati strukturu JWT tokena.
2. Dodaj JWT encode helper, koji će koristiti claim ugovor definisan u Bloku A.
3. Login endpoint neka vraća pravi token, ne placeholder. (`return Token(...)`)
4. Testiraj login endpoint sa validnim korisnikom i proveri da li vraća validan JWT.

Izlaz:

- login vraća validan JWT + `token_type=bearer`

---

### Pauza - 10 min

---

### Blok C - 50 min

Tema: Lekcija 13 decode faza

Zadatak:

1. Dodaj `OAuth2PasswordBearer`.
2. Napravi `get_current_user` decode + claim proveru.
3. Dodaj jedan protected endpoint i proveri 401 tok.

Izlaz:

- endpoint radi sa validnim tokenom
- bez tokena ili sa nevalidnim tokenom vraca 401

---

### Blok D - 35 min

Tema: Verifikacija i dokumentacija

Zadatak:

1. Proveri 4 slucaja:
   - valid token
   - no token
   - bad token
   - expired token (ako stignes)
2. Dopuni `dan_9.md` kratkim dnevnim izvestajem.

Izlaz:

- jasan log šta radi, šta ne radi, šta je sutra prioritet

---

## 7) Minimalni check-list za kraj dana

Dan je uspešan ako su ispunjena makar ova 4 kriterijuma:

1. `/auth/token` vraća pravi JWT
2. postoji `Token` schema
3. postoji `get_current_user` koji validira JWT
4. postoji bar jedna ruta koja koristi current user dependency

Ako ovo prodje, odrađen je najveći tehnicki skok u auth flow-u.

---

## 8) Preporuka za Udemy backend kurs (uz tvoj stil ucenja)

Pošto zelis kurs + transcript -> materijal pristup, najbolji izbor je:

1. Kurs koji je usko fokusiran na FastAPI + SQLAlchemy + Alembic + JWT
2. Kurs koji ima realan mini-projekat sa autorizacijom i deploy-om
3. Kurs koji je novijeg datuma (ili redovno azuriran)

Kako da odabereš konkretan kurs na Udemy-u (prakticno pravilo):

1. Filter: poslednje update datum + recency
2. Sadržaj mora imati:
   - FastAPI osnove
   - Pydantic v2
   - SQLAlchemy 2.x
   - Alembic
   - JWT authn/authz
   - tests
   - deployment
3. Pogledaj 2-3 preview lekcije da vidis stil instruktora

Ako hoćeš, sutra mogu da ti napravim kratak "course vetting" template:

- Šta tačno gledas u silabusu
- Koja pitanja postavljaš pre kupovine
- Kako da kurs uklopiš sa nasim dnevnim dokumentima

---

## 9) Sutrašnji start (dogovor)

Sutra krećemo od:

- `11_json_web_token_JWT_detaljno.md` konteksta koji si već spremio
- zatim direktno prelaz na praktični deo 12 i 13

Predlog prvih 15 minuta sutra:

1. Potvrda claims ugovora (`sub`, `exp`, eventualno `id`)
2. Potvrda gde tačno ide encode helper
3. Potvrda login response modela
4. Tek onda implementacija

Tako izbegavamo da pišemo kod pa da posle vraćamo arhitekturu.

---

## 10) Zakljucak za Dan 9

Nisi na početku - već imaš stabilan auth pre-JWT temelj.

Danasnji fokus nije "naučiti jos teorije", nego:

1. Povezati postojeći `auth` sa `JWT encode/decode` tokom login procesa uz odgovarajuće response modele i testove.
2. Razumeti put zahteva kroz `FastAPI` i `dependency sistem`
3. Postaviti prvi profesionalni security sloj koji je odvojiv i testabilan

Ako odradiš plan iznad, ulaziš u sledeći nivo backend razumevanja:

- ne samo da endpoint radi,
- nego znaš zašto radi,
- gde je bezbednosna granica,
- i kako da projekat ostane održiv kad poraste.
