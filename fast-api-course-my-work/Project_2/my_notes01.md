# Project 2 — beleške iz razgovora za 14.11.2026

## URL, path i query string

`HTTP zahtev` se sastoji od `metode`, `ciljne putanje/URL`-a, `zaglavlja (headers)` i, kada je potrebno, `tela (body)`. **Query string je deo URL-a**, pa ga u spisku delova zahteva treba prikazati kao deo URL-a, a ne kao nepovezanu stavku istog nivoa.

Primer:

```text
GET /books?author=Ana&page=2
```

- HTTP metoda: `GET`
- URL: `/books?author=Ana&page=2` — ceo URL koji uključuje path i query string
- path: `/books` — deo URL putanje koji se odnosi na resurs, bez query string-a
- query string: `author=Ana&page=2` — ceo deo posle `?` u URL-u
- query parametri: `author=Ana` i `page=2` — pojedinačne vrednosti u tom delu query string-a

Više query parametara obično se odvaja znakom `&`. Prvo ide `?`, a ne stavlja se novi `?` ispred svakog parametra.

---

## FastAPI `Query()` nije query string

`Query()` je FastAPI pomoćna funkcija koja se koristi u Python potpisu rute da bi se query parametar opisao, validirao i dokumentovao. Vrednost i dalje stiže kroz URL query string.

```python
@app.get("/books/")
async def read_books_by_rating(
    book_rating: int = Query(gt=0, le=5),
):
    ...
```

Poziv toj ruti može izgledati ovako:

```text
GET /books/?book_rating=5
```

U ovom primeru `book_rating` je query parametar. `Query(gt=0, le=5)` nalaže FastAPI-ju da validira celobrojnu vrednost veću od 0 i najviše 5. Pošto je tip `int`, prihvaćene celobrojne vrednosti su od 1 do 5. `Query()` ne pojavljuje se u URL-u — to je deo Python koda.

---

## Paginacija

**Paginacija** deli veliki skup rezultata na manje stranice, umesto da API vrati sve odjednom. Na primer:

```text
GET /books?page=2&page_size=10
```

`page=2` traži drugu stranicu, a `page_size=10` traži 10 rezultata po stranici.

Ako stranice počinju od 1, to bi tipično značilo knjige 11–20. Parametri `page` i `page_size` su query parametri.

---

## Statičke i dinamičke path putanje

- Statička ruta ima fiksnu putanju, npr. `@app.get("/books")`. (statički deo path string putanje)

- Dinamička ruta sadrži promenljivi deo u vitičastim zagradama, npr. `@app.get("/books/{book_id}")`. Zahtev za knjigu sa ID-jem 42 ide na `/books/42`. (dinamički deo path string putanje, koji se zadaje kroz `{book_id}`)

- Putanja može da kombinuje statičke i dinamičke delove, npr. `@app.get("/authors/{author_id}/books")`.

Vrednost iz `{book_id}` stiže kao **path parametar**. FastAPI `Path()` može da joj zada validaciju i dokumentaciju, na primer `book_id: int = Path(gt=0)`.

Analogno tome, `Query()` se koristi za query parametre takođe na nivou Python funkcije rute, dok se vrednosti i dalje prenose kroz URL query string. Primer:

```python
from fastapi import Query

@app.get("/books/")
async def read_books(page: int = Query(gt=0), page_size: int = Query(gt=0, le=100)):
    return {"page": page, "page_size": page_size}
```

Ovaj primer pokazuje kako se query parametri `page` i `page_size` definišu i validiraju koristeći `Query()`. Vrednosti se i dalje prenose kroz URL query string, npr. `/books/?page=2&page_size=10`. Ovo omogućava API-ju da automatski proveri validnost unetih vrednosti i generiše odgovarajuću dokumentaciju u Swagger UI-ju.

---

## Form podaci i gde se unose

Primer:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=ana&password=123
```

`username=ana&password=123` je telo zahteva u `application/x-www-form-urlencoded` formatu. To nije query string, iako zapis
liči na `ime=vrednost&ime=vrednost`:

- `query` vrednosti su u `URL`-u, npr. `/login?username=ana&password=123` i šalju se kao deo query string-a, dok su `form` vrednosti u `telu POST zahteva` i ne pojavljuju se u URL-u.

FastAPI ruta za form podatke koristi `Form()`:

```python
from fastapi import Form

@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}
```

Vrednosti se mogu uneti u Swagger UI-ju na `/docs`, u form polja koja ruta prikaže, ili poslati `curl`-om. Ne unose se u Markdown fajl. Unošenje u adresnu traku browsera poslalo bi ih kao query parametre, a ne kao form body.

---

## Šta je `curl` i odakle se pokreće?

`curl` je program za slanje HTTP zahteva iz **terminala**. U VS Code-u se može otvoriti kroz **Terminal → New Terminal**.

1. Pokreni FastAPI server u jednom terminalu, koristeći `.venv`.
2. Pošalji `curl` zahtev iz drugog terminala.

Za Project 1 `books.py`, iz korena repozitorijuma možeš pokrenuti server projektnim virtualenv interpreterom:

```bash
./.venv/bin/python -m uvicorn books:app \
  --app-dir fast-api-course-my-work/Project_1 --reload
