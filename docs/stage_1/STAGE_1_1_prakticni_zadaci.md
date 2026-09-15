# FastAPI Stage 1.1 - Prakticni Zadaci

Ovaj dokument sadrzi samo prakticne zadatke i expected output primere.

Pravilo rada:

- Svaki zadatak prvo radi u fajlu iz foldera tasks.
- Kada zavrsis, uporedi sa odgovarajucim fajlom iz foldera solutions.

Struktura fajlova:

- Tasks: docs/stage_1/stage_1_1/tasks
- Solutions: docs/stage_1/stage_1_1/solutions

---

## Zadatak 1 - Field validacija + create endpoint preko model_dump

Radni fajl:

- docs/stage_1/stage_1_1/tasks/task_01_field_and_create_book.py

Resenje:

- docs/stage_1/stage_1_1/solutions/solution_01_field_and_create_book.py

Sta treba uraditi:

1. U modelu BookRequest dodaj validacije sa Field:

- title min_length=3
- author min_length=2
- description min_length=5, max_length=200
- rating ge=1, le=5
- published_date ge=2000, le=2100

2. U create endpoint-u napravi novi Book preko model_dump.
3. Dodeli novi ID preko helper funkcije find_book_id.
4. Vrati kreiranu knjigu.

Expected output primeri:

Uspeh - POST /books
Request body:

```json
{
  "title": "FastAPI Patterns",
  "author": "Diana Evans",
  "description": "Practical patterns for real APIs",
  "rating": 5,
  "published_date": 2028
}
```

Response status: 201
Response body primer:

```json
{
  "id": 3,
  "title": "FastAPI Patterns",
  "author": "Diana Evans",
  "description": "Practical patterns for real APIs",
  "rating": 5,
  "published_date": 2028
}
```

Greska validacije - POST /books
Request body:

```json
{
  "title": "Fa",
  "author": "A",
  "description": "abc",
  "rating": 9,
  "published_date": 1800
}
```

Response status: 422
Response body: FastAPI validaciona greska za sva losa polja.

Mini Test Checklist (Swagger):

1. Pokreni fajl zadatka:

- `uvicorn docs.stage_1.stage_1_1.tasks.task_01_field_and_create_book:app --reload`

2. Otvori Swagger:

- `http://127.0.0.1:8000/docs`

3. Klikni endpoint `POST /books`.
4. Klikni `Try it out`.
5. Zalepi validan body i klikni `Execute`:

```json
{
  "title": "FastAPI Patterns",
  "author": "Diana Evans",
  "description": "Practical patterns for real APIs",
  "rating": 5,
  "published_date": 2028
}
```

6. Proveri da je status `201` i da response ima novi `id`.
7. Bez gasenja servera ponovo klikni `Try it out` i posalji nevalidan body:

```json
{
  "title": "Fa",
  "author": "A",
  "description": "abc",
  "rating": 9,
  "published_date": 1800
}
```

8. Proveri da je status `422` i da su prijavljene greske po poljima.

---

## Zadatak 2 - Path validacija + vracanje 404

Radni fajl:

- docs/stage_1/stage_1_1/tasks/task_02_path_and_get_by_id.py

Resenje:

- docs/stage_1/stage_1_1/solutions/solution_02_path_and_get_by_id.py

Sta treba uraditi:

1. Napravi GET /books/{book_id}.
2. book_id validiraj preko Path sa ge=1.
3. Ako knjiga ne postoji, vrati HTTPException 404.

Expected output primeri:

Uspeh - GET /books/1
Response status: 200
Response body primer:

```json
{
  "id": 1,
  "title": "Python Basics",
  "author": "Marko",
  "description": "Uvod u Python",
  "rating": 5,
  "published_date": 2024
}
```

Nepostojeci ID - GET /books/999
Response status: 404
Response body:

```json
{
  "detail": "Knjiga nije pronadjena"
}
```

Los ID - GET /books/0
Response status: 422
Response body: FastAPI validaciona greska jer je book_id manji od 1.

Mini Test Checklist (Swagger):

1. Pokreni fajl zadatka:

- `uvicorn docs.stage_1.stage_1_1.tasks.task_02_path_and_get_by_id:app --reload`

2. Otvori `http://127.0.0.1:8000/docs`.
3. Klikni `GET /books/{book_id}` pa `Try it out`.
4. Posalji `book_id = 1`, klikni `Execute`.
5. Proveri status `200` i telo sa knjigom `id=1`.
6. Posalji `book_id = 999`, klikni `Execute`.
7. Proveri status `404` i `detail: Knjiga nije pronadjena`.
8. Posalji `book_id = 0`, klikni `Execute`.
9. Proveri status `422` (Path validacija).

---

## Zadatak 3 - Search contains (case-insensitive)

Radni fajl:

- docs/stage_1/stage_1_1/tasks/task_03_search_contains_case_insensitive.py

Resenje:

- docs/stage_1/stage_1_1/solutions/solution_03_search_contains_case_insensitive.py

Sta treba uraditi:

1. Napravi GET /books/search.
2. Dodaj query parametre title i author (oba opcionalna).
3. Koristi strip i lower.
4. Filter treba da bude contains pretraga.

Expected output primeri:

GET /books/search?title=fastapi
Response status: 200
Response body: lista knjiga ciji title sadrzi rec fastapi bez obzira na velika/mala slova.

GET /books/search?author=ana
Response status: 200
Response body: lista knjiga ciji author sadrzi ana bez obzira na velika/mala slova.

GET /books/search?title=fastapi&author=jane
Response status: 200
Response body: samo knjige koje zadovoljavaju oba uslova.

