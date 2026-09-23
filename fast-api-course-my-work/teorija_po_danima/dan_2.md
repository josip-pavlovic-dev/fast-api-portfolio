# FastAPI - Query Parameters

## Dan 2 — Query Parameters u FastAPI

Query Parameters su sledeći važan korak posle Path Parameters. To su dodatni podaci koji dolaze u URL-u, ali ne menjaju samu putanju, već “filtriraju”, “opciono podešavaju” ili “prosleđuju dodatne informacije”.

---

## 1) Šta su Query Parameters?

Query Parameters su deo URL-a koji ide posle znaka `?`.

Primer:

```http
https://example.com/items?skip=0&limit=10
```

Ovo znači:

- `/items` je ruta
- `?skip=0&limit=10` su query parametri

U ovom slučaju:

- `skip=0`
- `limit=10`

To su dodatne informacije koje API može da koristi.

---

## 2) Kako se pišu?

Sintaksa je:

```http
/ruta?ime_parametra=vrednost
```

Ako ih ima više:

```http
/ruta?ime1=vrednost1&ime2=vrednost2&ime3=vrednost3
```

Primer:

```http
/users?role=admin
/users?active=true
/products?category=books&limit=5
```

---

## 3) Šta su Query Parameters u FastAPI?

U FastAPI-u ih definišeš kao argumente funkcije.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

Ako pozoveš:

```http
GET /items?skip=5&limit=20
```

dobijaš odgovor:

```json
{
  "skip": 5,
  "limit": 20
}
```

---

## 4) Objašnjenje ovog primera

U ovoj funkciji:

```python
def read_items(skip: int = 0, limit: int = 10):
```

- `skip` je query parametar
- `limit` je query parametar
- `= 0` i `= 10` su default vrednosti
- ako korisnik ne prosledi te parametre, funkcija koristi default vrednosti

Dakle, ovo znači:

```http
GET /items
```

je isto što i:

```http
GET /items?skip=0&limit=10
```

---

## 5) Zašto su korisni?

Query Parameters se koriste za:

- paginaciju
- filtriranje
- sortiranje
- pretragu
- opcione parametre

Primeri:

```http
/products?category=books
/products?category=books&limit=20
/users?role=admin
/users?active=true&sort=name
```

Ovo su stvari koje ne predstavljaju “konkretan resurs”, već dodatne opcije za traženi rezultat.

---

## 6) Path Parameters vs Query Parameters

Ovo je veoma važno da razumeš.

### Path Parameter
Koristi se kada želiš da pristupiš konkretnom objektu:

```http
/users/7
```

Ovo znači: “uzmi korisnika sa ID 7”.

### Query Parameter
Koristi se kada želiš da dodaš opcije ili filtere:

```http
/users?role=admin
```

Ovo znači: “uzmi korisnike, ali samo one sa rolom admin”.

---

## 7) Jasan primer poređenja

### Ruta sa path parametrom

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

Poziv:

```http
GET /users/10
```

### Ruta sa query parametrom

```python
@app.get("/users")
def get_users(role: str = None):
    return {"role": role}
```

Poziv:

```http
GET /users?role=admin
```

---

## 8) Query Parameters mogu biti opcioni

To je jedna od najvažnijih stvari.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

Ako korisnik pošalje:

```http
GET /items
```

dobija se:

```json
{"skip": 0, "limit": 10}
```

Ako pošalje:

```http
GET /items?limit=5
```

dobija se:

```json
{"skip": 0, "limit": 5}
```

---

## 9) Validacija tipova

FastAPI automatski validira query parametre, baš kao i path parametre.

Primer:

```python
@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

Ako korisnik pošalje:

```http
GET /items?skip=abc
```

FastAPI će vratiti grešku 422 jer `skip` mora biti integer.

To je vrlo korisno, jer ne moraš ručno da proveravaš tip.

---

## 10) Ruta sa Path i Query parametrima zajedno

Ovo je veoma čest slučaj.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/orders")
def get_orders(user_id: int, status: str = "all"):
    return {"user_id": user_id, "status": status}
```

