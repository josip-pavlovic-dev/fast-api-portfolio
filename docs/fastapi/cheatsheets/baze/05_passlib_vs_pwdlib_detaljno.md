# Passlib naspram pwdlib - detaljan teorijski materijal

## Kratak odgovor za tvoj trenutni plan

Da. Odabrani redosled je dobar:

1. Prvo prati kursni primer sa `Passlib` i `CryptContext`
2. Razumi tok `hash()` pri registraciji i `verify()` pri login-u
3. Završi teoriju lekcija 08-14
4. Uradi kursnu prakticnu implementaciju
5. Zatim izdvoji password logiku i zameni implementaciju sa `pwdlib`

Ne moraš čekati SQLAlchemy 2.0 refaktorisanje da bi prešao na `pwdlib`. Ove dve promene su uglavnom nezavisne. Ipak, za učenje je korisno da prvo završiš jednu konzistentnu kursnu verziju, umesto da istovremeno menjaš ORM, auth tok i password biblioteku.

Ovaj fajl objašnjava:

- šta je zajedničko za `Passlib` i `pwdlib`
- koje razlike postoje u API-ju i algoritmu
- koliko kursni primer zavisi od izabrane biblioteke
- kako se naredne lekcije 09-14 oslanjaju na password hashing
- kako kasnije uraditi migraciju bez menjanja password-a korisnika

---

## 1) Najvažnija podela: koncept naspram implementacije

Kurs uči konceptualni tok:

```text
plain password pri registraciji
	-> password hash
		-> hashed_password u bazi

plain password pri login-u + saved hash
	-> verify
		-> True ili False
```

Ovaj tok nije vlasništvo `Passlib` biblioteke. Isti princip važi za `pwdlib` i za druge proverene password hashing interfejse.

### Zajednički koncept

Obe biblioteke treba da omoguće:

```python
hashed_password = hash(plain_password)
is_valid = verify(plain_password, hashed_password)
```

Aplikacija treba da:

- nikada ne čuva plain password
- nikada ne vraća password ili hash u javnom response-u
- koristi `verify()` umesto ponovnog hashovanja i poređenja stringova
- čuva hash u koloni kao što je `Users.hashed_password`
- koristi isti interfejs za proveru pri svakom login-u

### Konkretna implementacija

Biblioteka određuje:

- naziv klase koju importujemo
- način konfiguracije algoritma
- algoritam i njegove podrazumevane parametre
- format novog hash stringa
- način provere i eventualne migracije hash-a

Zato se poslovna logika ne sme rasuti po endpointima. Najbolje je da endpoint poziva male helper funkcije:

```python
hashed_password = hash_password(plain_password)
is_valid = verify_password(plain_password, saved_hash)
```

Tada se biblioteka može zameniti unutar security sloja, dok `auth.py` zadržava isti tok.

---

## 2) Šta je `Passlib`

`Passlib` je biblioteka koja daje zajednički interfejs za više password hashing shema. Kurs koristi njen objekat `CryptContext`:

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

---

### Zašto je `CryptContext` koristan

`CryptContext` centralizuje password hashing konfiguraciju. On zna:

- koje scheme aplikacija koristi
- kako se pravi novi hash
- kako se proverava postojeci hash
- kako se prepoznaje format hash-a
- koje scheme su zastarele

To je dobar edukativni model jer jasno pokazuje da endpoint ne treba da zna detalje bcrypt algoritma.

---

### Da li je `Passlib` amaterski izbor

Ne u smislu osnovnih bezbednosnih koncepata. `Passlib` je dugo bio poznat i koristan projekat, a `bcrypt` kao algoritam nije amaterski.

Medjutim, kursni izbor jeste stariji i treba ga posmatrati kao **legacy ili edukativnu kombinaciju**, a ne kao automatski najbolji izbor za novi projekat. Vazne napomene su:

- `Passlib` nije biblioteka koju treba slepo birati za novi projekat bez provere odrzavanja
- `bcrypt==4.0.1` je pin iz konkretnog kursnog okruzenja
- kompatibilnost izmedju `Passlib` i novijih `bcrypt` verzija moze biti problem
- verziju iz kursa ne treba tretirati kao univerzalnu preporuku za 2026. godinu

