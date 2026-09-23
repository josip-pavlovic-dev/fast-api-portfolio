# Oblast 03 - Authentication and Authorization

## Lekcija 12 - Kreiranje, odnosno encoding JWT-a

Prethodna lekcija je objasnila strukturu JWT-a. Sada se ta ideja pretvara u tok aplikacije:

```text
uspesna autentifikacija
    -> korisnik je pronadjen
    -> password je validan
        -> napravi JWT
            -> vrati access token klijentu
```

Ova lekcija se fokusira na **encoding**, odnosno kreiranje potpisanog JWT stringa.

U transkriptu se uvode:

- `python-jose[cryptography]`
- secret key
- algoritam `HS256`
- funkcija `create_access_token`
- claims `sub`, `id` i `exp`
- `Token` response schema

### Vazna napomena za trenutni plan

Ovo je teorijski materijal. Ne instaliramo pakete, ne menjamo `requirements.txt`, ne dodajemo secret u kod i ne menjamo aktivne Python fajlove.

---

## 1) Gde se buduci kod smesta u tvom projektu

Kursni kod moze drzati sve u `auth.py`, ali tvoj organizovaniji raspored treba da razdvoji odgovornosti:

```text
fast-api-course-my-work/
    TodoApp/
        main.py
        models.py
        schemas.py
        api/
            routes/
                auth.py
        core/
            config.py
            security.py
        db/
            session.py
```

Buduca podela:

```text
TodoApp/core/config.py
    secret key
    JWT algorithm
    expiration podesavanja

TodoApp/core/security.py
    encode helper
    decode helper
    password security helperi

TodoApp/api/routes/auth.py
    /token endpoint
    authenticate_user poziv
    poziv create_access_token

TodoApp/schemas.py
    Token response schema

TodoApp/db/session.py
    db_dependency
```

Za teorijsko pracenje transkripta primeri ce ponekad biti prikazani zajedno, ali je ciljna lokacija za tvoj projekat ovako podeljena.

---

## 2) Instalacija JWT biblioteke

Transkript uvodi paket komandom slicnom:

```bash
pip install "python-jose[cryptography]"
```

`python-jose` pruza funkcije za JWT encoding i decoding.

Dodatak:

```text
[cryptography]
```

oznacava extra dependency-je potrebne za kriptografske funkcije.

U requirements fajlu se konceptualno moze zapisati:

```text
python-jose[cryptography]
```

To je runtime dependency jer aplikacija koristi JWT dok radi.

### Vazna napomena

Ne instaliramo paket sada. Kada dodjemo do prakticnog rada, proverice se:

- postojeci virtual environment
- verzija Python-a
- ostatak requirements fajla
- verzija biblioteke
- eventualne kompatibilnosti

---

## 3) Secret key

JWT sa HS256 algoritmom koristi secret key za potpisivanje.

Konceptualno:

```python
SECRET_KEY = "dugacak-tajan-string"
```

Secret treba da bude:

- dovoljno dugacak
- nasumican
- nepredvidiv
- razlicit izmedju okruzenja kada je potrebno
- dostupan serveru, ali ne klijentu

Kurs generise nasumican string alatom poput:

```bash
openssl rand -hex 32
```

To moze biti koristan nacin za generisanje testne tajne.

### Gde secret ne treba da stoji

Ne treba ga hardkodovati ovako u routeru:

```python
SECRET_KEY = "learn online"
```

Ne treba ga commit-ovati u git.

### Gde treba da stoji

Za tvoj projekat ciljni tok je:

```text
environment variable
    -> TodoApp/core/config.py
        -> TodoApp/core/security.py
```

Primer koncepta:

```text
JWT_SECRET_KEY u environment-u
    -> settings.secret_key
        -> jwt.encode(...)
```

U ovoj teorijskoj fazi ne dodajemo stvarnu tajnu u `.env` ili kod.

---

## 4) Algorithm

Transkript koristi:

```python
ALGORITHM = "HS256"
```

HS256 je HMAC-SHA-256 algoritam.

Kod simetricnog potpisa ista tajna se koristi za:

```text
encode tokena
decode/proveru tokena
```

Secret i algorithm rade zajedno:

```text
header + payload + secret + algorithm
    -> signature
        -> JWT
```

Algoritam nije tajna. Server treba eksplicitno da ocekuje dozvoljeni algoritam i ne treba slepo da prihvata vrednost koju klijent posalje u header-u tokena.

U vecim sistemima mogu se koristiti asymmetric algoritmi, ali ova lekcija prati HS256.

---

## 5) Funkcija `create_access_token`

Transkript uvodi pomocnu funkciju:

```python
def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta,
):
    ...
```

Funkcija prima podatke potrebne za claims:

```text
username
user_id
expires_delta
```

