# Oblast 03 - Authentication and Authorization

## Lekcija 11 - JSON Web Token (JWT)

JWT je skracenica za **JSON Web Token**.

U prethodnoj lekciji aplikacija je umela da proveri username i password. Sada je potrebno da rezultat uspesnog login-a bude koristan i za sledece zahteve.

Bez tokena bi klijent morao da salje username i password pri svakom zahtevu. Sa tokenom je tok drugaciji:

```text
login
    -> server proverava kredencijale
        -> server izdaje JWT
            -> klijent salje JWT uz sledece zahteve
                -> server proverava token
```

JWT je potpisana struktura podataka koju server moze da proveri. U ovoj lekciji se uci koncept, struktura i bezbednosne granice. Kod za kreiranje i dekodiranje JWT-a dolazi u narednim lekcijama.

### Vazna napomena za trenutni plan

Ovo je teorijski materijal. Ne menjamo aktivne Python fajlove, ne instaliramo JWT paket i ne dodajemo token logiku u `TodoApp` dok ne zavrsimo teoriju cele oblasti.

---

## 1) Authentication naspram authorization

JWT se u transkriptu opisuje kao deo authorization protokola, ali ga je najlakse razumeti kroz oba pojma.

### Authentication

Autentifikacija proverava:

```text
Ko si ti?
```

U nasoj aplikaciji to je:

```text
username + password
    -> pronadji korisnika
    -> verify password
```

### Authorization

Autorizacija proverava:

```text
Sta smes da uradis?
```

JWT omogucava serveru da pri sledecem zahtevu dobije proverljiv identitet i claims korisnika, na osnovu kojih moze da donese authorization odluku.

Na primer:

```text
validan token + role=user
    -> korisnik moze da cita svoje todos

validan token + role=admin
    -> korisnik moze da koristi admin endpoint
```

JWT ne odlucuje sam sta korisnik sme. Aplikacioni kod cita token i primenjuje authorization pravila.

---

## 2) Sta je JWT

JWT je string koji se koristi za prenos JSON podataka izmedju strana, najcesce izmedju klijenta i API servera.

JWT je:

- prenosiv
- samostalan u smislu da nosi claims
- digitalno potpisan
- proverljiv bez cuvanja session objekta na serveru

Primer izgleda:

```text
xxxxx.yyyyy.zzzzz
```

Tri dela su razdvojena tackama:

```text
header.payload.signature
```

Stvarni delovi sadrze Base64URL kodirane vrednosti, pa izgledaju kao duge sekvence karaktera.

JWT nije obicna lozinka i nije bezbedan zato sto izgleda nerazumljivo. Bezbednost dolazi od provere potpisa, tajnog kljuca, pravilnog algoritma, expiration-a i zastite transporta.

---

## 3) JWT nije enkripcija

Ovo je jedna od najvaznijih napomena.

JWT payload je obicno **kodiran**, a ne sifrovan.

Base64URL encoding nije enkripcija. Svako ko dobije JWT moze dekodirati header i payload i procitati claims koji nisu tajni.

Zato u JWT ne treba stavljati:

- password
- `hashed_password`
- API kljuceve
- secret key
- broj kartice
- druge poverljive podatke

JWT treba da sadrzi minimalne podatke potrebne za identitet i authorization.

Primer prihvatljivijih claims:

```json
{
  "sub": "42",
  "role": "user",
  "exp": 1780000000
}
```

I ovaj payload je citljiv klijentu. Potpis sprecava neovlascenu izmenu, ali ne skriva sadrzaj.

Ako je potrebna tajnost payload-a, to je druga tema, poput enkriptovanih tokena ili drugog mehanizma. Standardni potpisani JWT nije zamena za enkripciju.

---

## 4) Tri dela JWT-a

Svaki standardni JWT ima:

```text
1. header
2. payload
3. signature
```

Kombinuju se ovako:

```text
encoded_header.encoded_payload.encoded_signature
```

Tacke nisu deo JSON objekata. One samo razdvajaju komponente tokena.