Mini Test Checklist (Swagger):

1. Pokreni fajl zadatka:

- `uvicorn docs.stage_1.stage_1_1.tasks.task_03_search_contains_case_insensitive:app --reload`

2. Otvori `http://127.0.0.1:8000/docs`.
3. Klikni `GET /books/search` pa `Try it out`.
4. Test 1: unesi `title = fastapi`, ostavi `author` prazno, klikni `Execute`.
5. Proveri da vraca knjige ciji naslov sadrzi `fastapi` (bez obzira na slova).
6. Test 2: unesi `author = ANA`, ostavi `title` prazno, klikni `Execute`.
7. Proveri da vraca autora koji sadrzi `ana` (case-insensitive).
8. Test 3: unesi `title = fastapi` i `author = jane`, klikni `Execute`.
9. Proveri da su vracene samo knjige koje prolaze oba filtera.

---

## Zadatak 4 - Pattern i token pretraga

Radni fajl:

- docs/stage_1/stage_1_1/tasks/task_04_search_patterns_and_tokens.py

Resenje:

- docs/stage_1/stage_1_1/solutions/solution_04_search_patterns_and_tokens.py

Sta treba uraditi:

1. Napravi GET /books/search/pattern sa starts_with i ends_with.
2. Napravi GET /books/search/fulltext-lite sa query parametrom q.
3. fulltext-lite pravilo: sve reci iz q moraju postojati u title+author+description.

Expected output primeri:

GET /books/search/pattern?starts_with=Fast
Response status: 200
Response body: knjige ciji naslov pocinje sa fast (case-insensitive).

GET /books/search/pattern?ends_with=Guide
Response status: 200
Response body: knjige ciji naslov se zavrsava na guide.

GET /books/search/fulltext-lite?q=fastapi practical
Response status: 200
Response body: knjige gde i rec fastapi i rec practical postoje u kombinovanom tekstu.

Mini Test Checklist (Swagger):

1. Pokreni fajl zadatka:

- `uvicorn docs.stage_1.stage_1_1.tasks.task_04_search_patterns_and_tokens:app --reload`

2. Otvori `http://127.0.0.1:8000/docs`.
3. Klikni `GET /books/search/pattern` pa `Try it out`.
4. Test 1: unesi `starts_with = Fast`, klikni `Execute`.
5. Proveri da vraca naslove koji pocinju na `fast` (case-insensitive).
6. Test 2: unesi `ends_with = Guide`, klikni `Execute`.
7. Proveri da vraca naslove koji se zavrsavaju na `guide`.
8. Klikni `GET /books/search/fulltext-lite` pa `Try it out`.
9. Unesi `q = fastapi practical`, klikni `Execute`.
10. Proveri da svaka vracena knjiga sadrzi obe reci u zbiru polja title+author+description.

---

## Zadatak 5 - Kombinovani filteri + sortiranje + paginacija

Radni fajl:

- docs/stage_1/stage_1_1/tasks/task_05_advanced_filter_sort_paginate.py

Resenje:

- docs/stage_1/stage_1_1/solutions/solution_05_advanced_filter_sort_paginate.py

Sta treba uraditi:

1. Napravi GET /books/advanced.
2. Dodaj opcione filtere:

- min_rating
- max_rating
- published_from
- published_to

3. Dodaj sortiranje:

- sort_by: id, title, rating, published_date
- sort_order: asc ili desc

4. Dodaj paginaciju:

- skip >= 0
- limit izmedju 1 i 100

5. Vrati objekat sa total, skip, limit i items.

Expected output primeri:

GET /books/advanced?min_rating=4&published_from=2024&sort_by=rating&sort_order=desc&skip=0&limit=2
Response status: 200
Response body primer:

```json
{
  "total": 4,
  "skip": 0,
  "limit": 2,
  "items": [
    {
      "id": 1,
      "title": "FastAPI in Action",
      "author": "Bob",
      "description": "Practical API building",
      "rating": 5,
      "published_date": 2026
    },
    {
      "id": 3,
      "title": "Mastering FastAPI",
      "author": "Alice",
      "description": "Advanced techniques",
      "rating": 5,
      "published_date": 2025
    }
  ]
}
```

Los sort_by - GET /books/advanced?sort_by=price
Response status: 422
Response body: validaciona greska za sort_by.

Mini Test Checklist (Swagger):

1. Pokreni fajl zadatka:

- `uvicorn docs.stage_1.stage_1_1.tasks.task_05_advanced_filter_sort_paginate:app --reload`

2. Otvori `http://127.0.0.1:8000/docs`.
3. Klikni `GET /books/advanced` pa `Try it out`.
4. Test 1 (kombinovano):

- `min_rating = 4`
- `published_from = 2024`
- `sort_by = rating`
- `sort_order = desc`
- `skip = 0`
- `limit = 2`

5. Klikni `Execute` i proveri da response ima kljuceve `total`, `skip`, `limit`, `items`.
6. Proveri da je broj elemenata u `items` najvise `limit`.
7. Test 2 (validaciona greska): postavi `sort_by = price`, klikni `Execute`.
8. Proveri status `422`.
9. Test 3 (paginacija): stavi `skip = 1`, `limit = 1` i proveri da se vraca tacno jedan element na drugoj poziciji rezultata.

---

## Predlog redosleda rada

1. Zadatak 1
2. Zadatak 2
3. Zadatak 3
4. Zadatak 4
5. Zadatak 5

Ako uradis ovim redom, svaki sledeci zadatak direktno koristi ideje iz prethodnog.
