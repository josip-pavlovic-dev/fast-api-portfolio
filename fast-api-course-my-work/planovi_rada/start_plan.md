Updated todo list

Iću da ti dam jedan jednostavan teorijski plan korak po korak, tako da uvek radiš samo ono što je najvažnije za početak i ne previše opterećuješ.

## ✅ Predlog za bolju teoriju: uči “3 sloja”, a ne sve odjednom

Najbolji način za početak je da ne učiš “FastAPI kao ceo framework”, nego da prolaziš kroz 3 osnovna pojma:

1. Ruta + decorator + funkcija
2. Request i Response
3. Parametri i validacija

To je mnogo lakše od “sve odjednom”.

---

## 1) Prvi sloj: Ruta + decorator + funkcija

Ovo je najvažnije na početku.

Treba da razumeš:

- šta je dekorator `@app.get(...)`
- šta znači ruta `/items/{item_id}`
- šta funkcija radi kada dođe zahtev
- kako FastAPI “veže” URL sa funkcijom

Pitanja koja treba da znaš:

- Šta se dešava kada korisnik otvori URL?
- Zašto je funkcija ispod dekoratora bitna?
- Kako FastAPI zna da prosledi `item_id` iz URL-a u funkciju?

Ovo je osnovni “mentalni model” koji ti treba da razumeš pre nego što ideš dalje.

---

## 2) Drugi sloj: Request i Response

Nakon toga uči:

- šta je request
- šta je response
- šta znaš da pročitaš iz zahteva
- šta vraćaš kroz return

Primer:

- request = podatak koji klijent šalje
- response = podatak koji server vraća

Na primer:

- URL parametar = request deo
- JSON odgovor = response deo

Ovo ti daje potpuno jasno razumevanje da API nije samo “ruta”, nego komunikacija između klijenta i servera.

---

## 3) Treći sloj: Parametri i validacija

Ovo je već pravi “FastAPI nivo”.

Uči:

- Path Parameters
- Query Parameters
- Request Body
- validaciju tipova (`int`, `str`, `bool`)
- šta znači 422 error

Ovaj deo je najbolji nakon što razumeš:

- šta je ruta
- šta je funkcija
- šta je request/response

---

## Moj predlog za redosled učenja

### Korak 1

Nauči:

- dekorator
- ruta
- funkcija
- return

### Korak 2

Nauči:

- request
- response
- JSON
- path/query parametri

### Korak 3

Nauči:

- validacija
- status codes
- body
- database later

---

## Najvažnije pravilo

Ne uči “sve pojmove odjednom”.

Uči ovako:

- prvo: “šta se dešava”
- drugo: “zašto se dešava”
- treće: “kako se to zapisuje u kodu”

To je mnogo efikasnije nego da čitaš puno teorije bez veze.

---

## Preporučena teorija za tvoj nivo

Ja bih ti preporučio sledeći format:

- 5 minuta: objasni pojam
- 5 minuta: jednostavan primer
- 5 minuta: “šta je ovde ulaz, a šta izlaz”
- 5 minuta: kratko pitanje za proveru

Na primer:

- “Šta je ruta?”
- “Šta je funkcija?”
- “Šta vraća funkcija?”
- “Kako se path parametar prosleđuje?”
- “Šta je query parametar?”

- “Šta je request?”
- “Šta je response?”