Za tvoj projekat funkcija bi kasnije pripadala:

```text
TodoApp/core/security.py
```

Router ne treba da zna detalje kako se racuna signature. Router treba da pozove helper:

```python
token = create_access_token(
    username=user.username,
    user_id=user.id,
    expires_delta=timedelta(minutes=20),
)
```

---

## 6) Kreiranje encoding payload-a

Transkript pravi recnik claims-a:

```python
encode = {
    "sub": username,
    "id": user_id,
}
```

Ovi podaci ce biti deo JWT payload-a.

### `sub`

U transkriptu `sub` sadrzi username:

```python
"sub": username
```

U drugim projektima `sub` moze sadrzati korisnicki ID. Vazno je da aplikacija ima dosledno pravilo.

Za tvoj TodoApp preporucljiviji oblik je da identitet bude stabilan ID, na primer:

```python
"sub": str(user_id)
```

Username se moze promeniti, dok je database ID stabilniji identifikator.

Ako zbog vernosti kursu koristimo username u `sub`, to treba jasno zapamtiti kao kursni izbor.

### Privatni `id` claim

Transkript dodatno cuva:

```python
"id": user_id
```

To moze biti prakticno za kurs, ali uvodi dupliranje ako je `sub` vec user ID.

Modernije je izabrati jedno dosledno pravilo, na primer:

```json
{
  "sub": "42"
}
```

ili svesno koristiti oba:

```json
{
  "sub": "42",
  "user_id": 42
}
```

Ne treba bez razloga cuvati vise kopija istog identiteta.

---

## 7) Racunanje expiration vremena

Token treba da ima vreme isteka.

Transkript koristi:

```python
expire = datetime.now(timezone.utc) + expires_delta
```

Ako je:

```python
expires_delta = timedelta(minutes=20)
```

token istice 20 minuta od trenutka kreiranja.

### Zasto timezone-aware datum

Stari oblik:

```python
datetime.utcnow()
```

moze biti deprecated u novijim Python verzijama jer vraca naive datetime bez timezone informacija.

Preporuceni oblik je:

```python
from datetime import datetime, timezone


now = datetime.now(timezone.utc)
```

Time jasno kazemo da radimo sa UTC vremenom.

### Expiration kao claim

Dobijeno vreme se dodaje payload-u:

```python
encode["exp"] = expire
```

Biblioteka pri encoding-u pretvara datetime u odgovarajuci JWT NumericDate oblik.

---

## 8) `encode.update()`

Transkript radi:

```python
encode.update({"exp": expire})
```

To znaci da se u postojeci recnik dodaje novi key-value par.

Pre:

```python
encode = {
    "sub": username,
    "id": user_id,
}
```

Posle:

```python
encode = {
    "sub": username,
    "id": user_id,
    "exp": expire,
}
```

Mozemo ga napisati i direktno:

```python
encode = {
    "sub": username,
    "id": user_id,
    "exp": expire,
}
```

Oba oblika imaju isti konceptualni rezultat.

---

## 9) Poziv `jwt.encode`

Kada su claims pripremljeni, token se pravi ovako:

```python
return jwt.encode(
    encode,
    SECRET_KEY,
    algorithm=ALGORITHM,
)
```

Argumenti su:

```text
encode
    payload claims

SECRET_KEY
    tajna za potpis

algorithm
    algoritam potpisa
```

Rezultat je string oblika:

```text
encoded_header.encoded_payload.encoded_signature
```

Korisnik dobija token, ali ne dobija secret key.

---

## 10) Konceptualna funkcija za tvoj projekat

Kursni oblik moze izgledati ovako:

```python
from datetime import datetime, timedelta, timezone
from jose import jwt


async def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta,
):
    expire = datetime.now(timezone.utc) + expires_delta

    encode = {
        "sub": username,
        "id": user_id,
        "exp": expire,
    }

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
```

Za organizovaniji projekat, ciljna lokacija je:

```text
TodoApp/core/security.py
```

A secret i algorithm se citaju iz konfiguracije:

```python
async def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta,
):
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
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

Ovaj drugi oblik je ciljna arhitektonska dopuna, a ne doslovan kod transkripta.

---

## 11) Zasto funkcija moze biti `async`, a `jwt.encode` nije

JWT encoding je lokalna CPU operacija i sama biblioteka obicno nema potrebu za `await`.

Funkcija moze biti obicna:

```python
def create_access_token(...):
    ...
```

Ako je transkript definise kao `async`, pozivalac mora koristiti:

```python
token = await create_access_token(...)
```

Vazno je da se stil ne mesa:

```python
# async funkcija
async def create_access_token(...):
    ...

# async poziv
 token = await create_access_token(...)
```

ili:

```python
# sync funkcija
def create_access_token(...):
    ...

# sync poziv
 token = create_access_token(...)
