# Passlib naspram pwdlib - detaljan teorijski materijal

## Kratak odgovor za tvoj trenutni plan

Da. Odabrani redosled je dobar:

1. prvo prati kursni primer sa `Passlib` i `CryptContext`
2. razumi tok `hash()` pri registraciji i `verify()` pri login-u
3. zavrsi teoriju lekcija 08-14
4. uradi kursnu prakticnu implementaciju
5. zatim izdvoji password logiku i zameni implementaciju sa `pwdlib`

Ne moras cekati SQLAlchemy 2.0 refaktorisanje da bi presao na `pwdlib`. Ove dve promene su uglavnom nezavisne. Ipak, za ucenje je korisno da prvo zavrsis jednu konzistentnu kursnu verziju, umesto da istovremeno menjas ORM, auth tok i password biblioteku.

Ovaj fajl objasnjava:

- sta je zajednicko za `Passlib` i `pwdlib`
- koje razlike postoje u API-ju i algoritmu
- koliko kursni primer zavisi od izabrane biblioteke
- kako se naredne lekcije 09-14 oslanjaju na password hashing
- kako kasnije uraditi migraciju bez menjanja password-a korisnika

---

## 1) Najvaznija podela: koncept naspram implementacije

Kurs uci konceptualni tok:

```text
plain password pri registraciji
	-> password hash
		-> hashed_password u bazi

plain password pri login-u + saved hash
	-> verify
		-> True ili False
```

Ovaj tok nije vlasnistvo `Passlib` biblioteke. Isti princip vazi za `pwdlib` i za druge proverene password hashing interfejse.

### Zajednicki koncept

Obe biblioteke treba da omoguce:

```python
hashed_password = hash(plain_password)
is_valid = verify(plain_password, hashed_password)
```

Aplikacija treba da:

- nikada ne cuva plain password
- nikada ne vraca password ili hash u javnom response-u
- koristi `verify()` umesto ponovnog hashovanja i poredjenja stringova
- cuva hash u koloni kao sto je `Users.hashed_password`
- koristi isti interfejs za proveru pri svakom login-u

### Konkretna implementacija

Biblioteka odredjuje:

- naziv klase koju importujemo
- nacin konfiguracije algoritma
- algoritam i njegove podrazumevane parametre
- format novog hash stringa
- nacin provere i eventualne migracije hash-a

Zato se poslovna logika ne sme rasuti po endpointima. Najbolje je da endpoint poziva male helper funkcije:

```python
hashed_password = hash_password(plain_password)
is_valid = verify_password(plain_password, saved_hash)
```

Tada se biblioteka moze zameniti unutar security sloja, dok `auth.py` zadrzava isti tok.

---

## 2) Sta je `Passlib`

`Passlib` je biblioteka koja daje zajednicki interfejs za vise password hashing shema. Kurs koristi njen objekat `CryptContext`:

```python
from passlib.context import CryptContext

bcrypt_context = CryptContext(
	schemes=["bcrypt"],
	deprecated="auto",
)
```

Kursni kod zatim koristi:

```python
hashed_password = bcrypt_context.hash(plain_password)

is_valid = bcrypt_context.verify(
	plain_password,
	saved_hash,
)
```

### Zasto je `CryptContext` koristan

`CryptContext` centralizuje password hashing konfiguraciju. On zna:

- koje scheme aplikacija koristi
- kako se pravi novi hash
- kako se proverava postojeci hash
- kako se prepoznaje format hash-a
- koje scheme su zastarele

To je dobar edukativni model jer jasno pokazuje da endpoint ne treba da zna detalje bcrypt algoritma.

### Da li je `Passlib` amaterski izbor

Ne u smislu osnovnih bezbednosnih koncepata. `Passlib` je dugo bio poznat i koristan projekat, a `bcrypt` kao algoritam nije amaterski.

Medjutim, kursni izbor jeste stariji i treba ga posmatrati kao **legacy ili edukativnu kombinaciju**, a ne kao automatski najbolji izbor za novi projekat. Vazne napomene su:

- `Passlib` nije biblioteka koju treba slepo birati za novi projekat bez provere odrzavanja
- `bcrypt==4.0.1` je pin iz konkretnog kursnog okruzenja
- kompatibilnost izmedju `Passlib` i novijih `bcrypt` verzija moze biti problem
- verziju iz kursa ne treba tretirati kao univerzalnu preporuku za 2026. godinu

Dakle, zastarelost se odnosi prvenstveno na biblioteku, verzioni pin i ekosistemsku kompatibilnost. Ne odnosi se na ideju da se password hash-uje i proverava pomocu `verify()`.

---