```

`curl` zahtev nije vezan za određeni folder — možeš ga pokrenuti iz bilo kog direktorijuma jer cilj određuje URL. Folder je bitan ako komanda čita lokalni fajl, npr. `-d @payload.json`; tada se putanja do fajla tumači u odnosu na trenutni direktorijum terminala.

Primer slanja form podataka:

```bash
curl -X POST 'http://localhost:8000/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ana&password=123'
```

---

## Ulančano poređenje i provera ocene

Izraz:

```python
1 <= book_rating <= 5
```

Predstavlja **ulančano poređenje** (_chained comparison_). Znači da je rejting najmanje 1 i najviše 5; logički je ekvivalentan sa standardnim `and` operatorom:

```python
book_rating >= 1 and book_rating <= 5
```

Ovo je čitljiv i koncizan način da se izrazi opseg vrednosti, a Python omogućava i lančano poređenje sa više od dve granice, npr. `1 <= x <= 5 <= y <= 10`. Takva poređenja se evaluiraju kao logički `and` između svih pojedinačnih uslova.

Negacija:

```python
if not 1 <= book_rating <= 5:
```

Proverava da je vrednost izvan opsega. Isto se može napisati:

```python
if book_rating < 1 or book_rating > 5:
```

Granica mora biti `< 1`, ne `< 0`, jer je rejting `0` takođe nevažeći.

U `books2.py` se `Query(gt=0, le=5)` već koristi za validaciju HTTP zahteva. FastAPI odbacuje vrednost izvan tog opsega sa **422** pre ulaska u endpoint funkciju, pa je ručna provera unutar nje redundantna za zahteve kroz API. Jasnoća opsega može se poboljšati zapisom `Query(ge=1, le=5)`. Ručna provera može biti korisna ako istu logiku pozivaš direktno iz Python koda, mimo FastAPI validacije.

---

## DELETE: status kod i JSON odgovor

`204 No Content` znači da je DELETE uspešan i da odgovor **nema telo**. Zato Swagger ne prikazuje JSON za uspešan DELETE sa statusom 204. U proveri rute iz `books2.py`, odgovor je imao status `204`, a telo je bilo prazno (`b''`), iako je funkcija vraćala rečnik.

U praksi su oba uspešna odgovora uobičajena:

- **204 No Content** — nema dodatnog tela; često odgovara jednostavnom DELETE-u.
- **200 OK** — koristi se ako želiš da vratiš JSON, npr. potvrdu ili ID obrisane knjige.
- **202 Accepted** — zahtev je prihvaćen, ali brisanje će se završiti kasnije, npr. asinhrono.

Ako koristiš 204, funkcija može završiti bez vrednosti. Python tada vraća `None`, ali FastAPI zbog 204 ne šalje JSON `null` — šalje prazan body. Ne moraš pisati `return None`.

### `return`, `break` i flag za DELETE

`return` bez vrednosti odmah završava celu funkciju. U DELETE ruti je to jednostavan način da, nakon pronalaska i brisanja knjige, izađeš bez tela:

```python
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def ukloni_knjigu_iz_liste(book_id: int) -> None:
    for index, book in enumerate(BOOKS):
        if book.id == book_id:
            BOOKS.pop(index)
            return

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")
```

Ako samo izbrišeš `return` posle `BOOKS.pop(index)`, funkcija će nastaviti da izvršava kod posle brisanja. `break` prekida samo petlju, ne i funkciju; ako koristiš `break`, moraš odvojeno urediti tok posle petlje, na primer `for/else`. Za ovaj primer je direktan `return` najjednostavniji.

U prikazanom obrascu flag `book_deleted` nije potreban: uspeh odmah završava funkciju, a ako se petlja završi bez pronalaska knjige, izvršava se 404. Ako ne koristiš obrisani objekat, promenljiva `deleted_book` takođe može da se izostavi.

---

## Prazna kolekcija naspram nedefinisane `BOOKS`

`GET /books` vraća kolekciju, pa prazna lista nije greška: očekivan odgovor je `200 OK` sa `[]`. `404 Not Found` je namenjen slučaju kada se traži konkretna knjiga, npr. `GET /books/{book_id}`, ali taj ID ne postoji.

Ako promenljiva `BOOKS` uopšte nije definisana, to je greška u programu (`NameError`), a ne prazan skup knjiga niti 404. Pošto je `BOOKS` definisana na nivou modula, nije potrebno proveravati `globals()` niti pretvarati takvu grešku u uspešan prazan odgovor.

`200 OK` je podrazumevani status za GET, tako da je `status_code=200` u dekoratoru opcionalan. Može se ostaviti radi jasnoće ili vežbe.

---

## Statusi, `Path` i `Query` u `books2.py`

Provereni tokovi u skripti:

| Ruta/situacija                                            | Očekivan status i odgovor      |
| --------------------------------------------------------- | ------------------------------ |
| `GET /books`                                              | `200`; lista knjiga ili `[]`   |
| `GET /books/{book_id}` sa ID-jem `<= 0`                   | `422` zbog `Path(gt=0)`        |
| `GET /books/{book_id}` sa pozitivnim, nepostojećim ID-jem | `404` iz koda rute             |
| `GET /books/?book_rating=1` do `5`                        | `200`; poklapanja ili `[]`     |
| `GET /books/?book_rating=0` ili `6`                       | `422` zbog `Query(ge=1, le=5)` |
| POST za kreiranje knjige                                  | `201 Created`                  |
| PUT uspešno izmeni postojeću knjigu i vrati JSON          | `200 OK`                       |
| PUT bez ID-ja u telu                                      | `400` zbog ručne provere       |
| PUT sa ID-jem koji nije u `BOOKS`                         | `404` iz koda rute             |
| DELETE sa nevažećim ID-jem `<= 0`                         | `422` zbog `Path(gt=0)`        |
| DELETE sa pozitivnim, nepostojećim ID-jem                 | `404` iz koda rute             |
| DELETE uspešno ukloni knjigu                              | `204 No Content`, bez tela     |

`Query(gt=0, lt=6)` je takođe važio za celobrojni opseg 1–5. Zapis `Query(ge=1, le=5)` je izabran jer direktnije izražava uključive granice.
Isto tako, `Path(gt=0)` automatski odbija nulu i negativne ID-jeve pre izvršavanja funkcije.

---

## Kada FastAPI validira, a kada treba ručna provera?

- FastAPI/Pydantic proverava ulazna polja i ograničenja deklarisana u anotacijama i modelima. Neispravan tip ili vrednost van granice, npr. rejting `0`, dobija `422` pre nego što se izvrši telo endpointa.
- `status_code` u dekoratoru određuje status uspešnog odgovora. Sam po sebi ne proverava da li knjiga postoji.
- Pydantic ne zna šta se nalazi u globalnoj listi `BOOKS`. Endpoint mora da potraži zapis i podigne `HTTPException(404, ...)` ako knjige nema.
- FastAPI pretvara eksplicitno podignut `HTTPException` u HTTP odgovor sa navedenim statusom i detaljem. Ne pretvara svaku Python grešku u prikladan HTTP status automatski; neočekivana programska greška obično postaje `500`.

### Zašto PUT ručno proverava ID?

U [books2.py](./books2.py), `BookRequest.id` je `int | None` sa podrazumevanom vrednošću `None`, jer POST može da primi knjigu bez ID-ja. Kada je isti model upotrebljen u PUT ruti, nedostajući ID je po modelu dozvoljen, pa Pydantic ga automatski ne odbacuje. Ruta proverava da li je ID prisutan sa `if update_book.id is None` i vraća `400`.

Provera `hasattr(update_book, "id")` je suvišna: `BookRequest` uvek ima to polje. Dovoljno je:

```python
if update_book.id is None:
    raise HTTPException(
        status_code=400,
        detail="ID knjige je obavezan za ažuriranje.",
    )
