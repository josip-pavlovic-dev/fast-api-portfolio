# Karta pojmova za FastAPI

Ovo je osnovna karta pojmova za FastAPI. Napisana je jednostavno kako bi ti pomogla da brzo razumeš osnovne koncepte.

## Karta pojmova za FastAPI

### 1. FastAPI

FastAPI je Python framework za pravljenje API-ja.

- koristi se za backend aplikacije
- brzo se piše
- automatski validira podatke
- pravi JSON odgovore
- vrlo pogodan za REST API

---

### 2. API

API znači Application Programming Interface.

To je način na koji dve aplikacije komuniciraju.

Primer:

- frontend šalje zahtev
- backend vraća odgovor

---

### 3. Endpoint

Endpoint je ruta + funkcija koja obrađuje zahtev.

Primer:

```python
@app.get("/items")
def get_items():
    return {"items": []}
```

Ovo je endpoint.

---

### 4. Ruta

Ruta je URL adresa.

Primer:

```python
"/items"
"/users/1"
"/products/{product_id}"
```

Ruta govori “gde” se nalazimo u API-ju.

---

### 5. Decorator

Decorator je sintaksa koja povezuje URL sa funkcijom.

Primer:

```python
@app.get("/items")
```

Ovo znači:

- na ruti `/items`
- koristi se GET metod
- poziva se funkcija ispod

---

### 6. Function / Handler

To je Python funkcija koja se poziva kada korisnik pristupi ruti.

Primer:

```python
def get_items():
    return {"items": []}
```

Funkcija obrađuje zahtev i vraća odgovor.

---

### 7. Request

Request je zahtev koji klijent šalje serveru.

On može sadržati:

- URL
- query parametre
- path parametre
- body
- headers

---

### 8. Response

Response je odgovor koji server vraća klijentu.

Najčešće je to:

- JSON
- status code
- headers

Primer:

```json
{ "message": "Uspešno" }
```

---

### 9. GET

GET je HTTP metod za čitanje podataka.

Primer:

```python
@app.get("/users")
```

Koristi se kada želiš da dobiješ podatke.

---

### 10. POST

POST je HTTP metod za slanje novih podataka.

Primer:

```python
@app.post("/users")
```

Koristi se kada praviš novi objekat.

---

### 11. PUT

PUT se koristi za menjanje postojećeg podatka.

---

### 12. DELETE

DELETE se koristi za brisanje podataka.

---

### 13. Path Parameters

Path parameters su delovi URL-a koji su promenljivi.

Primer:

```python
@app.get("/users/{user_id}")
```

Ako je URL:

```http
/users/7
```

onda je `user_id = 7`.

---

### 14. Query Parameters

Query params su dodatni parametri u URL-u posle `?`.

Primer:

```http
/users?role=admin&active=true
```

Ovdje su:

- `role=admin`
- `active=true`

---

### 15. Request Body

Request body je telo zahteva, najčešće JSON.

Primer:

```json
{
  "name": "Ana",
  "age": 25
}
```

Koristi se sa POST ili PUT.

---

### 16. JSON

JSON je format podataka.

Primer:

```json
{ "name": "Ana", "age": 25 }
```

FastAPI najčešće vraća JSON.

---

### 17. Status Code

Status code je broj koji kaže da li je zahtev uspešan.

Najčešće:

- 200 OK
- 201 Created
- 400 Bad Request
- 404 Not Found
- 422 Unprocessable Entity

---

### 18. Validation

Validation znači proveravanje podataka.

FastAPI automatski proverava:

- da li je broj int
- da li je string
- da li je polje obavezno
- da li je vrednost pravilna

Primer:

```python
item_id: int
```

Ako se posalje string umesto broja, FastAPI može vratiti grešku.

---

### 19. Pydantic

Pydantic je biblioteka koja se koristi za validaciju podataka u FastAPI.

To je alat koji proverava da li su podaci ispravni.

---

### 20. Response Model

Response model je model koji opisuje kako će odgovor izgledati.

Primer:

```python
class Item(BaseModel):
    id: int
    name: str
```

To znači:

- odgovor mora da ima `id` i `name`

---

## Najkraća definicija za početak

FastAPI = framework za pravljenje API-ja

Endpoint = ruta + funkcija

Request = zahtev od klijenta

Response = odgovor od servera

Path params = promenljivi deo URL-a

Query params = dodatni parametri u URL-u

JSON = format podataka

---

## Jednostavno pamćenje

FastAPI radi ovako:

- klijent šalje zahtev
- ruta ga prepoznaje
- funkcija obradi zahtev
- return vraća odgovor
- FastAPI to šalje korisniku

---

## Napomena za tvoj kurs

Na početku ti nije potrebno da znaš sve detalje. Dovoljno je da razumeš:

- šta je ruta
- šta je funkcija
- šta je request
- šta je response
- šta su path i query parametri
- šta je JSON

To su osnovni “građevni blokovi”.

---
