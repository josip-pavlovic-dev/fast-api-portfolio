# Oblast 03 - Authentication and Authorization

## Lekcija 08 - Hashovanje password-a korisnika

Prethodna lekcija je napravila prvi `Users` objekat, ali je imala ozbiljan bezbednosni problem:

```python
hashed_password=create_user_request.password
```

Iako se kolona zove `hashed_password`, u njoj se tada čuvao originalni plain-text password.

Ova lekcija uvodi password hashing:

```text
plain password
    -> password hashing
        -> hashed_password u bazi
```

Ako korisnik unese:

```text
Test1234
```

u bazi ne treba da se pojavi:

```text
Test1234
```

već vrednost slična:

```text
$2b$12$...dugacak_hash...
```

### Važna napomena za trenutni plan

Ovo je teorijski fajl. Ne instaliramo pakete, ne menjamo `requirements.txt`, ne menjamo `auth.py` i ne dodajemo korisnika u bazu dok ne završimo teoriju cele oblasti.

---

## 1) Zašto password ne sme biti plain text

Plain-text password je originalna vrednost koju je korisnik uneo:

```text
Test1234
```

Ako se takva vrednost sačuva u bazi, svako ko dobije pristup bazi može da pročita password-e korisnika.

To predstavlja veliki rizik jer ljudi često koriste isti ili sličan password na više sajtova.

Rizici su:

- curenje baze otkriva stvarne password-e
- administrator baze može videti password
- logovi mogu slučajno sačuvati osetljive vrednosti
- napadac moze pokusati iste password-e na drugim servisima

Zato aplikacija treba da čuva samo password hash.

---

## 2) Šta je password hashing

Hashing je jednosmerna transformacija podataka.

Pojednostavljeno:

```text
ulaz:  Test1234
izlaz: dugacak hash string
```

Za razliku od enkripcije koja omogućava povratak originalnog podatka uz odgovarajući ključ, cilj password hashovanja nije da aplikacija kasnije dekriptuje password već da proveri njegovu ispravnost.

Pri login-u korisnik ponovo pošalje plain password. Biblioteka proveri da li taj password odgovara sačuvanom hash-u.

Tok registracije:

```text
korisnik unese password
    -> hash(password)
        -> čuva se hash u bazi
```

Tok login-a:

```text
korisnik unese password
    -> verify(password, sačuvani_hash)
        -> True ili False
```

Aplikacija ne mora da zna originalni password iz baze.

`verify()` funkcija se koristi za proveru plain password-a protiv sačuvanog hash-a. Ona vraća `True` ako password odgovara hash-u, a `False` u suprotnom.

PITANJE: Kako funkcioniše `verify()` funkcija? Kako se proverava da li unet plain password odgovara `hashed_password` vrednosti?

ODGOVOR: `verify()` funkcija uzima plain password i sačuvani hash. Biblioteka koristi parametre iz hash-a (uključujući `salt` i `troškove`) da ponovo izračuna hash za uneti password i uporedi ga sa sačuvanim hash-om. Ako se dobijeni hash poklapa sa sačuvanim, funkcija vraća `True`, inače `False`.

---

## 3) Hashing nije enkripcija

Ova razlika je važna.

### Enkripcija

```text
originalni podatak + ključ
    -> šifrovani podatak

šifrovani podatak + ključ
    -> originalni podatak
```

Enkripcija je namenjena da se podatak kasnije vrati u originalni oblik uz odgovarajući ključ.

### Hashing

```text
originalni password
    -> hash
```

Hash se ne koristi tako što aplikacija vraća originalni password.

Za password-e je potreban algoritam koji je namerno sporiji i otporan na masovno pogađanje, uz salt i podešavanja troška.

---

## 4) Salt i zašto isti password ne mora imati isti hash

Password hashing biblioteke koriste salt, odnosno nasumičnu vrednost koja se uključuje u proces hashovanja.