---

## 5) JWT header

Header opisuje token i algoritam potpisa.

Primer:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### `alg`

Oznacava algoritam koji se koristi za potpis.

U primeru je:

```text
HS256
```

### `typ`

Oznacava tip tokena:

```text
JWT
```

Header se zatim Base64URL kodira i postaje prvi deo tokena.

Vazno: klijent moze procitati header. Sam naziv algoritma nije tajna.

---

## 6) JWT payload

Payload sadrzi claims, odnosno tvrdnje o tokenu, korisniku ili nameni tokena.

Primer:

```json
{
  "sub": "42",
  "name": "Ana Jovanovic",
  "role": "user",
  "exp": 1780000000
}
```

Payload se takodje Base64URL kodira i postaje drugi deo tokena.

### Payload nije mesto za password

Ako se u payload stavi:

```json
{
  "password": "Test1234"
}
```

taj podatak nije bezbedno sakriven. Klijent moze dekodirati payload.

JWT payload treba da bude mali i minimalan.

---

## 7) Claims

Claims su polja u payload-u. Transkript ih deli u tri grupe:

```text
registered claims
public claims
private claims
```

### Registered claims

To su standardizovana imena koja su preporucena, ali ne moraju sva biti prisutna.

Najvaznija u ovoj lekciji su:

```text
iss
sub
exp
```

### Public claims

To su claims koji mogu biti definisani za javnu upotrebu, uz paznju da se izbegne konflikt sa standardnim imenima.

### Private claims

To su dogovorena polja izmedju nase aplikacije i njenih servisa.

Primer:

```json
{
  "role": "admin",
  "user_id": "42"
}
```

Privatni claim nije automatski poverljiv samo zato sto se zove private. I dalje je citljiv ako je token samo potpisan.

---

## 8) `iss` claim

`iss` je skracenica za issuer, odnosno izdavaoca tokena.

Primer:

```json
{
  "iss": "todoapp-api"
}
```

On moze pomoci serveru da zna ko je izdao token.

U sistemu sa vise servisa `iss` moze razlikovati pouzdanog izdavaoca od tokena drugog sistema.

Ako aplikacija koristi `iss`, mora ga dosledno proveravati pri validaciji.

---

## 9) `sub` claim

`sub` je subject, odnosno subjekt tokena.

Najcesce predstavlja identitet korisnika:

```json
{
  "sub": "42"
}
```

U Todo aplikaciji `sub` moze biti ID korisnika iz `Users` tabele.

Buduci tok:

```text
JWT sub = "42"
    -> current user ID = 42
        -> Todos.owner_id == 42
```

`sub` treba da bude jedinstven u opsegu u kom se token koristi. U nekim projektima se cuva kao string iako predstavlja numericki ID.

Ne treba nekriticki verovati samo vrednosti `sub`. Server mora validirati potpis tokena i ostale potrebne claims pre nego sto ga koristi.

---

## 10) `exp` claim

`exp` je expiration time, odnosno vreme isteka tokena.

Primer payload-a:

```json
{
  "sub": "42",
  "exp": 1780000000
}
```

Server pri validaciji proverava da li je trenutni datum pre expiration vremena.

Ako je token istekao:

```text
zahtev se odbija
```

### Zasto token mora da istekne

Ako token nikada ne istekne i procure klijentu ili napadacu, mogao bi dugo da omoguci pristup.

Expiration ogranicava period u kom token vazi.

Kratko trajanje smanjuje rizik, ali moze zahtevati refresh token ili ponovno prijavljivanje.

Transkript pominje primer od oko jednog sata neaktivnosti. Precizno ponasanje zavisi od toga da li sistem koristi:

- absolute expiration
- sliding expiration
- access token + refresh token

Ove razlike dolaze kasnije.

---

## 11) JWT signature

Signature je treci deo JWT-a.

Za HMAC algoritam kao sto je HS256 konceptualno se koristi:

```text
signature = HMAC(
    encoded_header + "." + encoded_payload,
    secret_key,
)
```

