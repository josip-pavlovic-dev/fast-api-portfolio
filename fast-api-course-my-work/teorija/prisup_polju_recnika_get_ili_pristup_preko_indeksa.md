# Pristup polju rečnika u Pythonu: direktno vs get()

Za tvoje trenutne podatke ovo je najčistija varijanta:

```python
if book["author"].casefold() == book_author.casefold():
```

Programeri često koriste direktni pristup kada je polje obavezno i garantovano postoji. Ali nije tačno da ne postoji nikakva mogućnost greške:

- ako nedostaje `"author"` → `KeyError`
- ako je vrednost `None` → `AttributeError`
- ako vrednost nije string → `AttributeError`

Pošto svi tvoji rečnici imaju ispravno tekstualno polje `author`, možeš bezbedno koristiti ovu verziju. Ona je čak korisna jer odmah otkrije neispravan podatak, umesto da ga tiho preskoči.

`get()` koristiš kada je polje opciono:

```python
if (book.get("author") or "").casefold() == book_author.casefold():
```

Za veće aplikacije najbolje rešenje su tipizovani Pydantic modeli, gde je `author: str` obavezno polje.

---

## `Project_1/books.py`

Ovde nema Pydantic modela, pa Python ne zna formalno koja su polja obavezna. Ipak, prema strukturi tvojih rečnika, svaki `book` ima:

- `title`
- `author`
- `category`

Ta polja su praktično obavezna.

Zato je najčistiji pristup:

```python
book["title"]
book["author"]
book["category"]
```

Primer:

```python
if book["author"].casefold() == author.casefold():
    ...
```

Ako bi neki rečnik bio bez `"author"`, dobićeš `KeyError`. To je korisno jer odmah otkriva neispravan podatak.

Ako je polje zaista opciono, koristi:

```python
(book.get("description") or "").casefold()
```

Za postojeći `books.py` preporuka:

```python
if book["title"].casefold() == book_title.casefold():
```

```python
if book["category"].casefold() == category.casefold():
```

```python
if book["author"].casefold() == author.casefold():
```

Pošto su sva tri polja prisutna u svim tvojim rečnicima, nema potrebe za `.get()`.

---

## `Project_2/books2.py`

Kod `BookRequest` modela sva polja su obavezna osim `id`:

```python
class BookRequest(BaseModel):
    id: int | None = Field(
        description="ID is not needed on create",
        default=None,
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)
```

### `id`

Opciono je:

```python
id: int | None = None
```

Prilikom kreiranja knjige klijent ne šalje `id`. Funkcija `find_book_id()` ga naknadno dodeljuje.

---

### `title`

Obavezno tekstualno polje, najmanje 3 karaktera:

```python
title: str = Field(min_length=3)
```
---

### `author`

Obavezno tekstualno polje, najmanje 1 karakter:

```python
author: str = Field(min_length=1)
```
---

### `description`

Kod tebe trenutno nije opciono. Obavezno je, ali mora imati između 1 i 100 karaktera:

```python
description: str = Field(min_length=1, max_length=100)
```

Da bi bilo opciono, napisao bi:

```python
description: str | None = Field(default=None, max_length=100)
```

Ako želiš da opciono polje bude prazan string umesto `None`:

```python
description: str = Field(default="", max_length=100)
```

---

### `rating`

Obavezno celobrojno polje između 1 i 5:

```python
rating: int = Field(gt=0, lt=6)
```
---

### `published_date`

Obavezno celobrojno polje između 2000 i 2030:

```python
published_date: int = Field(gt=1999, lt=2031)
```

## Sažetak

| Polje            | `Project_1`           | `BookRequest`                 |
| ---------------- | --------------------- | ----------------------------- |
| `id`             | nema formalno pravilo | opciono                       |
| `title`          | praktično obavezno    | obavezno, minimum 3 karaktera |
| `author`         | praktično obavezno    | obavezno, minimum 1 karakter  |
| `category`       | praktično obavezno    | ne postoji                    |
| `description`    | ne postoji            | obavezno, 1-100 karaktera     |
| `rating`         | ne postoji            | obavezno, 1-5                 |
| `published_date` | ne postoji            | obavezno, 2000-2030           |

Važna razlika:

- `dict.get("author")` znači: možda postoji, možda ne
- `book["author"]` znači: očekujem da mora postojati
- Pydantic `author: str` znači: FastAPI će odbiti zahtev ako autor nedostaje ili nije validan string

Za tvoj `Project_1` koristi direktan pristup `book["..."]`, jer je struktura podataka poznata i sva polja postoje.

---
