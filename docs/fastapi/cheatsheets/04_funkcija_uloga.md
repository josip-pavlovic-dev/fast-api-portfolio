# Uloga funkcije u FastAPI

U FastAPI funkcija koja stoji ispod dekoratora je najvažniji deo endpointa. To je “handler” funkcija, odnosno funkcija koja se poziva kada korisnik dođe na određeni URL.

Na primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Ovo znači:

- `@app.get("/items/{item_id}")` govori FastAPI: “Kad neko ode na `/items/5`, pozovi ovu funkciju”
- `read_item` je funkcija koja prima `item_id`
- FastAPI automatski ubacuje vrednost iz URL-a u `item_id`
- funkcija vraća rezultat, a FastAPI taj rezultat pretvara u HTTP response

---

## Uloga funkcije u FastAPI

Funkcija ne služi samo da vrati response. Ona obavlja:

- prima podatke iz URL-a, body-a, query parametara
- validira ulaz
- obrađuje logiku
- poziva bazu podataka ili neku drugu logiku
- vraća rezultat u obliku JSON-a

Dakle, ona predstavlja “srce” endpointa.

---

## Šta se tačno dešava?

Kada korisnik pozove:

```http
GET /items/5
```

FastAPI radi ovo:

1. Pogleda rutu `/items/{item_id}`
2. U vidi da je `item_id = 5`
3. Pozove funkciju:

```python
read_item(item_id=5)
```

4. Funkcija radi posao
5. Vraća `{"item_id": 5}`
6. FastAPI to pretvori u HTTP odgovor

---

## Zašto je funkcija bitna?

Jer bez nje nema endpointa. Decorator samo kaže “ovde je ruta”, a funkcija kaže:

- šta ta ruta treba da radi
- koje podatke prima
- šta vraća

To je kao:

- `dekorator` = “koja adresa postoji”
- `funkcija` = “šta se dešava kada se ta adresa otvori”

---

## Jednostavan primer sa logikom

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id == 1:
        return {"name": "Ana", "role": "admin"}
    elif user_id == 2:
        return {"name": "Marko", "role": "user"}
    else:
        return {"message": "User not found"}
```

Ovde `funkcija`:

- prima `user_id`
- proverava uslov
- vraća odgovarajući JSON

---

## Važno: return nije samo “odgovor”

Return je rezultat koji se šalje klijentu, ali funkcija može da radi mnogo više od toga. Na primer:

- proverava da li je korisnik prijavljen
- čita podatke iz baze
- filtrira podatke
- formatira podatke
- baca grešku ako nešto nije u redu

---

## Jedna mala analogija

Zamislite restoran:

- ruta = “sto sa brojem 5”
- funkcija = “kuvar koji priprema jelo za taj sto”
- return = “jelo koje se servira gostu”

Dekorator ne kuha hranu — samo kaže koje “sto” postoji. Funkcija je ono što pravi rezultat.

---

## Najbitnije da zapamtiš

- Funkcija u FastAPI je endpoint handler
- prima podatke iz request-a
- sadrži logiku
- vraća response
- bez nje nema API funkcionalnosti

---
