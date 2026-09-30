# Dan 8 - SQLAlchemy `Column[str]`, Pylance i tipovi ORM atributa

## 1) Pitanje iz `auth.py`

U funkciji za autentifikaciju imamo dva pristupa.

### Jednostavniji oblik iz kursa

```python
def authenticate_user_alternative(username: str, password: str, db: db_dependency):
	user = db.query(Users).filter(Users.username == username).first()
	if not user:
		return False
	if not bcrypt_context.verify(password, user.hashed_password):
		return False
	return True
```

---

### Trenutni oblik u projektu

```python
def authenticate_user(username: str, password: str, db: db_dependency):
	user = db.query(Users).filter(Users.username == username).first()
	if user is None:
		return False

# Runtime provera stvarno proverava tipove vrednosti iz ORM instance.
	hashed_password = getattr(user, "hashed_password", None)
	if not isinstance(hashed_password, str):
		return False

	if not bcrypt_context.verify(password, hashed_password):
		return False

	is_active = getattr(user, "is_active", None)
	if not isinstance(is_active, bool):
		return False
	if not is_active:
		return False

	return user
```

Oba pristupa prvo traže korisnika po username-u, a zatim proveravaju password. Razlika je u tipovima i u vrednosti koju funkcija vraća:

```text
kursni kod       -> vraća False ili True
trenutni kod     -> vraća False ili stvarnog Users korisnika
```

Vraćanje stvarnog korisnika je korisno jer će nam kasnije trebati korisnički podaci za izradu JWT-a, na primer `user.id`, `user.username` i `user.role`.

---

## 2) Pylance greška

Za kursni kod Pylance prijavljuje:

```text
Argument of type "Column[str]" cannot be assigned to parameter "hash"
of type "str | bytes | None" in function "verify"
```

Problem se pojavljuje na ovom delu:

```python
bcrypt_context.verify(password, user.hashed_password)
```

Metoda `verify()` očekuje približno:

```python
bcrypt_context.verify(
	secret: str | bytes,
	hash: str | bytes | None,
)
```

Prvi argument je običan password koji je korisnik poslao. Drugi argument treba da bude hash lozinke pročitan iz baze.

Pylance, međutim, za `user.hashed_password` vidi tip:

```text
Column[str]
```

a ne:

```text
str
```

Zato upozorava da `Column[str]` ne može biti prosleđen funkciji koja očekuje `str`.

---

## 3) Zašto Pylance vidi `Column[str]`

U modelu `Users` trenutno imamo stariji SQLAlchemy deklarativni stil:

```python
class Users(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True)
	username = Column(String, unique=True)
	hashed_password = Column(String)
	is_active = Column(Boolean, default=True)
```

Na nivou klase, `hashed_password` zaista jeste SQLAlchemy `Column` objekat:

```python
Users.hashed_password
```

Ovaj oblik se koristi za pravljenje SQLAlchemy izraza:

```python
Users.hashed_password == some_hash
```

što se prevodi u SQL uslov:

```sql
WHERE hashed_password = :some_hash
```

Zato je za klasu prirodno da Pylance vidi:

```text
Users.hashed_password -> Column[str]
```

Ali kada imamo instancu koju je ORM učitao iz baze:

```python
user = db.query(Users).first()
```

u runtime-u očekujemo:

```python
user.hashed_password -> stvarni string iz kolone baze
user.is_active       -> stvarni bool iz kolone baze
```

Na primer:

```text
Users.hashed_password  -> ORM descriptor/Column, koristi se za query
user.hashed_password   -> vrednost učitana iz reda baze
```

Ovo je važna razlika između:

```text
klasa  -> opis kolone i SQL izraza
instanca -> vrednost kolone za konkretan red
```

U runtime-u SQLAlchemy pravilno mapira vrednost. Problem je u tome što stariji `Column(...)` način deklarisanja ne daje Pylance-u dovoljno preciznu informaciju da isti atribut na instanci treba da bude običan `str`.

---

## 4) Da li je kursni kod neispravan?

Ne nužno. Kursni kod može raditi u runtime-u:

```python
if not bcrypt_context.verify(password, user.hashed_password):
	return False
```

Ako je `user` stvarna ORM instanca i ako `hashed_password` sadrži validan bcrypt hash, `passlib` će dobiti string iz baze i proveriti password.

Pylance greška je prvenstveno statička greška tipova:

```text
runtime ponašanje -> SQLAlchemy zna da vrati vrednost iz reda
statička analiza   -> vidi deklaraciju Column(String)
```

Ipak, upozorenje ne treba samo ignorisati. Ono pokazuje da model nije dovoljno precizno tipiziran za alat koji proverava kod.

---

## 5) Zašto je prethodni `cast()` kod zamenjen

