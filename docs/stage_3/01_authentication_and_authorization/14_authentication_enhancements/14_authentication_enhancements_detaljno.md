# Oblast 03 - Authentication and Authorization

## Lekcija 14 - Poboljsanja autentifikacije i organizacija auth ruta

Ovo je poslednja lekcija u oblasti **Authentication and Authorization**.

U prethodnoj lekciji napravljen je osnovni tok za citanje Bearer tokena i dobijanje current user-a. Ova lekcija ne uvodi novu veliku funkcionalnost, vec dovrsava taj tok kroz nekoliko vaznih poboljsanja:

1. neuspesan login vraca HTTP 401 umesto obicnog stringa
2. auth rute dobijaju zajednicki `/auth` prefix
3. auth rute se grupisu pod `auth` tagom u Swagger dokumentaciji
4. `tokenUrl` se uskladjuje sa stvarnom putanjom token endpointa
5. uklanja se duplirani `/auth/auth` iz putanje za kreiranje korisnika

Kao i u prethodnim lekcijama, materijal je teorijski. Aktivni Python kod, modeli, baza i dependency fajlovi se jos ne menjaju.

---

## 1) Sta je problem koji ova lekcija resava

Pre ovih izmena aplikacija moze imati rute slicne ovima:

```text
/auth/create_user
/token
/todo
/todo/{todo_id}
```

Pored toga, Swagger moze prikazati auth i Todo endpoint-e bez jasnog grupisanja.

To nije nuzno funkcionalna greska, ali API postaje manje pregledan:

- nije jasno koje rute pripadaju autentifikaciji
- auth prefix moze biti nedosledan
- Swagger UI prikazuje povezane rute razdvojeno
- pogresan `tokenUrl` moze zbuniti OAuth2/OpenAPI klijente
- neuspesan login vraca tekst umesto standardnog HTTP odgovora

Ciljani rezultat je:

```text
/auth/create_user
/auth/token
/todo
/todo/{todo_id}
```

U Swagger UI-ju:

```text
AUTH
    POST /auth/create_user
    POST /auth/token

TODO
    GET /todo
    POST /todo
    PUT /todo/{todo_id}
    DELETE /todo/{todo_id}
```

---

## 2) Ispravan HTTP odgovor za neuspesan login

U ranijem kodu neuspesna provera korisnika moze izgledati ovako:

```python
if not user:
    return "Failed authentication"
```

Ovo nije dobar API odgovor. HTTP status ostaje uspesan, iako autentifikacija nije uspela.

Klijent bi mogao dobiti tekst:

```text
Failed authentication
```

sa statusom `200 OK`.

To pogresno opisuje stanje. Login nije uspesan, zato odgovor treba da bude HTTP 401.

Teorijski oblik je:

```python
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

### Zasto je 401 vazan

HTTP status nije ukras. Klijentska aplikacija na osnovu njega odlucuje sta dalje radi:

```text
200 -> login je uspesan
401 -> kredencijali nisu validni
422 -> zahtev nema ocekivani format
500 -> greska na serveru
```

Ako server vrati `200` sa tekstom greske, klijent mora da pogadja da li je operacija stvarno uspela. Sa `401`, stanje je jasno i standardizovano.

---

## 3) `raise HTTPException` naspram `return`

U FastAPI endpointu:

```python
return "neki rezultat"
```

znaci da endpoint normalno zavrsava i vraca rezultat.

Nasuprot tome:

```python
raise HTTPException(...)
```

prekida normalan tok i FastAPI pravi error response sa odgovarajucim statusom.

Zato se autentifikacioni neuspeh ne vraca kao obican string:

```python
return "Failed authentication"  # los API ugovor
```

vec se prijavljuje kao HTTP greska:

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate user",
)
```

Ovo vazi i za:

- pogresno korisnicko ime
- pogresnu lozinku
- nepostojecg korisnika
- nevalidan JWT
- istekao JWT
- nedostajuci obavezni claim

---

## 4) Znacenje HTTP 401 u auth toku

HTTP 401 znaci da zahtev nema validne autentifikacione kredencijale.

U ovoj oblasti moze znaciti:

```text
login credentials nisu ispravni
Bearer token nedostaje
Bearer token je nevalidan
JWT je istekao
JWT nema potreban identitet
```

Za Bearer autentifikaciju standardno se dodaje:

```python
headers={"WWW-Authenticate": "Bearer"}
```

Ovaj header govori klijentu da server ocekuje Bearer autentifikaciju.

### 401 nije isto sto i 403

```text
401 Unauthorized
    korisnik nije autentifikovan ili kredencijali nisu validni

403 Forbidden
    korisnik je autentifikovan, ali nema potrebnu dozvolu
```

Na primer:

```text
pogresna lozinka -> 401
istekao access token -> 401
validan obican user na admin ruti -> 403
```

Naziv `Unauthorized` u HTTP standardu ume da zbuni, ali prakticno ga u ovoj fazi treba citati kao: identitet nije uspesno potvrden.

---

## 5) Router prefix

Kursni auth router konceptualno pocinje ovako:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

`prefix` se automatski dodaje svim rutama u tom routeru.

Ako auth router ima lokalne rute:

```python
@router.post("/create_user")
async def create_user(...):
    ...

@router.post("/token")
async def login_for_access_token(...):
    ...
```

javne putanje postaju:

```text
POST /auth/create_user
POST /auth/token
```

Router prefix je centralizovana konfiguracija. Ne moramo ponavljati `/auth` u svakom dekoratoru.

---

## 6) Zasto `/auth/auth` nastaje

Ako router vec ima:

```python
prefix="/auth"
```

a endpoint dodatno ima:

```python
@router.post("/auth/create_user")
```

FastAPI spaja oba dela:

```text
router prefix + endpoint path
/auth + /auth/create_user
= /auth/auth/create_user
```

To je tehnicki ocekivano ponasanje, ali je dizajnerski suvisno.

Ispravka je da endpoint koristi samo lokalni deo putanje:

```python
@router.post("/create_user")
```

Tada je javna putanja:

```text
/auth/create_user
```

### Pravilo za citanje putanje

Uvek odvojeno citaj:

```text
prefix routera
    /auth

lokalna putanja endpointa
    /create_user

javna putanja
    /auth/create_user
```

---

## 7) Router tagovi u Swagger UI-ju

Argument:

```python
tags=["auth"]
```

grupise sve endpoint-e iz routera u Swagger UI-ju.

Bez tagova, dokumentacija moze izgledati kao jedna duga lista.

Sa tagom:

```text
AUTH
    POST /auth/create_user
    POST /auth/token

TODO
    GET /todo
    POST /todo
```

Tag je dokumentaciona organizacija. On ne dodaje URL prefix i ne menja izvrsavanje funkcije.

Razlikuj:

```text
prefix
    menja javnu putanju

tags
    grupise endpoint-e u OpenAPI/Swagger prikazu
```

Ova dva argumenta se cesto koriste zajedno, ali imaju razlicite odgovornosti.

---

## 8) Mapiranje na tvoj projekat

U aktivnom projektu je ciljna lokacija auth routera:

```text
TodoApp/api/routes/auth.py
```

Konceptualna struktura je:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

U `TodoApp/main.py` router ce kasnije biti ukljucen slicno ovome:

```python
app.include_router(auth.router)
```

Tada rute iz `auth.py` dobijaju prefix koji je definisan u samom routeru.

Todo router moze imati zaseban tag:

```python
router = APIRouter(
    prefix="/todo",
    tags=["todo"],
)
```

ili drugi lokalni dogovor projekta. Bitno je da se auth i Todo endpoint-i dokumentaciono i URL-om jasno odvoje.

---

## 9) `tokenUrl` mora pratiti javnu putanju

U prethodnoj lekciji uveden je objekat:

```python
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="token",
)
```

Ako auth router dobije prefix `/auth`, token endpoint vise nije javno dostupan na:

```text
/token
```

vec na:

```text
/auth/token
```

Zato konfiguracija treba da bude uskladjena:

```python
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
)
```

`tokenUrl` opisuje javnu putanju na kojoj klijent dobija access token.

### Vazna razlika

`tokenUrl` ne salje automatski zahtev token endpointu i ne vrsi JWT validaciju.

On je deo OAuth2/OpenAPI opisa i treba da odgovara stvarnoj ruti.

---

## 10) Zasto pogresan `tokenUrl` pravi zabunu

Pretpostavimo da stvarna ruta glasi:

```text
POST /auth/token
```

a security dependency je konfigurisana kao:

```python
OAuth2PasswordBearer(tokenUrl="token")
```

Bearer dependency moze i dalje citati Authorization header, ali Swagger/OpenAPI prikaz vise ne opisuje API tacno.

Moguce posledice:

- Swagger dugme Authorize pokazuje pogresnu token putanju
- generisani klijenti imaju pogresne informacije
- novi developer ne zna gde se token dobija
- dokumentacija i stvarni API se razlikuju

API dokumentacija treba da bude izvrstiv opis stvarnog API-ja, ne priblizna beleška.

---

## 11) Relative i absolute `tokenUrl`

U zavisnosti od strukture aplikacije, `tokenUrl` se moze zapisati kao:

```python
tokenUrl="auth/token"
```

ili:

```python
tokenUrl="/auth/token"
```

Za kursni primer najvaznije je razumeti koncept: vrednost mora opisivati javnu token rutu u aplikaciji.