Server koristi svoj secret key da proveri da li signature odgovara header-u i payload-u.

Ako neko promeni payload:

```json
{ "role": "user" }
```

u:

```json
{ "role": "admin" }
```

ali ne moze da napravi validan novi potpis bez secret key-a, server ce odbiti token.

### Sta signature obezbedjuje

Signature pomaze da se utvrdi:

- da token dolazi od pouzdanog izdavaoca
- da payload nije menjan
- da token nije nevalidan zbog pogresnog kljuca

### Sta signature ne obezbedjuje

Signature ne skriva payload.

Takodje ne resava automatski:

- ukradeni token
- losu proveru role u aplikaciji
- predug expiration
- logovanje tokena
- HTTPS problem

---

## 12) Secret key

Secret key je vrednost koju server koristi za potpisivanje i proveru tokena.

Kod simetricnog HS256 pristupa isti secret se koristi za:

```text
sign token
verify token
```

Klijent ne sme da zna secret key.

Secret ne treba hardkodovati u routeru:

```python
SECRET_KEY = "learn online"
```

Kursni primer moze koristiti ovakav string radi demonstracije, ali moderniji projekat koristi:

```text
environment variable
    -> settings
        -> security kod
```

U tvom rasporedu buduća lokacija konfiguracije je:

```text
TodoApp/core/config.py
```

Security helper moze biti:

```text
TodoApp/core/security.py
```

Tajne ne treba commit-ovati u git repository.

---

## 13) Bearer token u Authorization header-u

Nakon login-a klijent salje JWT uz svaki protected request.

Standardni oblik header-a je:

```http
Authorization: Bearer <jwt-token>
```

`Bearer` znaci da onaj ko poseduje token moze pokusati da ga koristi.

Zato token treba tretirati kao kredencijal:

- ne slati ga u URL-u
- ne upisivati ga u javne logove
- koristiti HTTPS
- cuvati ga pazljivo na klijentu
- ograniciti mu trajanje

Server cita header, proverava scheme `Bearer`, dekodira token i validira signature/claims.

---

## 14) JWT i stateless server

Kod klasicne server-side session autentifikacije server moze cuvati session podatke u memoriji ili bazi.

Kod stateless JWT pristupa server ne mora cuvati svaki aktivni access token kao session zapis. Token nosi claims, a server proverava potpis pri svakom zahtevu.

To moze olaksati skaliranje:

```text
klijent -> API server 1
klijent -> API server 2
klijent -> API server 3
```

Svaki server koji ima odgovarajucu konfiguraciju moze validirati token.

Ali stateless ne znaci bez rizika. Opoziv tokena pre expiration-a je slozeniji, pa sistemi mogu koristiti:

- kratke access tokene
- refresh tokene
- token revocation listu
- rotaciju kljuceva

---

## 15) JWT u mikroservisima

Transkript opisuje scenario sa vise aplikacija ili mikroservisa.

Ako vise servisa veruje istom izdavaocu i moze validirati potpis, mogu razumeti isti token.

Primer:

```text
Auth service
    -> izdaje token

Todo service
    -> validira token

Admin service
    -> validira token i proverava role
```

U ovom scenariju svaki servis ne mora ponovo da implementira login formu.

Ipak, deljenje istog symmetric secret-a medju velikim brojem servisa povecava blast radius. Ako jedan servis izgubi secret, moze biti ugrozeno vise servisa.

U slozenijim sistemima mogu se koristiti asymmetric algoritmi:

```text
auth service ima private key i potpisuje
ostali servisi imaju public key i proveravaju
```

To je napredna tema i nije deo trenutne implementacije TodoApp projekta.

---

## 16) Sta JWT nije

JWT nije:

- baza podataka
- password hash
- enkripcija
- zamena za HTTPS
- automatska authorization logika
- dokaz da je korisnik i dalje aktivan bez dodatne provere
- dozvola da se u payload stave tajne

JWT je potpisani nosac claims-a koji server moze validirati.

---

