# PATCH i delimično ažuriranje

Ovo je dodatni korak koji pokazuje kako da ažuriraš samo deo podatka, a ne ceo objekat.

---

## 1) Zašto treba `PATCH`?

`PUT` menja celu knjigu.

Na primer, ako želiš da promeniš samo `price`, ne moraš ponovo slati sve ostale polja.

`PATCH` služi upravo za to:

- menjaš samo deo podataka
- ostalo ostaje nepromenjeno

---

## 2) Primer `PATCH` endpointa

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    description: str | None = None
    price: float | None = None
    year: int | None = None
    genre: str | None = None
    available: bool | None = None
    rating: float | None = None


books = [
    {
        "id": 1,
        "title": "Python za početnike",
        "author": "Marko",
        "description": "Dobar uvod",
        "price": 19.99,
        "year": 2024,
        "genre": "programming",
        "available": True,
        "rating": 4.8,
    }
]


@app.patch("/books/{book_id}")
async def patch_book(book_id: int, book_update: BookUpdate):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            for field, value in book_update.model_dump().items():
                if value is not None:
                    books[index][field] = value
            return books[index]

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

---

## 3) Razlika između `PUT` i `PATCH`

### `PUT`

```python
@app.put("/books/{book_id}")
```

- potpuno menja zapis
- očekuješ da pošalješ sve potrebne podatke

### `PATCH`

```python
@app.patch("/books/{book_id}")
```

- menja samo ono što si poslao
- ostalo ostaje nepromenjeno

---

## 4) Primer zahteva

```json
{
  "price": 25.99
}
```

Ako knjiga ima:

```json
{
  "id": 1,
  "title": "Python za početnike",
  "author": "Marko",
  "price": 19.99
}
```

posle `PATCH` će biti:

```json
{
  "id": 1,
  "title": "Python za početnike",
  "author": "Marko",
  "price": 25.99
}
```

---

## 5) Zašto je ovo korisno?

U realnim aplikacijama često želiš da promeniš samo jedno polje:

- cenu
- status dostupnosti
- ocenu
- naslov

Ne moraš da šalješ sve ostale podatke ponovo.

---

## 6) Stop korak

Ovo je poslednji dodatni materijal koji je preporučljiv da se vidi pre baze.

Posle ovog, pređi na SQLAlchemy i bazu podataka.

Zbog toga ovaj deo je “optional but useful” dodatak, a ne obavezna osnovna tema.