Prethodna verzija je izdvajala ORM atribute pomoću `cast()`:

```python
hashed_password = cast(str, getattr(user, "hashed_password"))
is_active = cast(bool, getattr(user, "is_active"))
```

Zatim se koriste vrednosti sa tipovima koje očekuju biblioteke:

```python
bcrypt_context.verify(password, hashed_password)
```

Ovde `cast(str, ...)` govori Pylance-u:

```text
Pretpostavi da je rezultat ovog izraza str.
```

A `cast(bool, ...)` govori:

```text
Pretpostavi da je rezultat ovog izraza bool.
```

`cast()` ne menja vrednost i ne vrši konverziju u runtime-u.

Na primer:

```python
value = cast(str, some_value)
```

ne znači:

```python
value = str(some_value)
```

`cast()` je instrukcija za statički alat, dok `str()` stvarno pokušava da pretvori vrednost.

U aktivnom kodu smo zato izabrali runtime proveru:

```python
hashed_password = getattr(user, "hashed_password", None)
if not isinstance(hashed_password, str):
	return False
```

Ona ne utišava samo Pylance, već zaista proverava vrednost koju smo dobili iz ORM instance.

---

## 6) Šta radi `getattr()`

Ovaj izraz:

```python
getattr(user, "hashed_password")
```

pristupa atributu po njegovom imenu kao stringu. Približno je sličan ovom kodu:

```python
user.hashed_password
```

Razlika je u tome što se ime atributa prosleđuje kao tekst:

```python
attribute_name = "hashed_password"
value = getattr(user, attribute_name)
```

Prednost u trenutnom primeru je što Pylance rezultat često tretira kao `Any`, pa ga zatim `cast(str, ...)` preciznije označava.

Ali `getattr()` ima i cenu:

```python
getattr(user, "hashed_pasword")
```

Pogrešno napisano ime može proći statičku proveru i izazvati grešku tek u runtime-u. Direktan pristup:

```python
user.hashed_password
```

bolje omogućava editoru da otkrije pogrešno ime atributa.

Zato je `getattr()` praktičan lokalni workaround za stariji model, ali nije najbolje dugoročno rešenje za tipizaciju celog projekta.

---

## 7) Najmanja lokalna ispravka

Ako želimo da zadržimo postojeći model, možemo koristiti `cast()` uz direktan pristup atributu:

```python
from typing import cast


hashed_password = cast(str, user.hashed_password)
is_active = cast(bool, user.is_active)
```

Zatim:

```python
if not bcrypt_context.verify(password, hashed_password):
	return False
if not is_active:
	return False
```

Ovaj oblik je kraći i zadržava proveru imena atributa u editoru. Međutim, cast i dalje samo govori type checker-u šta da pretpostavi; ne proverava stvarni tip podatka.

Ako iz baze stigne `None`, `cast(str, None)` neće napraviti string. Zato cast treba koristiti samo kada je pretpostavka opravdana modelom i bazom.

---

## 8) Bolje dugoročno rešenje: SQLAlchemy 2.x tipizovani model

Savremeniji SQLAlchemy 2.x stil koristi `Mapped[...]` i `mapped_column()`:

```python
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class Users(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	email: Mapped[str] = mapped_column(String, unique=True)
	username: Mapped[str] = mapped_column(String, unique=True)
	first_name: Mapped[str] = mapped_column(String)
	last_name: Mapped[str] = mapped_column(String)
	hashed_password: Mapped[str] = mapped_column(String)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	role: Mapped[str] = mapped_column(String)
```

Tada type checker može da razume razliku između SQLAlchemy klase i ORM instance:

```python
Users.hashed_password       # SQLAlchemy instrumented attribute za query-je
user.hashed_password        # str za konkretnu ORM instancu
```

Posle pravilno tipizovanog modela kursni kod može biti prihvaćen bez workaround-a:

```python
if not bcrypt_context.verify(password, user.hashed_password):
	return False
```

Ovo je najbolje rešenje kada projekat prelazi iz malog kursnog primera u ozbiljniju aplikaciju sa više modela, servisa i type checking-a.

### Važna napomena o nullable kolonama

U postojećem starijem modelu:

```python
hashed_password = Column(String)
```

nije eksplicitno navedeno da je kolona `nullable=False`. U bazi zato teoretski može postojati `NULL` vrednost.

Ako je password obavezan, precizniji model je:

```python
hashed_password: Mapped[str] = mapped_column(
	String,
	nullable=False,
)
```

Za nullable kolonu koristio bi se tip:

```python
nickname: Mapped[str | None] = mapped_column(String, nullable=True)
```

Tada type checker ispravno traži da obradimo mogućnost `None`:

```python
if nickname is not None:
	print(nickname.upper())
```

---

## 9) Poređenje tri rešenja

### Rešenje A: kursni kod

```python
if not bcrypt_context.verify(password, user.hashed_password):
	return False
```

Prednosti:

```text
kratko je
lako se prati na početku kursa
verovatno radi u runtime-u
```

Nedostatak:

```text
stariji model može izazvati Pylance grešku za Column[str]
```

--

### Rešenje B: runtime validacija u `auth.py`

```python
hashed_password = getattr(user, "hashed_password", None)
if not isinstance(hashed_password, str):
	return False

is_active = getattr(user, "is_active", None)
if not isinstance(is_active, bool) or not is_active:
	return False
```

Prednosti:

```text
stvarno proverava vrednosti iz ORM instance
ne zahteva promenu models.py
sprečava prosleđivanje None ili pogrešnog tipa u bcrypt
```

Nedostaci:

```text
getattr lako sakrije typo u imenu atributa
tipizacija modela ostaje starija
provere dodaju nekoliko linija koda
```

---

### Rešenje C: tipizovani SQLAlchemy 2.x model

```python
hashed_password: Mapped[str] = mapped_column(String, nullable=False)
```

Prednosti:

```text
type checker razume ORM atribute
direktan pristup user.hashed_password ostaje čitljiv
tipovi se šire na ceo model
nullable pravila su jasna
```

Nedostatak:

```text
zahteva pažljivu izmenu modela i proveru kompatibilnosti projekta
```

**Izabrano rešenje za trenutni projekat je Rešenje B: runtime validacija u `auth.py`**, bez promene `models.py` i bez aktivnog `cast()` workaround-a. Postojeći `Column(...)` model ostaje nepromenjen, a `auth.py` proverava vrednosti pomoću `getattr()` i `isinstance()`.

Rešenje C, odnosno SQLAlchemy 2.x `Mapped[...]` model, ostavljamo za kasniji refaktor kada budemo prelazili na moderni SQLAlchemy stil. Zbog toga sada nije potrebno menjati `models.py`.

---

## 10) Poređenje ponašanja autentifikacionih funkcija

Kursna funkcija:

```python
def authenticate_user_alternative(username, password, db):
	user = db.query(Users).filter(Users.username == username).first()
	if not user:
		return False
	if not bcrypt_context.verify(password, user.hashed_password):
		return False
	return True
```

Logika je:

```text
korisnik ne postoji       -> False
password nije dobar       -> False
password je dobar         -> True
```

Trenutna funkcija:

```python
def authenticate_user(username, password, db):
	user = db.query(Users).filter(Users.username == username).first()
	if user is None:
		return False
	hashed_password = cast(str, getattr(user, "hashed_password"))
	is_active = cast(bool, getattr(user, "is_active"))
	if not bcrypt_context.verify(password, hashed_password):
		return False
	if not is_active:
		return False
	return user
```

Logika je:

```text
korisnik ne postoji       -> False
password nije dobar       -> False
korisnik nije aktivan     -> False
password je dobar         -> Users objekat
```

U endpointu oba rezultata mogu da se koriste u uslovu:

```python
if not authenticated_user:
	raise HTTPException(...)
```

Ali samo trenutna funkcija omogućava da posle provere koristimo podatke korisnika:

```python
authenticated_user.id
authenticated_user.username
authenticated_user.role
```

To će biti važno kada budemo pravili JWT payload.

---

## 11) Zašto je `if user is None` preciznije

Kurs koristi:

```python
if not user:
	return False
```

Trenutni kod koristi:

```python
if user is None:
	return False
```

U ovom slučaju oba oblika najčešće rade isto, zato što query vraća ORM objekat ili `None`.

`is None` je preciznije kada želimo baš da proverimo da li rezultat ne postoji:

```python
if user is None:
```

Ne proverava opštu “falsy” vrednost. Tako se ne meša nepostojanje korisnika sa potencijalnim objektom koji bi imao posebno boolean ponašanje.

---

## 12) Važno: `cast()` nije validacija

Ovo:

```python
hashed_password = cast(str, value)
```

ne radi sledeće:

```text
ne proverava da je value stvarno str
ne pretvara value u str
ne čisti podatak iz baze
ne hvata None vrednost
```

Ako želimo stvarnu runtime proveru, možemo napisati:

```python
hashed_password = getattr(user, "hashed_password", None)
if not isinstance(hashed_password, str):
	return False
```

Tada je provera stvarna:

```python
if not bcrypt_context.verify(password, hashed_password):
	return False
```

Ovaj oblik je duži, ali štiti funkciju i od neočekivane vrednosti iz baze.

Za boolean:

```python
is_active = getattr(user, "is_active", None)
if not isinstance(is_active, bool) or not is_active:
	return False
```

