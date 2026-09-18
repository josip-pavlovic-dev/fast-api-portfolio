# Stage 2 - API Request Methods

## Lekcija 01 - GET all todos from database

## 0) Gde se nalazimo u progresiji

Završio si setup baze:

- `database.py` (engine, SessionLocal, Base)
- `models.py` (Users, Todos)
- `main.py` (create_all)
- `sqlite3` osnove

Sada prelazimo na novu oblast: API request methods.
Prvi korak je da kroz endpoint vratiš sve todo zapise iz baze.

---

## 1) Šta je cilj ove lekcije

Cilj nije samo `GET` endpoint, nego 3 stvari zajedno:

1. napraviti DB dependency (`get_db`)
2. ubaciti dependency injection u endpoint (`Depends`)
3. uraditi query i vratiti listu (`db.query(Todos).all()`)

To je osnovni obrazac koji ćeš koristiti gotovo svuda u FastAPI + SQLAlchemy.

---

## 2) Šta transcript pokriva (verno lekciji)

U transkriptu se radi sledeće:

1. pominje se da `create_all` kreira tabele samo kada ne postoje
2. pravi se `get_db()` funkcija sa `yield`
3. objašnjava se `Depends` i `Annotated`
4. pravi se `read_all` endpoint
5. endpoint vraća sve todo zapise
6. uvodi se skraćenica tipa `db_dependency = Annotated[...]`

To je odličan uvod u lifecycle DB sesije po request-u.

---

## 3) Realni kod iz Project 4 i kako je evoluirao

U tvom Project 4 kodu ovaj obrazac već postoji u router fajlu.
Bitna razlika u odnosu na najraniju verziju iz transkripta:

- ne vraća se više bukvalno sve iz tabele
- vraćaju se samo todos za ulogovanog korisnika

Prakticno:

```python
return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

Ovo je naprednija i bezbednija varijanta.

Zasto je bolje:

- korisnik vidi samo svoje podatke
- nema curenja tudjih todo zapisa
- endpoint je spremniji za realnu aplikaciju

---

## 4) Detaljno: get_db i zašto je `yield` bitan

Klasičan obrazac:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Šta se dešava po koracima:

1. FastAPI pozove dependency pre endpoint logike
2. `SessionLocal()` otvara DB sesiju
3. `yield db` prosleđuje sesiju endpoint funkciji
4. endpoint vrati response klijentu
5. posle response-a radi se `finally: db.close()`

Ključna prednost:

- konekcija je otvorena samo dok treba
- smanjuješ rizik curenja konekcija
- obrazac je skalabilan i standardan

---

## 5) Annotated + Depends bez magije

Primer:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Ovo čitaj ovako:

- `db` parametar treba da bude `Session`
- FastAPI će ga popuniti preko `get_db`

U endpointu:

```python
async def read_all(db: db_dependency):
    ...
```

Zasto je korisno:

- ne ponavljaš dugi tip u svakom endpointu
- kod je čitljiviji
- lakše održavanje

---

## 6) Endpoint logika za “get all”

Osnovna (rani nivo):

```python
@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
```

Project 4 varijanta (sa auth):

```python
@router.get("/", status_code=200)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

Napomena:

- druga varijanta je bezbednija i realnija

---

## 7) Važno o create_all iz transkripta

Transkript ispravno pominje:

```python
Base.metadata.create_all(bind=engine)
```

Ovo:

- kreira nedostajuće tabele
- ne radi kompleksne izmene postojećih tabela

Ako posle menjaš model (dodaješ kolonu), `create_all` nije pun migration alat.
Zato u ozbiljnijoj fazi koristiš Alembic migracije.

---

## 8) Najčešće greške početnika u ovoj lekciji

1. Zaboravljen `db.close()`

- može dovesti do curenja konekcija za svaku novu konekciju koja se otvori, a ne zatvori pravilno.

2. Pisanje globalne sesije umesto per-request sesije za svaki zahtev

- opasno za konkurentne zahteve, može dovesti do neočekivanih ponašanja.

3. Endpoint bez `auth` filtera vraća sve korisnike širom baze.

- može biti bezbednosni problem u realnoj aplikaciji, jer svaki korisnik može videti podatke drugih korisnika.

4. Mešanje `sync/async` bez razumevanja šta se dešava ispod haube

- endpoint je `async`, ali SQLAlchemy Session ovde radi sinhrono
- to je normalno za ovaj kurs setup

5. Očekivanje da `create_all` radi migracije

- ne radi ih pouzdano za sve promene shema.

---

## 9) “Šta se dešava ispod haube” kada pozoveš GET

Tok izgleda ovako:

1. HTTP zahtev pogodi rutu po kojoj je definisan endpoint.
2. FastAPI razreši dependency-je od endpointa od kojih zavisi (npr. `get_db`).
3. `get_db` otvori sesiju za bazu podataka.
4. endpoint izvrsi query nad bazom podataka.
5. SQLAlchemy prevede query u SQL koji se izvršava nad bazom podataka.
6. baza vrati redove koji odgovaraju SQL upitu.
7. FastAPI serijalizuje response u JSON format.
8. `finally` zatvori sesiju za bazu podataka.

Ako ovo razumeš, razumećeš srce FastAPI + DB request lifecycle-a.

---

## 10) SQL ekvivalent ORM izraza

ORM izraz:

```python
db.query(Todos).filter(Todos.owner_id == user_id).all()
```

SQL ideja:

```sql
SELECT *
FROM todos
WHERE owner_id = :user_id;
```

`:user_id` je parametrizovana vrednost.
To je bezbednije od konkatenacije (concatenating) stringova. Ovo smanjuje rizik od SQL injection napada.

`injection` napad predstavlja situaciju kada napadač može da ubaci maliciozni SQL kod u upit, što može dovesti do neovlašćenog pristupa ili manipulacije podacima. Zato je parametrizacija upita važna.

---

## 11) Praktična mini vežba (20-30 min)

1. Napiši endpoint koji vraća sve todos (bez filtera).
2. Zatim dodaj auth i filter po `owner_id`.
3. Uoči razliku u rezultatima.
4. Testiraj 2 korisnika i potvrdi da svaki vidi samo svoje podatke.

Bonus:

- Dodaj sortiranje po `id` od najmanjeg ka najvećem.

---

## 12) Samoprovera razumevanja

Ako možeš jasno da odgovoriš, lekcija je legla:

1. Zasto je `yield` bolji obrazac od prostog `return` u DB dependency?

`yield` omogućava da se izvrši neki kod nakon što endpoint završi sa radom, što je korisno za zatvaranje resursa kao što je DB sesija. U suprotnom, ako bi se koristio samo `return`, sesija bi mogla ostati otvorena duže nego što je potrebno, što može dovesti do curenja resursa.

2. Kada se tačno izvrši `db.close()`?

`db.close()` se izvršava nakon što endpoint završi sa radom i nakon što se kod iza `yield` u dependency-ju izvrši. To obezbeđuje da se DB sesija zatvori pravilno, čak i ako dođe do greške tokom obrade zahteva. Ovo je ključni razlog zašto je `yield` bolji obrazac od prostog `return` u DB dependency-ju.

3. Čemu služi `Depends(get_db)`?

`Depends(get_db)` služi za injektovanje DB sesije u endpoint. FastAPI će automatski pozvati `get_db` dependency, obezbediti DB sesiju i proslediti je endpoint funkciji. Nakon što endpoint završi, FastAPI će izvršiti kod iza `yield` u `get_db`, čime se sesija pravilno zatvara. Ovo omogućava sigurno i efikasno rukovanje DB resursima u svakom request-u.

4. Zašto je `owner_id` filter bitan u realnom API-ju?

`owner_id` filter je bitan jer omogućava da svaki korisnik vidi samo svoje podatke. Bez ovog filtera, korisnici bi mogli da pristupe podacima drugih korisnika, što predstavlja ozbiljan bezbednosni rizik. Zato je važno uvek filtrirati po `owner_id` u realnim API-jevima.

5. Koja je granica `create_all`, a kada treba Alembic migrations?

`create_all` je koristan za jednostavne projekte ili inicijalno kreiranje šeme baze podataka. Međutim, kada se šema baze menja tokom razvoja (dodavanje kolona, tabela, itd.), Alembic migrations su preporučeni jer omogućavaju kontrolisano i verzionisano upravljanje promenama u bazi podataka. Ovo je posebno važno u produkcionim okruženjima gde direktno menjanje šeme može dovesti do gubitka podataka ili nekompatibilnosti.

---

## 13) Veza sa sledećim lekcijama

Ova lekcija je baza za sve dalje request methods:

- `GET` by id
- `POST` create
- `PUT` update
- `DELETE`

Svi oni koriste isti dependency pattern za DB.
Zato je važno da ga sada razumeš potpuno.

---

## 14) Zaključak

Lekcija deluje jednostavno (jedan GET), ali zapravo uvodi najvažniji backend obrazac:

- per-request DB session (sa zatvaranjem nakon request-a uz `yield`)
- dependency injection (`Depends(get_db)` za DB sesiju)
- query kroz ORM (SQLAlchemy ORM model za tvoju tabelu `todos`)
- bezbedno filtriranje po korisniku (`owner_id` filter za identifikaciju vlasnika)

Kad ovo savladaš, ostali CRUD endpointi postaju samo varijacije iste osnove.
