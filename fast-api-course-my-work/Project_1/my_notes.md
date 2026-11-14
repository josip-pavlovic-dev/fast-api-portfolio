# Project 1 — beleške iz razgovora

Beleške za materijal koji se u razgovoru obrađivao uz `books1.py` i `books11.py`.
Po napomeni korisnika, sadržaj koji je u razgovoru nazvan `books11.py` odgovara
sadržaju koji je sada u [books.py](./books.py). U workspace-u se nalazi i
[books11.py](./books11.py).

## HTTP metode — kratki odgovori na engleskom

- **GET** — Retrieve data. *“I’d use GET to retrieve the book.”*
- **POST** — Create a resource. *“I’d use POST to create a book.”*
- **PUT** — Replace or update an existing resource. *“I’d use PUT to update the book.”*
- **DELETE** — Remove a resource. *“I’d use DELETE to remove the book.”*

Podsetnik: **GET = read, POST = create, PUT = update/replace, DELETE = remove.**

## GET: `None`, prazna lista i nedostajuća polja

Izbor zavisi od toga da li endpoint vraća jednu knjigu ili listu:

| Rezultat pretrage | Odgovor u vežbi bez HTTP grešaka |
|---|---|
| Jedna knjiga po naslovu nije pronađena | `None` |
| Nema knjiga za kategoriju/autora ili je `BOOKS` prazna | `[]` |

`None` i `[]` nisu zamenljivi: `None` znači da nema pojedinačnog rezultata,
dok je `[]` lista koja postoji, ali nema elemenata. Kada se koristi HTTP
status kod, nedostupna pojedinačna knjiga obično se prijavljuje kao **404**;
pretraga liste bez poklapanja i dalje normalno vraća **200** i `[]`.

Zaštita od nedostajućeg ključa u običnom rečniku:

```python
book_category = book.get("category")
if (
    book_category is not None
    and book_category.casefold() == category.casefold()
):
    lista_knjiga.append(book)
```

`.get()` vraća `None` ako ključ ne postoji, pa se izbegava `KeyError`.
Isti obrazac važi za `author` i `title`. Ova provera pokriva nedostajući ključ,
ali ne proverava sve moguće neispravne tipove vrednosti. Pydantic model može
kasnije da validira polja i tipove ulaznih podataka.

`if not BOOKS` pokriva praznu listu. Pošto je `BOOKS` definisana na nivou
modula, provera preko `globals()` nije potrebna: nedefinisana `BOOKS` bila bi
greška u programu koju ne treba prikrivati praznim rezultatom.

## Query parametar naspram path parametra

- **Query** je posle `?` i ima oblik `ime=vrednost`:
  `GET /books/author/?author=Author%20One`
- **Path** je deo putanje i mora imati `{ime}` u ruti:
  `@app.get("/books/author/{author}/")`, poziv:
  `/books/author/Author%20One/`

URL `...?Author%20One` nema parametar po imenu `author`, zato obavezni
`author: str` nedostaje i FastAPI vraća **422**. Razmak u vrednosti URL-a može
da se kodira kao `%20`.

Query parametar sam po sebi ne zahteva završnu kosu crtu. Putanja u zahtevu
treba da odgovara putanji iz dekoratora: za `@app.get("/books/")` koristi
`/books/?category=science`; za `@app.get("/books")` koristi
`/books?category=science`.

FastAPI bira rutu prema HTTP metodi i putanji, ne prema imenu query parametra.
Zato dve GET funkcije ne treba registrovati na istoj putanji očekujući da će
`?category=...` izabrati jednu, a `?author=...` drugu. Koristi različite
putanje ili jedan endpoint sa odgovarajućim parametrima.

## Šta Pydantic i FastAPI rešavaju?

- FastAPI proverava obavezne, tipizirane parametre. Ako nedostaje obavezan
  query parametar, podrazumevani odgovor je **422**.
- Pydantic model proverava oblik i ograničenja podataka koji se validiraju
  kroz taj model.
- Ni FastAPI ni Pydantic ne zaključuju da autor ili kategorija postoje u
  `BOOKS`. Pretraga liste bez poklapanja vraća `[]`; ako se traži jedna knjiga,
  kod mora da vrati `None` ili eksplicitno podigne `HTTPException(404)`.
- Ako običnom rečniku nedostaje ključ, `book["author"]` može podići
  `KeyError`; `.get("author")` je bezbedniji dok se radi sa sirovim rečnicima.