U dobro definisanom modelu sa `nullable=False`, ovakva provera možda nije potrebna svuda, ali je korisna za razumevanje razlike između statičke pretpostavke i runtime validacije.

---

## 13) Preporučena verzija za trenutni model

Ako ne menjamo odmah `models.py`, čitljiva verzija funkcije može izgledati ovako:

```python
def authenticate_user(username: str, password: str, db: db_dependency):
	"""Vraća korisnika ako postoje username, validan password i aktivan nalog."""
	user = db.query(Users).filter(Users.username == username).first()
	if user is None:
		return False

	hashed_password = getattr(user, "hashed_password", None)
	if not isinstance(hashed_password, str):
		return False

	if not bcrypt_context.verify(password, hashed_password):
		return False

	is_active = getattr(user, "is_active", None)
	if not isinstance(is_active, bool):
		return False
	if not is_active:
		return False

	return user
```

Zašto je ovo prihvatljivo sada?

```text
query vraća Users instancu ili None
isinstance stvarno proverava tipove vrednosti iz ORM instance
models.py ne mora da se menja za ovo rešenje
is_active sprečava login deaktiviranog korisnika
return user priprema podatke za JWT
```

Ali zapamti: ovo je praktično trenutno rešenje za postojeći stariji model. Sistemsko dugoročno rešenje je tipizovanje modela pomoću `Mapped[...]`, ali ga sada ne primenjujemo.

---

## 14) Tok provere password-a

```text
1. Klijent šalje username i password.
2. SQLAlchemy traži Users red po username-u.
3. Ako red ne postoji, vraća se False.
4. Iz ORM instance čita se hashed_password.
5. bcrypt proverava da li poslati password odgovara hash-u.
6. Ako password nije dobar, vraća se False.
7. Proverava se is_active.
8. Ako je nalog deaktiviran, vraća se False.
9. Ako je sve ispravno, vraća se Users objekat.
```

Važno je da se password nikada ne poredi ručno sa hash stringom:

```python
# Pogrešna ideja
if password == user.hashed_password:
	...
```

Hash nije originalni password. Ispravno je koristiti:

```python
bcrypt_context.verify(password, hashed_password)
```

Biblioteka iz poslatog password-a i sačuvanog hash-a računa da li se vrednosti podudaraju.

---

## 15) Najvažniji zaključci

```text
Column(String)       -> SQLAlchemy deklaracija kolone
Users.field          -> class-level SQLAlchemy atribut za query-je
user.field           -> vrednost polja za konkretnu ORM instancu
Column[str]           -> tip koji Pylance vidi kod starog modela
str                   -> tip koji bcrypt.verify očekuje za hash
cast(str, value)      -> uputstvo type checker-u, ne konverzija
Mapped[str]           -> savremeniji način tipizovanja ORM polja
```

Kursni kod je kraći i dobar za uvod u autentifikaciju. Trenutni kod rešava Pylance neslaganje i dodaje proveru aktivnog naloga, a vraćanje korisnika će biti korisno za JWT.

Najbolje dugoročno rešenje nije da svuda koristimo `getattr()`, već da ORM modele tipizujemo pomoću SQLAlchemy 2.x `Mapped[...]` deklaracija.

---

## 16) Pitanja za proveru

1. Zašto Pylance vidi `user.hashed_password` kao `Column[str]`?
2. Koja je razlika između `Users.hashed_password` i `user.hashed_password`?
3. Da li kursni kod nužno ne radi u runtime-u samo zato što Pylance javlja grešku?
4. Šta radi `cast(str, value)`?
5. Da li `cast()` stvarno pretvara vrednost u string?
6. Koja je cena korišćenja `getattr()` umesto direktnog pristupa atributu?
7. Zašto je `Mapped[str]` bolje dugoročno rešenje?
8. Zašto trenutna funkcija vraća `user`, a kursna vraća `True`?
9. Zašto proveravamo `is_active` pre uspešnog login-a?
10. Zašto se password proverava pomoću `bcrypt_context.verify()` umesto operatora `==`?

---

## 17) Kratak rezime

Pylance greška ne znači automatski da SQLAlchemy runtime ne može da pročita hash. Ona pokazuje da je model deklarisan starijim stilom koji type checker-u ne prenosi dovoljno precizno tip instance.

Za sada možemo koristiti lokalni workaround sa `cast()`, ali treba znati da je sistemsko rešenje modernizacija modela:

```python
hashed_password: Mapped[str] = mapped_column(
	String,
	nullable=False,
)
```

Tada će sledeći kod biti i čitljiv i bolje razumljiv Pylance-u:

```python
bcrypt_context.verify(password, user.hashed_password)
```
