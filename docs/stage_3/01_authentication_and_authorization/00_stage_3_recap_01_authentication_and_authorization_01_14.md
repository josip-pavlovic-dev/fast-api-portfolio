# Stage 3 Recap - Authentication and Authorization (Lekcije 01-14)

Ovaj recap povezuje svih 14 lekcija iz oblasti **Authentication and Authorization** u jednu mapu ucenja i implementacije.

Stage 2 je postavio temelje:

- SQLAlchemy konekciju sa bazom
- modele i tabele
- database session dependency
- CRUD operacije
- HTTP metode i status kodove

Stage 3 na taj temelj dodaje identitet korisnika i kontrolu pristupa:

```text
Stage 2:
klijent -> FastAPI CRUD endpoint -> SQLAlchemy -> baza

Stage 3:
klijent -> autentifikacija -> current user -> authorization -> dozvoljeni CRUD -> baza
```

Cilj nije samo da korisnik moze da se uloguje. Cilj je da aplikacija zna:

- ko je korisnik
- da li je login validan
- kako se identitet prenosi kroz JWT
- kako se current user dobija iz protected request-a
- da li korisnik sme da pristupi konkretnom resursu
- kako se auth logika odvaja od Todo poslovne logike

> Ovaj recap je teorijsko-prakticni plan. U skladu sa dogovorenim redosledom rada, prvo se zavrsava teorija cele oblasti, a tek zatim se menjaju aktivne skripte, dodaju `Users` tabela, auth routeri i ownership pravila.

---

## 1) Mapa oblasti

## Lekcija 01 - Starting Authentication and Authorization

Tema: uvod u autentifikaciju i autorizaciju i pregled onoga sto treba dodati postojecem Todo API-ju.

Ishod:

- razlikujes authentication od authorization
- razumes zasto CRUD bez korisnickog identiteta nije dovoljan za visekorisnicku aplikaciju
- razumes da se prvo potvrduje identitet, a zatim proveravaju dozvole
- prepoznajes vezu izmedju buduceg `Users` modela i postojeceg `Todos` modela

Kljucna pitanja:

```text
Authentication: Ko si ti?
Authorization: Sta ti je dozvoljeno da uradis?
```

Materijal:

- [01_starting_authentication_and_authorization/01_starting_authentication_and_authorization_detaljno.md](01_starting_authentication_and_authorization/01_starting_authentication_and_authorization_detaljno.md)

## Lekcija 02 - Routers: izdvajanje authentication fajla

Tema: izdvajanje auth ruta iz centralnog fajla i uvod u router organizaciju.

Ishod:

- razumes zasto auth endpointi ne treba da rastu unutar `main.py`
- razumes ulogu `APIRouter`
- razumes kako se router registruje u glavnoj aplikaciji
- razlikujes definisanje rute od ukljucivanja routera

Buduca lokacija u tvom projektu:

```text
TodoApp/api/routes/auth.py
```

Materijal:

- [02_routers_scale_authentication_file/02_routers_scale_authentication_file_detaljno.md](02_routers_scale_authentication_file/02_routers_scale_authentication_file_detaljno.md)

## Lekcija 03 - Router za Todo rute

Tema: izdvajanje Todo endpointa u poseban router.

Ishod:

- razumes zasto auth i Todo rute pripadaju razlicitim modulima
- razumes kako routeri smanjuju velicinu `main.py`
- povezujes router organizaciju sa kasnijim dependency injection-om
- pripremas Todo router za current user i ownership provere

Buduca lokacija:

```text
TodoApp/api/routes/todos.py
```

Materijal:

- [03_router_scale_todos_file/03_router_scale_todos_file_detaljno.md](03_router_scale_todos_file/03_router_scale_todos_file_detaljno.md)

## Lekcija 04 - One-to-many relationship

Tema: odnos izmedju jednog korisnika i vise Todo zapisa.

Ishod:

- razumes da jedan user moze posedovati vise todos
- razumes relaciju `Users -> Todos`
- razumes zasto jedan Todo pripada jednom owner-u
- pripremas koncept za filtriranje po `owner_id`

