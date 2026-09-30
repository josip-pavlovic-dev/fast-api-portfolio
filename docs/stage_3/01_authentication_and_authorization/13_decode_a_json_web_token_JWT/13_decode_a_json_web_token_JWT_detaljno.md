# Oblast 03 - Authentication and Authorization

## Lekcija 13 - Dekodiranje i validacija JWT-a

Prethodna lekcija je kreirala JWT nakon uspešnog login-a.

Sada aplikacija treba da proveri token koji klijent šalje uz protected request:

```text
klijent salje Authorization: Bearer <jwt>
    -> FastAPI izdvaja token
        -> server dekodira token
            -> proverava signature i claims
                -> dobija current user
```

Dekodiranje nije samo čitanje `payload`-a. Pravo dekodiranje u autentifikacionom kontekstu treba da potvrdi da je token validan, da nije izmenjen i da nije istekao.

---

## 1) Zasto se JWT dekodira

Kada korisnik uspešno izvrši `login`, server mu vrati `JWT`.

Pri sledećem zahtevu klijent šalje `token`, na primer:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Server mora da proveri:

- da li token ima ispravnu strukturu (`header.payload.signature`)
- da li je signature napravljen odgovarajućim `secret key`-em (server zna taj ključ)
- da li je korišćen dozvoljeni algoritam (`alg` u header-u)
- da li token nije istekao (`exp` claim)
- da li `payload` sadrži potrebne `claims` (npr. `sub` za identifikaciju korisnika)
- ko je korisnik predstavljen tokenom (`sub` claim)

Ako provera uspe, server može da napravi `current user` kontekst.

Ako provera ne uspe, `protected endpoint` ne treba da nastavi obradu. U tom slučaju server obično vraća `HTTP 401 Unauthorized`.

---

## 2) `OAuth2PasswordBearer`

Transkript uvodi:

```python
from fastapi.security import OAuth2PasswordBearer
```

Zatim pravi dependency:

```python
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="token",
)
```

U tvom projektu, ako auth router koristi prefix `/auth`, jasnija vrednost može biti:

```python
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
)
```

Tačna vrednost treba da odgovara javnoj putanji token endpointa i OpenAPI konfiguraciji.

### Šta ovaj objekat radi

`OAuth2PasswordBearer`:

1. čita `Authorization` header
2. očekuje scheme `Bearer`
3. izdvaja samo token string
4. ako header nedostaje ili je pogrešan, pokreće HTTP 401

On ne proverava sam JWT signature. On samo pribavlja Bearer token koji sledeći security helper treba da dekodira.

To je važna razlika:

```text
OAuth2PasswordBearer
    -> izdvaja token iz header-a

jwt.decode
    -> validira token i cita payload
```

---

## 3) Gde se dependency smesta u tvom projektu

Kursni primer može držati `oauth2_bearer` u `auth.py`.

U tvom ciljanom rasporedu moguće su dve faze:

### Početna kursna faza

```text
TodoApp/api/routes/auth.py
    oauth2_bearer
    get_current_user
    auth endpointi
```

---

### Organizovanija faza

```text
TodoApp/core/security.py
    oauth2_bearer
    decode helper
    current user security helper

TodoApp/api/routes/auth.py
    /token endpoint

TodoApp/api/routes/todos.py
    koristi current user dependency
```

Pošto je `get_current_user` security dependency, dugoročno pripada security sloju, a ne poslovnoj Todo logici.

---

## 4) `tokenUrl` nije secret i nije validacija

U izrazu:

```python
OAuth2PasswordBearer(tokenUrl="auth/token")
```

`tokenUrl` opisuje gde klijent dobija token tj. na koji `endpoint` treba da pošalje svoje kredencijale (`username` i `password`).

On nije:

- secret key
- URL koji server posebnim pozivom proverava
- zamena za JWT decode

Njegova glavna uloga je da `FastAPI/OpenAPI` zna koji `endpoint` predstavlja `OAuth2 token endpoint`.

Ako koristiš router prefix:

```python
router = APIRouter(prefix="/auth")
```

i lokalnu rutu:

```python
@router.post("/token")
```

javna putanja je:

```text
/auth/token
```

