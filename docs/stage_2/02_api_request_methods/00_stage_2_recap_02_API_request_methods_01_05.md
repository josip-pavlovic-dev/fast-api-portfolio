# Stage 2 Recap - API Request Methods (Lekcije 01-05)

Ovaj recap povezuje sve lekcije iz oblasti API request methods u jedan prakticni plan ucenja.
Cilj je da kroz par dana ucvrstis razumevanje i predjes od teorije ka sigurnoj praksi sa stvarnim CRUD endpointima.

## 1) Mapa oblasti

## Lekcija 01

Tema: GET all todos iz baze kroz FastAPI endpoint.
Ishod:

- razumes get_db dependency i yield lifecycle
- razumes dependency injection kroz Depends
- razumes query i `.all()` metodu
- znas da vratis listu zapisa

Materijal:

- [docs/stage_2/02_api_request_methods/01_get_all_todos_from_database/01_get_all_todos_from_database_detaljno.md](docs/stage_2/02_api_request_methods/01_get_all_todos_from_database/01_get_all_todos_from_database_detaljno.md)

## Lekcija 02

Tema: GET todo po konkretnom id.
Ishod:

- razumes path parametre i Path validaciju
- razumes `.first()` za jedan rezultat
- razumes 404 semantiku
- znas da vratis jedan zapis ili gresku

Materijal:

- [docs/stage_2/02_api_request_methods/02_get_todo_by_id/02_get_todo_by_id_detaljno.md](docs/stage_2/02_api_request_methods/02_get_todo_by_id/02_get_todo_by_id_detaljno.md)

## Lekcija 03

Tema: POST - kreiranje novog todo zapisa.
Ishod:

- razumes Pydantic request model i Field validacije
- razumes zasto se id ne salje u payload
- razumes model_dump, db.add, db.commit
- znas da kreiras red i da vratis 201

Materijal:

- [docs/stage_2/02_api_request_methods/03_post_request_todo_project/03_post_request_todo_project_detaljno.md](docs/stage_2/02_api_request_methods/03_post_request_todo_project/03_post_request_todo_project_detaljno.md)

## Lekcija 04

Tema: PUT - update kompletnog todo zapisa.
Ishod:

- razumes full update semantiku
- znas zasto se update radi nad postojecim modelom
- razumes 204 No Content odgovor
- znas da menjas polja i da commit

Materijal:

- [docs/stage_2/02_api_request_methods/04_put_request_todo_project/04_put_request_todo_project_detaljno.md](docs/stage_2/02_api_request_methods/04_put_request_todo_project/04_put_request_todo_project_detaljno.md)

## Lekcija 05

Tema: DELETE - brisanje todo zapisa.
Ishod:

- razumes delete logiku i 204 odgovor
- razumes zasto je provera postojanja 404 vazna
- znas da obrises red bezbedno
- razumes uloga owner_id filtera

Materijal:

- [docs/stage_2/02_api_request_methods/05_delete_request_todo_project/05_delete_request_todo_project_detaljno.md](docs/stage_2/02_api_request_methods/05_delete_request_todo_project/05_delete_request_todo_project_detaljno.md)

---

## 2) Plan ucenja za 3 dana

## Dan 1 (oko 120 minuta)

- Procitaj lekcije 01 i 02 redom.
- Nacrtaj mapu GET operacija: GET all vs GET by id.
- U svesci napisi razliku izmedju `.all()` i `.first()`.
- Uradi sve samoprovere iz obe lekcije.
- U Swagger-u (docs) testiraj GET all i GET by id na pravom serveru.

Exit kriterijum:

- mozes bez pomoci da napises query za GET all i GET by id.

## Dan 2 (oko 120 minuta)

- Procitaj lekciju 03 (POST).
- Napravi 5 razlicitih todos preko POST sa validnim payload-ima.
- Potvrdi kroz GET all da su se zapisi pojavili sa auto-increment id.
- Napisi 3 losih payload-a i potvrdi da dobijes 422.
- Procitaj lekciju 04 (PUT) i zatvori sa samoproverom.