Konceptualna veza:

```text
jedan Users red
    -> vise Todos redova

jedan Todos red
    -> jedan owner
```

Materijal:

- [04_one_to_many_relationship/04_one_to_many_relationship_detaljno.md](04_one_to_many_relationship/04_one_to_many_relationship_detaljno.md)

## Lekcija 05 - Foreign keys

Tema: povezivanje tabela preko foreign key kolone.

Ishod:

- razumes zasto `Todos.owner_id` pokazuje na `Users.id`
- razumes razliku izmedju primarnog i stranog kljuca
- razumes kako baza cuva referencijalnu vezu
- razumes zasto ownership treba da bude podrzan bazom, a ne samo dogovorom u kodu

Konceptualni model:

```text
Users.id  <-  Todos.owner_id
```

Materijal:

- [05_foreign_keys/05_foreign_keys_detaljno.md](05_foreign_keys/05_foreign_keys_detaljno.md)

## Lekcija 06 - Kreiranje Users tabele

Tema: dodavanje korisnickog modela i tabele.

Ishod:

- razumes zasto authentication zahteva korisnicke podatke
- razumes koja polja su potrebna za login i ownership
- povezujes `Users` model sa `Todos.owner_id`
- razumes da promena modela ne znaci automatski migraciju postojece baze

Konceptualna polja:

```text
Users:
    id
    username
    email
    hashed_password
    is_active
```

Napomena za aktivni projekat: `Users` tabela se dodaje tek nakon zavrsetka teorijske faze.

Materijal:

- [06_users_table_creation/06_users_table_creation_detaljno.md](06_users_table_creation/06_users_table_creation_detaljno.md)

## Lekcija 07 - Kreiranje prvog user-a

Tema: kreiranje prvog korisnika kroz API ili pripremljeni seed tok.

Ishod:

- razumes razliku izmedju request podataka i database modela
- razumes validaciju korisnickih podataka
- razumes zasto se lozinka ne cuva kao obican tekst
- razumes da korisnik mora postojati pre uspesnog login-a

Vazno:

```text
password koji klijent salje
    !=
password koji se cuva u bazi
```

Baza cuva password hash, ne originalnu lozinku.

Materijal:

- [07_create_first_user/07_create_first_user_detaljno.md](07_create_first_user/07_create_first_user_detaljno.md)

## Lekcija 08 - Hashovanje password-a

Tema: sigurno cuvanje lozinki pomocu password hashing biblioteke.

Ishod:

- razumes zasto se koristi `passlib`/`CryptContext`
- razumes razliku izmedju hashovanja i enkripcije
- razumes zasto se password proverava pomocu `verify()`
- razumes zasto se ne porede dva nova hasha kao mehanizam provere

Osnovni koncept:

```text
plaintext password
    -> hash(password)
        -> hashed_password u bazi

login password + stored hash
    -> verify(password, stored hash)
```

Materijal:

- [08_hash_users_password/08_hash_users_password_detaljno.md](08_hash_users_password/08_hash_users_password_detaljno.md)

## Lekcija 09 - Cuvanje user-a u bazi

Tema: povezivanje user requesta, hashovanja i SQLAlchemy session-a.

Ishod:

- razumes redosled: validacija -> hash -> model -> add -> commit
- razumes zasto se u bazu cuva hash
- razumes proveru jedinstvenosti korisnickog imena
- razumes kako se user model dobija nakon `db.refresh()`

Konceptualni tok:

```text
request schema
    -> password hash
        -> Users model
            -> db.add
                -> db.commit
                    -> db.refresh
```

Materijal:

- [09_save_user_to_database/09_save_user_to_database_detaljno.md](09_save_user_to_database/09_save_user_to_database_detaljno.md)

## Lekcija 10 - Authenticate a user

Tema: provera username/password kombinacije pri login-u.

Ishod:

- razumes kako se user pronalazi u bazi
- razumes kako se password proverava preko hash-a
- razumes zasto se nevalidni kredencijali odbijaju
- razumes zasto login endpoint treba da koristi standardni error status

Login tok:

```text
username/password
    -> pronadji user-a
        -> verify password
            -> neuspeh 401 ili nastavak
```

Materijal:

- [10_authenticate_a_user/10_authenticate_a_user_detaljno.md](10_authenticate_a_user/10_authenticate_a_user_detaljno.md)

## Lekcija 11 - JSON Web Token

Tema: svrha JWT-a i njegova struktura u auth sistemu.

Ishod:

- razumes zasto server posle login-a izdaje token
- razumes header, payload i signature delove JWT-a
- razumes da JWT payload nije enkriptovan
- razumes zasto client salje token uz naredne protected request-e

Pojednostavljena struktura:

```text
header.payload.signature
```

JWT predstavlja dokaz koji server kasnije proverava. Samo citanje payload-a nije dovoljno; signature i expiration moraju biti validirani.

Materijal:

- [11_json_web_token_JWT/11_json_web_token_JWT_detaljno.md](11_json_web_token_JWT/11_json_web_token_JWT_detaljno.md)

## Lekcija 12 - Encoding JWT-a

Tema: kreiranje access tokena posle uspesnog login-a.

Ishod:

- razumes kako se claims upisuju u payload
- razumes ulogu `SECRET_KEY`
- razumes ulogu algoritma
- razumes expiration claim
- razumes da secret i algorithm treba da budu u konfiguraciji, a ne razbacani po routerima

Konceptualni tok:

```text
validan user
    -> claims
        -> jwt.encode
            -> access token
```

Buduce lokacije:

```text
TodoApp/core/config.py
TodoApp/core/security.py
```

Materijal:

- [12_encode_json_web_token_JWT/12_encode_json_web_token_JWT_detaljno.md](12_encode_json_web_token_JWT/12_encode_json_web_token_JWT_detaljno.md)

## Lekcija 13 - Decoding JWT-a

Tema: citanje i validacija Bearer tokena i dobijanje current user-a.

Ishod:

- razumes `OAuth2PasswordBearer`
- razumes `get_current_user()` dependency
- razumes `jwt.decode()`
- razumes `JWTError`
- razumes proveru signature-a, algoritma, expiration-a i claims-a
- razumes razliku izmedju 401 i 403
- razumes kako se current user identitet kasnije koristi za Todo ownership

Tok:

```text
Authorization: Bearer <jwt>
    -> OAuth2PasswordBearer
        -> jwt.decode
            -> claims provera
                -> current user
```

Materijal:

- [13_decode_a_json_web_token_JWT/13_decode_a_json_web_token_JWT_detaljno.md](13_decode_a_json_web_token_JWT/13_decode_a_json_web_token_JWT_detaljno.md)

## Lekcija 14 - Authentication enhancements

Tema: zavrsni cleanup autentifikacionog API-ja i organizacija auth ruta.

Ishod:

- neuspesan login vraca HTTP 401 umesto obicnog stringa
- auth router dobija `prefix="/auth"`
- auth router dobija `tags=["auth"]`
- endpoint putanje ne ponavljaju prefix
- `tokenUrl` prati stvarnu javnu putanju `/auth/token`
- Swagger UI jasnije grupise auth i Todo endpoint-e

Ciljane rute:

```text
POST /auth/create_user
POST /auth/token
```

Materijal:

- [14_authentication_enhancements/14_authentication_enhancements_detaljno.md](14_authentication_enhancements/14_authentication_enhancements_detaljno.md)

---

## 2) Najvaznija promena strukture paketa u odnosu na Stage 2

Ovo je najvaznija arhitektonska promena ove oblasti.

Stage 2 je bio fokusiran na osnovni CRUD i mogao je poceti sa jednostavnijom strukturom, gde se veci deo logike nalazio u nekoliko centralnih fajlova:

```text
Stage 2 - pojednostavljena organizacija

TodoApp/
    main.py
    models.py
    schemas.py
    database.py ili db/session.py
```

U toj fazi aplikacija je uglavnom imala jednu vrstu poslovnog resursa: Todo.

Stage 3 uvodi vise od jedne odgovornosti:

- auth endpointi
- user model
- password hashing
- JWT encoding
- JWT decoding
- current user dependency
- Todo ownership
- buduce authorization provere

Zato se struktura razdvaja:

```text
Stage 3 - paketna organizacija

TodoApp/
    main.py
    models.py
    schemas.py
    api/
        __init__.py
        routes/
            __init__.py
            auth.py
            todos.py
    core/
        __init__.py
        config.py
        security.py
    db/
        __init__.py
        base.py
        database.py
        session.py
```

### Zasto je promena potrebna

#### 1. `main.py` vise ne treba da bude mesto za svu logiku

U Stage 2 je centralni fajl mogao ostati pregledan iako je sadrzao vise CRUD ruta.

Kada se dodaju login, register, token, users i security dependency, `main.py` bi brzo postao fajl koji:

- kreira FastAPI aplikaciju
- registruje modele
- definise auth rute
- definise Todo rute
- sadrzi password logiku
- sadrzi JWT logiku
- sadrzi database dependency

To je previse razlicitih odgovornosti u jednom modulu.

Zato `main.py` treba prvenstveno da bude composition root:

```text
kreiraj app
    -> registruj middleware
    -> ukljuci router-e
    -> pokreni startup konfiguraciju
```

#### 2. Auth i Todo imaju razlicite odgovornosti

Auth endpointi rade sa:

- korisnickim identitetom
- password-ima
- tokenima
- login greskama

Todo endpointi rade sa:

- Todo CRUD operacijama
- owner filterima
- statusima i validacijom Todo podataka

Ako se ove oblasti drze zajedno, svaka izmena u security logici povecava rizik za CRUD logiku i obrnuto.

Zato se uvode:

```text
api/routes/auth.py
api/routes/todos.py
```

#### 3. `api/routes` pokazuje javne API granice

`api/routes` je mesto za HTTP sloj:

- URL putanje
- request/response modele
- status kodove
- dependency injection na nivou endpointa
- pozivanje poslovne i security logike

To omogucava da se spoljasnji API citljivo organizuje po funkcionalnim oblastima.

#### 4. `core` cuva centralna pravila aplikacije

`core/config.py` je odgovarajuce mesto za:

- secret key
- JWT algorithm
- expiration podesavanja
- environment konfiguraciju

`core/security.py` je odgovarajuce mesto za:

- password hashing context
- password verification helper
- JWT encode helper
- JWT decode helper
- OAuth2 bearer dependency
- current user dependency

Ova pravila ne pripadaju pojedinacnom Todo endpointu.

#### 5. `db` odvaja pristup bazi od API logike

`db/session.py` cuva centralnu session dependency:

```text
endpoint
    -> Depends(get_db)
        -> SessionLocal
            -> yield session
                -> close session
```

`db/base.py` cuva zajednicki SQLAlchemy `Base`, a `db/database.py` engine i podesavanja konekcije.

Router ne treba svaki da pravi svoj engine ili kopira `get_db()`.

#### 6. Paketna struktura priprema rast projekta

Stage 2 projekat je ucio CRUD koncept. Stage 3 projekat postaje osnova za aplikaciju sa vise modula.

Paketna struktura omogucava da se kasnije dodaju, bez preopterecivanja `main.py`:

```text
api/routes/admin.py
api/routes/profile.py
api/routes/health.py
core/logging.py
core/exceptions.py
services/user_service.py
services/todo_service.py
```

Ne treba unapred dodavati sve ove fajlove. Poenta je da trenutna struktura ima jasna mesta za njihov buduci rast.

---

## 3) Stage 2 naspram Stage 3