`tokenUrl` treba uskladiti sa tim javnim API ugovorom.

---

## 5) `get_current_user()` nije API endpoint

Transkript pravi funkciju:

```python
async def get_current_user(token: str = Depends(oauth2_bearer)):
    ...
```

Ona nema dekorator poput:

```python
@router.get(...)
```

Zato nije samostalna ruta. To je `dependency` koju druge rute koriste:

```python
@router.get("/protected")
async def protected_route(
    current_user: CurrentUser = Depends(get_current_user),
):
    ...
```

Njena odgovornost je:

```text
Bearer token -> validiran current user identitet
```

Ne treba da sadrži `Todo query logiku`. Todo router kasnije koristi rezultat dependency-ja.

---

## 6) Tipiziranje token dependency-ja

Transkript koristi obrazac sličan:

```python
token: Annotated[str, Depends(oauth2_bearer)]
```

Značenje:

```text
token
    Python vrednost tipa string

Depends(oauth2_bearer)
    FastAPI treba da je dobavi iz Bearer header-a
```

Posle rešavanja dependency-ja, `token` sadrži samo JWT string, bez prefiksa:

```text
Authorization header:
Bearer eyJ...

vrednost token promenljive:
eyJ...
```

U tvom projektu se može koristiti postojeći `Annotated` stil iz `db/session.py`. Tada bi deklaracija token dependency-ja mogla izgledati ovako:

```python
token: Annotated[str, Depends(oauth2_bearer)]
```

Ovo je način da se jasno naznači da `token` dolazi iz Bearer header-a i da je tipiziran kao string.

---

## 7) `jwt.decode()`

Kada dobijemo token, dekodiranje konceptualno izgleda ovako:

```python
payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=[ALGORITHM],
)
```

Argumenti su:

```text
token
    Bearer JWT string

SECRET_KEY
    server secret za proveru potpisa

algorithms
    dozvoljena lista algoritama
```

### Važna napomena o `algorithms`

Decode kod treba eksplicitno da navede dozvoljene algoritme:

```python
algorithms=["HS256"]
```

Ne treba nekritički verovati algoritmu koji je token sam naveo u header-u.

Server zna koji algoritam očekuje kroz konfiguraciju.

---

## 8) Šta `jwt.decode()` proverava

U zavisnosti od biblioteke i podešavanja, `decode validacija` može proveriti:

- da li je JWT struktura ispravna (header.payload.signature)
- da li signature odgovara secret key-u (provera potpisa)
- da li je algoritam dozvoljen (u odnosu na listu `algorithms` prosleđenu `jwt.decode()`)
- da li je `exp` prošao (da li je token istekao)
- eventualno `iss`, `aud` ili druge claims ako ih konfigurišeš

Ako neko promeni `payload` bez validnog `potpisa`, decode treba da `padne`.

Ako token istekne, decode treba da odbije token. Ovo znači da će biblioteka podići izuzetak ili vratiti grešku prilikom pokušaja dekodiranja.

Ako se koristi pogrešan `secret`, `signature` neće odgovarati.

---

## 9) Čitanje claims-a iz `payload`-a

Posle uspešnog decode-a, `payload` je rečnik:

```python
payload = {
    "sub": "ana",
    "id": 1,
    "exp": 1780000000,
}
```

Claims se čitaju ovako:

```python
username = payload.get("sub")
user_id = payload.get("id")
```

U modernijem doslednom obliku možemo koristiti:

```python
subject = payload.get("sub")
```

gde je `subject` stabilan user ID.

Ne treba pretpostaviti da claim postoji samo zato što je token potpisan. Token može biti validno potpisan, ali pogrešno ili nepotpuno napravljen.

Zato se proverava:

```python
if username is None or user_id is None:
    raise HTTPException(...)
```

---

## 10) Zašto se proveravaju `sub` i `id`

Validan `signature` znači da token nije menjan od strane nekoga ko ne zna secret.

Ali server i dalje treba da proveri da li token ima podatke koje aplikacija zahteva.

Na primer, token sa payload-om:

```json
{
  "exp": 1780000000
}
```

Može imati validan `signature`, ali nema identitet korisnika.

