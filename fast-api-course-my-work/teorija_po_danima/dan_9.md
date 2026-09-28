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

---

## Pitanje 1

PITANJE: Da li mogu da pokrenem pip install iz fast-api-course-my-work foldera. Aktivirao sam `venv`?

---

## Odgovor 1

ODGOVOR: Da, možeš da pokreneš `pip install` iz `fast-api-course-my-work` foldera, pod uslovom da je aktiviran odgovarajući `venv`. To će instalirati pakete u aktivirani virtuelni environment, a ne globalno.

### Detaljno objašnjenje

Da, možeš slobodno iz foldera fast-api-course-my-work, ako je .venv aktivan.

Najbezbednije je da koristiš ovaj oblik komande:

1. `python -m pip install "python-jose[cryptography]"`
2. `python -m pip show python-jose`

Zašto ovako:

1. Aktiviran `.venv` znači instalacija ide u taj virtual environment.
2. `python -m pip` garantuje da koristiš pip iz trenutno aktivnog Python okruženja.

Brza provera pre instalacije:

1. `which python`
2. `python -m pip --version`

Ako oba pokazuju putanju ka tvom `.venv`, spreman si za instalaciju.

---

## Pitanje 2

PITANJE: Gde tačno treba da stavim `SECRET_KEY`, `ALGORITHM` i `funkciju create_access_token`? Da li `SECRET_KEY` i `ALGORITHM` idu u `fast-api-course-my-work/TodoApp/core/config.py` a funkcija create_access_token u `fast-api-course-my-work/TodoApp/core/security`? Takođe mi objasni `.env` fajl za `secret key` i da li treba da ga koristim i kako. Obeležio sam ti pasus sa tajnim ključem.

ODGOVOR:

Da, upravo tako treba da bude raspoređeno, i sada je povezano u projektu:

1. `SECRET_KEY` i `ALGORITHM` (kao `JWT_SECRET_KEY` i `JWT_ALGORITHM`) idu kroz `config` sloj.
2. `create_access_token` ide u `security` sloj (`TodoApp/core/security.py`).
3. `/auth/token` ruta koristi helper iz security sloja i vraća pravi JWT, ne placeholder.

### Šta je konkretno urađeno u kodu

1. Config sloj je prebačen na environment pristup u `TodoApp/core/config.py`.
2. Uveden je `Settings` objekat sa poljima:
   - `jwt_secret_key` (iz `.env` fajla ili environment varijable `JWT_SECRET_KEY`)
   - `jwt_algorithm` (iz `.env` fajla ili environment varijable `JWT_ALGORITHM`)
   - `access_token_expire_minutes` (iz `.env` fajla ili environment varijable `ACCESS_TOKEN_EXPIRE_MINUTES`)
3. Dodata je validacija da:
   - `JWT_SECRET_KEY` mora postojati
   - `ACCESS_TOKEN_EXPIRE_MINUTES` mora biti ceo broj i > 0
4. Dodat je JWT helper u `TodoApp/core/security.py`:
   - `create_access_token(...)`
   - koristi timezone-aware UTC (`datetime.now(timezone.utc)`)
   - `sub` claim je stabilan `user_id` (`str(user_id)`)
   - `username` je pomoćni claim
5. Dodata je `Token` schema u `TodoApp/schemas.py`.
6. Izmenjen je `/auth/token` endpoint u `TodoApp/api/routes/auth.py`:
   - sada ima `response_model=Token`
   - pravi JWT preko `create_access_token(...)`
   - vraća `Token(access_token=..., token_type="bearer")`
7. Dodat je `fast-api-course-my-work/.env` sa:
   - `JWT_SECRET_KEY`
   - `JWT_ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=20`

---

### Zašto je ovo dobar pristup za trenutni kurs (legacy SQLAlchemy stil)

Dogovor je da trenutno ostajemo kompatibilni sa kursnim stilom, pa su zadržani:

1. `db.query(...).filter(...).first()` obrasci (`legacy ORM query API`)
2. trenutna organizacija routera
3. postojeći auth flow sa minimumom invazivnih promena

