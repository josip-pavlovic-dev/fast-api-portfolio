## Najbolja kratka definicija za početak

FastAPI endpoint je:

- ruta koja definira URL
- funkcija koja obrađuje zahtev
- return koji vraća odgovor

To je dovoljno za prvi dan. Bez toga ne treba ići u naprednije stvari.

---

## ✅ Prvi korak: Ruta + decorator + funkcija

Naravno — i to je najbolji način da počneš. Ne moraš odmah da razumeš sve u FastAPI-ju. Prvo treba da razumeš 3 stvari:

1. šta je ruta
2. šta je decorator
3. šta radi funkcija ispod njega

---

## 1) Šta je ruta?

Ruta je URL adresa koja vodi do određenog dela aplikacije.

Primer:

```python
@app.get("/items")
```

To znači:

- kada korisnik otvori `/items`
- FastAPI zna da je to određena ruta u aplikaciji

Ruta je kao “adresa” koju korisnik poziva u browseru ili kroz API.

---

## 2) Šta je decorator?

Decorator je deo koda koji “kaže” FastAPI-u:

> “Ova funkcija predstavlja odgovor na ovaj URL.”

Primer:

```python
@app.get("/items")
```

- `@app` znači: ovo je aplikacija
- `.get` znači: ovo je GET zahtev
- `"/items"` je ruta

Dakle, decorator je uloga “povezivanja” između URL-a i funkcije.

---

## 3) Šta radi funkcija ispod dekoratora?

To je najvažnija stvar.

Funkcija ispod dekoratora je “handler” ili “endpoint” funkcija. Ona se poziva kada korisnik dođe na tu rutu.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def read_items():
    return {"message": "Hello from FastAPI"}
```

Ovo znači:

- korisnik ide na `/items`
- FastAPI uviđa da postoji ruta `/items`
- pozove funkciju `read_items()`
- funkcija vraća rezultat
- FastAPI to pretvara u HTTP response

---

## 4) Jednostavan mentalni model

Zamislite to ovako:

- ruta = adresa
- decorator = veza između adrese i funkcije
- funkcija = ono što se izvršava kada neko pristupi toj adresi
- return = odgovor koji se vraća klijentu

---

## 5) Šta je return?

`return` je rezultat koji funkcija vraća.

Primer:

```python
def read_items():
    return {"message": "Hello"}
```

To znači da će klijent dobiti JSON odgovor:

```json
{ "message": "Hello" }
```

Dakle:

- funkcija ne “samo piše tekst”
- ona vraća podatke koje FastAPI šalje korisniku

---

## 6) Primer koji pokazuje celu logiku

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Zdravo, svete!"}
```

Kada korisnik ode na:

```http
GET /hello
```

FastAPI radi ovo:

1. vidi rutu `/hello`
2. zna da je povezana sa funkcijom `say_hello`
3. pozove tu funkciju
4. funkcija vraća `{"message": "Zdravo, svete!"}`
5. FastAPI šalje taj odgovor

---

## 7) Šta je zapravo endpoint?

Endpoint je baš to:

- URL ruta
- povezana sa funkcijom
- koja vrati odgovor

U stvari, endpoint = ruta + funkcija.

---

## 8) Najbitnije pravilo za početak

Ne razmišljaj o FastAPI kao o “sve u jednom”.

Razmišljaj ovako:

- ruta: gde korisnik ide
- funkcija: šta se dogodi
- return: šta se vraća

To je basis za sve ostalo.

---

## 9) Kratko “proveri da li razumeš”

Pokušaj da odgovoriš na ova 4 pitanja:

- Šta je ruta?
- Šta je decorator?
- Šta radi funkcija ispod dekoratora?
- Šta je return?

Ako znaš odgovore, onda si spreman za sledeći korak.

---

## 10) Sledeći korak

Sledeći deo koji ide odmah posle ovog je:

- Request i Response
- šta je zahtev
- šta je odgovor
- kako se podaci šalju između klijenta i servera

To je drugi “sloj” u teoriji FastAPI-ja.

---

## ✅ Plan za naredni sadržaj

1. Request i Response
2. jednostavan primer
3. razlika između URL-a i JSON-a
4. kratka tabela “šta je šta”

---

Updated todo list

Nastavljam sa sledećim delom i fokusiraću se samo na request/response i jednostavan mentalni model, bez dodatnih detalja koji bi previše opteretili početak.

Naravno — nastavljamo sa sledećim korakom: Request i Response. Ovo je veoma važno, jer bez toga ne razumeš kako API zapravo radi.## Request i Response u FastAPI