Takav token ne treba koristiti za `current user logiku`.

Provera `claims`-a ima dva nivoa:

```text
kriptografska validacija
    signature, algorithm, expiration

aplikaciona validacija
    sub/id postoje i imaju prihvatljiv oblik
```

---

## 11) HTTP 401 za nevalidne kredencijale

Transkript koristi:

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)
```

HTTP 401 znači da zahtev nema validne autentifikacione kredencijale.

To može biti:

- nedostajući Bearer token
- pogrešan token
- istekao token
- pogrešan secret
- promenjen payload
- nedostajući obavezni claim

Za Bearer autentifikaciju koristan je i header:

```python
headers={"WWW-Authenticate": "Bearer"}
```

### 401 naspram 403

```text
401 Unauthorized
    identitet nije validno potvrđen

403 Forbidden
    identitet je poznat, ali nema potrebnu dozvolu
```

Primer:

```text
nevalidan JWT -> 401
validan user token, ali user nije admin -> 403
```

---

## 12) `JWTError`

Dekodiranje može baciti JWT-specificnu grešku:

```python
from jose import JWTError
```

Zato se koristi:

```python
try:
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
except JWTError:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

Ne treba korisniku vraćati detalje poput:

```text
signature mismatch at byte ...
```

Generički odgovor smanjuje otkrivanje internih detalja.

Interni log može imati više informacija, ali ne treba logovati ceo token ili secret.

---

## 13) Konceptualni `get_current_user()` helper

Kursni oblik je sličan:

```python
async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
            )

        return {
            "username": username,
            "id": user_id,
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )
```

Za organizovaniji tvoj projekat helper bi dugoročno bio u:

```text
TodoApp/core/security.py
```

A `auth.py` i `todos.py` bi ga importovali.

---

## 14) Pažnja na `HTTPException` unutar `try` bloka

Ako se `HTTPException` podigne zbog nedostajućeg claim-a unutar `try` bloka, siroki `except JWTError` je neće uhvatiti jer `HTTPException` nije `JWTError`.

Ipak, čitljiviji oblik može odvojiti `decode` od provere `claims`-a:

```python
try:
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
except JWTError as error:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ) from error

subject = payload.get("sub")
user_id = payload.get("id")

if subject is None or user_id is None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

Ovo jasnije razdvaja:

```text
kriptografski problem
    -> JWTError

nepotpun payload
    -> aplikaciona HTTPException