```

Za ovakav mali lokalni helper sync funkcija je cesto jednostavnija, ali teorijski pratimo transkriptni tok.

---

## 12) Pozivanje token helpera u auth routeru

Nakon uspesne autentifikacije:

```python
user = authenticate_user(
    form_data.username,
    form_data.password,
    db,
)

if not user:
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
    )
```

Kreira se token:

```python
token = create_access_token(
    username=user.username,
    user_id=user.id,
    expires_delta=timedelta(minutes=20),
)
```

Zatim se token vraca klijentu.

Ako je helper `async`:

```python
token = await create_access_token(...)
```

Ako je sync:

```python
token = create_access_token(...)
```

Ovaj token endpoint pripada:

```text
TodoApp/api/routes/auth.py
```

---

## 13) `Token` response schema

Transkript dodaje Pydantic model:

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

U tvom projektu buduca lokacija je:

```text
TodoApp/schemas.py
```

Schema opisuje oblik HTTP odgovora:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Endpoint moze koristiti:

```python
@router.post(
    "/token",
    response_model=Token,
)
```

### Znacenje polja

`access_token` je stvarni JWT string.

`token_type` govori klijentu kako da ga salje. U OAuth2 Bearer toku vrednost je:

```text
bearer
```

---

## 14) Zasto je response schema vazna

Bez response schema endpoint moze vratiti proizvoljan recnik.

Sa:

```python
response_model=Token
```

FastAPI i Pydantic pomazu da odgovor ima ocekivanu strukturu:

```text
access_token: string
token_type: string
```

To olaksava:

- Swagger dokumentaciju
- klijentsku integraciju
- validaciju odgovora
- citanje API ugovora

Token schema ne treba da sadrzi:

```text
secret_key
plain password
hashed_password
```

---

## 15) Konceptualni token endpoint

Prilagodjeni teorijski oblik:

```python
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...schemas import Token