| Oblast        | Stage 2                                  | Stage 3                                 |
| ------------- | ---------------------------------------- | --------------------------------------- |
| Glavni fokus  | CRUD nad Todo resursom                   | Identitet i kontrola pristupa           |
| Korisnik      | nije centralan koncept                   | `Users` postaje centralan model         |
| Password      | ne postoji                               | hash i verify tok                       |
| Token         | ne postoji                               | JWT access token                        |
| Routeri       | mogu biti jednostavni ili centralizovani | auth i Todo router se odvajaju          |
| Baza          | `Todos` tabela                           | `Users` i `Todos` sa relacijom          |
| Session       | koristi se za CRUD                       | koristi se i za user lookup i ownership |
| Request       | Todo payload                             | login, register i Todo payload          |
| Security      | nema protected ruta                      | Bearer token i current user dependency  |
| Dokumentacija | CRUD endpointi                           | odvojeni auth i Todo tagovi             |
| Statusi       | 200, 201, 204, 404, 422                  | dodaje se 401 i kasnije 403             |
| Struktura     | manji broj fajlova                       | paketi `api`, `core`, `db`              |

Najvaznija razlika je ova:

```text
Stage 2 proverava:
Da li Todo postoji i da li je request validan?

Stage 3 proverava:
Ko je korisnik i da li on sme da vidi ili menja taj Todo?
```

---

## 4) Kako se menja tok zahteva

### Stage 2 tok

```text
HTTP request
    -> FastAPI ruta
        -> Pydantic validacija
            -> get_db dependency
                -> SQLAlchemy query
                    -> response
```

### Stage 3 tok za login

```text
POST /auth/token
    -> OAuth2PasswordRequestForm
        -> pronalazenje user-a
            -> verify password
                -> kreiranje JWT-a
                    -> access token response
```

### Stage 3 tok za protected Todo zahtev

```text
GET /todo
    -> Authorization: Bearer <jwt>
        -> OAuth2PasswordBearer
            -> jwt.decode
                -> get_current_user
                    -> DB lookup user-a
                        -> authorization/ownership provera
                            -> Todo query
                                -> response
```

Upravo ovaj dodatni tok je razlog zbog kog Stage 3 zahteva bolju strukturu paketa.

---

## 5) Plan ucenja za 5 dana

Oblast ima 14 lekcija i uvodi bazu, security i novu arhitekturu. Realniji je plan od pet dana po oko 120 minuta.

## Dan 1 - arhitektura, routeri i relacije

Obradi lekcije 01-05:

- authentication naspram authorization
- auth router
- Todo router
- one-to-many relationship
- foreign key

Prakticne vezbe bez menjanja projekta:

- nacrtaj Stage 2 strukturu i Stage 3 strukturu
- nacrtaj `Users.id -> Todos.owner_id`
- objasni sta radi `APIRouter`
- napravi tabelu odgovornosti za `main.py`, `auth.py` i `todos.py`

Exit kriterijum:

- mozes objasniti zasto se auth i Todo rute razdvajaju
- mozes objasniti kako jedan user poseduje vise todos
- mozes izracunati javnu rutu iz router prefixa i lokalne putanje

## Dan 2 - Users tabela i prvi user

Obradi lekcije 06-07:

- Users model
- Users tabela
- prvi user
- request schema i database model
- validacija user podataka

Prakticne vezbe:

- napisi predlog `Users` polja
- objasni koji podaci se primaju, a koji se cuvaju
- nacrtaj odnos request schema -> model -> tabela
- razmisli sta treba da se desi za duplikat username-a

Exit kriterijum:

- mozes objasniti zasto user mora postojati pre login-a
- mozes razlikovati javni password od `hashed_password` vrednosti
- razumes da promena modela ne znaci automatski migraciju postojece baze

## Dan 3 - password hashing i login

Obradi lekcije 08-10:

- hash password-a
- cuvanje user-a
- authenticate user

Prakticne vezbe:

- objasni razliku izmedju hashovanja i enkripcije
- napisi redosled `hash -> add -> commit -> refresh`
- napisi login decision tree za postojecg i nepostojeceg user-a
- odredi kada se vraca 401

Exit kriterijum:

- mozes objasniti zasto se ne porede dva nova hasha
- mozes objasniti sta radi `verify(password, stored_hash)`
- mozes opisati login tok bez gledanja u materijal

## Dan 4 - JWT encoding i decoding

Obradi lekcije 11-13:

- struktura JWT-a
- encoding
- decoding
- Bearer token
- current user

Prakticne vezbe:

- nacrtaj `header.payload.signature`
- oznaci koji podaci su claims
- objasni razliku izmedju citanja payload-a i validacije tokena
- napisi kada se koristi 401
- objasni kako `sub` ili `id` povezuje token sa bazom

Exit kriterijum:

- mozes objasniti tok od login-a do protected request-a
- znas ulogu secret key-a, algoritma i expiration-a
- razumes sta radi `OAuth2PasswordBearer`, a sta `jwt.decode`

## Dan 5 - cleanup, mapa sistema i zavrsna provera

Obradi lekciju 14 i ovaj recap:

- HTTP 401 za neuspesan login
- `/auth` prefix
- `auth` tag
- `tokenUrl="auth/token"`
- razdvajanje auth i Todo routera
- Stage 2 naspram Stage 3 strukture

Prakticne vezbe:

- izracunaj javne putanje za auth router
- pronadji i ukloni hipoteticki `/auth/auth` problem
- nacrtaj celu paketnu strukturu
- napravi tabelu authentication i authorization odgovornosti
- napisi zavrsni report: 5 jasnih stvari, 3 stvari za dodatno vezbanje

Exit kriterijum:

- mozes usmeno objasniti celu oblast bez mesanja authentication i authorization pojmova
- mozes objasniti zasto je paketna struktura uvedena
- mozes napraviti plan implementacije bez menjanja koda nasumicno

---

## 6) Kompletnа mapa autentifikacionog toka

### Register tok

```text
POST /auth/create_user
    -> validacija request-a
        -> proveri da username ne postoji
            -> hash password-a
                -> Users model
                    -> db.add
                        -> db.commit
                            -> response bez plaintext password-a
```

### Login tok

```text
POST /auth/token
    -> username/password forma
        -> pronadji user-a
            -> verify password
                -> 401 ili nastavak
                    -> claims
                        -> jwt.encode
                            -> access token
```

### Protected request tok

```text
GET /todo
    -> Authorization: Bearer <token>
        -> OAuth2PasswordBearer
            -> jwt.decode
                -> proveri signature i expiration
                    -> proveri claims
                        -> pronadji current user-a
                            -> authorization/ownership
                                -> Todo query
```

### Neuspesni scenariji

```text
pogresan username/password -> 401
nedostajuci token          -> 401
nevalidan JWT              -> 401
istekao JWT                -> 401
validan user bez dozvole   -> 403
nepostojeci Todo           -> 404
los request payload        -> 422
```

---

## 7) Paketna mapa i odgovornosti

### `TodoApp/main.py`

Treba da bude mesto za sklapanje aplikacije:

- kreiranje `FastAPI()` objekta
- ukljucivanje routera
- globalna konfiguracija aplikacije
- startup/lifespan logika kada je potrebna

Ne treba da bude mesto za sve auth i Todo endpoint implementacije.

### `TodoApp/api/routes/auth.py`

Buduce odgovornosti:

- auth router
- `prefix="/auth"`
- `tags=["auth"]`
- create user endpoint
- token/login endpoint
- HTTP 401 za neuspesnu autentifikaciju

### `TodoApp/api/routes/todos.py`

Buduce odgovornosti:

- Todo CRUD rute
- current user dependency
- owner filter
- provera da korisnik ne menja tudji resurs

### `TodoApp/core/config.py`

Buduce odgovornosti:

- secret key
- JWT algorithm
- access token expiration
- environment vrednosti

Secret ne treba hardkodovati u routeru.

### `TodoApp/core/security.py`

Buduce odgovornosti:

- password hashing context
- password verification
- JWT encode helper
- JWT decode helper
- `OAuth2PasswordBearer`
- `get_current_user()`

### `TodoApp/db/base.py`

- centralni SQLAlchemy `Base`
- metadata za modele

### `TodoApp/db/database.py`

- database URL
- engine
- database connection podesavanja

### `TodoApp/db/session.py`

- `SessionLocal`
- `get_db()`
- `db_dependency`

### `TodoApp/models.py`

- `Users`
- `Todos`
- foreign key i relationships

### `TodoApp/schemas.py`