## 3) Sta je `pwdlib`

`pwdlib` je moderniji password hashing interfejs koji se uklapa u isti konceptualni tok. U modernom FastAPI primeru moze se koristiti ovako:

```bash
pip install "pwdlib[argon2]"
```

Primer:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

hashed_password = password_hash.hash(plain_password)

is_valid = password_hash.verify(
	plain_password,
	saved_hash,
)
```

`PasswordHash.recommended()` bira preporucenu konfiguraciju za podrzani password hashing backend. U prikazanom modernom FastAPI obrascu koristi se Argon2 backend, ali konkretan izbor i verzije treba proveriti u dokumentaciji i okruzenju projekta.

### Zasto se cesto pominje Argon2

Password hashing algoritam treba da bude projektovan tako da masovno pogadjanje bude skupo. Argon2 je memory-hard algoritam i cesto se bira u novim projektima kada nema zahteva za kompatibilnost sa starim bcrypt hash-ovima.

To ipak ne znaci:

- da svaki projekat mora odmah menjati bcrypt
- da sama biblioteka automatski resava sve security probleme
- da algoritam treba birati bez provere zahteva projekta

Bezbednost zavisi i od jacine password-a, secret konfiguracije, zastite endpointa, rate limiting-a, logovanja i pravilnog cuvanja podataka.

---

## 4) Direktno poredjenje

| Tema                             | Passlib + bcrypt                      | pwdlib + preporuceni backend                             |
| -------------------------------- | ------------------------------------- | -------------------------------------------------------- |
| Glavna uloga                     | Password hashing interfejs            | Password hashing interfejs                               |
| Kursni API                       | `CryptContext`                        | `PasswordHash`                                           |
| Kreiranje hash-a                 | `context.hash(password)`              | `password_hash.hash(password)`                           |
| Provera                          | `context.verify(password, hash)`      | `password_hash.verify(password, hash)`                   |
| Algoritam u kursu                | bcrypt                                | moderni preporuceni backend, cesto Argon2                |
| Format hash-a                    | bcrypt format, npr. `$2b$...`         | format koji pripada izabranom backend-u                  |
| Zajednicki princip               | hash + verify                         | hash + verify                                            |
| Direktna kompatibilnost hash-eva | Samo sa podrzanim Passlib scheme-ama  | Ne treba pretpostaviti bcrypt kompatibilnost bez provere |
| Pogodno za razumevanje kursa     | Da                                    | Da, ali odstupa od transkripta                           |
| Pogodno za novi kod              | Proveriti odrzavanje i kompatibilnost | Cesto jednostavniji moderni izbor                        |

Najvaznija posledica je da hash napravljen bcrypt algoritmom nije samo obican tekst koji mozemo automatski tretirati kao Argon2 hash. Format nosi informaciju o algoritmu.

---

## 5) Da li se menja baza

Ne menja se SQLAlchemy model samo zato sto se menja password hashing biblioteka.

Kolona moze ostati:

```python
hashed_password = Column(String)
```

ili odgovarajuca SQLAlchemy 2.0 deklaracija.

U oba slucaja u koloni se cuva tekstualni hash:

```text
bcrypt hash  -> jedan tekstualni format
Argon2 hash  -> drugi tekstualni format
```

Pre prelaska proveri samo da kolona ima dovoljno prostora za format koji koristis. U praksi je `String` bez suvise malog ogranicenja uobicajen izbor, ali konkretan model i baza projekta imaju poslednju rec.

Ne treba:

- cuvati algoritam u posebnoj koloni bez razloga
- rucno seci hash string
- menjati `hashed_password` u `password`
- pokusavati da de-hashujes stare vrednosti

Hash se ne dekriptuje. Ako se algoritam menja, stari hash se verifikuje starim algoritmom, a novi se pravi novim algoritmom.

---

## 6) Da li se menjaju sheme

Uobicajeno ne.

Request schema pri registraciji i login formi i dalje imaju plain password samo u memoriji tokom obrade zahteva:

```python
class CreateUserRequest(BaseModel):
	username: str
	password: str
```

Response schema ne treba da ima ni plain password ni `hashed_password`:

```python
class UserResponse(BaseModel):
	id: int
	username: str
	email: str
	role: str
	is_active: bool
```

Promena iz `Passlib` u `pwdlib` ne menja javni API ugovor. Menja se samo unutrasnja implementacija hashovanja.

---

## 7) Zavisnost po lekcijama 09-14

### Lekcija 09 - Cuvanje korisnika u bazu

Zavisi od password biblioteke samo u jednom koraku:

```text
CreateUserRequest.password
	-> hash_password(...)
		-> Users.hashed_password
