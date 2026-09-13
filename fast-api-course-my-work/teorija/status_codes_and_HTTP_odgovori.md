# Status Codes and HTTP Responses in FastAPI

## HTTP status codes

Status code je broj koji server vraća zajedno sa odgovorom.

On govori klijentu:

- da li je zahtev uspešno obrađen
- da li je nešto nedostajalo
- da li je došlo do greške
- da li je resurs kreiran, pronađen, ažuriran ili obrisan

U FastAPI-ju status codes se često koriste u `response_model`, `status_code` parametru, ili se automatski određuju prema metodu.

---

## 1) Zašto su status codes važni?

Zato što API ne vraća samo podatke, nego i informaciju o tome šta se desilo.

Primer:

```json
{
  "message": "Knjiga je kreirana"
}
```

To je dobar odgovor, ali bez status koda ne znaš da li je to:

- uspeh
- greška
- nepostojeći resurs
- loše traženje

---

## 2) Najvažniji status codes za početak

### 200 OK

Zahtev je uspešno obrađen.

Primer:

```http
GET /books
```

Ako postoji lista knjiga, često se vraća `200 OK`.

---

### 201 Created

Resurs je uspešno kreiran.

Primer:

```http
POST /books
```

Kada dodaješ novu knjigu, često server vraća `201 Created`.

---

### 204 No Content

Zahtev je uspešan, ali nema sadržaja za vraćanje.

Primer:

```http
DELETE /books/3
```

Ako je brisanje uspešno i ne želiš da vraćaš telo odgovora, možeš koristiti `204`.

---

### 400 Bad Request

Klijent je poslao loš zahtev.

Primer:

- pogrešan JSON
- nedostajuća polja
- neispravan format

---

### 404 Not Found

Traženi resurs ne postoji.

Primer:

```http
GET /books/999
```

ako knjiga sa tim ID ne postoji.

---

### 422 Unprocessable Entity

Ovo je vrlo važan status za FastAPI.

Znači:

- zahtev je stigao
- ali podaci nisu validni
- često zbog tipa ili strukture

Primer:

```http
POST /books
{
  "title": 123,
  "author": "Ana"
}
```

`title` je trebalo da bude string, ali je integer.

---

## 3) Najjednostavniji primer u FastAPI

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "Zdravo"}
```

Ovo po defaultu vraća status `200 OK`.

---

## 4) Postavljanje status code-a

U FastAPI-u to se radi sa parametrom `status_code`.

Primer:

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book():
    return {"message": "Knjiga je kreirana"}
```

Ovo znači:

- kada se pozove POST na `/books`
- server vraća status `201 Created`

---

## 5) Primer sa validacijom i error-om

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.post("/books", status_code=201)
def create_book(book: Book):
    return {"message": "Knjiga je kreirana", "book": book}
```

Ako pošalješ:

```json
{
  "title": 123,
  "author": "Ana"
}
```

FastAPI će vratiti `422` jer model očekuje string za `title`.

---

## 6) Status code za GET, POST, PUT, DELETE

Ovo je dobar pregled:

- GET → 200 OK
- POST → 201 Created
- PUT → 200 OK ili 204 No Content
- DELETE → 200 OK ili 204 No Content
- 404 Not Found → kada resurs ne postoji
- 422 → nevalidni podaci

---

## 7) Šta znači 422 u FastAPI?

To je jedan od najvažnijih statusa za početnika.

`422` znači:

- zahtev je stigao
- ali njegov body ili parametri nisu validni

Najčešće se javlja kada:

- očekuješ int, a dobijes string
- očekuješ string, a dobijes broj
- nedostaje obavezno polje

---

## 8) Jednostavna analogija

Status code je kao odgovor osobe:

- “Uspelo je” = 200
- “Kreirano” = 201
- “Nisam našao” = 404
- “Pogrešno si poslao podatke” = 422

To je jednostavno poruke za klijenta.

---

## 9) Zašto je ovo važno za API?

Jer frontend ili drugi programi često odlučuju šta da rade na osnovu status koda.

Primer:

- `200` → prikazati podatke
- `201` → pokazati da je kreirano
- `404` → prikazati poruku “ne postoji”
- `422` → prikazati poruku “podatak nije validan”

---

## 10) Dobar primer za pamćenje

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book():
    return {"message": "Uspešno dodata knjiga"}
```

Znači:

- POST metod
- kreiranje novog resursa
- vraća `201 Created`

---

## 11) Šta je najbitnije da zapamtiš?

U praksi, za početak znaš sledeće:

- `200` = uspeh
- `201` = kreirano
- `404` = nema resursa
- `422` = nevalidni podaci
- `400` = loš zahtev

To je dovoljna baza za prvi nivo.

---

## 12) Mini vežba

Pokušaj da napišeš ovaj kod:

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item():
    return {"message": "Item je kreiran"}
```

Zamislite da je ovo endpoint za kreiranje novog itema.

Koji status code će se vratiti?

Odgovor:

- `201 Created`

Ako znaš to, znači da razumeš osnovu status codes.

---

## 13) Predlog za dalje učenje

Sledeće što je najlogičnije posle status codes je:

- Response models
- Pydantic model za odgovor
- baza podataka
- SQLite ili SQLAlchemy

Ali to je već sledeći nivo.

---

## Ukratko

Status code je odgovor servera o tome šta se dogodilo sa zahtevom.

Najvažniji za početak su:

- 200 OK
- 201 Created
- 404 Not Found
- 422 Unprocessable Entity

To je dovoljno za prvi korak u ovom delu.

---