- create user schema
- token response schema
- Todo request/response schema
- eventualni current user schema

---

## 8) Sta se dobija paketnom strukturom

Paketna promena nije samo premestanje fajlova. Ona uvodi granice odgovornosti.

### Citljivost

Kada trazis problem sa login endpointom, prvo gledas `api/routes/auth.py`, a ne veliki centralni fajl.

### Ponovna upotreba

`get_current_user()` se definise jednom, a koristi na vise protected ruta.

### Testiranje

Mozes nezavisnije testirati:

- auth tok
- security helper
- Todo CRUD
- database session

### Manji rizik pri izmeni

Promena JWT expiration-a ne treba da zahteva pretragu svih Todo endpointa.

### Jasna skalabilnost

Nove funkcionalne oblasti mogu dobiti sopstveni router bez preopterecenja `main.py`.

### Laksa saradnja

Fajlovi imaju jasnu namenu, pa se lakse pronalazi gde promena pripada.

---

## 9) Sta ne treba raditi pri prelasku sa Stage 2

Ne treba:

- kopirati `get_db()` u svaki router
- stavljati secret key direktno u `auth.py`
- dekodirati JWT posebno u svakoj Todo funkciji
- dodavati `/auth` i u router prefix i u svaku lokalnu putanju
- cuvati plaintext password
- vracati `200 OK` kada login nije uspeo
- mesati `Users` model i token response schema
- koristiti URL `user_id` kao dokaz identiteta
- filtrirati Todo samo po njegovom ID-u kada ownership pravilo zahteva i owner ID
- menjati aktivni kod pre zavrsetka teorijske oblasti

Ispravan pravac je:

```text
centralizuj security logiku
centralizuj database dependency
odvoji HTTP routere po funkcionalnosti
povezi user-a i Todo kroz foreign key
proveri identitet pre ownership pravila
```

---

## 10) Status kodovi kroz Stage 2 i Stage 3

| Situacija                         | Status | Znacenje                                         |
| --------------------------------- | -----: | ------------------------------------------------ |
| uspesan GET                       |    200 | podaci su vraceni                                |
| uspesan user create               |    201 | novi resurs je kreiran                           |
| uspesan update/delete bez body-ja |    204 | operacija je uspela bez response body-ja         |
| Todo ili user nije pronadjen      |    404 | resurs ne postoji ili nije dostupan              |
| los request payload               |    422 | validacija ulaza nije prosla                     |
| pogresan login                    |    401 | kredencijali nisu validni                        |
| nedostajuci/nevalidan JWT         |    401 | autentifikacija nije uspela                      |
| validan user bez dozvole          |    403 | autentifikacija jeste uspela, authorization nije |

Kod ownership provere projekat moze izabrati razlicitu semantiku, na primer `404` da ne otkriva postojanje tudjeg resursa. Vazno je da odluka bude svesna i dosledna.

---

## 11) Zavrsna checklist za teorijsko razumevanje

Pre pocetka implementacije treba da mozes da odgovoris na sledece:

### Arhitektura

- [ ] Zasto `main.py` ne treba da sadrzi sve rute?
- [ ] Zasto se auth i Todo rute odvajaju?
- [ ] Sta pripada `api/routes` paketu?
- [ ] Sta pripada `core` paketu?
- [ ] Sta pripada `db` paketu?
- [ ] Zasto `get_db()` treba da bude centralizovan?

### Baza

- [ ] Sta predstavlja `Users` model?
- [ ] Sta predstavlja `Todos.owner_id`?
- [ ] Kako foreign key povezuje dve tabele?
- [ ] Zasto jedan user moze imati vise todos?
- [ ] Zasto promena modela nije isto sto i migracija baze?

### Password

- [ ] Zasto se password hash-uje?
- [ ] Zasto se hash ne dekriptuje?
- [ ] Kako `verify()` proverava login password?
- [ ] Zasto plaintext password ne sme u bazu ili response?

### JWT

