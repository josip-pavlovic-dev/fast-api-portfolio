# FastAPI: HTTP metode i status kodovi

Ovaj fajl nastavlja praksu koja nam je bila potrebna: ne gledamo samo “kako da napišemo endpoint”, nego i “šta znači svaki HTTP zahtev i zašto server vraća baš taj status”.

Bez ovog dela, API postaje “samo funkcije koje vraćaju nešto”, a ne razumljiv i ispravan HTTP servis.

---

## 1) Šta je HTTP metoda?

HTTP metoda govori serveru šta želiš da uradiš.

Najčešće metode u API-ju:

- `GET` -> čitanje podataka
- `POST` -> kreiranje novog resursa
- `PUT` -> potpuna izmena postojećeg resursa
- `PATCH` -> delimična izmena
- `DELETE` -> brisanje

Primer:

```http
GET /books
```

Znači: “vrati mi listu knjiga”.

```http
POST /books
```

Znači: “napravi novu knjigu”.

---

## 2) Zašto je metoda važna?

Ista ruta može da radi različite stvari, zavisno od metode:

```http
GET /books/5
POST /books
PUT /books/5
DELETE /books/5
```

To je normalan REST stil:

- `GET /books/5` => uzmi knjigu sa ID 5
- `POST /books` => napravi novu knjigu
- `PUT /books/5` => zameni knjigu sa ID 5
- `DELETE /books/5` => obriši knjigu sa ID 5

To nije slučajno. HTTP metode su deo semantike API-ja.

---

## 3) Objašnjenje po metodama

### `GET`

Koristi se za čitanje.

```python
@app.get("/books")
async def get_books():
    return books
```

- ne menja podatke
- ne pravi novi zapis
- koristi se za prikaz informacija

### `POST`

Koristi se za kreiranje novog resursa.

```python
@app.post("/books")
async def create_book():
    return {"message": "Book created"}
```

- obično vraća 201 Created
- kreira novi zapis

### `PUT`

Koristi se za potpuno ažuriranje resursa.

```python
@app.put("/books/{book_id}")
async def update_book(book_id: int):
    return {"message": f"Updated book {book_id}"}
```

- očekuješ da resurs potpuno postoji
- često menja sve polje koje definiše objekat

### `PATCH`

Koristi se za delimično ažuriranje.

```python
@app.patch("/books/{book_id}")
async def patch_book(book_id: int):
    return {"message": f"Patched book {book_id}"}
```

- menjaju se samo neka polja
- često se koristi kada menjaš samo jedan atribut

### `DELETE`

Koristi se za brisanje.

```python
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    return {"message": f"Deleted book {book_id}"}
```

- obično vraća 200 ili 204

---

## 4) Šta je status kod?

Status kod je odgovor servera klijentu.

On govori:

- da li je sve bilo uspešno
- da li je nešto nepostojeće
- da li je podatak nevažeći
- da li je server napravio grešku

Primer:

```http
200 OK
201 Created
400 Bad Request
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
```

Status kod je deo HTTP odgovora, a ne običan string.

---

## 5) Grupe status kodova

### 2xx -> uspešno

- `200 OK` -> uspešno završeno
- `201 Created` -> novi resurs je napravljen
- `204 No Content` -> uspešno, ali nema tela odgovora

### 3xx -> redirect

- `301` -> trajno premešteno
- `302` -> privremeno premešteno

### 4xx -> problem sa zahtevom ili resursom

- `400 Bad Request` -> loš zahtev
- `401 Unauthorized` -> nije prijavljen
- `403 Forbidden` -> zabranjeno
- `404 Not Found` -> resurs ne postoji
- `422 Unprocessable Entity` -> validacija je pala

### 5xx -> greška servera

- `500 Internal Server Error` -> nepredviđena server greška
- `503 Service Unavailable` -> servis trenutno nije dostupan

---

## 6) `status_code` u FastAPI-u

U FastAPI-u se status kod obično postavlja preko parametra `status_code` u dekoratoru.

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book():
    return {"message": "Knjiga je kreirana"}
```

Ovo znači:

- ako je endpoint uspešno završio,
- server vraća HTTP 201 Created.

### Zašto je ovo važno?

Jer API treba da vraća semantički ispravan odgovor, ne samo “uspešno radim nešto”.

### Jednostavan primer

```python
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    return None
```

Ovo znači: brisanje je uspelo, i nema tela odgovora.

---

## 7) `status` modul

FastAPI ima `status` modul, koji sadrži konstante:

```python
from fastapi import status
```

Primeri:

```python
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_400_BAD_REQUEST
status.HTTP_404_NOT_FOUND
status.HTTP_422_UNPROCESSABLE_ENTITY
```

Ovo je lepše i jasnije nego da pišeš brojeve direktno.

### Prednost

```python
status.HTTP_201_CREATED
```

je mnogo čitljivije od:

```python
201
```

---

## 8) `HTTPException`

`HTTPException` je način da server eksplicitno vrati grešku sa status kodom i detaljnim porukama.

Primer:

```python
from fastapi import HTTPException

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    if book_id == 999:
        raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
    return {"id": book_id, "title": "Python"}