Dakle, zastarelost se odnosi prvenstveno na biblioteku, verzioni pin i ekosistemsku kompatibilnost. Ne odnosi se na ideju da se password hash-uje i proverava pomocu `verify()`.

---

## 3) Šta je `pwdlib`

`pwdlib` je moderniji password hashing interfejs koji se uklapa u isti konceptualni tok. U modernom FastAPI primeru može se koristiti ovako:

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

---

### Zašto se često pominje Argon2

Password hashing algoritam treba da bude projektovan tako da masovno pogađanje bude skupo. Argon2 je memory-hard algoritam i često se bira u novim projektima kada nema zahteva za kompatibilnost sa starim bcrypt hash-ovima.

To ipak ne znači:

- da svaki projekat mora odmah menjati bcrypt-a
- da sama biblioteka automatski resava sve security probleme
- da algoritam treba birati bez provere zahteva projekta

Bezbednost zavisi i od jačine password-a, secret konfiguracije, zaštite endpointa, rate limiting-a, logovanja i pravilnog čuvanja podataka.

---

## 4) Direktno poređenje

| Tema                             | Passlib + bcrypt                      | pwdlib + preporučeni backend                             |
| -------------------------------- | ------------------------------------- | -------------------------------------------------------- |
| Glavna uloga                     | Password hashing interfejs            | Password hashing interfejs                               |
| Kursni API                       | `CryptContext`                        | `PasswordHash`                                           |
| Kreiranje hash-a                 | `context.hash(password)`              | `password_hash.hash(password)`                           |
| Provera                          | `context.verify(password, hash)`      | `password_hash.verify(password, hash)`                   |
| Algoritam u kursu                | bcrypt                                | moderni preporučeni backend, često Argon2                |
| Format hash-a                    | bcrypt format, npr. `$2b$...`         | format koji pripada izabranom backend-u                  |
| Zajednicki princip               | hash + verify                         | hash + verify                                            |
| Direktna kompatibilnost hash-eva | Samo sa podrzanim Passlib scheme-ama  | Ne treba pretpostaviti bcrypt kompatibilnost bez provere |
| Pogodno za razumevanje kursa     | Da                                    | Da, ali odstupa od transkripta                           |
| Pogodno za novi kod              | Proveriti odrzavanje i kompatibilnost | Cesto jednostavniji moderni izbor                        |

Najvažnija posledica je da hash napravljen bcrypt algoritmom nije samo običan tekst koji možemo automatski tretirati kao Argon2 hash. Format nosi informaciju o algoritmu.

---

## 5) Da li se menja baza

Ne menja se SQLAlchemy model samo zato što se menja password hashing biblioteka.

Kolona može ostati:

```python
hashed_password = Column(String)
```

ili odgovarajuća SQLAlchemy 2.0 deklaracija.

U oba slucaja u koloni se cuva tekstualni hash:

```text
bcrypt hash  -> jedan tekstualni format
Argon2 hash  -> drugi tekstualni format
```

Pre prelaska proveri samo da kolona ima dovoljno prostora za format koji koristiš. U praksi je `String` bez suviše malog ograničenja uobičajen izbor, ali konkretan model i baza projekta imaju poslednju reč.

Ne treba:

- čuvati algoritam u posebnoj koloni bez razloga
- ručno seći hash string
- menjati `hashed_password` u `password`
- pokušavati da de-hashuješ stare vrednosti

Hash se ne dekriptuje. Ako se algoritam menja, stari hash se verifikuje starim algoritmom, a novi se pravi novim algoritmom.

---

## 6) Da li se menjaju sheme

Uobičajeno ne.

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

Promena iz `Passlib` u `pwdlib` ne menja javni API ugovor. Menja se samo unutrašnja implementacija hashovanja.

---

## 7) Zavisnost po lekcijama 09-14

### Lekcija 09 - čuvanje korisnika u bazi

Zavisi od password biblioteke samo u jednom koraku:

```text
CreateUserRequest.password
	-> hash_password(...)
		-> Users.hashed_password
```

`db.add()` i `db.commit()` nemaju nikakve veze sa tim da li hash pravi `Passlib` ili `pwdlib`.

