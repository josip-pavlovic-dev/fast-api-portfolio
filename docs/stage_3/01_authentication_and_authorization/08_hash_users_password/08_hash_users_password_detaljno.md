# Oblast 03 - Authentication and Authorization

## Lekcija 08 - Hashovanje password-a korisnika

Prethodna lekcija je napravila prvi `Users` objekat, ali je imala ozbiljan bezbednosni problem:

```python
hashed_password=create_user_request.password
```

Iako se kolona zove `hashed_password`, u njoj se tada cuvao originalni plain-text password.

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

vec vrednost slicna:

```text
$2b$12$...dugacak_hash...
```

### Vazna napomena za trenutni plan

Ovo je teorijski fajl. Ne instaliramo pakete, ne menjamo `requirements.txt`, ne menjamo `auth.py` i ne dodajemo korisnika u bazu dok ne zavrsimo teoriju cele oblasti.

---

## 1) Zasto password ne sme biti plain text

Plain-text password je originalna vrednost koju je korisnik uneo:

```text
Test1234
```

Ako se takva vrednost sacuva u bazi, svako ko dobije pristup bazi moze da procita password-e korisnika.

To predstavlja veliki rizik jer ljudi cesto koriste isti ili slican password na vise sajtova.

Rizici su:

- curenje baze otkriva stvarne password-e
- administrator baze moze videti password
- logovi mogu slucajno sacuvati osetljive vrednosti
- napadac moze pokusati iste password-e na drugim servisima

Zato aplikacija treba da cuva samo password hash.

---

## 2) Sta je password hashing

Hashing je jednosmerna transformacija podataka.

Pojednostavljeno:

```text
ulaz:  Test1234
izlaz: dugacak hash string
```

Za razliku od enkripcije, cilj password hashovanja nije da aplikacija kasnije dekriptuje password.

Pri login-u korisnik ponovo posalje plain password. Biblioteka proveri da li taj password odgovara sacuvanom hash-u.

Tok registracije:

```text
korisnik unese password
    -> hash(password)
        -> cuva se hash
```

Tok login-a:

```text
korisnik unese password
    -> verify(password, sacuvani_hash)
        -> True ili False
```

Aplikacija ne mora da zna originalni password iz baze.

---

## 3) Hashing nije enkripcija

Ova razlika je vazna.

### Enkripcija

```text
originalni podatak + kljuc
    -> sifrovani podatak

sifrovani podatak + kljuc
    -> originalni podatak
```

Enkripcija je namenjena da se podatak kasnije vrati u originalni oblik uz odgovarajuci kljuc.

### Hashing

```text
originalni password
    -> hash
```

Hash se ne koristi tako sto aplikacija vraca originalni password.

Za password-e je potreban algoritam koji je namerno sporiji i otporan na masovno pogadjanje, uz salt i podesavanja troska.

---

## 4) Salt i zasto isti password ne mora imati isti hash

Password hashing biblioteke koriste salt, odnosno nasumicnu vrednost koja se ukljucuje u proces hashovanja.

Zato dva korisnika mogu imati isti password:

```text
korisnik A: Test1234
korisnik B: Test1234
```

a ipak dobiti razlicite hash vrednosti:

```text
hash A: $2b$12$...
hash B: $2b$12$...
```

To je pozeljno. Aplikacija zato ne treba da proverava password ovako:

```python
hash(uneseni_password) == sacuvani_hash
```

jer bi novi salt mogao proizvesti drugaciji string.

Umesto toga koristi se funkcija za proveru:

```python
password_context.verify(
    plain_password,
    saved_hash,
)
```

Biblioteka iz sacuvanog hash-a zna parametre potrebne za proveru.

---

## 5) Kursni izbor: Passlib i bcrypt

Transkript uvodi:

- `passlib`
- `bcrypt`
- `CryptContext`

U transkriptu se naziv biblioteke cuje kao nesto slicno `pathlib`, ali ovde je vazna ispravka:

```text
ispravno: passlib
nije password biblioteka: pathlib
```

`pathlib` je standardna Python biblioteka za rad sa putanjama fajlova.

`passlib` je biblioteka koja pruza interfejs za password hashing algoritme, ukljucujuci bcrypt.

Kursni konceptualni import izgleda ovako:

```python
from passlib.context import CryptContext
```

Zatim se pravi context:

```python
bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
```

### Znacenje `CryptContext`

`CryptContext` je konfiguracioni objekat koji zna:

- koji algoritam koristi
- kako da napravi hash
- kako da proveri hash
- kako da prepozna stare ili zastarele scheme

Umesto da endpoint direktno upravlja detaljima algoritma, koristi context:

```python
bcrypt_context.hash(password)
bcrypt_context.verify(password, saved_hash)
```

---

## 6) Kreiranje hash-a

Kada imamo `CreateUserRequest`, teorijski kod iz transkripta ide ka ovome:

```python
hash_password = bcrypt_context.hash(
    create_user_request.password
)
```

Sada `hash_password` nije originalni password, vec rezultat bcrypt algoritma.

Zatim se u model prosledjuje hash:

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

Koristi se pri registraciji ili promeni password-a:

```python
hashed_password = bcrypt_context.hash(plain_password)
```

Ulaz je plain password, a izlaz je hash.

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
verify(plain password, sacuvani hash)
```

Rezultat je boolean:

```python
True   # password odgovara
False  # password ne odgovara
```

Ne treba ponovo rucno hashovati i porediti stringove, jer salt moze dovesti do razlicitog hash stringa za isti plain password.

---

## 8) Kako se password proverava pri login-u

Buduci login tok:

```text
1. korisnik salje username i password
2. aplikacija pronalazi Users zapis
3. iz zapisa cita hashed_password
4. poziva verify(uneti_password, sacuvani_hash)
5. ako je rezultat True, password je ispravan
6. ako je False, login se odbija
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

U ovoj lekciji jos ne pravimo login endpoint. Ucimo mehanizam koji ce login koristiti.

---

## 9) Zasto se hash ne de-hashuje

Cesta pocetnicka zabuna je:

> Kako aplikacija zna da je password tacan ako ne moze da ga dekriptuje?

Odgovor je da aplikacija ne vraca sacuvani hash u originalni password.

Umesto toga password biblioteka proverava da li plain password odgovara hash vrednosti, uz parametre koji su zapisani u hash formatu.

Mentalni model:

```text
registracija:
    password -> hash

login:
    password + sacuvani hash -> verify -> True/False
```

Ne postoji korak:

```text
hash -> originalni password
```

---

## 10) Gde se hash context smesta u tvom projektu

Kursni primer moze staviti `bcrypt_context` direktno u `auth.py`.

Tvoja ciljna lokacija endpointa je:

```text
TodoApp/api/routes/auth.py
```

Za pocetak, u malom kursnom koraku, context moze biti blizu auth logike:

```text
TodoApp/api/routes/auth.py
    router
    bcrypt_context
    register endpoint
```

Kasnije, kada security logika poraste, bolja organizacija moze biti:

```text
TodoApp/
    core/
        security.py
    api/
        routes/
            auth.py
```

Tada bi `security.py` mogao da sadrzi funkcije poput:

```python
hash_password(...)
verify_password(...)
create_access_token(...)
```

a `auth.py` bi ih koristio.

Za ovu teorijsku lekciju najvaznije je razumeti podelu:

```text
auth.py
    HTTP endpoint i tok zahteva

security helper
    hashing i provera password-a
```

Prakticna implementacija organizacije dolazi kasnije.

---

## 11) Gde pripadaju dependencies

Password biblioteke su runtime dependency aplikacije. Kada bude vreme za implementaciju, pripadaju u:

```text
fast-api-portfolio/requirements.txt
```

Razvojni alati, test biblioteke i lint alati pripadaju:

```text
fast-api-portfolio/requirements-dev.txt
```

Passlib i bcrypt se koriste tokom rada aplikacije, pa su konceptualno runtime dependencies.

U ovoj teorijskoj fazi ne instaliramo nista.

---

## 12) Verzija bcrypt-a iz transkripta

Transkript posebno navodi:

```bash
pip install passlib
pip install bcrypt==4.0.1
```

To je kursna kompatibilna kombinacija za okruzenje u kom je lekcija snimljena.

### Zasto se navodi tacna verzija

Biblioteke mogu menjati:

- javne API-je
- interne module
- kompatibilnost sa drugim bibliotekama
- warning-e i ponasanje pri importu

Passlib i bcrypt verzije moraju medjusobno raditi. Zato kurs pin-uje verziju bcrypt-a.

### Vazna moderna napomena

Broj verzije iz kursa ne treba automatski smatrati vecitim standardom. U novom projektu treba proveriti:

- kompatibilnost sa izabranim Python interpreterom
- status odrzavanja biblioteke
- aktuelnu FastAPI dokumentaciju
- kompatibilnost `passlib` i bcrypt paketa
- bezbednosne preporuke za 2026. godinu

Noviji projekti mogu koristiti drugi provereni password hashing interfejs, na primer `pwdlib`, i algoritam koji je preporucen za konkretan projekat. To je moderna dopuna, odvojena od kursnog koraka.

### Sta ucimo od kursa

Kursni cilj nije da zauvek zapamtimo samo jednu verziju. Cilj je da razumemo:

```text
password hashing context
    -> hash pri registraciji
    -> verify pri login-u
```

---

## 13) Bcrypt output nije podatak za prikaz korisniku

Hash se cuva u bazi radi provere, ali ne treba da se prikazuje kroz javni API response.

Los demonstracioni response:

```json
{
  "username": "ana",
  "hashed_password": "$2b$12$..."
}
```

Iako hash nije originalni password, njegovo izlaganje je nepotrebno i povecava napadnu povrsinu.

Bezbedniji response sadrzi samo potrebne podatke:

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

Password hashing resava samo jedan deo sistema:

```text
bezbedno cuvanje i provera password-a
```

I dalje su potrebni:

- pronalazenje korisnika
- provera jedinstvenog email-a i username-a
- login endpoint
- session ili JWT
- current user dependency
- provera `is_active`
- authorization po `role`
- ownership filteri za `Todos.owner_id`