Sada kada znaš šta je ruta i funkcija, treba da razumeš još dve stvari:

- Request
- Response

To su osnovni “delovi” komunikacije između klijenta i servera.

---

## 1) Šta je Request?

Request je zahtev koji klijent šalje serveru.

To može biti:

- URL
- path parametar
- query parametar
- body (JSON)
- headers

Na primer, kada korisnik u browseru ili u Postman-u ode na:

```http
GET /items/5
```

to je request.

FastAPI prima taj request i zna:

- koja je ruta
- šta je zahtev
- šta treba da uradi

---

## 2) Šta je Response?

Response je odgovor koji server vraća klijentu.

Najčešće je to:

- JSON
- status code
- neki tekst ili podatak

Na primer:

```json
{ "item_id": 5 }
```

Ovo je response.

---

## 3) Jednostavan primer

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Ovde:

- request je: `GET /items/5`
- FastAPI uzme `item_id = 5`
- funkcija `read_item` obrađuje to
- return vraća: `{"item_id": 5}`
- to je response

---

## 4) Šta je “ulaz” i šta je “izlaz”?

Ovo je veoma važno da znaš.

### Ulaz (input)

Ulaz su podaci koje klijent šalje:

- URL
- path parametar
- query parametar
- JSON body

### Izlaz (output)

Izlaz su podaci koje server vraća:

- JSON
- status code
- poruka

---

## 5) Primer sa input i output

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Zdravo"}
```

### Ulaz:

Nema nikakvih dodatnih parametara, samo je zahtev na `/hello`.

### Izlaz:

```json
{ "message": "Zdravo" }
```

---

## 6) Šta je JSON?

JSON je format podataka koji se najčešće koristi u API-ju.

Primer:

```json
{
  "name": "Ana",
  "age": 25
}
```

FastAPI uglavnom vraća JSON.

---

## 7) Šta je status code?

Status code je broj koji govori da li je zahtev uspešan.

Najčešći primeri:

- `200` → OK
- `201` → Created
- `400` → Bad Request
- `404` → Not Found
- `422` → Validation error

Na primer, ako pošalješ pogrešan tip podatka, FastAPI može vratiti `422`.

---

## 8) Jednostavna analogija

Zamislite da je API kao restoran:

- klijent = gost
- server = restoran
- request = zahtev gosta
- response = jelo koje mu se servira
- ruta = koju sobu ili sto gost traži
- funkcija = kuvar koji priprema jelo

To ti odmah daje sliku: API je komunikacija između gosta i kuvara.

---

## 9) Šta je ključna stvar za početak?

Treba da razumeš da FastAPI radi ovako:

1. klijent šalje zahtev
2. ruta prepoznaje URL
3. funkcija prima potrebne podatke
4. funkcija obrađuje podatke
5. return vraća odgovor
6. FastAPI šalje response

To je osnovni tok.

---

## 10) Kratka tabela

- Ruta = URL adresa
- Decorator = povezuje URL sa funkcijom
- Funkcija = obrada zahteva
- Request = zahtev koji stiže
- Response = odgovor koji se vraća
- JSON = format odgovora
- Status code = informacija o uspehu/neuspehu

---

## 11) Pitanja za proveru

Pokušaj da odgovoriš na ova 3 pitanja:

- Šta je request?
- Šta je response?
- Šta je JSON?

Ako znaš odgovore, onda si spreman za sledeći deo.

---

## Sledeći korak: Path Parameters

Sada prelazimo na stvar koja je najrelevantnija za tvoje pitanje:

- šta su path parameters
- kako se pišu u URL-u
- kako se prosleđuju u funkciju
- zašto su korisni

To je sledeći deo koji sledi odmah posle ovog.

---

Updated todo list

I will go deeper into Path Parameters in a simple, beginner-friendly way and keep it to a clear, usable lesson for today.

## Path Parameters – detaljno, ali jednostavno

Danas ćemo obraditi samo ono što ti treba da razumeš da bi mogao da nastaviš kurs bez zastoja.

---

## 1) Šta su Path Parameters?

Path Parameters su promenljivi delovi URL-a.

Primer:

```python
@app.get("/users/{user_id}")
```

Ovo znači:

- ruta je `/users/{user_id}`
- `user_id` je promenljiva
- u praksi može da bude bilo šta, npr. `/users/1`, `/users/7`, `/users/42`

Dakle, deo URL-a koji se menja zove se path parameter.

---

## 2) Kako se pišu?

U FastAPI-ju path parametar se piše u zagradama:

```python
/users/{user_id}
```

ili

```python
/items/{item_id}
```

To je sintaksa koju FastAPI prepoznaje.

---

## 3) Kako to radi u funkciji?

Ruta i funkcija moraju imati isto ime.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

Ako pozoveš:

```http
GET /users/10
```

dobijaš:

```json
{ "user_id": 10 }
```

To znači:

- FastAPI prepozna URL `/users/10`
- prikupi vrednost `10`
- prosledi je u parametar `user_id`
- funkcija vraća odgovor

---

## 4) Zašto je ovo korisno?

Jer često želimo da radimo sa konkretnim objektom.

Primeri:

- `/users/1` → korisnik sa ID 1
- `/products/5` → proizvod sa ID 5
- `/orders/99` → narudžbina broj 99

To je idealno za resurse koji imaju jedinstven identifikator.

---

## 5) Path parameter i funkcija – pravilo koje je važno

Ruta i parametar moraju imati isto ime:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    ...
```

