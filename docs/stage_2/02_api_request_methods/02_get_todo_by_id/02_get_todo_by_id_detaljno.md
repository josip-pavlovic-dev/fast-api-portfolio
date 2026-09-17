# Stage 2 - API Request Methods

## Lekcija 02 - GET todo by id

## 0) Gde se ovo uklapa

U prethodnoj lekciji si napravio endpoint koji vraca listu todos zapisa.
Sada radis sledeci prirodan korak:

- vracanje jednog konkretnog todo zapisa
- po njegovom `id` path parametru

Ovo je osnova za sve detaljne prikaze resursa u REST API dizajnu.

---

## 1) Sta transcript pokriva (verno lekciji)

Transkript prolazi sledece tacke:

1. Novi GET endpoint sa path parametrom (`/todo/{todo_id}`)
2. Ponovna upotreba DB dependency obrasca
3. Query + filter po `Todos.id == todo_id`
4. Koriscenje `.first()`
5. 404 greska kada zapis ne postoji
6. Eksplicitan status kod 200
7. Path validacija (`todo_id > 0`) preko `Path(gt=0)`

To je tacno ono sto treba pocetniku u ovoj fazi.

---

## 2) Realni obrazac u Project 4

U tvom Project 4 kodu endpoint je:

- GET `/todo/{todo_id}`
- `status_code=200`
- `todo_id: int = Path(gt=0)`
- dodatni auth filter po `owner_id`

To znaci da je tvoj kod vec na boljem, bezbednijem nivou od bazicnog primera iz transkripta.

---

## 3) Kako izgleda endpoint logika

Konceptualno:

```python
@router.get("/todo/{todo_id}", status_code=200)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")
```

Razbijeno na korake:

1. FastAPI validira `todo_id` da je > 0
2. Auth dependency vrati trenutnog korisnika
3. DB dependency otvori sesiju
4. Query trazi zapis po `id` i `owner_id`
5. Ako postoji -> vraca ga
6. Ako ne postoji -> 404
7. Na kraju requesta sesija se zatvara

---

## 4) Zasto `.first()` ima smisla

U transkriptu se pominje optimizacija: "vrati prvi match".

To je logicno jer je `id` primarni kljuc:

- jedinstven je
- ocekujes najvise jedan red

`.first()` u tom slucaju ima smisla, jer ti treba jedan objekat ili `None`.

---

## 5) 404 i zasto je bitan

Kada trazeni todo ne postoji, pravi odgovor je:

- `404 Not Found`

To nije "error app-a", to je normalna poslovna situacija.

Dobra praksa:

- detalj poruke treba da bude jasan (`Todo not found.`)
- klijent odmah zna sta da radi dalje

---

## 6) Path validacija i 422

`todo_id: int = Path(gt=0)` znaci:

- mora biti ceo broj
- mora biti strogo veci od 0

Ako korisnik posalje `-1`, FastAPI pre endpoint logike vraca:

- `422 Unprocessable Entity`

Prednost:

- ne pises rucni `if todo_id <= 0`
- validacija je centralizovana i dosledna

---

## 7) Zasto owner filter menja sve

Bazicni transcript filtrira samo po `id`.
U realnoj app to nije dovoljno.

Bez owner filtera moguce je:

- pogoditi tudji `id`
- procitati tudji todo

Sa owner filterom:

- korisnik vidi samo svoje podatke
- endpoint je privacy-safe

Prakticna SQL ideja tvog query-ja:

```sql
SELECT *
FROM todos
WHERE id = :todo_id
  AND owner_id = :current_user_id
LIMIT 1;
```

---

## 8) Razlika izmedju 401, 404 i 422 u ovoj lekciji

- 401: korisnik nije autentifikovan
- 404: todo ne postoji za taj kriterijum
- 422: neispravan path input (npr. negativan id)

Ako ove tri razlike razumes, razumes osnovni API error model.

---

## 9) Najcesce greske pocetnika

1. Zaborave `Path(gt=0)`
2. Ne proveravaju `None` posle query-ja
3. Vracaju 200 sa praznim objektom umesto 404
4. Filter samo po `id` bez `owner_id`
5. Mesaju 401 i 404 semantiku

---

## 10) Brza mini vezba

1. Pozovi endpoint sa validnim `todo_id` koji postoji -> ocekuj 200.
2. Pozovi endpoint sa `todo_id` koji ne postoji -> ocekuj 404.
3. Pozovi endpoint sa `todo_id=-1` -> ocekuj 422.
4. Uloguj drugog korisnika i probaj tudji `todo_id` -> treba da dobijes 404.

Time pokrivas i funkcionalnost i bezbednost.

---

## 11) Kako ovo vodi u sledece lekcije

GET by id je obrazac koji ces kopirati i za:

- PUT by id
- DELETE by id
- kasnije PATCH by id

Jedina razlika je sta radis sa nadjenim objektom:

- GET: vratis ga
- PUT/PATCH: izmenis i commit
- DELETE: obrises i commit

---

## 12) Samoprovera razumevanja

Ako mozes da odgovoris na ova pitanja, lekcija je usvojena:

1. Zasto je `.first()` prirodan izbor kada trazis po primarnom kljucu?
2. Zasto koristimo `Path(gt=0)` umesto rucnog if-a?
3. Kada se vraca 404, a kada 422?
4. Zasto je filter po `owner_id` bezbednosno obavezan?
5. Sta radi DB dependency pre i posle endpoint funkcije?

---

## 13) Zakljucak

Lekcija 02 uvodi najvazniji detalj CRUD citanja:

- precizno trazenje jednog resursa
- pravilan HTTP odgovor po scenariju
- ulazna validacija
- i bezbedan pristup podacima korisnika

Kad ovo legne, POST/PUT/DELETE bice mnogo laksi jer dele isti skeleton rada.