```

---

## 15) Current user objekat

`get_current_user()` moze vratiti recnik:

```python
return {
    "username": username,
    "id": user_id,
}
```

Sledeci endpoint ga koristi:

```python
@router.get("/todo")
async def read_my_todos(
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    ...
```

Kasnije može postojati Pydantic ili typed struktura za current user kontekst.

Rečnik je jednostavan za kurs, ali typed objekat može smanjiti greške u većem projektu.

Važno je da current user rezultat predstavlja server-verifikovan identitet, a ne proizvoljan `user_id` iz URL-a.

---

## 16) Kako Todo endpoint koristi current user

Budući `Todo` query:

```python
@router.get("/todo")
async def read_my_todos(
    db: db_dependency,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]

    return (
        db.query(Todos)
        .filter(Todos.owner_id == user_id)
        .all()
    )
```

Tok je:

```text
Authorization header
    -> OAuth2PasswordBearer
        -> get_current_user
            -> validiran user ID
                -> Todos.owner_id filter
```

Ne treba prihvatati proizvoljan `user_id` samo zato što se nalazi u URL-u.

---

## 17) `sub` i `id` moraju biti dosledni

Ako encoding funkcija pravi:

```python
payload = {
    "sub": username,
    "id": user_id,
}
```

decode funkcija mora čitati:

```python
username = payload.get("sub")
user_id = payload.get("id")
```

Ako se kasnije promeni payload u:

```python
payload = {
    "sub": str(user_id),
    "username": username,
}
```

decode kod mora koristiti:

```python
user_id = payload.get("sub")
username = payload.get("username")
```

Encode i decode nisu nezavisne funkcije. One dele API ugovor o claims-ima.

Promena naziva claim-a zahteva promenu svih potrošača tokena i može invalidirati stare tokene.

---

## 18) Validacija tipova claims-a

`payload.get("id")` može vratiti:

- `None`
- string
- broj
- neočekivanu vrednost (npr. listu ili dict)

Zato se u ozbiljnijem kodu proverava i tip ili se koristi standardizovani `claim` format.

Primer:

```python
user_id = payload.get("sub")

if not isinstance(user_id, str) or not user_id:
    raise HTTPException(...)
```

Ako se ID pretvara u integer:

```python
try:
    user_id = int(user_id)
except (TypeError, ValueError) as error:
    raise HTTPException(...) from error
```

Ovo je **aplikaciona validacija** nakon JWT signature provere.

---

## 19) Secret i algorithm pri dekodiranju

Za dekodiranje se moraju koristiti isti konfiguracioni parametri kao pri encoding-u:

```text
encode secret = decode secret
encode algorithm = dozvoljeni decode algorithm
```

Ako se secret promeni:

```text
stari tokeni -> nevalidni
```

To može biti namerna rotacija ključa, ali zahteva plan za aktivne tokene.

U tvom projektu parametri pripadaju:

```text
TodoApp/core/config.py
```

Ne treba ih duplirati u više router fajlova jer se mogu razlikovati i izazvati teško uočljive greške.

---

## 20) Šta ova lekcija jos ne implementira

Ova lekcija još ne dodaje stvarnu zaštitu Todo endpointa.

Ne implementira još:

- `get_current_user` u aktivnom kodu (dependency)
- `OAuth2PasswordBearer` dependency u projektu (npr. `oauth2_bearer`)
- user lookup iz baze nakon decode-a (npr. `get_user_by_id(user_id)`)
- proveru da korisnik i dalje postoji (npr. `get_user_by_id(user_id)`)
- proveru `is_active` u current user dependency-ju (npr. `get_current_user`)
- role autorizaciju (npr. `get_current_user`)
- ownership filter u stvarnom routeru (npr. `Todos.owner_id`)
- refresh token (npr. `refresh_access_token`)

Ona priprema centralni security korak:

```text
Bearer token -> validiran current user identitet
```

---

## 21) Budući raspored fajlova

Ciljni raspored za kasniju implementaciju:

```text
TodoApp/
    main.py
    models.py
    schemas.py
    api/
        routes/
            auth.py
            todos.py
    core/
        config.py
        security.py
    db/
        session.py
```

### `core/config.py`

- secret key (npr. `SECRET_KEY`)
- algorithm (npr. `ALGORITHM`)
- token expiration (npr. `ACCESS_TOKEN_EXPIRE_MINUTES`)

---

### `core/security.py`

- `oauth2_bearer` (npr. `OAuth2PasswordBearer(tokenUrl="token")`)
- `get_current_user` (npr. `def get_current_user(token: str = Depends(oauth2_bearer))`)
- JWT decode helper (npr. `def decode_jwt(token: str) -> dict`)
- password helperi (npr. `def verify_password(plain_password: str, hashed_password: str) -> bool`)

---

### `api/routes/auth.py`

- `/token`
- register i login token endpoints

---

### `api/routes/todos.py`

- dependency injection current user-a (npr. `get_current_user`)
- owner filteri (npr. `Todos.owner_id`)

---

### `db/session.py`

- DB session dependency (npr. `def get_db() -> Session`)

---

### `models.py`

- `Users` (npr. `Users.id`, `Users.username`)
- `Todos.owner_id` (npr. `Todos.owner_id`)

---

## 22) Pitanja za proveru znanja

1. Zašto se JWT dekodira pri svakom protected request-u?

ODGOVOR: JWT se dekodira pri svakom protected request-u kako bi se validirao identitet korisnika i osiguralo da token nije istekao ili izmenjen. Na taj način se obezbeđuje sigurnost i integritet aplikacije.

2. Šta radi `OAuth2PasswordBearer`?

ODGOVOR: `OAuth2PasswordBearer` je dependency koji izvlači Bearer token iz Authorization header-a i prosleđuje ga dalje u funkcije koje ga zavise. Sam po sebi ne proverava validnost tokena.

3. Da li `OAuth2PasswordBearer` proverava JWT signature?

ODGOVOR: Ne, `OAuth2PasswordBearer` samo izvlači token iz header-a. Validacija tokena, uključujući proveru signature-a, se obavlja kasnije, obično u `get_current_user` funkciji.

4. Šta je uloga `tokenUrl` parametra?

ODGOVOR: `tokenUrl` parametar specificira URL endpoint-a na koji klijent treba da pošalje korisničke kredencijale kako bi dobio JWT token. FastAPI koristi ovaj URL za generisanje OpenAPI dokumentacije i za interaktivni Swagger UI.

5. Zašto `get_current_user()` nije API endpoint?

ODGOVOR: `get_current_user()` je dependency koji se koristi unutar drugih API endpoint-a kako bi se dobio trenutno ulogovani korisnik. Nije samostalni endpoint jer ne odgovara direktno na HTTP zahteve, već služi kao pomoćna funkcija za autorizaciju.

6. Šta radi `jwt.decode()`?

ODGOVOR: `jwt.decode()` uzima JWT token, secret i listu dozvoljenih algoritama, i vraća dekodirane claims ako je token validan. Ako je token nevalidan ili je istekao, baca izuzetak (`JWTError`).

7. Zašto decode mora dobiti secret i listu dozvoljenih algoritama?

ODGOVOR: `jwt.decode()` mora dobiti secret kako bi mogao da proveri signature tokena i osigura da token nije izmenjen. Lista dozvoljenih algoritama je potrebna da bi se sprečile sigurnosne ranjivosti povezane sa neautorizovanim algoritmima.

8. Šta se dešava ako je signature nevalidan?

ODGOVOR: Ako je signature nevalidan, `jwt.decode()` će baciti izuzetak (`JWTError`), što znači da token nije validan i ne može se koristiti za autentifikaciju.

9. Šta je `JWTError`?

ODGOVOR: `JWTError` je izuzetak koji se baca kada dođe do problema sa JWT tokenom, kao što su nevalidan signature, istekao token ili neispravan format tokena. Ovaj izuzetak omogućava aplikaciji da pravilno reaguje na nevalidne ili neupotrebljive tokene.

10. Zašto se proveravaju `sub` i `id` claims nakon decode-a?

ODGOVOR: Nakon što se JWT dekodira, proveravaju se `sub` i `id` claims kako bi se osiguralo da token sadrži identitet korisnika. Ovo je važno jer validan token sa ispravnim potpisom ne garantuje da token sadrži sve potrebne informacije za autorizaciju korisnika.

11. Šta znači HTTP 401?

ODGOVOR: HTTP 401 Unauthorized znači da korisnik nije autentifikovan ili da je autentifikacija neuspešna. Server odbija zahtev jer ne može da potvrdi identitet korisnika.

12. Koja je razlika između 401 i 403?

ODGOVOR: HTTP 401 Unauthorized znači da korisnik nije autentifikovan ili da je autentifikacija neuspešna, dok HTTP 403 Forbidden znači da je korisnik autentifikovan, ali nema dozvolu za pristup traženom resursu. U suštini, 401 se odnosi na problem sa autentifikacijom, a 403 na problem sa autorizacijom.

13. Zašto encode i decode moraju deliti isti claims ugovor?

ODGOVOR: Encode i decode moraju deliti isti claims ugovor kako bi se osiguralo da token sadrži sve potrebne informacije za autentifikaciju i autorizaciju korisnika. Ako encode i decode ne koriste isti ugovor, dekodirani token može biti nepotpun ili neupotrebljiv, što može dovesti do grešaka u aplikaciji.

14. Gde se u tvom projektu nalazi buduca security logika?

ODGOVOR: Buduća security logika se obično nalazi u sloju aplikacije koji obrađuje autentifikaciju i autorizaciju korisnika, kao što su rute, dependency-ji za dobijanje trenutnog korisnika i middleware koji proverava pristupne tokene.

15. Kako current user ID kasnije filtrira `Todos.owner_id`?

ODGOVOR: Current user ID se koristi za filtriranje `Todos.owner_id` kako bi se osiguralo da korisnik može pristupiti samo svojim zadacima. Ovo je deo autorizacione logike koja povezuje identitet korisnika sa resursima kojima može pristupiti.

16. Zašto token sa validnim potpisom ipak može biti aplikaciono neupotrebljiv?

ODGOVOR: Token sa validnim potpisom može biti aplikaciono neupotrebljiv ako ne sadrži sve potrebne claims, kao što su `sub` ili `id`. Iako je token kriptografski validan, aplikacija ne može da identifikuje korisnika ili da pravilno primeni autorizaciju bez ovih informacija.

---

## 23) Praktični zadaci

### Zadatak 1 - Rastavi Authorization header

Za header:

```http
Authorization: Bearer abc.def.ghi
```

oznaci:

- naziv header-a
- authentication scheme
- token vrednost

### Zadatak 2 - Razvrstaj odgovornosti

Popuni:

```text
OAuth2PasswordBearer ->
jwt.decode         ->
get_current_user   ->
Todo owner filter  ->
```

Objasni zasto nijedan od ovih koraka sam nije cela authorization logika.

### Zadatak 3 - Napisi decode tok

Nacrtaj:

```text
Bearer token
    -> OAuth2PasswordBearer
        -> jwt.decode
            -> claims provera
                -> current user
```

Uz svaki korak dodaj moguci neuspeh.

### Zadatak 4 - Prepoznaj nevalidan payload

Analiziraj payload:

```json
{
  "exp": 1780000000
}
```

Objasni zasto validan signature nije dovoljan ako nema identiteta korisnika.

### Zadatak 5 - Poredjaj status kodove

Povezi scenario sa statusom:

```text
nema Bearer tokena
nevalidan ili istekao token
validan user token na admin ruti
validan admin token
```

Koristi:

```text
401
403
200
```

### Zadatak 6 - Uporedi claims ugovor

Encode koristi:

```python
{"sub": username, "id": user_id}
```

Decode ocekuje:

```python
payload.get("sub")
payload.get("user_id")
```

Pronadji problem i objasni posledicu.

### Zadatak 7 - Napisi bezbedan error plan

Za svaki scenario napisi genericki odgovor:

- pogresan secret
- izmenjen payload
- istekao token
- nedostaje `sub`
- nedostaje `id`

Objasni zasto klijentu ne treba vracati interne detalje signature greske.

### Zadatak 8 - Povezi fajlove

Odredi lokaciju:

```text
oauth2_bearer
get_current_user
jwt.decode helper
secret i algorithm
Todo ownership query
```

Koristi:

```text
TodoApp/core/security.py
TodoApp/core/config.py
TodoApp/api/routes/todos.py
```

### Zadatak 9 - URL user ID naspram current user ID

Uporedi:

```python
user_id = path_user_id
```

```python
user_id = current_user["id"]
```

Objasni koji pristup se koristi za bezbedan ownership filter i zasto.

### Zadatak 10 - Plan protected endpointa

Napisi plan za buduci `GET /todo` endpoint:

1. Bearer token dependency
2. current user dependency
3. validacija tokena
4. dobijanje user ID-a
5. DB query po `owner_id`
6. response

Ne menjaj aktivni kod.

---

## 24) Zakljucak

Dekodiranje JWT-a je centralni korak za proveru tokena na protected endpointima.

Osnovni tok je:

```text
Authorization: Bearer <jwt>
    -> OAuth2PasswordBearer
        -> jwt.decode(token, secret, algorithms)
            -> proveri claims
                -> current user
```

Za tvoj projekat:

- `OAuth2PasswordBearer` i current user logika pripadaju budućem security sloju
- ciljna lokacija je `TodoApp/core/security.py`
- secret i algorithm pripadaju `TodoApp/core/config.py`
- auth endpoint ostaje u `TodoApp/api/routes/auth.py`
- Todo router kasnije koristi current user dependency
- `db/session.py` ostaje mesto za DB dependency
- `Todos.owner_id` se filtrira tek posle validacije identiteta

Najvaznije je zapamtiti:

> Citati payload nije isto sto i validirati token.

Server mora proveriti signature, algorithm, expiration i potrebne claims pre nego sto identitet tokena koristi za authorization odluke.

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