Ako projekat ima poseban root path, reverse proxy ili verzionisani API prefix, putanju treba uskladiti sa tim javnim deployment ugovorom.

Na primer:

```text
/api/v1/auth/token
```

zahteva odgovarajucu OAuth2 dokumentaciju, a ne genericko `token`.

---

## 12) Auth endpointi posle cleanup-a

Ciljani auth router izgleda konceptualno ovako:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/create_user")
async def create_user(...):
    ...

@router.post("/token")
async def login_for_access_token(...):
    ...
```

Javni API:

```text
POST /auth/create_user
POST /auth/token
```

Ovde su tri nivoa odvojena:

```text
router prefix
    /auth

lokalni endpoint path
    /create_user ili /token

Swagger tag
    auth
```

---

## 13) Razlika izmedju auth routera i Todo routera

Auth router se bavi identitetom i tokenima:

```text
create user
login
create access token
```

Todo router se bavi poslovnim podacima:

```text
create todo
read todo
update todo
delete todo
```

Kasnije ce Todo router koristiti security dependency:

```text
Todo endpoint
    -> get_current_user
        -> JWT validacija
            -> korisnicki identitet
                -> Todo ownership provera
```

Auth router ne treba da sadrzi Todo CRUD logiku. Todo router ne treba da kopira JWT decode logiku u svakoj funkciji.

Centralizovan dependency omogucava da se ista autentifikaciona provera koristi na vise endpointa.

---

## 14) Authentication naspram authorization

Naziv oblasti sadrzi oba pojma, ali oni nisu isti.

### Authentication

Pitanje:

```text
Ko si ti?
```

Obuhvata:

- username/password login
- proveru password-a
- kreiranje JWT-a
- citanje Bearer tokena
- validaciju signature-a i expiration-a
- pronalazenje current user-a

### Authorization

Pitanje:

```text
Sta smes da uradis?
```

Obuhvata:

- pristup protected endpointu
- proveru vlasnistva nad Todo zapisom
- role i permissions
- razliku izmedju user i admin korisnika
- zabranu pristupa tudem resursu

Ova lekcija zavrsava organizaciju authentication dela i priprema sledeci korak: stvarnu zastitu Todo endpointa.

---

## 15) Sta se smatra zavrsenim posle ove oblasti

Na teorijskom nivou sada treba razumeti ceo authentication tok:

```text
1. korisnik salje username i password
2. server proverava korisnika
3. password se proverava hash verification funkcijom
4. server kreira JWT
5. klijent cuva access token
6. klijent salje Authorization: Bearer <token>
7. OAuth2PasswordBearer izdvaja token
8. jwt.decode proverava token
9. current user se dobija iz claims-a i baze
10. protected endpoint moze koristiti identity
```

Sledeca oblast treba da doda authorization ponasanje:

```text
11. korisnik pristupa samo dozvoljenim rutama
12. Todo se filtrira po owner_id
13. korisnik ne moze menjati tud Todo
14. role/permission provere se dodaju gde su potrebne
```

---

## 16) Projektna mapa nakon cele oblasti

Buduca organizacija u tvom projektu:

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

### `TodoApp/api/routes/auth.py`

- router sa `prefix="/auth"`
- `tags=["auth"]`
- `POST /auth/create_user`
- `POST /auth/token`
- login neuspeh vraca HTTP 401

### `TodoApp/core/security.py`

- `OAuth2PasswordBearer`
- `tokenUrl="auth/token"`
- `get_current_user()`
- JWT decode i validacija

### `TodoApp/main.py`

- ukljucuje auth router
- ukljucuje Todo router
- ne treba da sadrzi svu auth logiku

### `TodoApp/api/routes/todos.py`

- koristi `get_current_user()`
- kasnije proverava ownership i authorization

---

## 17) Cesta neslaganja koja treba izbeci

### Neslaganje 1 - prefix i endpoint putanja

```python
prefix="/auth"
@router.post("/auth/token")
```

Rezultat:

```text
/auth/auth/token
```

Ispravno:

```python
prefix="/auth"
@router.post("/token")
```

### Neslaganje 2 - tokenUrl i stvarna ruta

```text
tokenUrl = token
stvarna ruta = /auth/token
```

Dokumentacija nije uskladjena sa API-jem.

### Neslaganje 3 - greska kao uspesan rezultat

```python
return "Failed authentication"
```

HTTP status ne pokazuje neuspeh.

### Neslaganje 4 - pogresan status za authorization

```text
validan user bez admin dozvole -> 403
nevalidan ili nedostajuci token -> 401
```

### Neslaganje 5 - dupliranje security logike

Svaki Todo endpoint ne treba sam da dekodira JWT. Koristi se zajednicki dependency.

---

## 18) Pitanja za proveru znanja

1. Zasto `return "Failed authentication"` nije dobar odgovor za neuspesan login?
2. Sta radi `raise HTTPException`?
3. Koji HTTP status se koristi za nevalidne kredencijale?
4. Sta oznacava `WWW-Authenticate: Bearer`?
5. Sta radi `prefix="/auth"`?
6. Kako nastaje putanja `/auth/auth/token`?
7. Kako se uklanja duplirani `/auth`?
8. Sta radi `tags=["auth"]`?
9. Da li tag menja stvarnu URL putanju?
10. Koja je javna putanja za lokalni endpoint `/token` unutar routera sa prefixom `/auth`?
11. Zasto `tokenUrl` treba promeniti na `auth/token`?
12. Da li `tokenUrl` sam validira JWT?
13. Koja je razlika izmedju authentication i authorization?
14. Zasto auth i Todo rute treba drzati u odvojenim routerima?
15. Zasto security logiku treba centralizovati u dependency-ju?
16. Kada se koristi 401, a kada 403?

---

## 19) Prakticni i analiticki zadaci

### Zadatak 1 - Izracunaj javne putanje

Za sledeci router:

```python
router = APIRouter(prefix="/auth", tags=["auth"])
```

i rute:

```python
@router.post("/create_user")
@router.post("/token")
```

napisi javne HTTP putanje.

### Zadatak 2 - Pronadji duplikat

Objasni problem u kodu:

```python
router = APIRouter(prefix="/auth")