Zato dva korisnika mogu imati isti password:

```text
korisnik A: Test1234
korisnik B: Test1234
```

a ipak dobiti različite hash vrednosti:

```text
hash A: $2b$12$...
hash B: $2b$12$...
```

To je poželjno. Aplikacija zato ne treba da proverava password ovako:

```python
hash(uneseni_password) == sacuvani_hash
```

jer bi novi salt mogao proizvesti drugačiji string.

Umesto toga koristi se funkcija za proveru:

```python
password_context.verify(
    plain_password,
    saved_hash,
)
```

Biblioteka iz sačuvanog hash-a zna parametre potrebne za proveru.

---

## 5) Kursni izbor: Passlib i bcrypt

Transkript uvodi:

- `passlib` (biblioteka za password hashing)
- `bcrypt` (password hashing algoritam)
- `CryptContext` (klasa iz `passlib` biblioteke za kreiranje konteksta za hashovanje)

`passlib` je biblioteka koja pruža interfejs za password hashing algoritme, uključujući bcrypt.

Kursni konceptualni import izgleda ovako:

```python
from passlib.context import CryptContext
```

Zatim se pravi context za bcrypt algoritam.

```python
bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
```

### Značenje `CryptContext`

`CryptContext` je konfiguracioni objekat koji zna:

- koji algoritam koristi (npr. bcrypt)
- kako da napravi hash (npr. bcrypt)
- kako da proveri hash (npr. bcrypt)
- kako da prepozna stare ili zastarele scheme (npr. bcrypt)

Umesto da endpoint direktno upravlja detaljima algoritma, koristi context:

```python
bcrypt_context.hash(password)
bcrypt_context.verify(password, saved_hash)
```

PITANJE: Šta predstavlja kontekst u password hashing-u?

ODGOVOR: Kontekst (`CryptContext`) predstavlja konfiguracioni objekat koji enkapsulira sve detalje o algoritmu za hashovanje password-a, uključujući kako se pravi hash, kako se proverava hash i kako se prepoznaju zastarele sheme. On omogućava aplikaciji da koristi hash funkcionalnost bez potrebe da direktno upravlja detaljima algoritma.

---

## 6) Kreiranje hash-a

Kada imamo `CreateUserRequest`, teorijski kod iz transkripta ide ka ovome:

```python
hash_password = bcrypt_context.hash(
    create_user_request.password
)
```

Sada `hash_password` nije originalni password, već rezultat bcrypt algoritma.

Zatim se u model prosleđuje hash:

```python
user_model = Users(
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role,
    hashed_password=hash_password,
    is_active=True,
)
```

Vrednost koja se cuva u `hashed_password` treba da bude hash, a ne:

```python
create_user_request.password
```

---

## 7) `hash()` naspram `verify()`

### `hash()`

Koristi se pri registraciji ili promeni password-a. Metod `hash()` uzima plain password i vraća njegov hash. Ključna stvar je da se plain password nikada ne čuva direktno u bazi.

```python
hashed_password = bcrypt_context.hash(plain_password)
```

Ulaz je plain password, a izlaz je hash.

---

### `verify()`

Koristi se pri login-u:

```python
is_correct = bcrypt_context.verify(
    plain_password,
    saved_hash,
)
```

Argumenti imaju redosled:

```text
verify(plain password, sačuvani hash)
```

Rezultat je boolean:

```python
True   # password odgovara hash-u
False  # password ne odgovara hash-u
```

Ne treba ponovo ručno hashovati i porediti stringove, jer `salt` može dovesti do različitog `hash` stringa za isti plain password.

---

## 8) Kako se password proverava pri login-u

Budući login tok:

```text
1. Korisnik šalje username i password u login formi.
2. Aplikacija pronalazi Users zapis u bazi.
3. Iz zapisa čita hashed_password iz baze.
4. Poziva verify(uneti_password, sačuvani_hash), i dobija True ili False.
5. Ako je rezultat True, password je ispravan i korisnik se može prijaviti.
6. Ako je False, login se odbija i korisnik ne može pristupiti aplikaciji.
```