Razlika u kodu je samo u helperu ili importu. Ostatak endpointa ostaje isti.

---

### Lekcija 10 - autentifikacija korisnika

Ova lekcija direktno koristi password biblioteku:

```python
verify_password(
	entered_password,
	user.hashed_password,
)
```

Ako se promeni biblioteka, mora se promeniti implementacija `verify_password()`. Tok lekcije ostaje isti:

```text
pronađi user
	-> pročitaj user.hashed_password
		-> verify
			-> user ili neuspešna autentifikacija
```

---

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

---

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

U teoriji mozes ući kursni oblik:

```python
bcrypt_context = CryptContext(
	schemes=["bcrypt"],
	deprecated="auto",
)
```

U praktičnom kodu je korisno odmah imati jedan mali sloj pomoćnih funkcija:

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

Registracioni endpoint i login endpoint zadržavaju pozive:

```python
hash_password(create_user_request.password)
verify_password(form_data.password, user.hashed_password)
```

To je razlog zašto se password logika izdvaja iz routera.

---

## 9) Važna migraciona zamka: stari hash-evi

Ako si korisnike već kreirao pomoću bcrypt-a, ne smeš samo promeniti biblioteku i pretpostaviti da će novi backend razumeti sve stare hash-eve.

Postoje tri moguća pristupa.

### Pristup A - obrisati razvojne korisnike

Ako je projekat još učenički i baza nema važne podatke:

1. promeniš security biblioteku
2. napraviš novu praznu razvojnu bazu ili obrišeš test korisnike
3. registruješ korisnike ponovo
4. proveriš novi format hash-a

Ovo je najjednostavniji pristup za tvoj trenutni portfolio projekat, pod uslovom da baza nema podatke koje moras sacuvati.

---

### Pristup B - podržati oba formata tokom migracije

Ako postoje korisnici koje moraš sačuvati:

```text
login
	-> prepoznaj format starog hash-a
		-> proveri odgovarajucim algoritmom
			-> ako je login uspean, napravi novi hash
				-> sacuvaj modernizovani hash
```

Ovo se zove postupna migracija pri login-u. Zahteva da aplikacija privremeno zna i stari i novi backend.

---

### Pristup C - reset password-a (ponovno postavljanje lozinke)

Korisnicima se pošalje tok za postavljanje novog password-a. Nakon uspešnog resetovanja čuva se samo novi format.

Ne treba pokušavati konverziju bez plain password-a:

```text
bcrypt hash -> Argon2 hash
```

To nije moguće direktno jer bcrypt hash nije originalni password. Potrebno je da korisnik ponovo unese password ili da se uspešno autentifikuje.

---

## 10) Šta se ne menja pri prelasku na `pwdlib`

Sledeće ideje ostaju potpuno iste:

```text
password nije enkriptovan u bazi
hash je jednosmeran rezultat
salt pravi razlicite hash-eve za isti password
verify prima plain password i saved hash
hash se ne vraca u javnom response-u
JWT ne treba da sadrži password ili hashed_password
```

Takođe ostaju iste odgovornosti modula:

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

## 11) Šta se menja pri prelasku na `pwdlib`

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

## 12) Razlika između password hashing-a i JWT potpisa

Ove dve teme se često pomešaju jer se obe koriste u authentication sistemu.

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

Password hash i JWT potpis (signature) nisu ista stvar:

- password hash nije token
- JWT nije password hash
- password hash se ne stavlja u JWT
- promena `Passlib` u `pwdlib` ne zahteva promenu JWT logike

---

## 13) Preporučeni redosled rada za tvoj `TodosApp`

### Faza 1 - kursno razumevanje

Učiti i zapisati:

```text
CryptContext
hash()
verify()
salt
hashed_password
authenticate_user()
```

U ovoj fazi je normalno da kod prati transkript.

---

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

---

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

---

### Faza 4 - migracija na `pwdlib`

Tek kada kursni tok radi:

1. Dodaj odgovarajući `pwdlib` dependency
2. Zameni implementaciju helpera
3. Proveri nove registracije
4. Proveri login sa novim hash-evima
5. Odluči sta radiš sa starim bcrypt korisnicima
6. Ukloni `Passlib` tek kada više nije potreban

---