```

Ako korisnik traži knjigu koja ne postoji, server vraća:

```json
{
  "detail": "Knjiga nije pronađena"
}
```

### Zašto je to korisno?

Jer korisnik treba da zna:

- što je problem
- šta se desilo
- koja je greška

### Dobra praksa

```python
raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

je bolje od:

```python
raise HTTPException(status_code=404)
```

Jer prva verzija daje jasnu poruku.

---

## 9) Kada koristimo `status_code` a kada `HTTPException`?

To je često pitanje početnika.

### `status_code`

Koristi se kada endpoint uspešno radi, ali želiš eksplicitno da vratiš konkretnu HTTP status oznaku.

```python
@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book():
    return {"message": "Kreirano"}
```

### `HTTPException`

Koristi se kada nešto nije u redu i treba da vratiš grešku.

```python
raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Jednostavna formula

- uspeh => `status_code`
- greška => `HTTPException`

---

## 10) Najčešći REST obrasci u API-ju

### Kreiranje

```python
@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    return {"message": "created"}
```

### Čitanje svih

```python
@app.get("/books")
async def get_books():
    return books
```

### Čitanje jednog

```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    return book
```

### Ažuriranje punim PUT

```python
@app.put("/books/{book_id}")
async def update_book(book_id: int, book: BookUpdate):
    return {"message": f"Updated {book_id}"}
```

### Delimično PATCH

```python
@app.patch("/books/{book_id}")
async def patch_book(book_id: int):
    return {"message": f"Patched {book_id}"}
```

### Brisanje

```python
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    return None
```

---

## 11) Realan primer: kompletan CRUD endpoint

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None

books = [
    {"id": 1, "title": "Python", "author": "Marko"},
    {"id": 2, "title": "FastAPI", "author": "Ana"},
]

@app.get("/books")
async def get_books():
    return books

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
    }
    books.append(new_book)
    return new_book

@app.put("/books/{book_id}")
async def update_book(book_id: int, book: BookUpdate):
    for i, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            books[i].update({
                "title": book.title or existing_book["title"],
                "author": book.author or existing_book["author"],
            })
            return books[i]
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            del books[i]
            return None
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

Ovo je dobar praktičan pattern za svaki API.

---

## 12) Najčešće greške sa status kodovima

### Greška 1: vraćaš 200 za sve

```python
return {"message": "Kreirano"}
```

Ako je zapravo kreiranje novog resursa, bolje je:

```python
@app.post("/books", status_code=status.HTTP_201_CREATED)
```

### Greška 2: ne vraćaš detalj u `HTTPException`

```python
raise HTTPException(status_code=404)
```

Bolje:

```python
raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Greška 3: koristiš `201` bez kreiranja novog resursa

Ne treba da koristiš `201 Created` za običan GET.

---

## 13) Kako to zapamtiti jednostavno

### GET

- “uzmi podatke”
- 200 OK

### POST

- “napravi novi zapis”
- 201 Created

### PUT

- “zameni ceo resurs”
- 200 OK ili 204 No Content

### PATCH

- “izmeni samo deo”
- 200 OK

### DELETE

- “obriši”
- 200 OK ili 204 No Content

### GREŠKA

- 400, 404, 422, 500 itd.

---

## 14) Najvažnija filozofija

API nije samo “funkcija koja vraća dictionary”.

API je sistem koji treba da komunicira sa klijentom preko standardizovanih pravila:

- koja metoda se koristi
- koja ruta se traži
- koji status se vraća
- koja poruka se šalje u slučaju greške

Ako to razumeš, već si mnogo dalje od običnog “copy-paste” programiranja.

---

## 15) Kratka šema za pamćenje

```text
GET     -> read       -> 200 OK
POST    -> create     -> 201 Created
PUT     -> replace    -> 200 OK
PATCH   -> partial    -> 200 OK
DELETE  -> delete     -> 204 / 200
```

I:

```text
4xx -> problem sa zahtevom ili resursom
5xx -> problem sa serverom
```

---

## 16) Dobar zadatak za praksu

Napiši 5 endpointa za knjige:

1. `GET /books`
2. `GET /books/{id}`
3. `POST /books`
4. `PUT /books/{id}`
5. `DELETE /books/{id}`

Pa za svaki endpoint odgovori:

- koja je HTTP metoda?
- koji je status kod prirodan?
- da li treba `HTTPException`?

Ako to uradiš, naučićeš mnogo više nego samo od “pričanja o FastAPI-ju”.
