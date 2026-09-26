# FastAPI: delovi HTTP zahteva — Path, Query, Body, Form

Ovaj fajl je napravljen da ti razjasni jednu stvar koja često zbunjuje početnike:

Kako je HTTP zahtev “poslagan” i zašto se u FastAPI-u koristi `Path`, `Query`, `Body`, `Form`.

Cilj je da to ne razumeš kao “četiri različita načina da proslediš podatke”, nego kao četiri različite uloge u jednom zahtevu.

---

## 1) Osnovna ideja: HTTP zahtev ima više “delova”

Svaki HTTP zahtev ima nekih nekoliko ključnih delova:

1. metoda (GET, POST, PUT, DELETE, PATCH)
2. URL
3. zaglavlja (headers)
4. query string (dio URL-a posle ?)
5. body (telo zahteva)

Primer:

```http
POST /books/5/comments?sort=latest HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "text": "Odlican članak",
  "author": "Marko"
}
```

Ovde je:

- `POST` = metoda
- `/books/5/comments` = path
- `?sort=latest` = query
- `Content-Type: application/json` = header koji govori da je body JSON
- `{ "text": ..., "author": ... }` = body

---

## 2) Šta je URL?

URL se sastoji od više delova:

```text
https://example.com/books/42?category=programming&page=2
```

Podeljeno:

- `https://` = scheme
- `example.com` = host
- `/books/42` = path
- `?category=programming&page=2` = query string

Nije sve u URL isto.

Path i query su potpuno različite uloge.

---

## 3) `Path` parametri

### Definicija

`Path` parametri su deo URL-a koji označava konkretan resurs.

Primer:

```http
GET /books/10
```

Ovo znači:

- želiš da pristupiš resursu sa identifikatorom `10`
- `/books/10` je “adresa” konkretne knjige

U FastAPI-u:

```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    return {"book_id": book_id}
```

### Zašto je ovo važno?

Pošto path parametar opisuje “šta je cilj”:

- `/users/7` => korisnik broj 7
- `/books/10` => knjiga broj 10
- `/products/99` => proizvod broj 99

### Jednostavna mentalna slika

Path parametar je kao:

- “na kojoj ulici živiš?”
- “koji je ID objekta?”
- “koji resurs želim da otvorim?”

---

## 4) `Query` parametri

### Definicija

`Query` parametri su dodatni podaci u URL-u, posle `?`.

Primer:

```http
GET /books?category=python&limit=10&page=2
```

Ovde je:

- `/books` = putanja do kolekcije
- `?category=python` = filter
- `&limit=10` = ograničenje broja rezultata
- `&page=2` = broj strane

U FastAPI-u:

```python
@app.get("/books")
async def get_books(category: str | None = None, limit: int = 10, page: int = 1):
    return {"category": category, "limit": limit, "page": page}
```

### Zašto je ovo važno?

Query parametri služe za:

- filtriranje
- pretragu
- paginaciju
- sortiranje
- dodatne opcije

### Jednostavna mentalna slika

Query parametri su kao:

- “prikaži mi samo Python knjige”
- “vrati 10 rezultata”
- “prikaži drugu stranu”

To nisu identifikatori resursa, nego parametri koje koristiš za kontrolu prikaza ili filtera.

---

## 5) `Body`

### Definicija

`Body` je telo HTTP zahteva, najčešće JSON.

Primer:

```http
POST /books
Content-Type: application/json

{
  "title": "Python",
  "author": "Marko",
  "description": "Uvod"
}
```

U FastAPI-u:

```python
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None

@app.post("/books")
async def create_book(book: BookCreate):
    return book
```

### Zašto je ovo važno?

Body se koristi za podatke koje se šalju sa zahtevom, posebno kada praviš novi resurs:

- kreiranje knjige
- kreiranje korisnika
- kreiranje naloga
- izlaz sa velikim objektom

Body ne ide u URL, nego u telo zahteva.

### Jednostavna mentalna slika

Body je kao:

- “ovo je sadržaj koji šaljem serveru”
- “neka nova knjiga koju želim da dodam”

---

## 6) `Form`

### Definicija

`Form` je specijalni oblik body-ja, koji se koristi kada podaci dolaze iz HTML formi.

To je najčešće kod browser formi, a ne JSON-a.

Primer HTML forme:

```html
<form action="/login" method="post">
  <input type="text" name="username" />
  <input type="password" name="password" />
  <button type="submit">Login</button>
</form>
```

U FastAPI-u:

```python
from fastapi import Form

@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username, "password": password}
```

### Značenje

`Form` se koristi kada:

- korisnik šalje podatke preko HTML forme
- podaci dolaze kao `application/x-www-form-urlencoded`
- ili za upload fajlova (`multipart/form-data`)

### Bitna razlika

- `Body` = najčešće JSON
- `Form` = oblik podataka iz browser forme

Nije isto:

```python
book: BookCreate
```

i:

```python
username: str = Form()
```

Prvo je JSON objekat, drugo su form polja u HTML obrascu.

---

## 7) Najveća zbunjenost: “šta ide gde?”

To je ta stvar koja najviše zbunjuje početnike.

### Podela po ulogama

#### Path parametri

Koriste se za identifikaciju konkretne stvari:

```http
GET /books/5
```

- ovde je `5` identifikator knjige

#### Query parametri

Koriste se za dodatne opcije i filtere:

```http
GET /books?category=python&limit=10
```

- `category` i `limit` nisu objekti, nego opcije

#### Body

Koriste se za podatke koje šalješ sa requestom:

```http
POST /books
```

Telo:

```json
{
  "title": "Python",
  "author": "Marko"
}
```

- ovo je stvarni sadržaj koji se kreira

#### Form

Koriste se za browser forme ili upload:

```http
POST /login
```

Telo forme:

```text
username=ana&password=123456
```

---

## 8) Jednostavna tabela razlike

### Path

- deo URL-a
- koristi se za ID resursa
- npr. `/books/3`
- ne koristi se za filtere

### Query

- deo URL-a posle `?`
- koristi se za filter, page, sort, search
- npr. `/books?genre=python&limit=5`

### Body

- u telu zahteva
- koristi se za JSON objekte
- npr. `{ "title": "Python" }`

### Form

- u telu zahteva, ali u form formatu
- koristi se za HTML submit forme
- npr. `username=ana&password=123`

---

## 9) Realni primer kroz jedno potpuno pitanje

### Zahtev 1

```http
GET /books/10
```

Pitaš:

- “daj mi knjigu broj 10”

Ovde je `10` path parametar.

---

### Zahtev 2

```http
GET /books?genre=python&limit=5
```

Pitaš:

- “daj mi knjige koje su Python, maksimalno 5”

Ovde su `genre` i `limit` query parametri.

---

### Zahtev 3

```http
POST /books
```

Telo:

```json
{
  "title": "FastAPI",
  "author": "Ana"
}
```

Pitaš:

- “napravi novu knjigu i posalji mi njen sadržaj”

Ovde je `Body`.

---

### Zahtev 4

```http
POST /login
```

Forma:

```text
username=ana&password=secret
```

Pitaš:

- “prijavi korisnika preko forme u browseru”

Ovde je `Form`.

---

## 10) Koja je ključna razlika između `Query` i `Body`?

Najjednostavnije:

- `Query` = parametri za filtriranje i kontrolu u URL-u
- `Body` = stvarni sadržaj koji se šalje serveru

### Primer

```http
GET /books?author=Marko&limit=5
```

Ovo su query parametri.

Ali:

```http
POST /books
{
  "author": "Marko",
  "title": "Python"
}
```

Ovo je body.

---

## 11) Koja je ključna razlika između `Path` i `Query`?

### `Path`

- koristi se za identifikaciju konkretnog resursa
- deo URL-a koji sadrži glavni cilj
- npr. `/books/5`

### `Query`

- koristi se za dodatna podešavanja i filtere
- npr. `/books?genre=python&page=2`

Pat h parametar = “koj i resurs”, query parametar = “kako da ga prikažem / filtriram”.

---

## 12) Kod u FastAPI-u, često se koristi ovako

```python
from fastapi import FastAPI, Query, Path, Body, Form
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.get("/books/{book_id}")
async def read_book(
    book_id: int = Path(..., description="ID knjige"),
    q: str | None = Query(default=None, description="Pretraga")
):
    return {"book_id": book_id, "q": q}

@app.post("/books")
async def create_book(book: Book):
    return book

@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username, "password": password}
```

Ovo lepo pokazuje razliku:

- `book_id` = path
- `q` = query
- `book` = body
- `username` i `password` = form

---

## 13) Jednostavna pravila za pamćenje

### Kada koristiš `Path`?

Kad znaš tačno koji resurs želiš.

```http
/books/7
/users/3
/products/11
```

---

### Kada koristiš `Query`?

Kad želiš da dodaš filter, pretragu, paginaciju ili opcije.

```http
/books?search=python&limit=10&page=2
```

---

### Kada koristiš `Body`?

Kad šalješ podatke za kreiranje ili izmenu nečega.

```json
{
  "title": "Python",
  "author": "Marko"
}
```

---

### Kada koristiš `Form`?

Kad šalješ podatke iz HTML forme.

```text
username=ana&password=123
```

---

## 14) Najvažnija stvar za razumevanje

FastAPI nije “mnogo različitih načina za podatke”.

To je jedan HTTP zahtev, a razni delovi tog zahteva imaju različitu svrhu:

- path => gde je resurs
- query => dodatne opcije za taj resurs
- body => sadržaj podataka
- form => posebna vrsta sadržaja za HTML forme

Ako ovo razumeš, sve ostalo postaje mnogo lakše.

---

## 15) Kratka definicija u jednoj rečenici

- `Path` = “koji resurs?”
- `Query` = “kako da ga filtriram / pogledam?”
- `Body` = “šta šaljem u JSON-u?”
- `Form` = “šta šaljem preko HTML forme?”

---

## 16) Dodatni zadatak za tebe

Napiši 4 zahteva i razmisli šta je šta:

1. `GET /books/3`
2. `GET /books?genre=python&limit=5`
3. `POST /books` sa JSON body-jem
4. `POST /login` sa form podacima

I posle toga odgovori:

- koji je path?
- koji je query?
- koji je body?
- koji je form?

Ako to uradiš, razumevanje je već veoma dobro.