### Faza 5 - SQLAlchemy 2.0 refaktorisanje

SQLAlchemy 2.0 može raditi pre ili posle `pwdlib` migracije. Praktično je da promene budu odvojene:

```text
promena A: password backend
promena B: SQLAlchemy query/model stil
```

Ako se obe rade istovremeno, teže je utvrditi da li je greška u auth logici, hash biblioteci ili ORM kodu.

---

## 14) Minimalni testovi koji važe za obe biblioteke

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

Ne treba testirati implementaciju ovako (jer zavisi od konkretne biblioteke):

```python
assert saved_hash.startswith("$2b$")
```

osim ako je cilj bas kursna bcrypt konfiguracija. Takav test će se očekivano promeniti pri prelasku na `pwdlib` i Argon2.

---

## 15) Česta pitanja

### Da li moram ponovo menjati podatke u bazi kada promenim biblioteku?

Ne automatski. Postojeći bcrypt hash-evi ostaju validni za bcrypt proveru. Problem nastaje samo ako novi backend ne zna da ih proveri. Tada biraš brisanje razvojnih podataka, dvostruku podršku ili reset password-a.

---

### Da li `pwdlib` menja SQLAlchemy model?

Ne. Menja se vrednost koja se upisuje u `hashed_password`, ne uloga ORM modela.

---

### Da li se menja JWT?

Ne. JWT se kreira tek nakon uspesne provere password-a i ima zasebnu biblioteku i konfiguraciju.

---

### Da li `Passlib` znači da je ceo kurs loš?

Ne. Kursni primer je koristan za učenje auth toka, ali konkretne dependency izbore treba osvežiti za novi projekat. Dobro je učiti stabilan koncept, a zatim proveriti aktuelni alat.

---

### Da li mogu odmah koristiti `pwdlib` i preskočiti Passlib?

Tehnički da, ali za tvoj plan nije potrebno. Ako pratiš transkript, `Passlib` će ti olakšati razumevanje njegovog koda. Posle toga `pwdlib` može biti mali, jasan refaktorisajući korak.

---

### Da li je `bcrypt==4.0.1` univerzalno bezbedna verzija?

Ne. To je konkretan kursni pin koji je izabran zbog kompatibilnosti okruzenja. Verziju treba posmatrati u kontekstu Python verzije, Passlib kompatibilnosti, statusa odrzavanja i bezbednosnih preporuka.

---

## 16) Zadaci za proveru razumevanja

### Zadatak 1 - Označi odgovornost

Za svaku stavku napiši da li pripada password hashing-u ili JWT-u:

```text
salt
CryptContext
PasswordHash
secret key
exp claim
verify(password, saved_hash)
Bearer token
```

---

### Zadatak 2 - Uporedi pozive

Napravi tabelu za:

```python
bcrypt_context.hash(password)
password_hash.hash(password)
bcrypt_context.verify(password, saved_hash)
password_hash.verify(password, saved_hash)
```

---

### Zadatak 3 - Pronađi granicu

Objasni koji deo sledećeg toka zavisi od password biblioteke:

```text
form data
	-> authenticate_user
		-> verify
			-> user
				-> create_access_token
					-> JWT
```

---

### Zadatak 4 - Plan migracije

Napravi plan za slučaj u kome baza već ima bcrypt korisnike, a novi kod treba da koristi Argon2. Navedi najmanje dve moguće strategije i njihove posledice.

---

### Zadatak 5 - Razdvoji promene

Napravi dva odvojena commit plana na papiru:

```text
commit A: password backend migracija
commit B: SQLAlchemy 2.0 refaktorisanje
```

Za svaki napiši koje fajlove bi očekivao da menjaš i koje testove bi pokrenuo.

---

## 17) Zaključak

Za naredne lekcije možeš bez problema nastaviti sa kursnom kombinacijom `Passlib + bcrypt`, jer je cilj da razumes ceo auth tok. Sledeće lekcije ne postaju neupotrebljive ako kasnije predješ na `pwdlib`.

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

Kursni izbor nije amaterski u osnovnom konceptu, ali je tehnički stariji. Nauči ga kao mapu problema, a `pwdlib` uvedi kao svesnu modernizaciju kada završiš kursni tok.
