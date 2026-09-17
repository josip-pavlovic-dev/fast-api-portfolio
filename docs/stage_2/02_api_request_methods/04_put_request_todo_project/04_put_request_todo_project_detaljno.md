# Stage 2 - API Request Methods

## Lekcija 04 - PUT request: update todo u bazi

## 0) Gde se ova lekcija uklapa

Do sada imas:

- GET all
- GET by id
- POST create

Sada dodajes UPDATE deo CRUD-a kroz PUT.
To znaci da menjas postojeci red u bazi, ne kreiras novi.

---

## 1) Sta transcript pokriva (verno lekciji)

U lekciji se radi:

1. novi PUT endpoint sa putanjom `/todo/{todo_id}`
2. status kod `204 No Content`
3. query po id + `.first()`
4. 404 ako zapis ne postoji
5. prepis svih polja iz `todo_request` u `todo_model`
6. `db.add(todo_model)` + `db.commit()`
7. path validacija kroz `Path(gt=0)`

To je klasican full update obrazac.

---

## 2) Kljucna ideja PUT zahteva

PUT je full update.

To u praksi znaci:

- klijent salje kompletan objekat koji zeli da ostane nakon izmene
- server prepisuje ciljni red tim vrednostima

Za parcijalne izmene (samo neka polja) kasnije ide PATCH.

---

## 3) Realni obrazac iz Project 4

Tvoj obrazac u routers fajlu je (koncept):

```python
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
```

Bitno:

- filtriras i po `owner_id`, ne samo po `id`
- time korisnik ne moze menjati tudji todo

---

## 4) Zasto update radimo nad vec ucitanim modelom

Transcript dobro naglasava ovo.

Ispravno:

- ucitas postojeci `todo_model` iz baze
- menjas njegova polja
- commit

Zasto ne pravimo novi objekat za update:

- SQLAlchemy bi to mogao tumaciti kao insert novog reda
- rizik duplikata ili konflikta primarnog kljuca

Pravilo:

- update = izmeni postojeci objekat
- create = napravi novi objekat

---

## 5) 204 No Content i sta to znaci

`204` znaci:

- akcija je uspesna
- response body je prazan

To je legitiman izbor za PUT kada ne vracas azurirani objekat.

Alternativa (takodje cesta):

- `200 OK` + vracen azurirani resurs

U ovom kursu ostajemo na `204`.

---

## 6) Path validacija: Path(gt=0)

`todo_id: int = Path(gt=0)` daje automatsku zastitu:

- `todo_id` mora biti pozitivan broj

Ako klijent posalje `-1`:

- FastAPI vraca `422 Unprocessable Entity`
- endpoint logika se ni ne pokrece

Ovo smanjuje potrebu za rucnim if validacijama.

---

## 7) Error semantika u ovom endpointu

- `401`: korisnik nije autentifikovan
- `404`: todo ne postoji ili ne pripada korisniku
- `422`: neispravan path parametar ili payload
- `204`: uspesna izmena bez response tela

Ako znas da razlikujes ove kodove, znas kako API treba da se ponasa.

---

## 8) Pydantic validacije i njihov uticaj na PUT

PUT koristi isti `TodoRequest` kao POST.
To znaci da i za update vaze ista pravila:

- title min 3
- description min 3 max 100
- priority 1-5
- complete bool

Rezultat:

- neispravni podaci ne stizu do baze
- integritet podataka ostaje stabilan

---

## 9) SQL ideja iza ORM update toka

ORM tok:

1. pronadji red
2. prepiši polja
3. commit

SQL ideja iza toga:

```sql
UPDATE todos
SET title = :title,
    description = :description,
    priority = :priority,
    complete = :complete
WHERE id = :todo_id
  AND owner_id = :user_id;
```

Ako nema match reda, u API logici to mapiras na 404.

---

## 10) Ceste greske pocetnika u PUT lekciji

1. Prave novi objekat umesto update postojeceg
2. Zaborave proveru `None` posle query-ja
3. Nemaju owner filter, pa menjaju tudje podatke
4. Oslone se na implicitne statuse, bez jasne semantike
5. Mesaju PUT i PATCH filozofiju

---

## 11) Mini test scenariji koje obavezno probaj

1. Validan update postojeceg todo -> ocekuj 204
2. Update nepostojeceg `todo_id` -> ocekuj 404
3. Update sa `todo_id=-1` -> ocekuj 422
4. Update sa losim payload-om (npr. priority=10) -> ocekuj 422
5. Uloguj drugog korisnika i probaj tudji id -> ocekuj 404

To je minimalni set da proveris i funkcionalnost i bezbednost.

---

## 12) PUT vs PATCH (kratko unapred)

PUT:

- potpuna zamena predvidjenih polja
- tipicno koristi full request model

PATCH:

- parcijalna izmena
- menja samo poslata polja

U ovoj lekciji radis cist PUT model.

---

## 13) Samoprovera razumevanja

Ako mozes da odgovoris, lekcija je usvojena:

1. Zasto update treba raditi nad objektom ucitanim iz baze?
2. Zasto 204 nema telo odgovora?
3. Kada dobijas 404, a kada 422?
4. Zasto je `owner_id` filter obavezan u realnoj aplikaciji?
5. Koja je sustinska razlika PUT i PATCH?

---

## 14) Zakljucak

PUT lekcija je prvi ozbiljan korak u menjanju podataka kroz API.

Ako si savladao:

- trazenje ciljnog reda
- validaciju ulaza i putanje
- bezbedan update po korisniku
- commit transakcije

onda imas cvrstu osnovu za sledecu lekciju DELETE i kompletiranje CRUD ciklusa.