```

`db.add()` i `db.commit()` nemaju nikakve veze sa tim da li hash pravi `Passlib` ili `pwdlib`.

Razlika u kodu je samo u helperu ili importu. Ostatak endpointa ostaje isti.

### Lekcija 10 - Autentifikacija korisnika

Ova lekcija direktno koristi password biblioteku:

```python
verify_password(
	entered_password,
	user.hashed_password,
)
```

Ako se promeni biblioteka, mora se promeniti implementacija `verify_password()`. Tok lekcije ostaje isti:

```text
pronadji user
	-> procitaj user.hashed_password
		-> verify
			-> user ili neuspesna autentifikacija
```

### Lekcija 11 - JWT

JWT ne proverava password. JWT dolazi posle uspesne autentifikacije.

Biblioteka za password hashing moze biti bilo koja kompatibilna biblioteka, jer JWT helper prima rezultat autentifikacije, na primer korisnika ili njegov ID.

```text
password verify uspe
	-> create_access_token(user.id)
```

JWT lekcija ima svoje zasebne teme:

- secret key
- algoritam potpisa
- claims
- expiration
- `python-jose` ili druga JWT biblioteka

### Lekcija 12 - Encoding JWT-a

Ne zavisi od `Passlib` ili `pwdlib`.

Ova lekcija dobija vec autentifikovanog korisnika i pravi token. Password hash ne treba stavljati u payload.

### Lekcija 13 - Dekodiranje JWT-a

Ne zavisi od password biblioteke.

Ona proverava JWT signature, algoritam, expiration i claims. `OAuth2PasswordBearer` izdvaja Bearer token, a JWT biblioteka ga validira.

### Lekcija 14 - Poboljsanja autentifikacije

Ne zavisi direktno od password biblioteke. HTTP 401, router prefix, tagovi i `tokenUrl` ostaju isti.

Jedina indirektna veza je sto neuspesan `verify()` treba da vodi ka standardnom 401 odgovoru.

### Tabela zavisnosti

| Lekcija                | Direktna zavisnost od password biblioteke | Sta se menja pri migraciji         |
| ---------------------- | ----------------------------------------: | ---------------------------------- |
| 09 - save user         |                  Da, pri kreiranju hash-a | `hash_password()` implementacija   |
| 10 - authenticate user |                           Da, pri proveri | `verify_password()` implementacija |
| 11 - JWT               |                                        Ne | Nista zbog password biblioteke     |
| 12 - encode JWT        |                                        Ne | Nista zbog password biblioteke     |
| 13 - decode JWT        |                                        Ne | Nista zbog password biblioteke     |
| 14 - enhancements      |                           Samo indirektno | Nista ili samo poziv auth helpera  |

---

## 8) Kako da pratiš kursnu verziju bez zakljucavanja za buducnost

U teoriji mozes uciti kursni oblik:

```python
bcrypt_context = CryptContext(
	schemes=["bcrypt"],
	deprecated="auto",
)
```

U prakticnom kodu je korisno odmah imati jedan mali sloj pomocnih funkcija:

```python
def hash_password(password: str) -> str:
	return bcrypt_context.hash(password)


def verify_password(password: str, saved_hash: str) -> bool:
	return bcrypt_context.verify(password, saved_hash)
```

Tada `auth.py` ne mora svuda da zna da postoji `CryptContext`.

Kasnija migracija menja samo security modul:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
	return password_hash.hash(password)


def verify_password(password: str, saved_hash: str) -> bool:
	return password_hash.verify(password, saved_hash)
```

Registracioni endpoint i login endpoint zadrzavaju pozive:

```python
hash_password(create_user_request.password)
verify_password(form_data.password, user.hashed_password)
```

To je razlog zasto se password logika izdvaja iz routera.

---

## 9) Vazna migraciona zamka: stari hash-evi

Ako si korisnike vec kreirao pomocu bcrypt-a, ne smes samo promeniti biblioteku i pretpostaviti da ce novi backend razumeti sve stare hash-eve.

Postoje tri moguca pristupa.

### Pristup A - obrisati razvojne korisnike

Ako je projekat jos ucenicki i baza nema vazne podatke:

1. promenis security biblioteku
2. napravis novu praznu razvojnu bazu ili obrises test korisnike
3. registrujes korisnike ponovo
4. proveris novi format hash-a

Ovo je najjednostavniji pristup za tvoj trenutni portfolio projekat, pod uslovom da baza nema podatke koje moras sacuvati.

### Pristup B - podrzati oba formata tokom migracije

Ako postoje korisnici koje moras sacuvati:

```text
login
	-> prepoznaj format starog hash-a
		-> proveri odgovarajucim algoritmom
			-> ako je login uspean, napravi novi hash
				-> sacuvaj modernizovani hash
```

Ovo se zove postupna migracija pri login-u. Zahteva da aplikacija privremeno zna i stari i novi backend.

### Pristup C - reset password-a

Korisnicima se posalje tok za postavljanje novog password-a. Nakon uspesnog resetovanja cuva se samo novi format.

Ne treba pokusavati konverziju bez plain password-a:

```text
bcrypt hash -> Argon2 hash
```

To nije moguce direktno jer bcrypt hash nije originalni password. Potrebno je da korisnik ponovo unese password ili da se uspešno autentifikuje.

---

## 10) Sta se ne menja pri prelasku na `pwdlib`

Sledece ideje ostaju potpuno iste:

```text
password nije enkriptovan u bazi
hash je jednosmeran rezultat
salt pravi razlicite hash-eve za isti password
verify prima plain password i saved hash
hash se ne vraca u javnom response-u
JWT ne treba da sadrzi password ili hashed_password
```

Takodje ostaju iste odgovornosti modula:

```text
auth.py
	request/response i tok endpointa

security.py
	hash, verify, JWT helperi

models.py
	Users ORM model

schemas.py
	request i response validacija

db/session.py
	SQLAlchemy session dependency
```

---

## 11) Sta se menja pri prelasku na `pwdlib`

Menja se uglavnom:

- dependency u `requirements.txt`
- import
- instanca password hashing objekta
- format novih hash vrednosti
- testovi koji proveravaju konkretan format, ako takvi postoje
- migraciona strategija za stare korisnike

Ne treba menjati:

- naziv request polja `password`
- naziv baze `hashed_password`, osim ako postoji poseban razlog
- `Users` relaciju sa `Todos`
- JWT claims samo zato sto je promenjen password backend
- SQLAlchemy session kod
- router prefix i HTTP status kodove

---

## 12) Razlika izmedju password hashing-a i JWT potpisa

Ove dve teme se cesto pomesaju jer se obe koriste u authentication sistemu.

### Password hashing

```text
plain password
	-> password hash
		-> cuva se u bazi
```

Koristi se da aplikacija bezbednije cuva password.

### JWT signing

```text
claims + secret key
	-> potpisani JWT
```

Koristi se da server moze da proveri da token nije promenjen.

Password hash i JWT signature nisu ista stvar:

- password hash nije token
- JWT nije password hash
- password hash se ne stavlja u JWT
- promena `Passlib` u `pwdlib` ne zahteva promenu JWT logike

---

## 13) Preporuceni redosled rada za tvoj `TodosApp`

### Faza 1 - kursno razumevanje

Uciti i zapisati:

```text
CryptContext
hash()
verify()
salt
hashed_password
authenticate_user()
```

U ovoj fazi je normalno da kod prati transkript.

### Faza 2 - kursna implementacija

Implementirati tok:

```text
register
	-> hash password
		-> Users.hashed_password
			-> db.add
				-> db.commit

login
	-> query user
		-> verify password
			-> create JWT
```

Testirati da se plain password ne pojavljuje u bazi i response-u.

### Faza 3 - izolovanje security logike

Izdvojiti:

```text
TodoApp/core/security.py
```

Uvesti helper funkcije:

```python
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

### Faza 4 - migracija na `pwdlib`

Tek kada kursni tok radi:

1. dodaj odgovarajuci `pwdlib` dependency
2. zameni implementaciju helpera
3. proveri nove registracije
4. proveri login sa novim hash-evima
5. odluci sta radis sa starim bcrypt korisnicima
6. ukloni `Passlib` tek kada vise nije potreban

### Faza 5 - SQLAlchemy 2.0 refaktorisanje

SQLAlchemy 2.0 mozes raditi pre ili posle `pwdlib` migracije. Prakticno je da promene budu odvojene:

```text
promena A: password backend
promena B: SQLAlchemy query/model stil
```

Ako se obe rade istovremeno, teze je utvrditi da li je greska u auth logici, hash biblioteci ili ORM kodu.

---

## 14) Minimalni testovi koji vaze za obe biblioteke

Ovi testovi proveravaju koncept, a ne naziv biblioteke:

```python
def test_password_is_not_saved_as_plain_text():
	password = "Test1234!"
	saved_hash = hash_password(password)

	assert saved_hash != password


def test_correct_password_is_verified():
	password = "Test1234!"
	saved_hash = hash_password(password)

	assert verify_password(password, saved_hash) is True


def test_wrong_password_is_rejected():
	saved_hash = hash_password("Test1234!")

	assert verify_password("WrongPassword!", saved_hash) is False