@router.post("/auth/create_user")
async def create_user(...):
    ...
```

Napisi korigovanu lokalnu putanju.

### Zadatak 3 - Ispravi login gresku

Prepravi:

```python
if not user:
    return "failed authentication"
```

tako da koristi `HTTPException`, status `401` i Bearer header.

### Zadatak 4 - Uskladi `tokenUrl`

Stvarna ruta je:

```text
POST /auth/token
```

Dopuni:

```python
OAuth2PasswordBearer(tokenUrl="...")
```

Objasni zasto izabrana vrednost odgovara stvarnom endpointu.

### Zadatak 5 - Odvoji prefix i tag

Za svaki izraz napisi da li menja URL, Swagger grupisanje ili oba:

```python
prefix="/auth"
tags=["auth"]
```

### Zadatak 6 - Status kodovi

Dodeli status:

```text
pogresna lozinka
istekao JWT
validan token, user nije vlasnik Todo-a
uspesno kreiran token
```

Koristi `200`, `401` i `403`, uz obrazlozenje.

### Zadatak 7 - Nacrtaj auth tok

Nacrtaj kompletan tok:

```text
POST /auth/token
    -> provera user-a
        -> HTTP 401 ili JWT
            -> Authorization header
                -> get_current_user
```

Dodaj gde se ukljucuje `tokenUrl`.

### Zadatak 8 - Napravi Swagger plan

Zamisli da postoje auth i Todo router. Napisi koje tagove i prefix-e bi koristio da Swagger bude pregledan.

### Zadatak 9 - Authentication ili authorization

Razvrstaj stavke:

```text
provera password-a
JWT signature provera
provera Todo.owner_id
admin permission
kreiranje access tokena
```

### Zadatak 10 - Zavrsna kontrolna lista

Pre implementacije proveri:

- da li auth router ima prefix
- da li auth router ima tag
- da li lokalne rute ne ponavljaju prefix
- da li `tokenUrl` prati javnu putanju
- da li login neuspeh vraca 401
- da li postoji `WWW-Authenticate` header
- da li Todo router ostaje odvojen
- da li current user logic nije kopirana u svaki endpoint

---

## 20) Zakljucak cele oblasti

Lekcija 14 ne uvodi novi tip tokena. Ona dovrsava kvalitet postojeceg auth API-ja.

Najvaznije izmene su:

```text
neuspeh login-a -> HTTP 401
auth router -> prefix /auth
auth router -> Swagger tag auth
create user -> /auth/create_user
token endpoint -> /auth/token
tokenUrl -> auth/token
```

Kompletan rezultat treba da bude jasan i klijentima i developerima:

```text
POST /auth/create_user
POST /auth/token
```

`OAuth2PasswordBearer` sada zna gde se token dobija, a kasnije ce `get_current_user()` koristiti taj Bearer token za autentifikaciju protected zahteva.

Ovim je zavrsena teorijska oblast Authentication and Authorization na nivou kursnog authentication toka. Sledeci korak je implementacija authorization pravila nad Todo zapisima: provera current user-a, ownership-a i dozvola pristupa.

Do tada aktivne skripte, `Users` tabela, routeri i baza ostaju nepromenjeni, u skladu sa dogovorenim theory-first planom.
