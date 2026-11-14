# FastAPI: delovi HTTP zahteva — Path, Query, Body, Form

Ovaj fajl je napravljen da ti razjasni jednu stvar koja često zbunjuje početnike:

Kako je HTTP zahtev “poslagan” i zašto se u FastAPI-u koristi `Path`, `Query`, `Body`, `Form`.

Cilj je da to ne razumeš kao “četiri različita načina da proslediš podatke”, nego kao četiri različite uloge u jednom zahtevu.

---

## 1) Osnovna ideja: HTTP zahtev ima više “delova”

HTTP (Hypertext Transfer Protocol) zahtev je poruka koju klijent šalje serveru da bi tražio neki resurs ili izvršio neku akciju. Sastoji se od metode, URL-a, zaglavlja i opcionalnog tela (body), pri čemu svaki deo ima svoju specifičnu ulogu u komunikaciji između klijenta i servera.

Ključni delovi HTTP zahteva su:

1. HTTP metode koje koriste klijent i server. Server koristi metodu da odredi koju akciju treba da izvrši nad resursom dok klijent koristi metodu da naznači šta želi da uradi sa tim resursom.
   - `GET`, `POST`, `PUT`, `DELETE`, `PATCH` i druge metode koje definišu akciju nad resursom
2. URL (Uniform Resource Locator) koji koristi klijent da identifikuje resurs na serveru i eventualno prosledi dodatne parametre putem query string-a. Server koristi URL da odredi koji resurs treba da obradi i kako da primeni dodatne parametre.
   - path: /books/5/comments
   - query string: ?sort=latest
3. `Headers` (Zaglavlja) koja sadrže dodatne informacije o zahtevu, kao što su tip sadržaja, autorizacija, keševi (cache) itd. pa samim time najčešće služe za specifikaciju tipa sadržaja (`Content-Type`), autentifikaciju (`Authorization`) i keširanje (`Cache-Control`). Koriste ih i klijenti i serveri. Ove informacije pomažu serveru da pravilno obradi zahtev. Klijent šalje zaglavlja zajedno sa zahtevom, a server ih koristi za pravilno tumačenje i obradu podataka. Sve metode HTTP protokola mogu koristiti zaglavlja, i oni su ključni za kontrolu i sigurnost komunikacije između klijenta i servera.
   - primer: `Content-Type: application/json`
4. `Body` (Opcionalno telo zahteva) koje nosi podatke koje klijent šalje serveru, najčešće u JSON formatu. Server koristi body da dobije informacije potrebne za kreiranje ili izmenu resursa. Najčešće se koristi za `POST` i `PUT` metode, gde klijent šalje nove ili izmenjene podatke serveru.
   - primer: `{ "text": "Odlican članak", "author": "Marko" }`

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

URL (Uniform Resource Locator) se sastoji od više delova:

```text
https://example.com/books/42?category=programming&page=2
```

Podeljeno:

- `https://` = scheme (protokol koji se koristi za komunikaciju)
- `example.com` = host (domen servera na koji šaljemo zahtev)
- `/books/42` = path (putanja do resursa na serveru)
- `?category=programming&page=2` = query string (dodatni parametri za filtriranje, pretragu, paginaciju itd.)

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

---

### Zašto je ovo važno?

Pošto path parametar opisuje “šta je cilj”:

- `/users/7` => korisnik broj 7
- `/books/10` => knjiga broj 10
- `/products/99` => proizvod broj 99

---

### Jednostavna mentalna slika

Path parametar je kao:

- “na kojoj ulici živiš?”
- “koji je ID objekta?”
- “koji resurs želim da otvorim?”

---

## 4) `Query` parametri

### Definicija

`Query` parametri su dodatni podaci u URL-u, posle `?`. Oni služe za filtriranje, pretragu, paginaciju i druge opcije koje ne menjaju identitet resursa, već način na koji se resursi prikazuju ili pretražuju.

Primer:

```http
GET /books?category=python&limit=10&page=2
```