Istovremeno su primenjene moderne prakse koje ne lome tvoj trenutni stil:

1. secret više nije hardkodovan u auth ruti
2. settings su centralizovani
3. token response ima jasan API ugovor (`Token` schema)
4. JWT vreme koristi UTC aware datetime
5. claim ugovor je stabilniji (`sub` = user_id)

To je dobar kompromis: moderno i bezbedno, ali bez prisilnog prelaska na SQLAlchemy 2.0 stil pre dogovorene faze.

---

## Analiza lekcija 12, 13 i 14 (pravac kursa)

### Lekcija 12 - Encode JWT

Suština:

1. Posle uspešnog login-a server kreira access token.
2. Uvodi se secret + algorithm + expiration.
3. Token endpoint dobija jasan response model.

Poruka lekcije:

- Authentication više nije samo "username/password check".
- Postaje `state-less` token flow: klijent nosi dokaz identiteta kroz JWT.

---

### Lekcija 13 - Decode JWT i current user

Suština:

1. `OAuth2PasswordBearer` čita Bearer token iz header-a.
2. `jwt.decode(...)` validira signature/exp/claims.
3. `get_current_user` postaje centralni security dependency.

Poruka lekcije:

- Token koji nije validiran ne sme da otvara pristup endpointu.
- Security treba centralizovati kroz dependency, ne kopirati po rutama.

---

### Lekcija 14 - Authentication enhancements

Suština:

1. Standardizuju se auth rute (`/auth/...`).
2. Sređuje se `tokenUrl` da odgovara stvarnoj ruti (`auth/token`).
3. Login greške vraćaju pravi HTTP 401 (ne plain string).
4. Swagger organizacija (`tags=["auth"]`) postaje jasnija.

Poruka lekcije:

- Kurs prelazi sa "radi" na "radi ispravno i čitljivo".
- Ugovor API-ja (putanje, status kodovi, OpenAPI) postaje jednako važan kao i sama logika.

---

## Kuda ide kurs odmah posle ove tri lekcije

Posle 12/13/14 praktični pravac je gotovo sigurno:

1. protected endpoint-i nad Todo resursima
2. current user ownership filter (`owner_id == current_user_id`)
3. razlika 401 vs 403 u realnim scenarijima
4. eventualno role-based provere (admin/user)

Drugim rečima:

1. lekcija 12 daje "token issuance"
2. lekcija 13 daje "token verification"
3. lekcija 14 daje "API contract cleanup"
4. sledeća oblast prirodno prelazi na "authorization nad resursima"

To je tačka gde auth prestaje da bude izolovan modul i počinje da utiče direktno na CRUD ponašanje aplikacije.

---

## Kratka tehnička napomena o `.env`

`.env` treba da koristiš za lokalni development jer:

1. drži tajne van source koda (`.env` fajl)
2. olakšava promenu vrednosti po okruženju (`.env` fajl za lokalni development, environment varijable za produkciju)
3. sprečava slučajno commit-ovanje secret-a (uz `.gitignore`)

Da, `.env` treba da bude u `.gitignore`.

U tvom projektu to je već podešeno u root `.gitignore` fajlu (`.env` stavka postoji), što je ispravno.

Važna napomena:

Ako je `.env` nekad ranije već bio commit-ovan, samo dodavanje u `.gitignore` nije dovoljno; tada ga treba ukloniti iz Git praćenja (tracking), a zatim rotirati sve tajne koje su možda procurele.

Za produkciju, secret se ne drži u repozitorijumu niti u javnim fajlovima, već kroz `deployment secret manager/environment mehanizam.`

---

## Pitanje 3

PITANJE: Kako da proverim koji su sve fajlovi praćeni na `Git-u` a promenili su rutu? Katovao sam ih iz jednog u drugi folder ali nisam obrisao prethodno praćene fajlova na staroj root-i? Kako da ih uklonim iz Git praćenja?

---

## Odgovor 3

ODGOVOR: Najpre možeš da proveriš koji su fajlovi praćeni na Git-u koristeći komandu:

```bash
git ls-files
```

Ako želiš da ukloniš fajl iz Git praćenja, koristi:

```bash
git rm --cached putanja/do/fajla
```

Posle toga, fajl više neće biti praćen od strane Git-a, ali će i dalje postojati u tvom lokalnom fajl sistemu.

Ako je fajl katovan (premešten) u drugi folder, prethodna putanja automatski više neće biti praćena, ali nova putanja će biti dodata u Git praćenje kada izvršiš `git add` na novoj lokaciji.

Takođe, ako želiš da ukloniš sve prethodno praćene fajlove koji više ne postoje na starim lokacijama, možeš koristiti:

```bash
git ls-files --deleted -z | xargs -0 git rm --cached
```

Ova komanda će pronaći sve fajlove koji su obrisani iz radnog direktorijuma, ali su i dalje praćeni od strane Git-a, i ukloniće ih iz Git praćenja.

### Detaljno objašnjenje

1. Nema rename zapisa trenutno u git status izlazu (nema R linija).
2. Samo jedan .gitignore postoji: `.gitignore`.
3. .env fajl nije praćen u git-u.
4. Pravilo iz `.gitignore` već ignoriše i .env u root-u i .env u podfolderu fast-api-course-my-work.

Kako da proveriš koje su praćene putanje i da li je nešto ostalo praćeno na staroj lokaciji

1. Pregled promena sa statusima:
   git status --short

2. Pregled sa tipom promene (A/M/D/R):
   git diff --name-status
   git diff --cached --name-status

3. Da vidiš da li je konkretan fajl još praćen:
   git ls-files | rg "deo_putanje_ili_ime_fajla"

4. Da vidiš da li ignore pravilo radi za staru i novu lokaciju:
   git check-ignore -v stara_putanja nova_putanja

Ako je fajl nekad bio praćen, a sad treba da ostane lokalan

1. Ukloni ga samo iz git praćenja (ne briše lokalni fajl):
   git rm --cached putanja/fajla

2. Commit:
   git commit -m "Stop tracking moved/local file"

3. Proveri ponovo:
   git status --short

Za tvoj konkretan slučaj sa `.env` trenutno ne moraš ništa dodatno da radiš, jer nije praćen i ignore pravilo već radi.

---

## Pitanje 4

PITANJE: Koji je tačan redosled kreiranja fajlova i importa za JWT deo, da ne upadnem u problem tipa `config.py` radi bez importa, a `security.py` ne radi bez config-a?

---

## Odgovor 4

ODGOVOR: Za tvoj projekat i trenutni kursni (legacy SQLAlchemy) stil, najčistiji redosled je ovaj:

### Redosled kreiranja (korak po korak)