Ne možeš napisati:

```python
@app.get("/items/{item_id}")
def read_item(id: int):
    ...
```

Zato što FastAPI očekuje da se naziv parametra poklapa sa nazivom u ruti.

---

## 6) Tipovi path parametara

Najčešće koristiš:

- `int`
- `str`
- `float`

Primer:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Ovo znači:

- `item_id` mora biti integer
- ako korisnik pošalje `/items/abc`, FastAPI će vratiti grešku

To je divno, jer FastAPI automatski validira podatke.

---

## 7) Validacija tipa

Primer:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Ako dođe zahtev:

```http
GET /items/abc
```

dobijaš grešku, najčešće 422.

To je normalno, jer je očekivan broj, a dobio se tekst.

To je jedan od najvažnijih FastAPI mehanizama.

---

## 8) Više path parametara u istoj ruti

Možeš imati više promenljivih delova u URL-u.

Primer:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/orders/{order_id}")
def get_user_order(user_id: int, order_id: int):
    return {
        "user_id": user_id,
        "order_id": order_id
    }
```

Poziv:

```http
GET /users/3/orders/10
```

Odgovor:

```json
{
  "user_id": 3,
  "order_id": 10
}
```

Ovo je vrlo često u API-ju.

---

## 9) Path Parameters vs Query Parameters

Ovo je vrlo važno da razlikuješ.

### Path Parameters

Koriste se za konkretan resurs:

```http
GET /users/5
```

Ovo znači: “daj mi korisnika sa ID 5”.

### Query Parameters

Koriste se za filtere, pretragu, opcije:

```http
GET /users?role=admin
```

Ovdje je `role=admin` dodatni parametar.

---

## 10) Jednostavno pravilo

Pitaj se:

> “Da li je ovo identifikator konkretnog resursa?”

Ako jeste, to je path parameter.

Primer:

- `/users/7`
- `/products/12`

Ako je:

- filter
- pretraga
- sorting
- opcije

onda je query parameter.

---

## 11) Najvažnije stvari koje treba da zapamtiš

- Path parameter je deo URL-a
- Piše se kao `{ime}`
- Koristi se za konkretan resurs
- Mora da ima isto ime u ruti i u funkciji
- FastAPI automatski pokušava da ga konvertuje u tip koji si naveo
- Ako nije validno, vratiće grešku

---

## 12) Kratki primer za pamćenje

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Znači:

- URL: `/items/15`
- `item_id` = `15`
- odgovor: `{"item_id": 15}`

Jednostavno i jasno.

---

## 13) Dobar način razmišljanja

Zamislite da je URL “šablon”:

```python
"/users/{user_id}"
```

a vrednost koja dolazi u njega je “popunjena” u momentu zahteva:

```python
/users/7
```

Tada je:

```python
user_id = 7
```

To je u suštini cela logika.

---

## 14) Mala vežba za danas

Pokušaj da sam napišeš ovaj kod:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/books/{book_id}")
def get_book(book_id: int):
    return {"book_id": book_id}
```

Zatim zamisli request:

```http
GET /books/25
```

i odgovori šta ćeš dobiti.

Odgovor je:

```json
{ "book_id": 25 }
```

Ako to razumeš, onda si savladao osnovu path parameters.

---

## 15) Dovoljno za danas

Za danas je dovoljno da razumeš:

- šta su path parameters
- kako se pišu
- kako se prosleđuju u funkciju
- kako se razlikuju od query parameters
- zašto su korisni
- kako validacija radi

---
