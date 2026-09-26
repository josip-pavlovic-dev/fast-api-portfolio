# FastAPI - POST, PUT i DELETE Requests

## Dan 3 — Request Body i POST u FastAPI

Ovo je sledeći logičan korak. Do sada si radio sa:

- URL rutom
- Path Parameters
- Query Parameters

Sada učiš nešto što je najvažnije za “pravi API”:

- kako klijent šalje podatke serveru
- kako se ti podaci zovu Request Body
- kako se kreira novi resurs preko POST zahteva

---

## 1) Šta je Request Body?

Request Body je deo HTTP zahteva u kome se šalju podaci.

To nisu parametri u URL-u, kao što su:

- `/users/5`
- `/items?limit=10`

To je podatak koji ide u telo zahteva, najčešće u JSON formatu.

Primer JSON tela zahteva:

```json
{
  "title": "Python za početnike",
  "author": "Marko"
}
```

To znači:

- klijent šalje podatke
- server ih prima
- server može da ih snimi, obradi, ili vrati nazad

---

## 2) Gde se Request Body koristi?

Najčešće se koristi u metodima:

- POST → kreiranje novog resursa
- PUT → izmena postojećeg resursa
- PATCH → delimična izmena

Mi ćemo prvo obraditi POST, a kasnije PUT i DELETE.

---

## 3) Šta je POST?

POST je HTTP metod koji se koristi kada želiš da kreiraš novi objekat.

Primer:

```python
@app.post("/books")
```

Ovo znači:

- na ruti `/books`
- poslaće se novi podatak
- server će napraviti novu knjigu

---

## 4) Osnovni primer: POST bez Request Body-a

Možeš da imaš i jednostavan POST bez tela zahteva, ali u praksi gotovo uvek postoji body.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/hello")
def create_hello():
    return {"message": "Pozdrav iz POST zahteva"}
```

Ovo je validno, ali ne koristi podatke koje šalje klijent.

Najčešće ćemo ipak slati JSON podatke.

---

## 5) POST sa Request Body-jem

Evo najvažnijeg primera za početak:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.post("/books")
def create_book(book: Book):
    return {
        "message": "Knjiga je kreirana",
        "book": book
    }
```

---

## 6) Objašnjenje koda

### `from pydantic import BaseModel`

Pydantic je biblioteka koja nam pomaže da definišemo strukturu podataka i da ih validiramo.

### `class Book(BaseModel):`

Ovo je model podatka. On kaže:

- `title` mora biti string
- `author` mora biti string

Znači:

```python
Book(
    title="Python",
    author="Marko"
)
```

je validno.

Ali ovo ne bi bilo validno:

```python
Book(
    title=123,
    author="Marko"
)
```

jer `title` mora biti string.

---

## 7) Kako FastAPI koristi Request Body?

Kada klijent pošalje zahtev:

```http
POST /books
```

sa telom:

```json
{
  "title": "Python za početnike",
  "author": "Marko"
}
```

FastAPI će:

1. pročitati JSON body
2. proveriti da li odgovara modelu `Book`
3. proslediti objekat `book` funkciji `create_book`
4. funkcija vraća odgovor

---

## 8) Primer odgovora

Ako pošalješ zahtev:

```http
POST /books
Content-Type: application/json
```

sa telom:

```json
{
  "title": "Python za početnike",
  "author": "Marko"
}
```

odgovor će biti:

```json
{
  "message": "Knjiga je kreirana",
  "book": {
    "title": "Python za početnike",
    "author": "Marko"
  }
}
```

To je veoma tipičan API odgovor.

---

## 9) Šta je JSON body?

JSON (JavaScript Object Notation) je format podataka u kome se podaci šalju kao ključevi i vrednosti.

Primer:

```json
{
  "title": "Python",
  "author": "Ana"
}
```

To je isto što i Python dict:

```python
{
    "title": "Python",
    "author": "Ana"
}
```

---

## 10) Request Body vs Path Parameters vs Query Parameters

Ovo je veoma važno da razlikuješ.

### Path Parameters

Koriste se za konkretan resurs:

```http
GET /books/7
```

### Query Parameters

Koriste se za dodatne opcije:

```http
GET /books?category=python&limit=5
```

### Request Body

Koriste se za podake koje se šalju da bi se kreirao ili izmenio resurs:

```http
POST /books
{
  "title": "Python",
  "author": "Ana"
}
```

---

## 11) Zašto je Request Body bitan?

Jer mnogo API-ja radi sa podacima koje korisnik unosi.

Primeri:

- kreiranje nove knjige
- kreiranje novog korisnika
- pravljenje novog proizvoda
- slanje poruke
- kreiranje naloga

U svim tim slučajevima korisnik treba da pošalje podatke u telu zahteva, a ne u URL-u.

---

## 12) Najčešće greške za početnike

### Greška 1: šalješ podatke u URL umesto u body

Netačno:

```http
POST /books?title=Python&author=Ana
```

To može raditi, ali to nije “pravi” način za POST body. U praksi se koristi JSON body.

---

### Greška 2: ne praviš model

Netačno:

```python
@app.post("/books")
def create_book(title: str, author: str):
    return {"title": title, "author": author}
```

Ovo radi, ali to je drugačiji pristup. U FastAPI-u je puno čistije i profesionalnije koristiti Pydantic model.

---

### Greška 3: ne koristiš JSON format

Ako pošalješ body u pogrešnom formatu, FastAPI možda neće znati šta da radi.

Pravilan JSON body je:

```json
{
  "title": "Python",
  "author": "Ana"
}
```

---

## 13) Zašto Pydantic model pomaže?

Pydantic model pomaže zato što:

- definiše strukturu podataka
- validira tipove
- preventira neispravan unos
- čini kod jasnijim i urednijim

Na primer, model:

```python
class Book(BaseModel):
    title: str
    author: str
```

znači:

- `title` mora biti tekst
- `author` mora biti tekst

To je mnogo bolji način od ručnog proveravanja.

---

## 14) Jednostavan mentalni model

Zamislite da API radi kao forma:

- path parametri = adresa
- query parametri = opcije
- request body = podatak koji user unosi u formu

Primer:

- `/books/3` → konkretna knjiga
- `/books?category=python` → filter
- POST /books sa body-om → kreiranje nove knjige

---

## 15) Šta ćeš koristiti u praksi?

Na početku, najčešće ćeš raditi:

- `GET` za čitanje
- `POST` za kreiranje
- `PUT` za izmenu
- `DELETE` za brisanje

A Request Body će biti centralni deo za POST i PUT.

---

## 16) Vežba za danas

Pokušaj da napišeš ovaj primer:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.post("/books")
def create_book(book: Book):
    return {"message": "Knjiga kreirana", "data": book}
```

I zamisli da pošalješ:

```json
{
  "title": "Django za početnike",
  "author": "Petar"
}
```

Kako bi trebao da izgleda odgovor?

Trebao bi da bude:

```json
{
  "message": "Knjiga kreirana",
  "data": {
    "title": "Django za početnike",
    "author": "Petar"
  }
}
```

Ako to znaš da objasniš, znaš osnovu Request Body i POST metoda.

---

## 17) Ključne stvari koje treba da zapamtiš

- Request Body je podatak koji ide u telo zahteva
- Najčešće je u JSON formatu
- Koristi se za kreiranje i izmenu podataka
- U FastAPI-u se definiše preko Pydantic modela
- POST se koristi za kreiranje novog resursa
- FastAPI automatski validira podatke

---

## 18) Sledeći korak

Nakon ovog dela, prirodno ide:

1. PUT
2. DELETE
3. Request Body + validacija u većim primerima
4. Pydantic modeli za više polja

To je sledeći korak u razvoju API-ja.

---


## Dan 4 — PUT u FastAPI

Sada kada znaš šta je Request Body i šta radi POST, prelazimo na sledeću vrlo važnu operaciju: PUT.

PUT se koristi za izmenu postojećeg resursa.

---

## 1) Šta je PUT?

PUT znači:

- “nađi postojeći resurs”
- “zameni ga novim podacima”
- “ili ga potpuno ažuriraj”

Na primer:

```http
PUT /books/1
```

znači:

- želim da izmenim knjigu sa ID 1

---

## 2) PUT vs POST

To je vrlo važno da razumeš.

### POST

Kreira novi resurs:

```http
POST /books
```

### PUT

Menja postojeći resurs:

```http
PUT /books/1
```

Dakle:

- POST = novi zapis
- PUT = izmena postojećeg zapisa

---

## 3) Primer PUT endpointa

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    return {
        "message": "Knjiga je ažurirana",
        "book_id": book_id,
        "book": book
    }
```

Ovo znači:

- `book_id` je path parametar
- `book` je request body
- endpoint menja knjigu sa tim ID-jem

---

## 4) Kako se poziva PUT?

Zahtev izgleda ovako:

```http
PUT /books/1
Content-Type: application/json
```

Telo zahteva:

```json
{
  "title": "Python za napredne",
  "author": "Ana"
}
```

