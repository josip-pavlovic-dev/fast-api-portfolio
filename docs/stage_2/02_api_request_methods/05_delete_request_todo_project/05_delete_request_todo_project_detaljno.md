# Stage 2 - API Request Methods

## Lekcija 05 - DELETE request: brisanje todo zapisa iz baze

## 0) Gde se ova lekcija uklapa

Do sada imas:

- GET all
- GET by id
- POST create
- PUT update

Sada zatvaras CRUD ciklus sa DELETE endpointom.
To je poslednji komad osnovnog API request methods modula.

---

## 1) Sta transcript pokriva (verno lekciji)

U transkriptu se radi:

1. kreira se `DELETE /todo/{todo_id}`
2. eksplicitno se postavlja `204 No Content`
3. dodaje se path validacija (`todo_id > 0`)
4. radi se provera da zapis postoji
5. ako ne postoji vraca se 404
6. ako postoji radi se delete + commit
7. kroz Swagger se potvrdi da je red nestao

To je tacan i dobar minimum za delete operaciju.

---

## 2) Realni obrazac iz Project 4

U tvom Project 4 kodu DELETE je sigurniji od bazicne varijante, jer filtrira i po korisniku.

Konceptualno:

```python
@router.delete("/todo/{todo_id}", status_code=204)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()
```

Znaci:

- korisnik moze obrisati samo svoj todo
- nema brisanja tudjih zapisa

---

## 3) Zasto prvo radimo check pa tek delete

Prakticna logika:

1. pronadji red
2. ako ne postoji -> 404
3. ako postoji -> obrisi

Zasto je to dobro:

- klijent dobija smislen odgovor
- izbegavas "tihi fail"
- API ponasanje je predvidivo

---

## 4) 204 No Content u DELETE kontekstu

`204` znaci:

- akcija je uspela
- nema response body

To je standardan izbor za uspesan delete.

Alternativa je 200 sa porukom, ali 204 je cist i cest REST stil.

---

## 5) Path validacija: todo_id mora biti pozitivan

Kao i u prethodnim lekcijama:

```python
todo_id: int = Path(gt=0)
```

Ako klijent posalje `-1`:

- FastAPI vraca 422
- delete logika se ne izvrsava

Ovo je odlicna zastita na ulazu.

---

## 6) Razlika 401, 404, 422, 204

U ovom endpointu:

- 401: korisnik nije autentifikovan
- 404: trazeni todo ne postoji ili ne pripada korisniku
- 422: nevalidan path parametar
- 204: uspesno obrisan todo

Ako razumes ove kodove, razumes i error model endpointa.

---

## 7) SQL ideja iza ORM delete toka

ORM izraz:

```python
db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user_id).delete()
```

SQL ideja:

```sql
DELETE FROM todos
WHERE id = :todo_id
  AND owner_id = :user_id;
```

Pa zatim:

```sql
COMMIT;
```

Bez commit-a promena ne ostaje trajno upisana.

---

## 8) Dve ceste strategije u SQLAlchemy

Za delete obicno imas dva pristupa:

1. Query delete pristup

- kao u tvom kodu: `query(...).delete()`

2. Object delete pristup

- ucitas model pa `db.delete(todo_model)`

Oba mogu biti validna.
U ovoj fazi je bitno da razumes uslov filtriranja i commit.

---

## 9) Ceste greske pocetnika u delete lekciji

1. Delete bez owner filtera

- bezbednosni problem

2. Zaboravljen commit

- deluje da je obrisano, ali zapravo nije

3. Bez prethodne provere postojanja

- API ne vraca jasan 404

4. Pogresan status code

- npr. 200 bez razloga ili 201

5. Slaba validacija todo_id

- nepotrebne greske dublje u logici

---

## 10) Mini prakticna vezba (obavezna)

1. Napravi dummy todo preko POST.
2. Potvrdi da postoji kroz GET all.
3. Obrisi ga preko DELETE sa tacnim id.
4. Potvrdi da vise ne postoji kroz GET all.
5. Probaj isti id opet i potvrdi 404.
6. Probaj `todo_id=-1` i potvrdi 422.

Ovim testiras i funkcionalnost i granicne slucajeve.

---

## 11) Bezbednosna napomena

U multi-user sistemu, delete je kriticna operacija.
Filter po `owner_id` nije opcioni luksuz, vec obavezna zastita.

Bez toga, korisnik moze probati tudje id vrednosti i brisati tudje podatke.

---

## 12) Kako ovo zatvara CRUD modul

Sada imas komplet:

- Create -> POST
- Read list -> GET all
- Read single -> GET by id
- Update -> PUT
- Delete -> DELETE

To je puna osnova svake backend aplikacije.

---

## 13) Samoprovera razumevanja

Ako mozes da odgovoris, lekcija je usvojena:

1. Zasto je 204 dobar izbor za delete success?
2. Zasto je potrebno i `id` i `owner_id` filtriranje?
3. Sta se desava ako zaboravis commit?
4. Kada vracas 404, a kada 422?
5. Koja je razlika izmedju query delete i object delete pristupa?

---

## 14) Zakljucak

DELETE lekcija deluje kratko, ali je bezbednosno i funkcionalno veoma vazna.

Kad je uradis kako treba, zatvaras ceo osnovni CRUD ciklus nad realnom bazom,
uz jasnu validaciju, pravilne HTTP kodove i kontrolu vlasnistva podataka.