Konceptualni kod:

```python
user = find_user_by_username(username)

if user is None:
    reject_login()

if not bcrypt_context.verify(
    entered_password,
    user.hashed_password,
):
    reject_login()

allow_login(user)
```

U ovoj lekciji još ne pravimo login endpoint. Učimo mehanizam koji će login koristiti.

---

## 9) Zašto se hash ne de-hashuje

Česta početnička zabuna je:

> Kako aplikacija zna da je password tačan ako ne može da ga dekriptuje?

Odgovor je da aplikacija ne vraća sačuvani hash u originalni password.

Umesto toga password biblioteka (npr. `Passlib`) proverava da li plain password odgovara hash vrednosti, uz parametre koji su zapisani u hash formatu.

Mentalni model:

```text
registracija:
    password -> hash

login:
    password + sauvani hash -> verify -> True/False
```

Ne postoji korak:

```text
hash -> originalni password
```

---

## 10) Gde se hash context smešta u tvom projektu

Kursni primer može staviti `bcrypt_context` direktno u `auth.py`.

Tvoja ciljna lokacija endpointa je:

```text
TodoApp/api/routes/auth.py
```

Za početak, u malom kursnom koraku, context može biti blizu auth logike:

```text
TodoApp/api/routes/auth.py
    router
    bcrypt_context
    register endpoint
```

Kasnije, kada security logika poraste, bolja organizacija može biti:

```text
TodoApp/
    core/
        security.py
    api/
        routes/
            auth.py
```

Tada bi `security.py` mogao da sadrži funkcije poput:

```python
hash_password(...)
verify_password(...)
create_access_token(...)
```

a `auth.py` bi ih koristio.

Za ovu teorijsku lekciju najvažnije je razumeti podelu:

```text
auth.py
    HTTP endpoint i tok zahteva

security helper
    hashing i provera password-a
```

Praktična implementacija organizacije dolazi kasnije.

---

## 11) Gde pripadaju dependencies (zavisnosti)

Password biblioteke (npr. `Passlib` i `bcrypt`) su runtime dependency aplikacije (tj. potrebne su dok aplikacija radi). Kada dođe vreme za implementaciju, smeštaju se u `requirements.txt`.

```text
fast-api-portfolio/requirements.txt
```

Razvojni alati, test biblioteke i lint alati pripadaju:

```text
fast-api-portfolio/requirements-dev.txt
```

`Passlib` i `bcrypt` se koriste tokom rada aplikacije, pa su konceptualno `runtime dependencies`.

U ovoj teorijskoj fazi ne instaliramo ništa. Instalacija će biti objašnjena kasnije.

---

## 12) Verzija bcrypt-a iz transkripta

Transkript posebno navodi:

```bash
pip install passlib
pip install bcrypt==4.0.1
```

To je kursna kompatibilna kombinacija za okruženje u kom je lekcija snimljena.

### Zašto se navodi tačna verzija

Biblioteke mogu menjati:

- javne API-je tokom vremena
- interne module unutar biblioteke
- kompatibilnost sa drugim bibliotekama (npr. `Passlib` i `bcrypt`)
- `warning`-e i ponašanje pri importu tokom vremena

`Passlib` i `bcrypt` verzije moraju međusobno raditi. Zato kurs pin-uje verziju bcrypt-a.

---

### Važna moderna napomena

Broj verzije iz kursa ne treba automatski smatrati večitim standardom. U novom projektu treba proveriti:

- kompatibilnost sa izabranim Python interpreterom
- status održavanja biblioteke
- aktuelnu FastAPI dokumentaciju
- kompatibilnost `passlib` i bcrypt paketa
- bezbednosne preporuke za 2026. godinu