Celokupan tok ce izgledati ovako:

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

## 15) Sta ova lekcija jos ne radi

Ova lekcija ne implementira:

- login endpoint
- proveru password-a preko `verify()` u stvarnom endpointu
- JWT
- cuvanje korisnika u bazi
- `Users` model u aktivnim skriptama
- Alembic migraciju
- security helper modul

U teorijskoj fazi ne menjamo:

```text
TodoApp/api/routes/auth.py
TodoApp/models.py
TodoApp/schemas.py
requirements.txt
```

Cilj je da prvo razumemo zasto se password hash-uje i kako se kasnije proverava.

---

## 16) Pitanja za proveru znanja

1. Zasto plain-text password ne sme da se cuva u bazi?
2. Sta je password hashing?
3. Koja je razlika izmedju hashing-a i enkripcije?
4. Zasto dva ista password-a mogu imati razlicite hash vrednosti?
5. Sta radi `CryptContext`?
6. Koja je razlika izmedju `hash()` i `verify()`?
7. Zasto nije dobro ponovo hashovati password i porediti stringove?
8. Koji je ispravan redosled argumenata za `verify()`?
9. Gde se cuva rezultat `hash()`?
10. Zasto naziv `hashed_password` ne znaci da je vrednost automatski hashovana?
11. Koja je razlika izmedju `passlib` i `pathlib`?
12. Gde bi se u tvom projektu nalazio auth endpoint?
13. Gde bi kasnije mogao da se izdvoji security helper?
14. Zasto bcrypt verzija moze biti pin-ovana?
15. Zasto hash ne treba vracati u javnom response-u?
16. Koje funkcionalnosti nedostaju za kompletnu autentifikaciju?

---

## 17) Prakticni zadaci

### Zadatak 1 - Prepoznaj razliku

Za svaku vrednost oznaci da li je plain password ili hash:

```text
Test1234
$2b$12$abcdefghijkl...
```

Objasni zasto se druga vrednost ne moze citati kao originalni password.

### Zadatak 2 - Nacrtaj tok hashovanja

Nacrtaj:

```text
CreateUserRequest.password
    -> bcrypt_context.hash(...)
        -> Users.hashed_password
```

Uz svaku strelicu napisi sta se desava.

### Zadatak 3 - Nacrtaj tok provere

Nacrtaj:

```text
entered_password + saved_hash
    -> verify(...)
        -> True / False
```

Objasni sta se desava u oba rezultata.

### Zadatak 4 - Ispravi los kod

Pronadji problem:

```python
user_model = Users(
    hashed_password=create_user_request.password,
)
```

Napisi teorijski ispravljen oblik sa `bcrypt_context.hash(...)`.

### Zadatak 5 - Ispravi pogresnu proveru

Objasni zasto je ovaj kod problematican:

```python
bcrypt_context.hash(entered_password) == user.hashed_password
```

Napisi sta treba koristiti umesto toga.

### Zadatak 6 - Razlikuj biblioteke

Popuni tabelu:

```text
Biblioteka | Uloga
passlib    |
pathlib    |
bcrypt     |
pwdlib     |
```

Za `pwdlib` napisi da je moderna alternativa/napomena za dalju proveru, a ne deo osnovnog kursnog primera.

### Zadatak 7 - Planiraj dependency promenu

Napravi plan, bez menjanja fajlova, gde bi zapisao:

```text
runtime dependency
development dependency
```

Zatim uvrsti `passlib` i `bcrypt` u odgovarajucu kategoriju i obrazlozi izbor.

### Zadatak 8 - Response bez tajnih vrednosti

Od sledecih polja napravi listu bezbednih response polja:

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

Objasni zasto `hashed_password` izostaje.

### Zadatak 9 - Analiziraj kursni version pin

Objasni zasto transkript insistira na:

```bash
bcrypt==4.0.1
```

Zatim napisi sta bi proverio pre koriscenja te verzije u novom Python okruzenju.

### Zadatak 10 - Povezi lekcije

Povezi sledece delove sistema:

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

## 18) Zakljucak

Password hashing zamenjuje opasno cuvanje plain-text password-a sigurnijim cuvanjem hash vrednosti.

Osnovni tok je:

```text
registracija:
    plain password -> hash() -> hashed_password

login:
    plain password + hashed_password -> verify() -> True/False
```

Za tvoj projekat:

- auth endpoint pripada `TodoApp/api/routes/auth.py`
- `Users` model pripada `TodoApp/models.py`
- runtime dependency pripada `requirements.txt`
- security helper kasnije moze pripadati `TodoApp/core/security.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- glavna aplikacija ostaje u `TodoApp/main.py`

Ispravke u odnosu na transkript koje treba zapamtiti:

- biblioteka je `passlib`, ne `pathlib`
- login treba da koristi `verify()`, a ne prosto poredjenje novih hash stringova
- `bcrypt==4.0.1` je kursna kompatibilna verzija, ne univerzalna preporuka za svaki buduci projekat
- hash se ne vraca kroz javni response
- hashovanje samo po sebi jos ne predstavlja kompletnu autentifikaciju

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