## 17) Buduci raspored u tvom TodoApp projektu

Kada dodjemo do implementacije, odgovornosti mogu izgledati ovako:

```text
fast-api-course-my-work/
    TodoApp/
        main.py
        models.py
        schemas.py
        api/
            routes/
                auth.py
                todos.py
                users.py
        core/
            config.py
            security.py
        db/
            base.py
            database.py
            session.py
```

### `api/routes/auth.py`

- login endpoint
- `/token` ruta
- poziv `authenticate_user`
- kreiranje access tokena

### `core/security.py`

- password context
- password verify helper
- JWT encode helper
- JWT decode helper

### `core/config.py`

- secret key iz environment-a
- algorithm
- access token expiration
- eventualni issuer/audience settings

### `api/routes/todos.py`

- protected Todo endpointi
- current user dependency
- `Todos.owner_id` filter

### `db/session.py`

- `get_db()`
- `db_dependency`

### `main.py`

- glavna FastAPI aplikacija
- include router pozivi

---

## 18) Buduci tok autentifikacije i authorization-a

Ciljni tok izgleda ovako:

```text
1. klijent salje username i password
2. auth router poziva authenticate_user
3. server pronalazi Users red
4. server proverava password hash
5. server pravi JWT sa minimalnim claims
6. klijent cuva access token
7. klijent salje Authorization: Bearer token
8. server proverava signature i exp
9. server dobija current user iz sub
10. Todo endpoint filtrira Todos.owner_id
11. authorization proverava role/is_active
```

Ovaj tok povezuje lekcije 07 do 11:

```text
Users tabela
    -> password hash
        -> sacuvani korisnik
            -> authenticate_user
                -> JWT
                    -> current user
                        -> ownership i role authorization
```

---

## 19) Oprez sa JWT debugger alatima

Transkript pominje `jwt.io` za prikaz tokena.

Takvi alati mogu biti korisni za ucenje strukture tokena, ali ne treba unositi:

- pravi production token
- pravi secret key
- licne podatke
- stvarne korisnicke claims

Kod HS256 debug alat koji zna secret moze generisati validan potpis. Zato secret nikada ne treba slati u javni online alat.

Za ucenje koristiti potpuno izmisljene vrednosti.

---

## 20) Sta ova lekcija jos ne implementira

Ova lekcija objasnjava JWT, ali jos ne implementira:

- JWT encode funkciju
- JWT decode funkciju
- access token response model
- current user dependency
- Bearer security dependency u aktivnom kodu
- expiration proveru u endpointu
- role authorization
- Todo ownership filter

Takodje ne menjamo:

```text
TodoApp/main.py
TodoApp/models.py
TodoApp/schemas.py
TodoApp/api/routes/auth.py
TodoApp/core/config.py
TodoApp/core/security.py
```

Sledece lekcije ce postepeno obraditi kreiranje i dekodiranje JWT-a.

---

## 21) Pitanja za proveru znanja

1. Sta znaci JWT?
2. Koja su tri dela JWT-a?
3. Cemu sluzi header?
4. Cemu sluzi payload?
5. Cemu sluzi signature?
6. Da li je Base64URL encoding isto sto i enkripcija?
7. Zasto password ne treba da bude u payload-u?
8. Sta znace claims `iss`, `sub` i `exp`?
9. Zasto je `exp` vazan?
10. Sta signature proverava?
11. Sta secret key treba da zastiti?
12. Zasto secret key ne sme biti hardkodovan u routeru?
13. Kako izgleda Bearer Authorization header?
14. Sta znaci stateless JWT pristup?
15. Koja je razlika izmedju authentication i authorization u JWT toku?
16. Gde u tvom projektu pripadaju `config.py` i `security.py`?
17. Zasto JWT payload nije mesto za tajne podatke?
18. Koje funkcionalnosti jos nedostaju pre zastite Todo ruta?

---

## 22) Prakticni zadaci

### Zadatak 1 - Rastavi JWT

Uzmi izmisljeni token:

```text
header-example.payload-example.signature-example
```

Oznaci:

- prvi deo
- drugi deo
- treci deo
- separator

### Zadatak 2 - Napravi bezbedan payload na papiru

Napravi konceptualni JSON payload sa:

```text
sub
role
exp
```

Ne koristi pravi username, email, password ili secret.

Objasni cemu sluzi svako polje.

### Zadatak 3 - Pronadji nebezbedne claims

Oznaci koja polja ne treba staviti u JWT payload:

```text
sub
role
exp
password
hashed_password
secret_key
email
```

Napomena: email moze biti osetljiv u zavisnosti od aplikacije, pa odluku treba donositi svesno.

### Zadatak 4 - Nacrtaj JWT tok

Nacrtaj:

```text
header + payload + secret
    -> signature
        -> JWT
```

Zatim nacrtaj validaciju:

```text
JWT + server secret
    -> validan ili nevalidan token
```

### Zadatak 5 - Izmeni payload bez tajne

Na papiru promeni:

```json
{ "role": "user" }
```

u:

```json
{ "role": "admin" }
```

Objasni zasto server treba da odbije token ako signature nije ponovo validno napravljen.

### Zadatak 6 - Authorization header

Napisi tacan oblik header-a:

```http
Authorization: Bearer <token>
```

Objasni zasto se token ne stavlja u URL query parametar.

### Zadatak 7 - Povezi `sub` sa Todo ownership-om

Nacrtaj tok:

```text
JWT sub = 7
    -> current_user_id = 7
        -> Todos.owner_id == 7
```

Objasni zasto ovaj tok mora da pocne validacijom signature-a.

### Zadatak 8 - Odredi fajlove

Za svaki deo odredi lokaciju:

```text
SECRET_KEY
JWT_ALGORITHM
access token expiration
JWT encode
JWT decode
/token endpoint
current user dependency
Todos.owner_id filter
```

Koristi:

```text
TodoApp/core/config.py
TodoApp/core/security.py
TodoApp/api/routes/auth.py
TodoApp/api/routes/todos.py
```

### Zadatak 9 - Expiration scenario

Pretpostavi da je token istekao, ali signature je validan.

Odgovori:

- da li token treba prihvatiti
- koji claim proveravas
- zasto validan signature nije dovoljan

### Zadatak 10 - Mikroservis scenario

Zamisli tri servisa:

```text
auth service
todo service
admin service
```

Objasni kako mogu koristiti isti issuer i validirati token, a zatim navedi jedan rizik deljenja istog symmetric secret-a.

### Zadatak 11 - Debug alat bezbednost

Objasni zasto ne treba nalepiti pravi token i secret key u javni JWT debugger.

Napisi koje izmisljene podatke bi koristio za vezbu.

### Zadatak 12 - Plan implementacije

Napisi redosled buducih implementacionih lekcija:

```text
JWT config
JWT encode
JWT decode
OAuth2 Bearer dependency
current user
Todo authorization
```

Za svaki korak navedi fajl u tvom `TodoApp` rasporedu.

---

## 23) Zakljucak

JWT je potpisani JSON Web Token koji se najcesce salje ovako:

```http
Authorization: Bearer <jwt>
```

Njegova struktura je:

```text
header.payload.signature
```

Za tvoj projekat najvaznije je zapamtiti:

- JWT omogucava prenos proverljivih claims-a izmedju klijenta i servera
- payload je kodiran, ali standardni JWT nije enkriptovan
- signature otkriva neovlascenu izmenu
- secret key ostaje samo na serveru
- `exp` ogranicava trajanje tokena
- `sub` moze nositi ID korisnika
- Bearer token se salje kroz Authorization header
- JWT nije zamena za password hashing, HTTPS ili authorization pravila
- `core/config.py` je mesto za konfiguraciju
- `core/security.py` je buduce mesto za token i password helper funkcije
- `api/routes/auth.py` ostaje mesto za auth endpoint-e
- `api/routes/todos.py` koristi current user i ownership filtere

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