Odgovor:

```json
{
  "message": "Knjiga je ažurirana",
  "book_id": 1,
  "book": {
    "title": "Python za napredne",
    "author": "Ana"
  }
}
```

---

## 5) Šta je zajedničko sa POST?

I POST i PUT koriste Request Body.

Razlika je u smislu:

- POST: pravi novi resurs
- PUT: menja postojeći resurs

U oba slučaja se podaci šalju u JSON telu zahteva.

---

## 6) Zašto je PUT koristan?

PUT je koristan kada:

- želiš da promeniš celo polje
- želiš da zamenimo celu strukturu objekta
- menjaš podatke za konkretan ID

Primer:

```json
{
  "title": "Novi naslov",
  "author": "Novi autor"
}
```

Ovo može da zameni postojeće podatke za knjigu.

---

## 7) PUT i validacija

Kao i kod POST, FastAPI validira body modelom.

Ako pošalješ:

```json
{
  "title": 123,
  "author": "Ana"
}
```

to neće proći, jer `title` mora biti string.

---

## 8) PUT + Path Param + Body

Ovo je osnovni obrazac za većinu API endpointa.

```python
@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    ...
```

To znači:

- `book_id` identifikuje resurs
- `book` sadrži nove vrednosti
- funkcija radi izmenu

---

## 9) Dobar mentalni model

Zamislite to ovako:

- path param = “koji objekat menjam”
- body = “kakve nove vrednosti želim”

Na primer:

```http
PUT /books/7
```

sa body-om:

```json
{
  "title": "Novi naslov",
  "author": "Marko"
}
```

znači:

- menjam knjigu broj 7
- postaviću joj novi naslov i novog autora

---

## 10) Najčešće greške

### Greška 1: PUT bez path parametra

Netačno:

```python
@app.put("/books")
def update_book(book: Book):
    ...
```

Ako menjaš konkretan objekat, ti treba ID:

```python
@app.put("/books/{book_id}")
```

---

### Greška 2: zaboraviš body

PUT bez body-a nema smisla, jer moraš poslati nove podatke za izmenu.

---

### Greška 3: mešaš POST i PUT

- POST = kreiraj novi
- PUT = izmeni postojeći

---

## 11) Dovoljno za danas

Za danas je dovoljno da razumeš:

- šta je PUT
- kada se koristi
- kako kombinuješ path parametre i body
- kako se razlikuje od POST

---

## 12) Ključni koncept za pamćenje

PUT endpoint izgleda ovako:

```python
@app.put("/resource/{resource_id}")
def update_resource(resource_id: int, payload: Model):
    ...
```

To znači:

- resurs se identifikuje preko `resource_id`
- novo stanje dolazi iz `payload`

---

## 13) Šta sledi posle PUT?

Sledeća logika je:

- DELETE
- kako se briše konkretan resurs
- kako se kombinuje path parametar i delete metoda

To je prirodan nastavak i odmah posle toga možemo da uradimo i DELETE u istom stilu.

---

## Kratka vežba za danas

Napiši ovaj kod:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    return {"book_id": book_id, "updated_book": book}
```

Zamisli zahtev:

```http
PUT /books/3
```

sa body-om:

```json
{
  "title": "Nova knjiga",
  "author": "Petar"
}
```

Ako znaš šta će odgovor biti, onda si savladao PUT.

---

Naravno — i DELETE nije komplikovan ako znaš prethodne dve stvari.

Najvažnije je da razumeš:

- DELETE se koristi za brisanje
- obično radi sa path parametrom
- nema Request Body u većini jednostavnih slučajeva
- endpoint zna “koji resurs da obriše” preko ID-ja

---

## Dan 5 — DELETE u FastAPI

DELETE je HTTP metoda koja se koristi kada želiš da obrišeš neki resurs.

Najčešće se koristi ovako:

```http
DELETE /books/3
```

To znači:

- obriši knjigu sa ID 3

---

## 1) Šta je DELETE?

DELETE je metoda za brisanje.

Primer endpointa:

```python
from fastapi import FastAPI