1. `fast-api-course-my-work/.env`
   - prvo upišeš `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
   - razlog: config fajl treba odmah da ima odakle da čita vrednosti

2. `fast-api-course-my-work/TodoApp/core/config.py`
   - praviš `settings` (učitavanje env varijabli + validacija)
   - razlog: `security.py` zavisi od `settings`

3. `fast-api-course-my-work/TodoApp/core/security.py`
   - praviš `create_access_token(...)`
   - importuješ `settings` iz `core/config.py`
   - razlog: security sloj koristi secret/algorithm/expire iz config sloja

4. `fast-api-course-my-work/TodoApp/schemas.py`
   - dodaješ `Token` response model
   - razlog: auth ruta vraća tipizovan odgovor

5. `fast-api-course-my-work/TodoApp/api/routes/auth.py`
   - importuješ `create_access_token` (i po potrebi `settings`)
   - menjaš `/auth/token` da vraća pravi JWT (`response_model=Token`)
   - razlog: auth endpoint je poslednji sloj koji "spaja" config + security + schema

6. Tek onda test i commit
   - `python -m pip show python-jose`
   - test login rute
   - proveri git status, pa commit

### Kratko pravilo zavisnosti

Zavisnosti treba da idu u jednom smeru:

1. `.env` -> `config.py`
2. `config.py` -> `security.py`
3. `security.py` + `schemas.py` -> `auth.py`

`config.py` ne treba da importuje `security.py`, i `schemas.py` ne treba da zavisi od auth rute.

### Mini mental model (da lakše pamtiš)

1. Konfiguracija: odakle čitam tajne i parametre?
2. Security helper: kako pravim token?
3. Schema: kako izgleda odgovor?
4. Ruta: kada pozivam helper i šta vraćam klijentu?

Ako pratiš ovaj red, izbegavaš kružne importe i "polu-gotov" kod koji puca pri importovanju modula.

---

## Pitanje 5

PITANJE: Kako da proverim verziju `python-jose[cryptography]` za requirements.txt? Da li može i bez verzije?

---

## Odgovor 5

ODGOVOR: Verzija se proverava tako što pokreneš komandu:

```bash
python -m pip show python-jose
```

Ako želiš da proveriš i dependency koji dolazi kroz extra, proveri posebno:

```bash
python -m pip show cryptography
```

Ako želiš da dodaš u `requirements.txt` bez fiksne verzije, možeš napisati:

```text
python-jose[cryptography]
```

ali preporučljivo je da ipak fiksiraš verziju kako bi izbegao potencijalne probleme sa kompatibilnošću u budućnosti. Na primer:

```text
python-jose[cryptography]==3.5.0
```

### Detaljno objašnjenje

Može i bez verzije, ali je bolje sa verzijom zbog stabilnosti i reprodukovanja okruženja.

Bitno: `python-jose[cryptography]` je ispravan format za `pip install`, ali nije ispravan argument za `pip show`.

Proverio sam ti trenutno instalirane verzije (`python -m pip show python-jose` i `python -m pip show cryptography`) u venv-u:

1. python-jose: 3.5.0

2. cryptography: 50.0.1

Šta da staviš u `requirements.txt`:

#### Opcija A (preporučeno za tebe sada):

```text
python-jose[cryptography]==3.5.0
```

---

#### Opcija B (još strožije pinovanje):

```text
python-jose[cryptography]==3.5.0
cryptography==50.0.1
```

Odgovor na tvoje pitanje:

1. Da, može bez verzije.
2. Ali bez verzije pri sledećem install-u možeš dobiti noviju verziju i drugačije ponašanje.
3. Za kurs/projekat je sigurnije da pinuješ bar python-jose verziju.

---

## Pitanje 6

PITANJE: Potrebna mi je detalja analize liniju po liniju sa objašnjenjem. Od imorta i modula pa sve do kraja config.py.

---

## Odgovor 6

ODGOVOR: U nastavku je detaljna analiza liniju po liniju za `TodoApp/core/config.py`, od prvog importa do poslednje linije.

### Ceo kod (referenca)

```python
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Učitava varijable iz .env fajla ako postoji.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int


def get_settings() -> Settings:
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        raise RuntimeError(
            "JWT_SECRET_KEY nije postavljen. Dodaj ga u environment ili .env fajl."
        )

    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    expire_minutes_raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")
    try:
        access_token_expire_minutes = int(expire_minutes_raw)
    except ValueError as error:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti ceo broj.") from error

    if access_token_expire_minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti > 0.")

    return Settings(
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
    )


settings = get_settings()
```

---

### Linija po linija objašnjenje

Ovaj fajl definiše konfiguraciju aplikacije koristeći environment varijable i `.env` fajl. Sadrži klasu `Settings` koja čuva ključne konfiguracione vrednosti i funkciju `get_settings` koja validira i vraća instancu te klase. Na kraju, kreira se globalni objekat `settings` koji se koristi u ostatku aplikacije.

#### Linija 1: `import os`

Koristi se za čitanje environment varijabli preko `os.getenv(...)` na taj način da aplikacija može da pristupi konfiguracionim vrednostima definisanim u environment-u (npr. preko terminala ili sistema da pristupi operativnom sistemu) ili `.env` fajlu koji se učitava pomoću `load_dotenv()`.

POJMOVI i FUNKCIJE:

1. `os.getenv(...)` - standardna funkcija koja čita vrednost environment varijable. I dalje se koristi u modernom programiranju. Ako varijabla ne postoji, vraća `None` ili default vrednost ako je prosleđena kao drugi argument. Potpis funkcije bez Optional import-a (od Python 3.8+ je dovoljno koristiti `str` tip za return vrednost):

```python
os.getenv(key: str, default: str = None) -> str:
    """Čita vrednost environment varijable sa ključem `key`
    koji je ustvari naziv varijable u environment-u.
    Ako varijabla ne postoji, vraća `default` vrednost."""

    return os.getenv(key, default)