Ovde je:

- `/books` = putanja do kolekcije resursa (npr. svih knjiga)
- `?category=python` = filter po kategoriji (npr. samo Python knjige)
- `&limit=10` = ograničenje broja rezultata po strani (npr. prikazati najviše 10 knjiga po strani)
- `&page=2` = broj strane rezultata koji želimo da prikažemo (npr. druga strana sa rezultatima)

U FastAPI-u:

```python
@app.get("/books")
async def get_books(category: str | None = None, limit: int = 10, page: int = 1):
    return {"category": category, "limit": limit, "page": page}
```

---

### Zašto je ovo važno?

Query parametri služe za:

- filtriranje (npr. po kategoriji, tagovima ili drugim atributima)
- pretragu (npr. traženje resursa po ključnim rečima)
- paginaciju (kontrola broja i redosleda rezultata po stranama)
- sortiranje (npr. po ceni, datumu ili abecednom redu)
- dodatne opcije (npr. filtriranje po tagovima, statusu ili drugim atributima)

---

### Jednostavna mentalna slika

Query parametri su kao:

- “prikaži mi samo Python knjige”
- “vrati 10 rezultata”
- “prikaži drugu stranu”

To nisu identifikatori resursa, nego parametri koje koristiš za kontrolu prikaza ili filtera.

---

## 5) `Body`

### Definicija

`Body` je telo HTTP zahteva, najčešće JSON. Sadrži podatke koje klijent šalje serveru, a server ih koristi za kreiranje ili izmenu resursa. Ovo je mesto gde se šalju svi detalji novog ili izmenjenog objekta, a ne samo identifikator resursa.

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

---

### Zašto je ovo važno?

Body se koristi za podatke koje se šalju sa zahtevom, posebno kada praviš novi resurs:

- kreiranje knjige (slanje svih detalja nove knjige)
- kreiranje korisnika (slanje svih potrebnih informacija za novog korisnika)
- kreiranje naloga (slanje svih potrebnih informacija za novi nalog)
- izlaz sa velikim objektom (slanje kompletnog sadržaja koji se kreira ili menja)

VAŽNO: Body ne ide u URL, nego u telo zahteva.

---

### Jednostavna mentalna slika

Body je kao:

- “ovo je sadržaj koji šaljem serveru” (npr. novi ili izmenjeni objekat)
- “neka nova knjiga koju želim da dodam” (sadržaj koji šaljem serveru)

---

## 6) `Form`

### Definicija

`Form` je specijalni oblik body-ja, koji se koristi kada podaci dolaze iz HTML formi. To znači da se podaci šalju kao `application/x-www-form-urlencoded` ili `multipart/form-data`, a ne kao JSON.

HTML forme predaju podatke serveru kroz `Form` objekat. HTML forme šalje browser kada korisnik popuni formu (npr. unese korisničko ime i lozinku) i klikne na dugme za slanje. Server tada prima podatke kao `Form` parametre, a ne kao JSON. FastAPI omogućava da ove parametre direktno mapiraš u funkcijske argumente (npr. `username: str = Form()`) koristeći `Form()`. Ovo je korisno kada želiš da obradiš podatke iz HTML formi bez potrebe za JSON-om.

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

---

### Značenje

`Form` se koristi kada:

- korisnik šalje podatke preko HTML forme (npr. popunjava login formu)
- podaci dolaze kao `application/x-www-form-urlencoded` do servera ako je forma obična HTML forma (bez fajlova)
- ili za upload fajlova (`multipart/form-data`) kada forma sadrži fajl input polja (npr. `<input type="file" name="file" />`). Input polja za fajlove se takođe mapiraju koristeći `Form()` ili `File()` u FastAPI-u.

---

### Bitna razlika

- `Body` = najčešće JSON objekat koji se šalje u telu zahteva
- `Form` = oblik podataka iz browser forme koji se šalje u telu zahteva kao `application/x-www-form-urlencoded` ili `multipart/form-data`

Nije isto:

```python
book: BookCreate
```

i:

```python
username: str = Form()
```

Prvo je JSON objekat i služi za prenos struktuisanih podataka u telu zahteva, drugo su form polja u HTML obrascu i služe za prenos podataka iz browsera u telu HTTP zahteva.

---

## 7) Najveća zbunjenost: “šta ide gde?”

Ovo je deo gde mnogi početnici najviše greše, jer nije uvek jasno kada koristiti path parametre, query parametre, body ili form. U suštini, razlika se svodi na to šta šalješ i kako to šalješ: URL, query string, telo zahteva ili HTML formu.

### Podela po ulogama

#### Path parametri

Koriste se za identifikaciju konkretne stvari:

```http
GET /books/5
```

- ovde je `5` identifikator knjige

---

#### Query parametri

Koriste se za dodatne opcije i filtere:

```http
GET /books?category=python&limit=10
```

- `category` i `limit` nisu objekti, nego opcije

---

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

- ovo je stvarni sadržaj koji se kreira i šalje serveru u telu HTTP zahteva

---

#### Form

Koriste se za browser forme ili upload:

```http
POST /login
```

Telo forme: ovo je sadržaj koji se šalje serveru kada korisnik popuni HTML formu i pošalje je.

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

---

### Query

- deo URL-a posle `?`
- koristi se za filter, page, sort, search
- npr. `/books?genre=python&limit=5`
- ne koristi se za prenos struktuisanih podataka, već samo za opcije i filtere

---

### Body (JSON)

- U telu HTTP zahteva se nalazi JSON objekat koji se šalje serveru
- Koristi se kada želiš da pošalješ strukturisane podatke serveru, kao što su objekti ili složeni podaci
- npr. `{ "title": "Python" }`

---

### Form (HTML)

- U telu HTTP zahteva, ali u `form` formatu (`application/x-www-form-urlencoded` ili `multipart/form-data`) se šalju podaci iz HTML forme koja je popunjena u browseru
- Koristi se kada želiš da pošalješ podatke iz HTML forme serveru
- npr. `username=ana&password=123`, što predstavlja podatke koje je korisnik uneo u HTML formu.

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

Najkraće rečeno:

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

Ovo je body, odnosno sadržaj koji se šalje serveru u telu HTTP zahteva.

---

## 11) Koja je ključna razlika između `Path` i `Query`?

### `Path`

- Koristi se za identifikaciju konkretnog resursa
- deo URL-a koji sadrži glavni cilj
- npr. `/books/5`

### `Query`

- Koristi se za dodatna podešavanja i filtere
- npr. `/books?genre=python&page=2`

Path parametar = “Koji resurs”
Query parametar = “Kako da ga prikažem / filtriram”.

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

To je `jedan HTTP zahtev`, a razni delovi tog zahteva imaju različitu svrhu:

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

Napiši 4 zahteva u HTTP formatu i razmisli šta je šta:

1. `GET /books/3`

```http
http://example.com/books/3
```

2. `GET /books?genre=python&limit=5`

```http
http://example.com/books?genre=python&limit=5
```

3. `POST /books` sa JSON body-jem

```http
POST /books HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "title": "Python",
  "author": "Marko"
}
```

4. `POST /login` sa form podacima

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=ana&password=123
```

I posle toga odgovori:

- Koji je path?
- Path je deo URL-a koji identifikuje konkretan resurs, npr. `/books/3` ili `/users/3`.
- Koji je query?
- Query je deo URL-a koji sadrži dodatne opcije ili filtere, npr. `?genre=python&limit=5`.
- Koji je body?
- Body je sadržaj koji se šalje u telu HTTP zahteva, obično u JSON formatu, npr. `{"title": "Python", "author": "Marko"}`.
- Koji je form?
- Form je sadržaj koji se šalje preko HTML forme, obično u `application/x-www-form-urlencoded` formatu, npr. `username=ana&password=123`.

Ako to uradiš, razumevanje je već veoma dobro.