- [ ] Sta su header, payload i signature?
- [ ] Zasto JWT payload nije tajna enkripcija?
- [ ] Cemu sluze secret key i algorithm?
- [ ] Sta je expiration claim?
- [ ] Sta radi `jwt.encode()`?
- [ ] Sta radi `jwt.decode()`?
- [ ] Sta radi `OAuth2PasswordBearer`?
- [ ] Zasto se proveravaju claims nakon decode-a?

### API organizacija

- [ ] Kako `prefix="/auth"` menja javnu putanju?
- [ ] Kako nastaje `/auth/auth` greska?
- [ ] Cemu sluzi `tags=["auth"]`?
- [ ] Zasto `tokenUrl` mora biti `auth/token` kada je javna ruta `/auth/token`?
- [ ] Zasto login neuspeh vraca 401?
- [ ] Kada se koristi 401, a kada 403?

---

## 12) Minimalni prakticni zadatak za kraj oblasti

Pre stvarne implementacije, uradi sledeci analiticki zadatak u posebnom tekstualnom fajlu ili svesci:

1. Nacrtaj Stage 2 strukturu.
2. Nacrtaj Stage 3 strukturu sa `api/routes`, `core` i `db` paketima.
3. Objasni razlog svake strukturalne promene.
4. Nacrtaj `Users.id -> Todos.owner_id` vezu.
5. Napisi register tok.
6. Napisi login tok.
7. Napisi protected Todo tok.
8. Navedi status kod za svaki neuspesni scenario.
9. Napisi javne auth putanje.
10. Objasni gde se cuva svaki tip logike.

Definition of done:

- mozes da objasnis celu oblast bez gledanja u kod
- znas gde bi pripadala svaka nova funkcija
- ne mesas password hashing, JWT encoding i JWT decoding
- ne mesas authentication sa authorization
- razumes zasto se paketna struktura promenila u odnosu na Stage 2
- spreman si da implementaciju radis u malim proverljivim koracima

---

## 13) Prelaz na implementaciju

Kada teorijska provera bude zavrsena, implementacija treba da ide postepeno:

1. potvrditi trenutni Stage 2 kod i bazu
2. uvesti ili potvrditi paketnu strukturu
3. izdvojiti auth i Todo router
4. dodati `Users` model i vezu ka `Todos`
5. dodati user schema
6. dodati password hashing
7. sacuvati prvog user-a
8. dodati login proveru
9. dodati JWT config i helper
10. dodati `OAuth2PasswordBearer`
11. dodati `get_current_user()`
12. zastititi Todo endpoint-e
13. dodati ownership filtere
14. testirati 401, 403, 404, 422 i uspesne slucajeve

Ovaj redosled cuva jasnu vezu izmedju teorije i stvarne promene u aplikaciji.

---

## 14) Zakljucak

Stage 3 uvodi korisnicki identitet u aplikaciju koja je u Stage 2 bila fokusirana na CRUD.

Najvazniji koncepti su:

1. authentication odgovara na pitanje ko je korisnik
2. authorization odgovara na pitanje sta korisnik sme
3. password se cuva kao hash
4. JWT prenosi identitet kroz protected request
5. `jwt.decode()` proverava validnost tokena
6. current user je dependency, a ne duplirana logika u svakom endpointu
7. `Users` i `Todos` se povezuju preko foreign key-a
8. auth i Todo endpointi se organizuju u odvojene routere
9. `core` cuva centralne security i configuration odluke
10. `db` cuva database foundation i session lifecycle
11. `main.py` sklapa aplikaciju umesto da bude skladiste sve logike
12. `/auth` prefix, Swagger tag i `tokenUrl` moraju biti uskladjeni

U odnosu na Stage 2, najveca promena nije samo dodavanje JWT-a. Najveca promena je sto aplikacija dobija vise odgovornosti i zato zahteva jasnije granice paketa.

```text
Stage 2: jedan funkcionalni CRUD tok
Stage 3: korisnici + security + protected CRUD + jasna arhitektura
```

Kada se ova oblast implementira, Todo API vise nece samo odgovarati na pitanje da li zapis postoji. Moci ce da proveri ko mu pristupa i da li taj korisnik ima pravo da ga vidi ili menja.