```

2. `from dotenv import load_dotenv` - uvozi funkciju `load_dotenv` koja učitava `.env` fajl u environment. Ovaj modul je third-party i omogućava da konfiguracione vrednosti budu definisane u `.env` fajlu umesto direktno u environment-u.

3. `environment` - skup varijabli koje definišu konfiguraciju aplikacije u operativnom sistemu. Ove varijable se mogu čitati pomoću `os.getenv(...)` i mogu biti definisane direktno u sistemu ili učitane iz `.env` fajla. One su dostupne tokom celog životnog ciklusa aplikacije.

---

#### Linija 2: `from dataclasses import dataclass`

Uvozi dekorator za jednostavnu i tipizovanu (`type-annotated`) konfiguracionu klasu. Modul `dataclasses` je standardni Python modul za rad sa klasama koje sadrže polja definisana tipovima. (`dataclass` dekorator) On omogućava automatsko generisanje metoda kao što su `__init__`, `__repr__` i `__eq__`, čineći kod čistijim i lakšim za održavanje.

POJMOVI i FUNKCIJE:

1. Kada kažemo za klasu da je `dataclass`, to znači da je klasa prvenstveno namenjena za čuvanje podataka i da će Python automatski generisati osnovne metode kao što su `__init__`, `__repr__` i `__eq__`. Ovo čini kod čitljivijim i smanjuje potrebu za ručnim pisanjem boilerplate koda.

2. `frozen=True` - opcija koja čini dataclass immutable, što znači da se vrednosti polja ne mogu menjati nakon inicijalizacije. Ovo je korisno za konfiguracione klase gde želimo da osiguramo da se vrednosti ne menjaju tokom runtime-a.

3. `@dataclass(frozen=True)` - dekorator koji se primenjuje na klasu da bi postala immutable dataclass tj klasa koja ne može da menja svoje polja nakon inicijalizacije i osigurava konzistentnost podataka tokom celog životnog ciklusa objekta `Settings` i svih njegovih instanci zahvaljujući `frozen=True` opciji.

---

#### Linija 4: `from dotenv import load_dotenv`

Uvozi funkciju koja učitava `.env` varijable u environment. Koristi se da bi se konfiguracione vrednosti definisane u `.env` fajlu učitale u environment pre nego što se pozovu `os.getenv(...)`.

---

#### Linija 7: `load_dotenv()`

Ovo se izvršava pri importu modula i priprema varijable potrebne za `os.getenv` pozive. Pravilo za module je da se prvi put u toku importovanja modula sve linije na vrhu fajla (top-level modul koda) izvršavaju, što znači da će `.env` fajl biti učitan pre nego što se bilo koja funkcija koja zavisi od environment varijabli pozove. Modul se učitava samo jednom. `sys.modules` čuva referencu na učitane module i njemu se pristupa pri svakom narednom importu istog modula što osigurava da se `load_dotenv()` ne izvršava više puta.

---

#### Linija 10: `@dataclass(frozen=True)`

`Settings` postaje `immutable dataclass` i time sprečava slučajno runtime menjanje konfiguracije. Ovo osigurava da konfiguracija ostaje konzistentna (podaci su istog tipa i vrednosti) tokom celog životnog ciklusa aplikacije.

---

#### Linija 11: `class Settings:`

Definiše tip koji predstavlja centralnu JWT konfiguraciju. Sve instance ove klase su immutable i predstavljaju konzistentnu (nepromenljivu) konfiguraciju tokom celog životnog ciklusa aplikacije.

---

#### Linija 12: `jwt_secret_key: str`

Tajni ključ za potpisivanje/verifikaciju JWT-a. Mora biti čuvan u tajnosti i ne sme biti hardkodovan u kodu. U praksi se čuva u environment varijablama ili tajnim menadžerima. (npr. `HashiCorp Vault`, `AWS Secrets Manager` i slični sistemi)

---

#### Linija 13: `jwt_algorithm: str`

Naziv algoritma (npr. `HS256`). Mora biti u skladu sa JWT standardima i podržan od strane biblioteke koja se koristi za generisanje i verifikaciju tokena.

---

#### Linija 14: `access_token_expire_minutes: int`

Trajanje access tokena u minutima. Mora biti pozitivan ceo broj. Ako nije, aplikacija će odmah prijaviti grešku i prekinuti izvršavanje. U obzir se uzimaju samo validne, pozitivne vrednosti tipa int.

---

#### Linija 17: def get_settings() -> Settings:

Funkcija `get_settings` čita, validira i vraća jednu konzistentnu konfiguraciju. Ako dođe do greške u konfiguraciji, aplikacija će odmah prijaviti grešku i prekinuti izvršavanje. Od parametara environment varijabli (varijabli iz `.env` fajla i sistema) pravi se finalni, validirani `Settings` objekat.

---

#### Linija 18: jwt_secret_key = os.getenv("JWT_SECRET_KEY")

Čita obaveznu varijablu iz environment-a (`.env fajla`) i dodeljuje je lokalnoj promenljivoj `jwt_secret_key`.

---

#### Linija 19: if not jwt_secret_key:

Provera da li `jwt_secret_key` postoji i da li nije prazan string. Provera da li je prazan string je važna jer prazan string tehnički postoji, ali nije validan tajni ključ. Ovu proveru obezbeđuje `if not jwt_secret_key:` uslov. Posto je prazan string "falsy" u Pythonu, uslov će biti zadovoljen i aplikacija će prijaviti grešku.

PITANJE: Zašto ne koristimo `if jwt_secret_key is None:` umesto `if not jwt_secret_key:`?

ODGOVOR: Koristimo `if not jwt_secret_key:` jer želimo da obuhvatimo oba slučaja: kada varijabla ne postoji (`None`) i kada je prazan string (`""`). `if jwt_secret_key is None:` bi obuhvatio samo slučaj kada varijabla ne postoji, ali ne bi detektovao prazan string, koji takođe nije validan tajni ključ. U praksi je bolje koristiti `if not jwt_secret_key:` jer je jednostavnije i pokriva oba scenarija.

---

#### Linije 20-22: raise RuntimeError(...)

Ako secret nedostaje, aplikacija se zaustavlja odmah sa jasnom porukom.

---

#### Linija 24: jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

Čita algoritam i koristi default `HS256` ako varijabla nije setovana. Dodeljuje ga lokalnoj promenljivoj `jwt_algorithm`. Za default vrednost se koristi string `"HS256"` zato što je to najčešće korišćen i bezbedan algoritam za HMAC. Njega smo i definisali kao default u kodu.

---

#### Linija 26: expire_minutes_raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")

Čita trajanje kao string sa default vrednošću `20`.

---

#### Linija 27: try:

Počinje bezbedna konverzija stringa u broj.

---

#### Linija 28: access_token_expire_minutes = int(expire_minutes_raw)

Parsira minute u integer.

---

#### Linija 29: except ValueError as error:

Hvata slučaj pogrešnog unosa (npr. `abc`).

---

#### Linija 30: raise RuntimeError(...) from error

Vraća jasnu poruku i čuva originalni uzrok greške.

PITANJE: Prvi put vidim `raise RuntimeError(...) from error`. Šta znači `from error`?

ODGOVOR: `from error` u `raise RuntimeError(...) from error` zadržava originalni exception (`ValueError` u ovom slučaju) kao uzrok za pojavljivanja novog exception-a (`RuntimeError`). To omogućava da traceback pokaže oba exception-a, što olakšava debagovanje. Bez `from error`, originalni exception (`ValueError`) bi bio izgubljen i traceback bi pokazivao samo novi exception (`RuntimeError`). Ovakva sintaksa se naziva "exception chaining" i korisna je za praćenje uzroka grešaka. Na ovaj način možeš videti kompletnu istoriju grešaka i lakše identifikovati problem. Primer "exception chaining"-a bi bio:

```python
try:
    access_token_expire_minutes = int(expire_minutes_raw)
