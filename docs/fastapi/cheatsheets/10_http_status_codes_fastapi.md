# HTTP status codes cheat sheet za FastAPI

Ovo je kratka referenca za najvažnije HTTP status kodove koje koristiš u FastAPI-u.

---

## 1) Najvažniji status kodovi

### `200 OK`

Znači: zahtev je uspešno obrađen.

```python
@app.get("/books")
async def get_books():
    return {"message": "OK"}
```

Koristi se kada:

- vraćaš podatke
- čitaš listu ili jedan zapis

---

### `201 Created`

Znači: novi resurs je uspešno kreiran.

```python
@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book():
    return {"message": "Knjiga je kreirana"}
```

Koristi se kada:

- praviš novi zapis
- dodaješ novu knjigu, korisnika, proizvod itd.

---

### `204 No Content`

Znači: zahtev je uspešno obavljen, ali nema sadržaja za odgovor.

```python
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    pass
```

Koristi se kada:

- obrišeš nešto
- nemaš potrebu da vraćaš JSON odgovor

---

### `400 Bad Request`

Znači: zahtev je loš ili neispravan.

```python
raise HTTPException(status_code=400, detail="Loš zahtev")
```

Koristi se kada:

- klijent šalje neispravne podatke
- logika zahteva ne prođe

---

### `401 Unauthorized`

Znači: korisnik nije prijavljen ili nema validne kredencijale.

```python
raise HTTPException(status_code=401, detail="Niste prijavljeni")
```

---

### `403 Forbidden`

Znači: korisnik je prijavljen, ali nema dozvolu da pristupi resursu.

```python
raise HTTPException(status_code=403, detail="Nemaš dozvolu")
```

---

### `404 Not Found`

Znači: traženi resurs ne postoji.

```python
raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

Koristi se kada:

- nema knjige sa datim ID-jem
- nema korisnika, proizvoda itd.

---

### `409 Conflict`

Znači: postoji konflikt sa postojećim podacima.

```python
raise HTTPException(status_code=409, detail="Knjiga već postoji")
```

Koristi se kada:

- pokušavaš da dodaš duplikat
- resurs već postoji

---

### `422 Unprocessable Entity`

Znači: podatak je poslat, ali ne prolazi validaciju.

Ovo je često automatski vrati Pydantic ako JSON ne odgovara modelu.

```python
# primer: title je obavezno, a nije poslato
```

Koristi se kada:

- nedostaju polja
- tipovi nisu ispravni
- validacija ne prođe

---

## 2) Šta je `status` modul u FastAPI-u?

`status` je objekat u `fastapi` modulu koji sadrži konstante za najčešće HTTP status kodove.

```python
from fastapi import status

print(status.HTTP_200_OK)
print(status.HTTP_201_CREATED)
print(status.HTTP_404_NOT_FOUND)
```

To daje:

- jasnije čitanje koda
- standardizovan HTTP kod
- bolji nadzor nad odgovorom

---

## 3) Šta je `status_code`?

`status_code` je parametar decorator-a u FastAPI-u.

```python
@app.post("/books", status_code=status.HTTP_201_CREATED)
```

Znači:

- ova ruta će vratiti HTTP 201
- server će klijentu javiti da je novi resurs kreiran

---

## 4) Razlika između `status` i `status_code`

### `status`

- skup konstanti
- npr. `status.HTTP_201_CREATED`

---

### `status_code`

- parametar koji se prosleđuje endpointu
- npr. `status_code=201`

Dakle:

```python
status_code=status.HTTP_201_CREATED
```

je isto što i:

```python
status_code=201
```

samo je čitljivije i standardizovanije.

---

## 5) Najčešći parovi u FastAPI-u

- `GET` -> `200 OK`
- `POST` -> `201 Created`
- `PUT` -> `200 OK` ili `204 No Content`
- `DELETE` -> `200 OK` ili `204 No Content`
- `404` -> ne postoji resurs
- `422` -> neispravan payload / validaciona greška

---

## 6) Jednostavan primer svih najvažnijih status kodova

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items")
async def get_items():
    return {"message": "OK"}

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item():
    return {"message": "Kreirano"}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id == 999:
        raise HTTPException(status_code=404, detail="Item nije pronađen")
    return {"id": item_id, "name": "Laptop"}
```

---

## 7) Kratka lista za pamćenje

- `200` = OK
- `201` = Created
- `204` = No Content
- `400` = Bad Request
- `401` = Unauthorized
- `403` = Forbidden
- `404` = Not Found
- `409` = Conflict
- `422` = Validation Error
- `500` = Internal Server Error

---

## 8) Primeri za tvoju aplikaciju

Za knjige:

- `GET /books` -> `200`
- `POST /books` -> `201`
- `GET /books/{book_id}` -> `200` ili `404`
- `PUT /books/{book_id}` -> `200` ili `404`
- `DELETE /books/{book_id}` -> `200` ili `404`

---

## 9) Ključna stvar za razumevanje

HTTP status code nije samo “broj”.

To je signal koji kaže klijentu:

- da li je sve bilo dobro
- da li je resurs kreiran
- da li je nešto nedostalo
- da li je nešto zabranjeno
- da li je nešto nepostojeće

To je osnovni jezik web aplikacija.

---

## 10) Finalna definicija

```python
status_code=status.HTTP_201_CREATED
```

Znači:

- endpoint će odgovoriti sa HTTP 201 Created
- `status` je skup gotovih HTTP konstanti iz FastAPI-ja
- `status_code` je parametar koji kaže FastAPI-u koji status treba da vrati

---

Ako želiš, mogu odmah da ti napravim i drugi cheat sheet:

- `HTTPException` cheat sheet
- `response_model` cheat sheet
- `PUT vs PATCH vs DELETE` cheat sheet