app = FastAPI()

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    return {"message": f"Knjiga {book_id} je obrisana"}
```

Ako pozoveš:

```http
DELETE /books/5
```

odgovor će biti:

```json
{
  "message": "Knjiga 5 je obrisana"
}
```

---

## 2) DELETE i path parameter

DELETE najčešće koristi path parametar za identifikaciju resursa.

Primer:

```python
@app.delete("/books/{book_id}")
```

Ovde je:

- `book_id` = konkretan ID knjige koju brišemo

To je vrlo uobičajeno i vrlo jednostavno.

---

## 3) DELETE vs POST i PUT

### POST

Kreira novi resurs

```http
POST /books
```

### PUT

Menja postojeći resurs

```http
PUT /books/3
```

### DELETE

Briše postojeći resurs

```http
DELETE /books/3
```

To je čitav osnovni CRUD ciklus:

- Create = POST
- Read = GET
- Update = PUT
- Delete = DELETE

---

## 4) Primer sa kombinacijom svih 4 metoda

Evo jednostavnog primera koji pokazuje cilj celog koncepta:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

books = []

@app.get("/books")
def get_books():
    return {"books": books}

@app.post("/books")
def create_book(book: Book):
    books.append(book)
    return {"message": "Knjiga je kreirana", "book": book}

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    if book_id >= len(books):
        return {"message": "Knjiga nije pronađena"}
    books[book_id] = book
    return {"message": "Knjiga je ažurirana", "book": book}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id >= len(books):
        return {"message": "Knjiga nije pronađena"}
    deleted = books.pop(book_id)
    return {"message": "Knjiga je obrisana", "book": deleted}
```

Ovo je jednostavan, ali vrlo dobar primer kako API radi u praksi.

---

## 5) Najvažnija stvar o DELETE-u

DELETE obično ne treba Request Body.

Zašto?

Jer ID resursa koji se briše već postoji u URL-u:

```http
DELETE /books/7
```

Ne treba da pišeš:

```http
DELETE /books/7
{
  "id": 7
}
```

To je nepotrebno.

---

## 6) Kada DELETE koristi body?

U praksi se ponekad koristi, ali za početak to nije potreban model. Kod jednostavnog API-ja, DELETE sa path parametrom je potpuno normalno.

---

## 7) Primer odgovora

Ako pozoveš:

```http
DELETE /books/2
```

odgovor može biti:

```json
{
  "message": "Knjiga 2 je obrisana"
}
```

Ili nešto malo detaljnije:

```json
{
  "message": "Knjiga je obrisana",
  "deleted_book_id": 2
}
```

---

## 8) DELETE i validacija

DELETE obično ne validira body, jer nema body.

Ali validira path parametar:

```python
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    ...
```

Ovo znači:

- `book_id` mora biti int
- ako pošalješ `/books/abc`, FastAPI će vratiti grešku 422

---

## 9) Kratko poređenje

### POST

```http
POST /books
{
  "title": "Python",
  "author": "Ana"
}
```

### PUT

```http
PUT /books/1
{
  "title": "Novi Python",
  "author": "Ana"
}
```

### DELETE

```http
DELETE /books/1
```

---

## 10) Mentalni model za DELETE

DELETE ide ovako:

- “Znam koji resurs želim da obrišem”
- “To je iskazano u URL-u”
- “Ne šaljem body, jer ID sam po sebi dovoljno govori šta se briše”

---

## 11) Ključne stvari za pamćenje

- DELETE briše resurs
- najčešće koristi path parametar
- nema body u standardnom slučaju
- najčešće se koristi sa `/{id}`
- FastAPI validira ID tip

---

## 12) Mini vežba

Napiši ovaj kod:

```python
from fastapi import FastAPI

app = FastAPI()

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    return {"message": f"Knjiga {book_id} je obrisana"}
```

Zamisli zahtev:

```http
DELETE /books/9
```

Odgovor će biti:

```json
{
  "message": "Knjiga 9 je obrisana"
}
```

Ako znaš to, onda znaš osnovu DELETE.

---

## 13) Dovoljno za danas

Za ovaj dan je dovoljno da razumeš:

- šta je DELETE
- kada se koristi
- kako radi sa path parametrom
- kako se razlikuje od POST i PUT
- da je DELETE obično jednostavan i bez body-ja

---

## 14) Kraj osnovnog CRUD-a

Ovo je praktično kraj osnovnog dela:

- GET
- POST
- PUT
- DELETE

To je već dovoljna osnova za rad sa API endpointima u praksi.

---

## 15) Sledeći pravac

Nakon CRUD-a, prirodno dolaze:

- status codes
- response models
- Pydantic models za odgovor
- database
- SQLAlchemy / SQLite

Ali to je već sledeći nivo, a za sada si već dobro prošao osnovu.

---

Ako želiš, mogu odmah da nastavimo u jednom od ova 3 pravca:

1. Status codes i HTTP odgovori
2. Response models i Pydantic
3. Mini CRUD projekat sa knjigama, korak po korak