except ValueError as e:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti ceo broj.") from e
    # Ovaj deo koda osigurava da se greška pravilno propagira i da originalni ValueError nije izgubljen.
```

Primer sa višestrukim exception chaining-om bi bio:

```python
try:
    access_token_expire_minutes = int(expire_minutes_raw)
    if access_token_expire_minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti > 0.")
except ValueError as e:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti ceo broj.") from e
except RuntimeError as e:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti > 0.") from e
    # Ovaj deo koda osigurava da se greška pravilno propagira i da originalni RuntimeError nije izgubljen.
    # Ako se desi bilo koja druga greška, ona će biti propagirana dalje.
    pass
```

---

#### Linija 32: if access_token_expire_minutes <= 0:

Semantička validacija: vrednost za koliko minuta token važi mora biti pozitivna.

---

#### Linija 33: raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti > 0.")

Fail-fast za nelogičnu konfiguraciju. Ovo znači da aplikacija neće ni pokušati da radi sa nevalidnim podešavanjima, već će odmah prijaviti grešku i zaustaviti se. Tek nakon što se sve konfiguracije uspešno validiraju, aplikacija nastavlja sa radom.

---

#### Linije 35-39: return Settings(...)

Pravi finalni, validirani settings objekat koji se koristi u ostatku aplikacije. Dodeljuje atributima klase `Settings` vrednosti iz environment-a ili default vrednosti, osiguravajući da su sve konfiguracije validirane pre nego što aplikacija počne sa radom.

---

#### Linija 42: settings = get_settings()

Pravi modulsku instancu konfiguracije koju drugi moduli importuju kao jedinstven izvor istine.

---

### Šta je ovde najvažnije da zapamtiš

1. `load_dotenv()` mora da se desi pre `getenv` čitanja. Ovo osigurava da su sve vrednosti iz `.env` fajla učitane u environment pre nego što ih aplikacija pokuša da pročita.
2. `JWT_SECRET_KEY` je obavezan i nema default (bezbednosno ispravno). On mora biti eksplicitno definisan u environment-u.
3. `JWT_ALGORITHM` i `ACCESS_TOKEN_EXPIRE_MINUTES` mogu imati default. On omogućava aplikaciji da radi sa podrazumevanim vrednostima ako nisu eksplicitno definisane u environment-u.
4. `settings = get_settings()` znači da greške u config-u vidiš odmah pri startu aplikacije za razliku od situacije kada bi se greške pojavile tek tokom runtime-a. Greške se tako detektuju ranije, što olakšava debugging i povećava pouzdanost aplikacije.
5. `frozen=True` sprečava runtime menjanje konfiguracije i povećava predvidljivost. Ovo je posebno korisno u većim aplikacijama gde bi neočekivane promene konfiguracije mogle dovesti do teških za otkrivanje bug-ova.

---

## Pitanje 7

PITANJE: Potrebna mi je detaljna analiza liniju po liniju za `security.py`, isto kao za `config.py`.

---

## Odgovor 7

ODGOVOR: U nastavku je detaljna analiza liniju po liniju za `TodoApp/core/security.py`.

### Ceo kod (referenca)

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from .config import settings


def create_access_token(
   *,  # sve argumente nakon * je potrebno proslediti po imenu (keyword arguments)
   username: str,
   user_id: int,
   expires_delta: timedelta | None = None,
) -> str:
   expire_delta = expires_delta or timedelta(
      minutes=settings.access_token_expire_minutes
   )
   expire = datetime.now(timezone.utc) + expire_delta

   # sub nosi stabilan identitet (user_id), username je pomoćni claim.
   payload: dict[str, Any] = {
      "sub": str(user_id),
      "username": username,
      "exp": expire,
   }

   return jwt.encode(
      payload,
      settings.jwt_secret_key,
      algorithm=settings.jwt_algorithm,
   )
```

