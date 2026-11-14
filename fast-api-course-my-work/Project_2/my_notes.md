# Project 2 — beleške iz razgovora

Beleške za teme obrađene uz [books2.py](./books2.py) i [books22.py](./books22.py).

## HTTP metode — kratki odgovori na engleskom

- **GET** — Retrieve data. _“I’d use GET to retrieve the book.”_
- **POST** — Create a resource. _“I’d use POST to create a book.”_
- **PUT** — Replace or update an existing resource. _“I’d use PUT to update the book.”_
- **DELETE** — Remove a resource. _“I’d use DELETE to remove the book.”_

Podsetnik: **GET = read, POST = create, PUT = update/replace, DELETE = remove.**

## Zašto funkcija može da koristi `BOOKS` bez `global`?

`BOOKS` je promenljiva na nivou modula. Funkcija može da je čita bez `global`.
`global BOOKS` je potreban ako funkcija treba da promeni na šta ime pokazuje,
na primer `BOOKS = []`. Nije potreban kada se menja postojeća lista, npr.
`BOOKS.append(book)`, niti kada se menja atribut objekta, npr. `book.id = 7`.

U `automatski_id(book)` funkcija čita `BOOKS`, menja prosleđeni objekat `book`
i vraća taj objekat. Promena njegovog atributa vidljiva je i pozivaocu jer oba
imena upućuju na isti objekat.

## Kako radi izraz za dodeljivanje ID-ja?

```python
book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
```

Ovo je **uslovni izraz** (_conditional expression_, često „ternarni izraz“).
`len(BOOKS) == 0` je poređenje. Ako je lista prazna, ID postaje `1`; inače
postaje ID poslednje knjige u listi plus `1`.

Isto napisano kao `if/else`:

```python
if len(BOOKS) == 0:
    book.id = 1
else:
    book.id = BOOKS[-1].id + 1
```

Izraz koristi ID poslednjeg elementa, ne nužno najveći ID. Zato pretpostavlja
da se knjige dodaju redom. U kasnijoj verziji aplikacije ID-jeve obično dodeljuje
baza podataka.

## Da li POST može da vrati samo ID?

Da. FastAPI može da vrati JSON broj: `return new_book.id` daje, na primer, `7`.
To je validan JSON, iako nije JSON objekat. Ako želiš strukturiran odgovor,
možeš vratiti `{"id": new_book.id}`, što daje `{"id": 7}`. Možeš vratiti i
celu kreiranu knjigu; izbor zavisi od toga šta klijentu treba.

HTTP status i telo odgovora su odvojene stvari:

- `status_code=status.HTTP_201_CREATED` postavlja HTTP status na **201**.
- `return {"id": new_book.id}` određuje JSON telo.
- U `books2.py`, vraćanje `status.HTTP_201_CREATED` iz funkcije dodatno šalje
  broj `201` kao telo; ako dekorator već postavlja status, to je obično
  nepotrebno.

## Razlika između `Book` i `BookRequest`

- `Book` u ovim skriptama je obična Python klasa koja predstavlja knjigu.
- `BookRequest(BaseModel)` je Pydantic model za podatke koji dolaze u zahtevu.
  Pydantic proverava polja i ograničenja, npr. dužinu naslova/opisa i dozvoljen
  opseg ocene. Ne proverava sam da li knjiga sa datim ID-jem postoji u `BOOKS`.
- `BookRequest.id` je opcionalan i podrazumevano `None`; aplikacija zatim
  dodeljuje ID novoj knjizi.

## Zašto `books2.py` radi bez povratnih anotacija, a `books22.py` prijavljuje grešku?

FastAPI koristi povratnu anotaciju rute kao podrazumevani response model. Ako
ruta nema povratnu anotaciju (i nije joj posebno zadat `response_model`),
FastAPI ne pokušava da izvede Pydantic šemu iz tipa `Book`. I dalje kodira
vraćene vrednosti u JSON. Proverom preko TestClient-a potvrđeno je da su
`GET /books` i `GET /books/1` u `books2.py` vratili status **200** i JSON.

Ako ruta ima anotaciju `-> Book` ili `-> list[Book]`, FastAPI pokušava da od
`Book` napravi response model. Pošto je `Book` obična klasa, a ne Pydantic
model, aplikacija može da padne pri pokretanju, dok registruje rute — pre
nego što primi zahtev. Anotacija na pomoćnoj funkciji kao
`automatski_id(book: Book) -> Book` sama po sebi nije problem, jer ta funkcija
nije FastAPI ruta.

U trenutnom sadržaju `books22.py`, `sve_knjige()` nema povratnu anotaciju, ali
`pronadji_knjigu_po_id(...) -> Book` je ima. Zato trenutni pokušaj pokretanja
pada na ruti za knjigu po ID-ju. Raniji traceback se odnosio na prethodno
stanje fajla, gde je ruta za sve knjige imala `-> list[Book]`; uzrok je isti.

Uklanjanje povratne anotacije zaobilazi automatsko pravljenje response modela,
ali znači i manje validacije odgovora i slabiji opis odgovora u OpenAPI/Swagger
dokumentaciji. Dugoročno je bolje koristiti Pydantic model za odgovor (ili
posebnu response šemu). Ako se običan objekat `Book` vraća kroz takvu šemu,
potrebno je omogućiti validaciju iz atributa objekta. Pri prelasku `Book` klase
na Pydantic model, uskladi kreiranje: ID treba da bude dodeljen pre nego što se
napravi model odgovora.

## Česti statusi u CRUD API-ju

- **200 OK** — zahtev je uspešan i odgovor obično ima telo.
- **201 Created** — POST je uspešno kreirao resurs.
- **204 No Content** — uspeh bez tela odgovora.
- **404 Not Found** — traženi resurs nije pronađen; aplikacija to eksplicitno
  prijavljuje, npr. pomoću `HTTPException`.
- **422 Unprocessable Entity** — FastAPI/Pydantic odbio je neispravan ulazni
  podatak.

## Pokretanje `books22.py` preko projektne `.venv`

Iz korena repozitorijuma:

```bash
source .venv/bin/activate
python -m uvicorn books22:app --app-dir fast-api-course-my-work/Project_2 --reload
```

Ili direktno pozovi interpreter iz virtualenv-a:

```bash
./.venv/bin/python -m uvicorn books22:app --app-dir fast-api-course-my-work/Project_2 --reload
```

Dok ruta vraća običan `Book` kroz nevažeću response anotaciju, Uvicorn neće
završiti pokretanje aplikacije.
