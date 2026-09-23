# Oblast 03 - Authentication and Authorization

## Lekcija 13 - Dekodiranje i validacija JWT-a

Prethodna lekcija je kreirala JWT nakon uspesnog login-a.

Sada aplikacija treba da proveri token koji klijent salje uz protected request:

```text
klijent salje Authorization: Bearer <jwt>
    -> FastAPI izdvaja token
        -> server dekodira token
            -> proverava signature i claims
                -> dobija current user
```

Dekodiranje nije samo citanje payload-a. Pravo dekodiranje u autentifikacionom kontekstu treba da potvrdi da je token validan, da nije izmenjen i da nije istekao.

### Vazna napomena za trenutni plan

Ovo je teorijski materijal. Ne menjamo aktivne Python fajlove, ne dodajemo OAuth2 dependency u routere i ne instaliramo pakete dok ne zavrsimo teoriju cele oblasti.

---

## 1) Zasto se JWT dekodira

Kada korisnik uspesno izvrsi login, server mu vrati JWT.

Pri sledecem zahtevu klijent salje token, na primer:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Server mora da proveri:

- da li token ima ispravnu strukturu
- da li je signature napravljen odgovarajucim secret key-em
- da li je koriscen dozvoljeni algoritam
- da li token nije istekao
- da li payload sadrzi potrebne claims
- ko je korisnik predstavljen tokenom

Ako provera uspe, server moze da napravi current user kontekst.

Ako provera ne uspe, protected endpoint ne treba da nastavi obradu.

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

U tvom projektu, ako auth router koristi prefix `/auth`, jasnija vrednost moze biti:

```python
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
)
```

Tacna vrednost treba da odgovara javnoj putanji token endpointa i OpenAPI konfiguraciji.

### Sta ovaj objekat radi

`OAuth2PasswordBearer`:

1. cita `Authorization` header
2. ocekuje scheme `Bearer`
3. izdvaja samo token string
4. ako header nedostaje ili je pogresan, pokrece HTTP 401

On ne proverava sam JWT signature. On samo pribavlja Bearer token koji sledeci security helper treba da dekodira.

To je vazna razlika:

```text
OAuth2PasswordBearer
    -> izdvaja token iz header-a

jwt.decode
    -> validira token i cita payload
```

---

## 3) Gde se dependency smesta u tvom projektu

Kursni primer moze drzati `oauth2_bearer` u `auth.py`.

U tvom ciljanom rasporedu moguce su dve faze:

### Pocetna kursna faza

```text
TodoApp/api/routes/auth.py
    oauth2_bearer
    get_current_user
    auth endpointi
```

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

Pošto je `get_current_user` security dependency, dugorocno pripada security sloju, a ne poslovnoj Todo logici.

---

## 4) `tokenUrl` nije secret i nije validacija

U izrazu:

```python
OAuth2PasswordBearer(tokenUrl="auth/token")
```

`tokenUrl` opisuje gde klijent dobija token.

On nije:

- secret key
- URL koji server posebnim pozivom proverava
- zamena za JWT decode

Njegova glavna uloga je da FastAPI/OpenAPI zna koji endpoint predstavlja OAuth2 token endpoint.

Ako koristis router prefix:

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

Zato nije samostalna ruta. To je dependency koju druge rute koriste:

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

Ne treba da sadrzi Todo query logiku. Todo router kasnije koristi rezultat dependency-ja.

---

## 6) Tipiziranje token dependency-ja

Transkript koristi obrazac slican:

```python
token: Annotated[str, Depends(oauth2_bearer)]
```

Znacenje:

```text
token
    Python vrednost tipa string

Depends(oauth2_bearer)
    FastAPI treba da je dobavi iz Bearer header-a
```

Posle resavanja dependency-ja, `token` sadrzi samo JWT string, bez prefiksa:

```text
Authorization header:
Bearer eyJ...

vrednost token promenljive:
eyJ...
```

U tvom projektu moze se koristiti postojeci `Annotated` stil iz `db/session.py`.

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

### Vazna napomena o `algorithms`

Decode kod treba eksplicitno da navede dozvoljene algoritme:

```python
algorithms=["HS256"]
```

Ne treba nekriticki verovati algoritmu koji je token sam naveo u header-u.

Server zna koji algoritam ocekuje kroz konfiguraciju.

---

## 8) Sta `jwt.decode()` proverava

U zavisnosti od biblioteke i podesavanja, decode validacija moze proveriti:

- da li je JWT struktura ispravna
- da li signature odgovara secret key-u
- da li je algoritam dozvoljen
- da li je `exp` prosao
- eventualno `iss`, `aud` ili druge claims ako ih konfigurises

Ako neko promeni payload bez validnog potpisa, decode treba da padne.

Ako token istekne, decode treba da odbije token.

Ako se koristi pogresan secret, signature nece odgovarati.

---

## 9) Citanje claims-a iz payload-a

Posle uspesnog decode-a, `payload` je recnik:

```python
payload = {
    "sub": "ana",
    "id": 1,
    "exp": 1780000000,
}
```

Claims se citaju ovako:

```python
username = payload.get("sub")
user_id = payload.get("id")
```

U modernijem doslednom obliku mozemo koristiti:

```python
subject = payload.get("sub")
```

gde je `subject` stabilan user ID.

