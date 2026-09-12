# Path Parameters u FastAPI

## Path Parameters u FastAPI – jednostavno i bez zbrke

Najpre da razjasnimo šta je URL. URL (Uniform Resource Locator) je adresa koja identifikuje resurs na internetu. Na primer:

```
https://example.com/users/1
```

Path Parameters su delovi URL-a koji predstavljaju promenjive vrednosti u ruti. Ruta predstavlja putanju do resursa. Resurs je konkretan objekat ili podatak koji želiš da dobiješ ili manipulišeš. Path Parameters omogućavaju da deo te putanje bude promenljiv.

Postoje dve vrste Path Parameters: statički i dinamički. Staticki parametri su fiksni delovi rute, dok su dinamički promenjivi i označeni sa `{}`.

Primer statičkog parametra je `/users`, dok je primer dinamičkog parametra `/users/{user_id}`. Ovo znači da je deo rute unutar `{}` promenljiv i može se menjati za različite zahteve.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
# NAPOMENA: Path parameter mora imati isto ime u ruti i funkciji.
# U suprotnom, FastAPI neće moći da poveže vrednost iz URL-a sa argumentom funkcije.
# Funkcija predstavlja handler za tu rutu i prima path parameter kao argument.
```

Ako pozoveš:

```http
GET /items/5
```

dobijaš:

```json
{ "item_id": 5 }
```

To znači da je `5` vrednost koju prosleđuješ kroz URL, a `item_id` je promenljiva u ruti.

---

## Šta je to u praksi?

Path parameter je deo URL-a koji se menja:

- `/users/1`
- `/users/2`
- `/users/42`

Ovde je `1`, `2`, `42` vrednost parametra.

U FastAPI to definišeš tako što u ruti napišeš:

```python
@app.get("/users/{user_id}")
```

a u funkciji prihvatiš isto ime:

```python
def get_user(user_id: int):
    ...
```

---

## Kako se razlikuje od Query Parameters?

To je važno da znaš.

### Path Parameters

Koriste se za identifikaciju resursa:

```http
GET /users/7
```

Ovo znači: “daj mi korisnika sa ID = 7”.

### Query Parameters

Koriste se za filtriranje, paginaciju, pretragu:

```http
GET /users?role=admin&active=true
```

Ovdje `role` i `active` nisu deo putanje, nego se nalaze posle `?`.

---

## Zašto su korisni?

Path parameters su najbolji kada:

- želiš da pristupiš konkretnom objektu
- dinamički zadaš ID, username, slug, itd.
- ruta treba da ima promenljivo “ime” resursa

Primeri:

```python
@app.get("/products/{product_id}")
@app.get("/posts/{post_slug}")
@app.get("/orders/{order_id}")
```

---

## FastAPI i validacija tipova

Ovo je jedna od najkorisnijih stvari u FastAPI.

Ako napišeš:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

onda `item_id` mora biti broj.

Ako pozoveš:

```http
GET /items/abc
```

FastAPI će vratiti grešku 422, jer je očekivan `int`, a dobio je string.

To je jako korisno jer:

- preuzimaš validaciju “automatski”
- ne moraš ručno pisati mnogo proveravanja
- API je sigurniji i bolji za korisnika

---

## Više parametara u jednoj ruti

Možeš imati i više path parametara:

```python
@app.get("/users/{user_id}/orders/{order_id}")
def read_order(user_id: int, order_id: int):
    return {
        "user_id": user_id,
        "order_id": order_id
    }
```

Poziv:

```http
GET /users/10/orders/25
```

Odgovor:

```json
{
  "user_id": 10,
  "order_id": 25
}
```

---

## Bitno pravilo: ime mora da se poklopi

Ruta i parametar moraju imati isto ime:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    ...
```

Ne možeš da napišeš:

```python
@app.get("/items/{item_id}")
def read_item(id: int):
    ...
```

Ako ne poklapaju, FastAPI neće povezati vrednost.

---

## Jednostavan mentalni model

Zamislite to ovako:

- Ruta je šablon
- Path parameter je mesto koje se popunjava
- Funkcija prima tu vrednost kao argument

Primer:

```python
"/items/{item_id}"
```

znači:

- URL može biti `/items/1`
- URL može biti `/items/5`
- URL može biti `/items/999`

Sve to ide u `item_id`.

---

## Dobar primer sa više slučajeva

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"message": f"Item ID je {item_id}"}

@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: int):
    return {"message": f"Profil korisnika {user_id}"}
```

Pozivi:

```http
GET /items/10
GET /users/3/profile
```

---

## Najvažnije stvari koje treba da zapamtiš

- Path parameter je deo URL-a
- Koristi se za “konkretan resurs”
- Piše se u zagradama u ruti: `{id}`
- U funkciji moraš imati parametar sa istim imenom
- Najčešće se tipizuje: `int`, `str`, `float`, itd.
- FastAPI automatski validira tip
- Ako vrednost ne valja, dobijaš 422 grešku

---

## Kratka tabela

- `/users/5` → path parameter: `5`
- `/products/10` → path parameter: `10`
- `/search?q=python` → query param: `q=python`
- `/items/{item_id}` → ruta sa dinamičkim segmentom

---

## Savet za početak

Uvek razmišljaj ovako:

> “Da li je ovo konkretan objekat koji želim da dohvatim?”
> Ako da, to je path parameter.

Ako je:

> “Da li je ovo dodatni filter ili opcija?”
> to je query parameter.

---

Ako želiš, mogu odmah da ti napravim i:

1. mini primer sa više ruta,
2. objašnjenje Query Parameters odmah nakon toga,
3. ili kratku “karta pojmova” za FastAPI na početku kursa.