Postavljanje `status_code` na dekoratoru određuje uspešan status, ali samo po
sebi ne proverava da li knjiga postoji. PUT/DELETE kod mora da pronađe knjigu
i podigne `HTTPException` sa **404** ako je nema.

## POST i PUT

### POST — dodavanje

`POST /books` prima knjigu u JSON telu i dodaje je u listu. `append()` radi i
kada je `BOOKS` prazna, pa za taj slučaj nije potrebna posebna zaštita.

Anotacija `dict[str, str]` opisuje rečnik stringova, ali sama po sebi ne
zahteva da rečnik sadrži baš ključeve `title`, `author` i `category`. Pydantic
request model može kasnije da zahteva ta polja i validira njihove vrednosti.

### PUT — zamena postojeće knjige

Stariji oblik `PUT /books/update_book` tražio je knjigu poređenjem sa naslovom
iz JSON tela. Završna ruta koristi naslov iz putanje kao ključ:

```text
PUT /books/Title%20One
```

Telo sadrži **ceo novi zapis**, jer PUT u ovoj vežbi zamenjuje postojeću
knjigu:

```json
{
  "title": "Title One",
  "author": "Updated Author",
  "category": "science"
}
```

Putanja identifikuje knjigu pod njenim trenutnim/starim naslovom. Ako se menja
i naslov, URL i telo zato sadrže različite naslove: stari naslov ide u URL, a
novi u telo. Ako knjiga ne postoji, ruta podiže `HTTPException(404)`.

Naslov je privremeni identifikator i trebalo bi da bude jedinstven. Stabilnije
rešenje je ID u putanji, npr. `PUT /books/7`.

## `curl` za ručno isprobavanje API-ja

`curl` šalje HTTP zahteve iz terminala:

```bash
curl -X 'POST' \
  'http://localhost:8000/books' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{"title": "Title Seven", "author": "Author Seven", "category": "science"}'
```

- `curl` pokreće klijentski program.
- `-X POST` bira HTTP metodu.
- `\` nastavlja istu shell komandu u sledećem redu.
- `http://localhost:8000/books` je adresa servera: `localhost` je lokalni
  računar, `8000` port, a `/books` putanja.
- `-H 'accept: */*'` kaže da klijent prihvata bilo koji format odgovora.
- `-H 'Content-Type: application/json'` označava JSON format tela zahteva.
- `-d '...'` šalje JSON podatke.

Kod `curl`-a `-d` već podrazumeva POST, tako da je `-X POST` tehnički
suvišan, ali može da učini metodu očiglednom. Server mora biti pokrenut, a
njegova POST ruta mora prihvatati poslata polja.

## PUT/DELETE i status 404

U završnoj skripti PUT zamenjuje knjigu i vraća ažurirani zapis. DELETE uklanja
knjigu i vraća potvrdu. Obe rute vraćaju **404** ako naslov nije pronađen,
uključujući slučaj prazne liste. To se radi eksplicitno kroz
`HTTPException(status_code=404, ...)`; FastAPI ne zna sam da li naslov postoji
u tvojoj listi.

## `assert` testovi i pokretanje iz `.venv`

`assert` testovi proveravaju logiku funkcija direktno:

- GET: postojeće/nepostojeće knjige, pretrage bez obzira na velika/mala slova,
  nedostajuće ključeve i praznu listu;
- POST: dodavanje knjige i dodavanje kada je lista prazna;
- PUT: zamenu cele knjige, nepostojeći naslov i 404;
- DELETE: uspešno brisanje, nepostojeći naslov i 404.

Pošto su rute `async`, test funkcije ih pozivaju uz `await`, a pokreću se kroz
`asyncio.run(...)` samo kada se skripta izvršava direktno. `finally` vraća
`BOOKS` u početno stanje, a `if __name__ == "__main__"` sprečava pokretanje
testova kada Uvicorn uvozi aplikaciju.

Za proveru koristi projektni virtualenv:

```bash
./.venv/bin/python fast-api-course-my-work/Project_1/books.py
```

U prethodnoj proveri FastAPI **0.115.6** je već bio instaliran u `.venv`;
sistemski `/usr/bin/python` ga nije imao. Zato komande treba pokretati iz
`.venv`, a nije potrebno instalirati paket ako je već prisutan tamo.