Poziv:

```http
GET /users/5/orders?status=paid
```

Odgovor:

```json
{
  "user_id": 5,
  "status": "paid"
}
```

Ovde:

- `user_id` je path parameter
- `status` je query parameter

---

## 11) Najčešće greške za početnike

### Greška 1: zaboraviš znak `?`
Netačno:

```http
/usersrole=admin
```

Tačno:

```http
/users?role=admin
```

---

### Greška 2: koristiš query paramete kao path parametre
Netačno:

```python
@app.get("/users/{role}")
```

Ako `role` nije identifikator resursa, to nije dobro.

Bolje:

```python
@app.get("/users")
def get_users(role: str = None):
    ...
```

---

### Greška 3: zaboraviš da parametri u funkciji moraju imati ista imena
Netačno:

```python
@app.get("/items")
def read_items(skip_value: int = 0):
    ...
```

Ako URL je `/items?skip=10`, ovo neće raditi kao očekivano.

Tačno:

```python
@app.get("/items")
def read_items(skip: int = 0):
    ...
```

---

## 12) Mentalni model

Najjednostavnije:

- Path parameter = deo URL-a koji identificira objekat
- Query parameter = dodatne informacije o tom objektu ili listi objekata

Primer:

```http
/products/3?category=books
```

Ovo znači:

- `/products/3` → konkretan proizvod
- `?category=books` → dodatni filter

---

## 13) Primer sa više query parametara

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/products")
def list_products(category: str = "all", limit: int = 10):
    return {
        "category": category,
        "limit": limit
    }
```

Poziv:

```http
GET /products?category=books&limit=5
```

Odgovor:

```json
{
  "category": "books",
  "limit": 5
}
```

---

## 14) Zašto je to važno za API?

U praksi API često koristi query parametre za:

- paginaciju: `?skip=0&limit=10`
- pretragu: `?q=python`
- filtriranje: `?status=active`
- sortiranje: `?sort=price`

To je jedan od najčešće korišćenih načina za komunikaciju sa API-jem.

---

## 15) Šta treba da znaš do kraja ovog dana?

Za danas je dovoljno da razumeš:

- šta su query parameters
- kako se pišu u URL-u
- zašto su korisni
- kako se definišu u FastAPI
- kako se razlikuju od path parameters
- kako default vrednosti i validacija funkcionišu

---

## 16) Mini vežba za danas

Pokušaj da napišeš ovaj kod:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/books")
def get_books(category: str = "all", limit: int = 5):
    return {"category": category, "limit": limit}
```

Zatim zamisli request:

```http
GET /books?category=python&limit=3
```

Odgovor će biti:

```json
{
  "category": "python",
  "limit": 3
}
```

Ako to znaš da objasniš, znači da si savladao osnovu query parameters.

---

## 17) Kratka lista za pamćenje

- Query parametri idu posle `?`
- Više ih je podeljeno sa `&`
- Koriste se za filtere i opcije
- Ne predstavljaju konkretan resurs
- U FastAPI-u se definišu kao argumenti funkcije
- Mogu imati default vrednosti
- FastAPI ih validira automatski

---

## 18) Sledeći korak

Pošto smo prošli Path i Query, sledeće teme koje dolaze prirodno su:

- Request Body
- POST metoda
- Pydantic model
- Validacija podataka kroz modele

To je sledeći logičan korak, i tu već ulazimo u “pravi API” način rada, ne samo u jednostavne URL parametre.

---

Ako želiš, mogu odmah da nastavim sa sledećim tekstom:

1. Request Body i POST
2. Pydantic model
3. primer sa formiranjem celog API endpointa

i to ću napisati u istom nastavnom stilu, samo malo detaljnije od ovoga.