Exit kriterijum:

- mozes bez pomoci da kreiras i update todo, sa jasnim statusima za svaki slucaj.

## Dan 3 (oko 120 minuta)

- Procitaj lekciju 05 (DELETE).
- Kreiraj dummy todo, obrisi ga i potvrdi da vise ne postoji.
- Pokusaj svaki granicni slucaj (negativan id, nepostojeći id, pravi id).
- Kraci test: za jedan todo radi sve CRUD operacije redom (C-R-U-D).
- Napisi kratki report: koje HTTP kodove koristis i zasto.

Exit kriterijum:

- sigurno manipulis svim CRUD operacijama bez straha od greske.

---

## 3) Kompletna CRUD checklist

Minimalna vezba za krajnji test:

1. GET /todos -> vracas sve
2. POST /todos -> kreiras jedan
3. GET /todos/{id} -> vracas jedan po id
4. PUT /todos/{id} -> menjas sve polje
5. DELETE /todos/{id} -> brises jedan

Svaka operacija treba da vrsi i proveri bezbednosno:

- validan ulaz -> success sa pravim statusima
- neispravan ulaz -> 422
- neautentifikovan -> 401
- ne-ownership -> 404

---

## 4) Mapiranje HTTP metoda na CRUD

- CREATE -> POST (201 Created)
- READ (list) -> GET / (200 OK)
- READ (single) -> GET /{id} (200 OK ili 404 Not Found)
- UPDATE -> PUT /{id} (204 No Content ili 404)
- DELETE -> DELETE /{id} (204 No Content ili 404)

Ako ovo jasno razumes, razumes i osnovu svake REST API.

---

## 5) Kljucne stvari koje treba da pamtis

1. Dependency injection (`Depends`) je osnova za DB sesije.
2. Path validacija `Path(gt=0)` je brza zastitta.
3. Pydantic model validira ulaz pre nego sto dosegne bazu.
4. 204 nema body, 404 znaci nije nadeno, 422 znaci ulaz je pogresan.
5. owner_id filter u read/update/delete sprecava curenje podataka.
6. db.add() + db.commit() je redosled za trajne izmene.
7. `.first()` za jedan rezultat, `.all()` za listu.

---

## 6) Najbole greske koje se prave u ovoj oblasti

1. Zaboravljen commit -> izgleda da radi ali nije trajno
2. Nema owner filtera -> korisnik vidi/menja tudje podatke
3. Pogresan status kod -> 200 gde ide 204, 201 gde ide 200
4. Mesh query sa delete -> mislis da zelis jedno a obrises sve
5. Ignorisanje Path(gt=0) -> loose validacija na ulazu

---

## 7) Spremnost za sledecu oblast

Spreman si za sledeci nivo kada bez pomoci mozes:

- objasniti HTTP metode (GET, POST, PUT, DELETE)
- pisati i testirati sve CRUD operacije
- razumeti i primeniti dependency injection
- validirati ulaz kroz Path i Field
- pravilno koristiti HTTP status kodove
- bezbedno filtrirati po korisniku (owner_id)

Ako sve ovo legne, prelazis na sledeci modul sa solidnom vezom.

---

## 8) Kratka istorija sto je do sada urađeno

Sve od Stage 2 lekcija:

- 01_setup_database/01-05: kako se baza kreira i testira
- 02_api_request_methods/01-05: kako se sa bazom radi kroz API

To je temelj: bez baze nema API-ja, bez API-ja korisnik ne vidi bazu.

Zajedno, cine opitu cirkulaciju podataka od klijenta do baze i nazad.

---

## 9) Zakljucak

Stage 2 modul 02 je veliki korak jer prvi put radis sa pravim CRUD sistemom.

Ovde se prelazi od teorije ka praksi: ne samo da znas SQL ili ORM,
nego ga koristiš kroz API preko HTTP zahteva sa jasnom validacijom, autentifikacijom i autorizacijom.

Kad ovaj modul zavrsish, imas spreman, funkcionalan CRUD API koji se moze prosiriti dalje u sledecim stagovima.