Noviji projekti mogu koristiti drugi provereni `password hashing interfejs`, na primer `pwdlib`, i algoritam koji je preporučen za konkretan projekat. To je moderna dopuna, odvojena od kursnog koraka.

### Šta učimo od kursa

Kursni cilj nije da zauvek zapamtimo samo jednu verziju. Cilj je da razumemo:

```text
password hashing context
    -> hash pri registraciji
    -> verify pri login-u
```

---

## 13) Bcrypt output nije podatak za prikaz korisniku

Hash se čuva u bazi radi provere, ali ne treba da se prikazuje kroz javni API response.

Loš demonstracioni response:

```json
{
  "username": "ana",
  "hashed_password": "$2b$12$..."
}
```

Iako hash nije originalni password, njegovo izlaganje je nepotrebno i povećava napadnu površinu.

Bezbedniji response sadrži samo potrebne podatke:

```json
{
  "id": 1,
  "username": "ana",
  "email": "ana@example.com",
  "role": "user",
  "is_active": true
}
```

Za to se koristi poseban `UserResponse` schema bez password polja.

---

## 14) Hashing nije dovoljan za kompletnu autentifikaciju

Password hashing rešava samo jedan deo sistema:

```text
bezbedno čuvanje i provera password-a
```

I dalje su potrebni:

- pronalaženje korisnika (npr. po email-u)
- provera jedinstvenog email-a i username-a (npr. pri registraciji)
- login endpoint (npr. POST /login)
- session ili JWT (npr. kreiranje i verifikacija tokena)
- current user dependency (npr. `get_current_user`)
- provera `is_active` (npr. da li je nalog aktivan)
- authorization po `role` (npr. admin vs user)
- ownership filteri za `Todos.owner_id` (npr. korisnik moze videti samo svoje zadatke)

Celokupan tok eksponiran kroz API endpoint-e će izgledati ovako:

```text
register
    -> hash password
        -> sacuvaj Users

login
    -> verify password
        -> izdaj token

protected request
    -> dekodiraj token
        -> current user
            -> proveri role i owner_id
```

---

## 15) Šta ova lekcija još ne radi

Ova lekcija ne implementira:

- login endpoint (npr. POST /login)
- proveru password-a preko `verify()` u stvarnom endpointu (npr. u POST /login)
- JWT (npr. kreiranje i verifikacija tokena)
- čuvanje korisnika u bazi (npr. SQLAlchemy session commit)
- `Users` model u aktivnim skriptama (npr. definisan u `TodoApp/models.py`)
- Alembic migraciju (npr. `alembic revision --autogenerate -m "create users table"`)
- security helper modul (npr. `TodoApp/api/security.py`)

U teorijskoj fazi ne menjamo:

```text
TodoApp/api/routes/auth.py
TodoApp/models.py
TodoApp/schemas.py
requirements.txt
```

Cilj je da prvo razumemo zašto se password hash-uje i kako se kasnije proverava.

---

## 16) Pitanja za proveru znanja

1. Zasto plain-text password ne sme da se čuva u bazi?
2. Šta je password hashing?
3. Koja je razlika između hashing-a i enkripcije?
4. Zašto dva ista password-a mogu imati različite hash vrednosti?
5. Sta radi `CryptContext`?
6. Koja je razlika između `hash()` i `verify()`?
7. Zašto nije dobro ponovo hashovati password i porediti stringove?
8. Koji je ispravan redosled argumenata za `verify()`?
9. Gde se čuva rezultat `hash()`?
10. Zašto naziv `hashed_password` ne znači da je vrednost automatski hashovana?
11. Koja je razlika između `passlib` i `pathlib`?
12. Gde bi se u tvom projektu nalazio auth endpoint?
13. Gde bi kasnije mogao da se izdvoji security helper?
14. Zašto bcrypt verzija može biti pin-ovana?
15. Zašto hash ne treba vraćati u javnom response-u?
16. Koje funkcionalnosti nedostaju za kompletnu autentifikaciju?