### Linija po linija objašnjenje

#### Linija 1: `from datetime import datetime, timedelta, timezone`

Uvozi alate za rad sa vremenom. `timedelta` služi da definišeš koliko token traje, `datetime` i `timezone` da izračunaš tačan UTC trenutak isteka.

---

#### Linija 2: `from typing import Any`

Koristi se za tip `payload` rečnika (`dict[str, Any]`), jer JWT claims mogu imati različite tipove vrednosti (string, datetime, broj).

Linija 3 je prazna.

Stilsko razdvajanje standardnih i third-party importa.

---

#### Linija 4: `from jose import jwt`

Uvozi JWT API iz `python-jose` biblioteke. Ovaj objekat ima `encode` i `decode` funkcije.

---

#### Linija 6: `from .config import settings`

Uvozi centralnu konfiguraciju iz `config.py`. Time `security.py` ne hardkoduje secret ni algorithm, već ih čita iz jednog izvora.

---

#### Linija 9: `def create_access_token(`

Početak helper funkcije koja pravi JWT access token.

---

#### Linija 10: `*,`

Sve argumente posle `*` moraš proslediti po imenu (keyword-only). Ovo je dobra praksa za čitljivost i smanjuje greške pri pozivu.

---

#### Linija 11: `username: str,`

Username koji ubacuješ u payload kao pomoćni claim.