Ne treba pretpostaviti da claim postoji samo zato sto je token potpisan. Token moze biti validno potpisan, ali pogresno ili nepotpuno napravljen.

Zato se proverava:

```python
if username is None or user_id is None:
    raise HTTPException(...)
```

---

## 10) Zasto se proveravaju `sub` i `id`

Validan signature znaci da token nije menjan od strane nekoga ko ne zna secret.

Ali server i dalje treba da proveri da li token ima podatke koje aplikacija zahteva.

Na primer, token sa payload-om:

```json
{
  "exp": 1780000000
}
```

moze imati validan signature, ali nema identitet korisnika.

Takav token ne treba koristiti za current user logiku.

Provera claims-a ima dva nivoa:

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

HTTP 401 znaci da zahtev nema validne autentifikacione kredencijale.

To moze biti:

- nedostajuci Bearer token
- pogresan token
- istekao token
- pogresan secret
- promenjen payload
- nedostajuci obavezni claim

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

Dekodiranje moze baciti JWT-specificnu gresku:

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

Ne treba korisniku vracati detalje poput:

```text
signature mismatch at byte ...
```

Genericki odgovor smanjuje otkrivanje internih detalja.

Interni log moze imati vise informacija, ali ne treba logovati ceo token ili secret.

---

## 13) Konceptualni `get_current_user()` helper

Kursni oblik je slican:

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

Za organizovaniji tvoj projekat helper bi dugorocno bio u:

```text
TodoApp/core/security.py
```

A `auth.py` i `todos.py` bi ga importovali.

---

## 14) Paznja na `HTTPException` unutar `try` bloka

Ako se `HTTPException` podigne zbog nedostajuceg claim-a unutar `try` bloka, siroki `except JWTError` je nece uhvatiti jer `HTTPException` nije `JWTError`.

Ipak, citljiviji oblik moze odvojiti decode od provere claims-a:

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

Kasnije moze postojati Pydantic ili typed struktura za current user kontekst.

Recnik je jednostavan za kurs, ali typed objekat moze smanjiti greske u vecem projektu.

Vazno je da current user rezultat predstavlja server-verifikovan identitet, a ne proizvoljan `user_id` iz URL-a.

---

## 16) Kako Todo endpoint koristi current user

Buduci Todo query:

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

Ne treba prihvatati proizvoljan `user_id` samo zato sto se nalazi u URL-u.

---

## 17) `sub` i `id` moraju biti dosledni

Ako encoding funkcija pravi:

```python
payload = {
    "sub": username,
    "id": user_id,
}
```

decode funkcija mora citati:

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

Promena naziva claim-a zahteva promenu svih potrosaca tokena i moze invalidirati stare tokene.

---

## 18) Validacija tipova claims-a

`payload.get("id")` moze vratiti:

- `None`
- string
- broj
- neocekivanu vrednost

Zato se u ozbiljnijem kodu proverava i tip ili se koristi standardizovani claim format.

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

Ovo je aplikaciona validacija nakon JWT signature provere.

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

To moze biti namerna rotacija kljuca, ali zahteva plan za aktivne tokene.

U tvom projektu parametri pripadaju:

```text
TodoApp/core/config.py
```

Ne treba ih duplirati u vise router fajlova jer se mogu razlikovati i izazvati tesko uocljive greske.

---

## 20) Sta ova lekcija jos ne implementira

Ova lekcija jos ne dodaje stvarnu zastitu Todo endpointa.

Ne implementira jos:

- `get_current_user` u aktivnom kodu
- `OAuth2PasswordBearer` dependency u projektu
- user lookup iz baze nakon decode-a
- proveru da korisnik i dalje postoji
- proveru `is_active` u current user dependency-ju
- role authorization
- ownership filter u stvarnom routeru
- refresh token

Ona priprema centralni security korak:

```text
Bearer token -> validiran current user identitet
```

---

## 21) Buduci raspored fajlova

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

- secret key
- algorithm
- token expiration

### `core/security.py`

- `oauth2_bearer`
- `get_current_user`
- JWT decode helper
- password helperi

### `api/routes/auth.py`

- `/token`
- register i login tok

### `api/routes/todos.py`

- dependency injection current user-a
- owner filteri

### `db/session.py`

- DB session dependency

### `models.py`

- `Users`
- `Todos.owner_id`

---

## 22) Pitanja za proveru znanja

1. Zasto se JWT dekodira pri svakom protected request-u?
2. Sta radi `OAuth2PasswordBearer`?
3. Da li `OAuth2PasswordBearer` proverava JWT signature?
4. Sta je uloga `tokenUrl` parametra?
5. Zasto `get_current_user()` nije API endpoint?
6. Sta radi `jwt.decode()`?
7. Zasto decode mora dobiti secret i listu dozvoljenih algoritama?
8. Sta se desava ako je signature nevalidan?
9. Sta je `JWTError`?
10. Zasto se proveravaju `sub` i `id` claims nakon decode-a?
11. Sta znaci HTTP 401?
12. Koja je razlika izmedju 401 i 403?
13. Zasto encode i decode moraju deliti isti claims ugovor?
14. Gde se u tvom projektu nalazi buduca security logika?
15. Kako current user ID kasnije filtrira `Todos.owner_id`?
16. Zasto token sa validnim potpisom ipak moze biti aplikaciono neupotrebljiv?

---

## 23) Prakticni zadaci

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