def test_same_password_does_not_require_equal_hash_strings():
	first_hash = hash_password("Test1234!")
	second_hash = hash_password("Test1234!")

	assert first_hash != second_hash
	assert verify_password("Test1234!", first_hash) is True
	assert verify_password("Test1234!", second_hash) is True
```

Ne treba testirati implementaciju ovako:

```python
assert saved_hash.startswith("$2b$")
```

osim ako je cilj bas kursna bcrypt konfiguracija. Takav test ce se ocekivano promeniti pri prelasku na `pwdlib` i Argon2.

---

## 15) Cesta pitanja

### Da li moram ponovo menjati podatke u bazi kada promenim biblioteku?

Ne automatski. Postojeci bcrypt hash-evi ostaju validni za bcrypt proveru. Problem nastaje samo ako novi backend ne zna da ih proveri. Tada biras brisanje razvojnih podataka, dvostruku podrsku ili reset password-a.

### Da li `pwdlib` menja SQLAlchemy model?

Ne. Menja se vrednost koja se upisuje u `hashed_password`, ne uloga ORM modela.

### Da li se menja JWT?

Ne. JWT se kreira tek nakon uspesne provere password-a i ima zasebnu biblioteku i konfiguraciju.

### Da li `Passlib` znaci da je ceo kurs los?

Ne. Kursni primer je koristan za ucenje auth toka, ali konkretne dependency izbore treba osveziti za novi projekat. Dobro je uciti stabilan koncept, a zatim proveriti aktuelni alat.

### Da li mogu odmah koristiti `pwdlib` i preskociti Passlib?

Tehnicki da, ali za tvoj plan nije potrebno. Ako pratis transkript, `Passlib` ce ti olaksati razumevanje njegovog koda. Posle toga `pwdlib` moze biti mali, jasan refaktorisuci korak.

### Da li je `bcrypt==4.0.1` univerzalno bezbedna verzija?

Ne. To je konkretan kursni pin koji je izabran zbog kompatibilnosti okruzenja. Verziju treba posmatrati u kontekstu Python verzije, Passlib kompatibilnosti, statusa odrzavanja i bezbednosnih preporuka.

---

## 16) Zadaci za proveru razumevanja

### Zadatak 1 - Oznaci odgovornost

Za svaku stavku napisi da li pripada password hashing-u ili JWT-u:

```text
salt
CryptContext
PasswordHash
secret key
exp claim
verify(password, saved_hash)
Bearer token
```

### Zadatak 2 - Uporedi pozive

Napravi tabelu za:

```python
bcrypt_context.hash(password)
password_hash.hash(password)
bcrypt_context.verify(password, saved_hash)
password_hash.verify(password, saved_hash)
```

### Zadatak 3 - Pronadji granicu

Objasni koji deo sledeceg toka zavisi od password biblioteke:

```text
form data
	-> authenticate_user
		-> verify
			-> user
				-> create_access_token
					-> JWT
```

### Zadatak 4 - Plan migracije

Napravi plan za slucaj u kome baza vec ima bcrypt korisnike, a novi kod treba da koristi Argon2. Navedi najmanje dve moguce strategije i njihove posledice.

### Zadatak 5 - Razdvoji promene

Napravi dva odvojena commit plana na papiru:

```text
commit A: password backend migracija
commit B: SQLAlchemy 2.0 refaktorisanje
```

Za svaki napisi koje fajlove bi ocekivao da menjas i koje testove bi pokrenuo.

---

## 17) Zakljucak

Za naredne lekcije mozes bez problema nastaviti sa kursnom kombinacijom `Passlib + bcrypt`, jer je cilj da razumes ceo auth tok. Sledece lekcije ne postaju neupotrebljive ako kasnije predjes na `pwdlib`.

Direktno su vezane za password biblioteku samo:

```text
Lekcija 09 - hash pri cuvanju korisnika
Lekcija 10 - verify pri autentifikaciji
```

Lekcije 11-14 uglavnom koriste rezultat autentifikacije i bave se JWT-om, Bearer tokenom, current user dependency-jem, HTTP statusima i organizacijom ruta.

Najbolji plan za tvoj projekat je:

```text
kursni koncept
	-> kursna implementacija
		-> testovi
			-> security helper sloj
				-> pwdlib migracija
					-> odvojeni SQLAlchemy 2.0 refaktorisanje
```

Kursni izbor nije amaterski u osnovnom konceptu, ali je tehnicki stariji. Nauci ga kao mapu problema, a `pwdlib` uvedi kao svesnu modernizaciju kada zavrsis kursni tok.
