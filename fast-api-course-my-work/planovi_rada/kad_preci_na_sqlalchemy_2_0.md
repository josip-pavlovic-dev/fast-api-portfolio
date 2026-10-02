# Kad preći na SQLAlchemy 2.0

Na osnovu trenutnog napretka, **još ne bih sada refaktorisao kod u SQLAlchemy 2.0**.

Trenutno si u delu autentifikacije, a najkorisniji trenutak za prelazak je:

**posle završetka Section 11: Authenticate Requests, a pre Section 12/13**, odnosno pre ozbiljnog production database setup-a i Alembic migracija.

Tada ćeš već razumeti:

- modele i kolone
- `Session` i dependency
- `query()`, `filter()`, `first()`
- ORM instance
- autentifikaciju i rad sa korisničkim modelom
- osnovni CRUD

Pre Alembic-a je dobro imati konačniju verziju modela, na primer:

```python
from sqlalchemy.orm import Mapped, mapped_column

hashed_password: Mapped[str] = mapped_column(nullable=False)
is_active: Mapped[bool] = mapped_column(default=True)
```

Moj predlog redosleda:

1. Završi autentifikaciju i JWT deo.
2. Nauči osnovnu Alembic teoriju, ali još ne radi migracije.
3. Pređi na SQLAlchemy 2.0 stil i refaktoriši modele/query-je.
4. Tek onda radi Section 12 i Section 13 sa production bazom i Alembic migracijama.
5. Nakon toga nastavi na testing, deployment i full-stack delove.

Dakle, **checkpoint za SQLAlchemy 2.0: kraj Section 11, pre Section 12/13**.

---

## Pitanje

U našem planu piše da treba da završim i 02_authenticate_requests pa onda da pređem na sqlalchemy 2.0 . Analiziraj sadržaj 02_authenticate_requests pa proceni da li da odmah krenem sa sqllchemy 2.0 ili da prvo završim i 02_authenticate_requests?

### VAŽNO PITANJE

Na šta tačno treba da se skoncentrisem u mojoj trenutnoj verziji TodoApp a šta će se menjati uvođenjem `sqlalchemy 2.0`? Shvatio sam da npr. `db.query(Users).filter(Users.id==user_id).first()` više ne važi ali to je sve što znam!

---

## Odgovor

1. Ne čekaj da “idealno” završiš sve iz 02 da bi tek onda krenuo `SQLAlchemy 2.0`.
2. Završi samo kritični `minimum` iz 02 (`users ruta`), pa odmah kreni 2.0 refaktor.
3. Admin deo može i posle početka 2.0, jer je više authorization dizajn nego ORM osnova.

Šta sam video u tvom projektu

1. Ownership CRUD je već dobro postavljen u `todos.py:18` i koristi filter po owner_id kroz sve operacije.
2. Security tok je stabilan u `security.py:36`, sa centralnim get_current_user.
3. Users i admin rute su još prazne:
   `users.py`
   `admin.py`
4. Main trenutno uključuje samo auth i todos:
   `main.py:18`

### Zaključak za tvoje prvo pitanje

1. Ako `“završiti 02_authenticate_requests”` znači i users i admin full implementation, to nije neophodan uslov da bi krenuo 2.0.
2. Ako `“završiti 02”` znači imati `kompletan user self-service` (get me + change password), to bih završio prvo, jer zatvara auth celinu i daje stabilan baseline pre refaktora.
3. Dakle: prvo `users minimum`, pa `SQLAlchemy 2.0` odmah nakon toga.

---

### VAŽNO za `db.query` primer koji si naveo

1. Nije baš da “više ne važi”.
2. U `SQLAlchemy 2.0` taj stil uglavnom i dalje radi radi kompatibilnosti, ali je legacy stil.
3. Preporučeni stil je `select + execute + scalars`.

---

## Na šta tačno da se skoncentrišeš sada (trenutni TodoApp)

1. `Security` pravila, ne sintaksa.
2. Invarianta (pravilo koje se uvek poštuje) da klijent nikad ne određuje `owner_id`.
3. Invarianta da svuda ostane `id` + `owner_id` zaštita za `read by id`, `update`, `delete`.
4. Dosledni status kodovi `401`, `403`, `404` prema istoj logici.

`401` - Unauthorized, kada korisnik nije autentifikovan. Ovu grešku vraćamo kada JWT token nije prisutan ili nije validan.
`403` - Forbidden, kada korisnik nema pravo pristupa resursu. Ovu grešku vraćamo kada JWT token postoji i validan je, ali korisnik nema odgovarajuće dozvole.
`404` - Not Found, kada resurs ne postoji ili nije dostupan korisniku. Ovu grešku vraćamo kada resurs sa datim ID-om ne postoji ili pripada drugom korisniku.

5. Users ruta kao minimalno zatvaranje oblasti 02:
   `get current user`, `change password`, bez vraćanja `hashed_password`.

---

## Šta će se menjati uvođenjem `SQLAlchemy 2.0`

1. Menja se ORM stil pisanja modela:
   `Column` pristup prelazi na `Mapped` i `mapped_column`.
2. Menja se stil upita:
   `query/filter/first/all` prelazi na `select/where/execute/scalars`.
3. Menja se način razmišljanja o rezultatima:
   `execute` vraća rezultat `set`, pa onda `scalars` koji vraća `ORM instance`.
4. Menja se postepeno i bez menjanja API ugovora:
   `rute`, `URL`, `auth pravila`, `response semantika` treba da ostanu isti.

---

## Šta se ne menja (ostaje isto)

1. `JWT` logika i `get_current_user` koncept.
2. `Authorization` pravilo `ownership-a`.
3. `Biznis ponašanje` endpointa.
4. `HTTP` ugovor ka klijentu.

---

## Najbolji redosled od danas

1. Implementiraj users rutu (1 fokus sesija). Prvo minimalno zatvori oblast 02 sa `get current user` i `change password`.

2. Napravi mali smoke test `auth` + `todos` + `users`. Primer:
   - Registracija novog korisnika
   - Login i dobijanje JWT tokena
   - Kreiranje novog Todo zapisa
   - Dohvatanje liste Todo zapisa
   - Dohvatanje trenutnog korisnika (`/users/me`)
   - Promena lozinke (`/users/password`)
   - Provera da li su svi odgovori i status kodovi u skladu sa očekivanjima (`401`, `403`, `404`).
   - Provera da li su ownership i role pravila pravilno primenjena.
   - Provera da li su svi endpointi u skladu sa očekivanim sigurnosnim pravilima.

3. Kreni SQLAlchemy 2.0 refaktor. Počni prvo sa read upitima (`select/where/execute/scalars`), a zatim pređi na write operacije (`insert/update/delete`). Redosled je bitan da bi se prvo osigurala stabilnost čitanja podataka pre nego što se menja baza. Pravilan redosled skripti i testova je ključan za bezbedan prelazak na novi ORM stil:

   - Refaktorisanje read upita u svim servisima i endpointima. (`get/list` endpoints -> `select/where/execute/scalars`)
   - Refaktorisanje write operacija u svim servisima i endpointima. (`post/put/delete` endpoints -> `insert/update/delete`)

4. Tek kada to radi stabilno, ulazi dublje u Alembic migracije.