@router.post(
    "/token",
    response_model=Token,
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: db_dependency = None,
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        expires_delta=timedelta(minutes=20),
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
```

Kod je edukativan i jos nije spreman za kopiranje u aktivni projekat. Posebno treba prilagoditi dependency potpis i konfiguraciju.

---

## 16) Secret i konfiguracija u `core/config.py`

Buduca konfiguracija moze sadrzati:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
```

Konceptualni settings tok:

```text
environment
    JWT_SECRET_KEY=nasumicna-vrednost
    JWT_ALGORITHM=HS256

TodoApp/core/config.py
    Settings objekat

TodoApp/core/security.py
    koristi settings

TodoApp/api/routes/auth.py
    poziva security helper
```

Ne treba da `auth.py` generise novi secret pri svakom importu ili restartu aplikacije. Ako se secret promeni, stari tokeni vise nece moci da se validiraju.

U produkciji secret dolazi iz sigurnog environment/secrets sistema, ne iz javnog repozitorijuma.

---

## 17) Expiration odluka

Transkript koristi:

```python
timedelta(minutes=20)
```

To je kursni primer.

Trajanje tokena je bezbednosna odluka:

```text
kraci access token
    manji period rizika ako token procure

duzi access token
    manje cesto osvezavanje, ali duzi rizik
```

U realnijem sistemu moze postojati:

```text
kratak access token
duze vazeci refresh token
```

Ovaj kursni korak koristi samo access token. Refresh tokene ne uvodimo unapred.

---

## 18) `datetime.utcnow()` i timezone-aware kod

Transkript napominje da je:

```python
datetime.utcnow()
```

zastareo u novijim Python verzijama.

Moderniji oblik:

```python
from datetime import datetime, timezone


expire = datetime.now(timezone.utc) + expires_delta
```

Prednost je sto objekat eksplicitno nosi UTC timezone informaciju.

Kod autentifikacije vreme mora biti dosledno. Ako jedan deo sistema koristi naive lokalno vreme, a drugi UTC vreme, expiration provere mogu biti pogresne.

---

## 19) Bezbednosne granice encoding-a

Kreiranje tokena nije dovoljno samo po sebi.

Mora se paziti na:

- secret key
- dozvoljeni algorithm
- minimalan payload
- expiration
- HTTPS
- neizlaganje password-a
- neizlaganje secret-a
- response schema
- validaciju korisnika pre encoding-a

Ne treba kreirati token ovako:

```python
if user:
    token = jwt.encode(
        {"username": form_data.username},
        "tajna-u-kodu",
        algorithm="HS256",
    )
```

ako je tajna javno zapisana ili ako se ne proverava password.

Pravilniji redosled je:

```text
authenticate_user
    -> validan user
        -> create_access_token
```

---

## 20) Sta ova lekcija jos ne implementira

Ova lekcija jos ne obradjuje potpuno:

- decoding JWT-a
- proveru signature-a u protected endpointu
- `OAuth2PasswordBearer`
- current user dependency
- role authorization
- Todo ownership filter
- refresh token
- revoke token

Ona samo pravi token posle uspesne autentifikacije.

U teorijskoj fazi ne menjamo:

```text
TodoApp/api/routes/auth.py
TodoApp/core/config.py
TodoApp/core/security.py
TodoApp/schemas.py
requirements.txt
```

---

## 21) Pitanja za proveru znanja

1. Sta znaci encoding JWT-a?
2. Koja biblioteka se koristi u transkriptu za JWT?
3. Zasto je potreban secret key?
4. Sta radi `HS256`?
5. Gde u tvom projektu treba da stoji secret konfiguracija?
6. Sta sadrzi payload iz funkcije `create_access_token`?
7. Sta znaci claim `sub`?
8. Zasto je `sub` sa stabilnim user ID-em cesto bolji od promenljivog username-a?
9. Sta radi `exp`?
10. Zasto se koristi `datetime.now(timezone.utc)`?
11. Sta radi `jwt.encode()`?
12. Zasto `Token` response schema ima `access_token` i `token_type`?
13. Zasto secret ne treba da stoji direktno u `auth.py`?
14. Zasto se token kreira tek nakon `authenticate_user()`?
15. Koja je razlika izmedju kursnog primera i ciljne strukture `core/security.py`?
16. Koje JWT funkcionalnosti jos nedostaju nakon encoding-a?

---

## 22) Prakticni zadaci

### Zadatak 1 - Napravi claims recnik

Na papiru ili u Markdown-u napravi payload sa:

```text
sub
id ili user_id
exp
```

Koristi izmisljene vrednosti i objasni svaku.

### Zadatak 2 - Izaberi subject

Uporedi:

```python
{"sub": username}
```

```python
{"sub": str(user_id)}
```

Napisi prednosti i mane oba izbora za TodoApp.

### Zadatak 3 - Racunanje expiration-a

Ako je sada:

```text
2026-09-23 12:00 UTC
```

a expiration delta je 20 minuta, odredi expiration vreme.

Objasni zasto treba koristiti UTC.

### Zadatak 4 - Rastavi `jwt.encode`

Objasni uloge svakog argumenta:

```python
jwt.encode(payload, secret_key, algorithm="HS256")
```

### Zadatak 5 - Response schema

Napravi konceptualnu `Token` schemu sa:

```text
access_token: str
token_type: str
```

Zatim napisi primer JSON response-a.

### Zadatak 6 - Pronadji secret problem

Analiziraj:

```python
SECRET_KEY = "learn online"
```

Navedi najmanje tri problema i predlozi gde bi secret stajao u tvom projektu.

### Zadatak 7 - Sync naspram async helpera

Uporedi:

```python
def create_access_token(...):
    ...
```

```python
async def create_access_token(...):
    ...
```

Objasni razliku u pozivu i zasto treba biti dosledan.

### Zadatak 8 - Povezi fajlove

Odredi lokaciju:

```text
Settings
create_access_token
Token schema
/token endpoint
DB dependency
```

Koristi:

```text
TodoApp/core/config.py
TodoApp/core/security.py
TodoApp/schemas.py
TodoApp/api/routes/auth.py
TodoApp/db/session.py
```

### Zadatak 9 - Redosled sigurnog toka

Poredjaj:

```text
jwt.encode
authenticate_user
request forma
response Token
HTTP 401
```

Napravi tok za uspesan i neuspesan login.

### Zadatak 10 - Plan implementacije bez menjanja koda

Napisi buduci redosled:

1. dodaj dependency
2. dodaj config
3. napravi security helper
4. napravi Token schema
5. povezi token endpoint
6. proveri expiration
7. tek kasnije dodaj decode/current user

Uz svaki korak navedi fajl i sta treba proveriti.

---

## 23) Zakljucak

Encoding JWT-a pretvara claims, secret i algoritam u potpisani token:

```text
payload + secret + algorithm
    -> jwt.encode()
        -> access token
```

Za tvoj projekat najvaznije je zapamtiti:

- `python-jose[cryptography]` je runtime dependency za JWT funkcije
- secret key ne sme biti hardkodovan ili commit-ovan
- konfiguracija pripada `TodoApp/core/config.py`
- JWT helper pripada buducem `TodoApp/core/security.py`
- `/token` endpoint pripada `TodoApp/api/routes/auth.py`
- `Token` response schema pripada `TodoApp/schemas.py`
- `sub` treba da bude dosledno definisan
- `exp` ogranicava trajanje tokena
- timezone-aware UTC vreme je bolji izbor
- token se kreira tek posle uspesne autentifikacije
- encoding jos nije isto sto i decoding i current user authorization

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