```

Ako želiš automatski `422` za PUT bez ID-ja, napravi poseban model za izmenu sa obaveznim poljem `id: int`. Tada će Pydantic odbiti nedostajući ID pre poziva funkcije. Nezavisno od toga, ID koji postoji u zahtevu, ali ne odgovara nijednoj knjizi, i dalje treba da dobije `404`.

---

## Opcionalni filter po godini izdavanja

Ruta za godinu je definisana kao opcionalni query parametar:

```python
published_date: int | None = Query(
    default=None,
    gt=1999,
    lt=2100,
)
```

Anotacija `int | None` odgovara podrazumevanoj vrednosti `None`. Ako parametar nije poslat, funkcija vraća sve knjige — filter se ne primenjuje. Ako je poslat, prihvata godine **2000–2099** i vraća knjige koje imaju tačnu godinu;
Ako nema poklapanja, vraća `[]`. Godina `1999` ili `2100` odbacuje se sa
`422 Unprocessable Entity`.

Bez posebne provere `published_date is None`, lista-komprehencija bi tražila
knjige čija je godina baš `None`, umesto da vrati sve knjige.

---

## Šta radi skripta

`books2.py` je mala FastAPI biblioteka knjiga sa podacima u memoriji:

- `BOOKS` je Python lista instanci obične klase `Book`; podaci nisu sačuvani u bazi i vraćaju se na početno stanje kada se aplikacija ponovo pokrene.
- `BookRequest` je Pydantic model za validaciju tela POST i PUT zahteva:
  - Naslov ima najmanje 3 znaka
  - Autor najmanje 1
  - Opis 1–100 znakova
  - Rejting je 1–5
  - Godina izdavanja je opcionalna i, ako je navedena, mora biti između 2000–2099.
    Dodatna polja nisu dozvoljena.
- `automatski_id()` postavlja ID na 1 ako je lista prazna, inače na ID
  poslednje knjige plus 1. Ovo je pojednostavljeno rešenje za listu u memoriji;
  u aplikaciji sa bazom ID se obično dodeljuje u bazi.
- Kreiranje i izmena vraćaju JSON odgovore; uspešan DELETE nema telo zbog 204.

### Endpointi

| Metoda i putanja                              | Namena                                                           |
| --------------------------------------------- | ---------------------------------------------------------------- |
| `GET /`                                       | Vraća osnovni opis API-ja.                                       |
| `GET /books`                                  | Vraća sve knjige; prazna kolekcija je `[]`.                      |
| `GET /books/{book_id}`                        | Vraća jednu knjigu po ID-ju.                                     |
| `GET /books/?book_rating=5`                   | Filtrira knjige po rejtingu 1–5; bez parametra vraća sve knjige. |
| `GET /books/bypublished/?published_date=2022` | Opcionalno filtrira po godini; bez parametra vraća sve knjige.   |
| `POST /create-book`                           | Validira i kreira knjigu, automatski joj dodeljuje ID.           |
| `PUT /books/update_book`                      | Ažurira postojeću knjigu po ID-ju; šalje se ceo zahtevni model.  |
| `DELETE /books/{book_id}`                     | Briše knjigu po ID-ju.                                           |

---

### Status kodovi

| Status                     | Kada se koristi                                                                               |
| -------------------------- | --------------------------------------------------------------------------------------------- |
| `200 OK`                   | GET uspeh, uključujući prazne rezultate; PUT uspešno ažuriranje.                              |
| `201 Created`              | POST uspešno kreira knjigu.                                                                   |
| `204 No Content`           | DELETE uspeh; odgovor nema JSON telo.                                                         |
| `400 Bad Request`          | PUT telo nema ID (`BookRequest.id` je opcionalan za POST, pa PUT to proverava ručno).         |
| `404 Not Found`            | Traženi ID ne postoji u listi.                                                                |
| `422 Unprocessable Entity` | FastAPI/Pydantic odbija neispravan tip, vrednost van `Path`/`Query` opsega ili nevažeće telo. |

`Path(gt=0)` dozvoljava samo pozitivne ID-jeve; `Query(ge=1, le=5)` dozvoljava rejtinge 1–5. `Query(gt=1999, lt=2100)` dozvoljava godine 2000–2099. Nevažeći ulazi dobijaju 422 pre ulaska u endpoint. Kod i dalje mora eksplicitno
proveriti postojanje zapisa i podići 404 kada vrednost jeste validna, ali zapis ne postoji.

`status_code` u dekoratoru određuje uspešan status, a ne proverava uspeh poslovne operacije. Na primer, PUT dekorator postavlja 200; telo funkcije proverava ID i podiže 400 ili 404 kada je potrebno.

---

## Inline `assert` testovi u skripti

Dodati su testovi koji koriste FastAPI `TestClient`, pa proveravaju stvarne HTTP zahteve, ne samo direktne pozive Python funkcija. Pokrivaju:

- GET odgovore i praznu kolekciju;
- postojeći ID, nepostojeći ID i nevažeći Path parametar;
- validne, nevažeće i izostavljene Query parametre za rejting i godinu;
- POST uspeh, automatsku dodelu ID-ja i nevažeći Pydantic ulaz;
- PUT uspeh, nedostajući ID (`400`), nepostojeći ID (`404`) i nevažeće telo;
- DELETE uspeh (`204` bez tela), nevažeći ID i nepostojeći zapis;
- dodelu ID-ja 1 kada se knjiga doda u praznu listu.

Testovi se pokreću samo pri direktnom izvršavanju skripte; Uvicorn ih ne pokreće pri uvozu aplikacije. `finally` vraća `BOOKS` na početno stanje.

`TestClient` se uvozi unutar test-funkcije kako testna zavisnost ne bi bila potrebna za normalno pokretanje aplikacije.

Iz korena repozitorijuma pokreni:

```bash
./.venv/bin/python fast-api-course-my-work/Project_2/books2.py
```

Uspešan rezultat:

```text
Svi books2 assert testovi su prosli.
```