---

#### Linija 12: `user_id: int,`

Stabilan identitet korisnika koji koristiš za `sub` claim.

---

#### Linija 13: `expires_delta: timedelta | None = None,`

Opcioni argument: ako pozivalac ne pošalje custom trajanje, koristi se default iz settings.

---

#### Linija 14: `) -> str:`

Funkcija vraća string, tj. JWT token

---

#### Linije 15-17: `expire_delta = expires_delta or timedelta(...)`

Ako je prosleđen `expires_delta`, koristi njega. Ako nije, pravi `timedelta` iz `settings.access_token_expire_minutes`.

---

#### Linija 18: `expire = datetime.now(timezone.utc) + expire_delta`

Računa tačno vreme isteka koristeći timezone-aware UTC vreme. Ovo je ispravno i modernije od naive pristupa.

---

#### Linija 20 je komentar

Objašnjava dizajn odluku za claim-ove: `sub` nosi stabilan ID, `username` je pomoćna informacija.

---

#### Linija 21: `payload: dict[str, Any] = {`

Početak payload rečnika koji ulazi u JWT.

---

#### Linija 22: `"sub": str(user_id),`

Najvažniji claim identiteta. `user_id` se pretvara u string radi doslednosti JWT claim formata.

---

#### Linija 23: `"username": username,`

Dodatni claim koristan za debug ili prikaz, ali ne treba da bude jedini identitet.

---

#### Linija 24: `"exp": expire,`

Claim isteka. Biblioteka će ovaj datetime obraditi u JWT-compatible format.

--

#### Linija 25: `}`

Kraj payload rečnika.

---

#### Linije 27-31: `return jwt.encode(...)`

Kreira i vraća potpisan JWT string. Argument 1 je `payload`, argument 2 je secret (`settings.jwt_secret_key`), a `algorithm` uzimaš iz settings (`settings.jwt_algorithm`).

---

### Zašto je ovaj helper dobar za tvoj trenutni projekat

1. Kompatibilan je sa trenutnim (legacy) SQLAlchemy stilom, jer ne menja ORM pattern.
2. Uklanja hardkodovane tajne iz route fajla.
3. Drži JWT logiku izolovanu u `core/security.py`, što olakšava sledeći korak (decode/current user).
4. Koristi UTC-aware vreme i centralizovanu konfiguraciju, što je pouzdanije za produkcijski tok.

---

### Najvažnije da zapamtiš

1. `settings` dolazi iz config sloja i mora biti validan pri startu aplikacije.
2. `sub` je najvažniji identitetski claim i treba da ostane dosledan i u decode fazi.
3. `exp` mora postojati da token ne bi bio praktično "beskonačan".
4. `jwt.encode(...)` ne enkriptuje payload; on ga potpisuje. Zato nikad ne stavljaj osetljive podatke u claims.

---