---

## 17) Praktični zadaci

### Zadatak 1 - Prepoznaj razliku

Za svaku vrednost oznaci da li je plain password ili hash:

```text
Test1234
$2b$12$abcdefghijkl...
```

Objasni zašto se druga vrednost ne može čitati kao originalni password.

---

### Zadatak 2 - Nacrtaj tok hashovanja

Nacrtaj:

```text
CreateUserRequest.password
    -> bcrypt_context.hash(...)
        -> Users.hashed_password
```

Uz svaku strelicu napiši tačno šta se dešava.

---

### Zadatak 3 - Nacrtaj tok provere

Nacrtaj:

```text
entered_password + saved_hash
    -> verify(...)
        -> True / False
```

Objasni šta se dešava u oba rezultata.

---

### Zadatak 4 - Ispravi loš kod

Pronadji problem:

```python
user_model = Users(
    hashed_password=create_user_request.password,
)
```

Napiši teorijski ispravljen oblik sa `bcrypt_context.hash(...)`.

---

### Zadatak 5 - Ispravi pogrešnu proveru

Objasni zašto je ovaj kod problematičan:

```python
bcrypt_context.hash(entered_password) == user.hashed_password
```

Napiši šta treba koristiti umesto toga.

---

### Zadatak 6 - Razlikuj biblioteke

Popuni tabelu:

```text
Biblioteka | Uloga
passlib    |
pathlib    |
bcrypt     |
pwdlib     |
```

Za `pwdlib` napiši da je moderna alternativa/napomena za dalju proveru, a ne deo osnovnog kursnog primera.

---

### Zadatak 7 - Planiraj dependency promenu

Napravi plan, bez menjanja fajlova, gde bi zapisao:

```text
runtime dependency
development dependency
```

Zatim uvrsti `passlib` i `bcrypt` u odgovarajuću kategoriju i obrazloži izbor.

---

### Zadatak 8 - Response bez tajnih vrednosti

Od sledećih polja napravi listu bezbednih response polja:

```text
id
username
email
first_name
last_name
role
is_active
hashed_password
```

Objasni zašto `hashed_password` izostaje.

---

### Zadatak 9 - Analiziraj kursni version pin

Objasni zašto transkript insistira na:

```bash
bcrypt==4.0.1
```

Zatim napiši šta bi proverio pre korišćenja te verzije u novom Python okruženju.

---

### Zadatak 10 - Povezi lekcije

Poveži sledeće delove sistema:

```text
Users model
password hashing
login
JWT
current user
Todos.owner_id
role
is_active
```

Napravi redosled od registracije do pristupa korisnikovim todo zapisima.

---

## 18) Zaključak

Password hashing zamenjuje opasno čuvanje plain-text password-a sigurnijim čuvanjem hash vrednosti.

Osnovni tok je:

```text
registracija:
    plain password -> hash() -> hashed_password

login:
    plain password + hashed_password -> verify() -> True/False
```

Za tvoj projekat:

- `auth endpoint` pripada `TodoApp/api/routes/auth.py`
- `Users` model pripada `TodoApp/models.py`
- runtime dependency pripada `requirements.txt`
- security helper kasnije može pripadati `TodoApp/core/security.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- glavna aplikacija ostaje u `TodoApp/main.py`

Ispravke u odnosu na transkript koje treba zapamtiti:

- login treba da koristi `verify()`, a ne prosto poređenje novih hash stringova
- `bcrypt==4.0.1` je kursna kompatibilna verzija, ne univerzalna preporuka za svaki budući projekat
- `hash` se ne vraća kroz javni response već se koristi interno za verifikaciju lozinke.
- Hashovanje samo po sebi još ne predstavlja kompletnu autentifikaciju ali je ključni deo sigurnog sistema za upravljanje lozinkama.

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne završi teorija cele oblasti.
