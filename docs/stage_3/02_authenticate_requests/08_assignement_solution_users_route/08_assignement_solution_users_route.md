# Oblast 03 - Authenticate Requests

## Lekcija 08 - Rešenje assignment-a: users ruta, get_user i change_password

Ova lekcija je nastavak assignment zadatka iz prethodnog videa i daje kompletan konceptualni obrazac za users rutu.

Transcript prikazuje osnovno kursno rešenje, a ovde je objašnjenje prošireno i usklađeno sa tvojim trenutnim TodoApp projektom.

---

## 1) Šta je cilj rešenja

Potrebno je dobiti users sloj koji omogućava:

1. current user profil (`get_user`),
2. promenu sopstvene lozinke (`change_password`).

Sve operacije su vezane za trenutno ulogovanog korisnika, ne za proizvoljan `user_id` iz URL-a.

---

## 2) Usklađeno stanje tvog koda pre implementacije

U ovom trenutku:

1. `api/routes/users.py` postoji, ali je prazan.
2. `main.py` još ne uključuje users router.
3. `get_current_user` je već gotov i vraća `Users` ORM objekat.
4. Password hashing/verifikacija je već korišćena u `auth.py` preko `CryptContext`.

To znači da su ti svi ključni gradivni blokovi već spremni.

---

## 3) Predlog users router konfiguracije

Kao početni dizajn:

1. `prefix="/users"`
2. `tags=["users"]`

Preporučene rute:

1. `GET /users/me` za podatke current user-a.
2. `PUT /users/password` za promenu lozinke.

Napomena:

U transcriptu je korišćen `/user/` stil. U tvom projektu je doslednije koristiti množinu `/users` kao i `/todos`.

---

## 4) get_user endpoint - šta treba da vrati

Uloga endpointa:

1. Authentifikuje korisnika kroz dependency.
2. Vrati podatke tog korisnika bez osetljivih polja.

Važno poboljšanje u odnosu na transcript:

Transcript demonstrira i vraćanje `hashed_password`, ali u realnom API dizajnu to ne treba vraćati klijentu.

Zato je ispravno koristiti response model poput tvog `UserResponse` koji već ne sadrži `hashed_password`.

---

## 5) change_password endpoint - ključna pravila

Endpoint treba da primi body sa:

1. `current_password`
2. `new_password`

I da sprovede sledeći tok:

1. current user se dobije iz tokena,
2. verifikuje se da je `current_password` tačan,
3. ako nije tačan, odbija se zahtev,
4. ako jeste tačan, nova lozinka se hash-uje,
5. hash se upisuje u bazu,
6. radi se commit.

---

## 6) Zašto je verifikacija stare lozinke obavezna

Bez verifikacije stare lozinke, svako ko ima aktivnu sesiju na kompromitovanom uređaju mogao bi odmah promeniti lozinku.

Zato je bezbednosno pravilo:

1. prvo dokaz da znaš trenutnu lozinku,
2. tek onda dozvoli promenu.

---

## 7) Veza sa postojećim auth modulom

Tvoj `auth.py` već sadrži `bcrypt_context` i proveru lozinke pri login-u.

Users ruta treba da koristi isti hashing/verifying standard, da bi ponašanje bilo konzistentno kroz ceo projekat.

To znači:

1. ista hash biblioteka,
2. isti algoritam,
3. ista logika validacije tipova i grešaka.

---

## 8) Status kodovi i semantika

Praktičan i čist set:

1. `200` za uspešan `GET /users/me`.
2. `204` za uspešan `PUT /users/password` bez body-ja.
3. `401` kada auth nije validan.
4. `400` ili `401` kada je stara lozinka pogrešna (odaberi i drži dosledno).

U tvom auth toku trenutno je dominantan obrazac `401` za auth neuspehe.

---

## 9) Šta obavezno treba uraditi u main.py

Nakon implementacije users routera:

1. importuj users modul,
2. dodaj `app.include_router(users.router)`.

Bez toga Swagger i API neće prikazati nove rute.

---

## 10) Test scenariji koje treba proći

### Scenario A - get_user bez tokena

1. Poziv bez Authorization header-a.
2. Očekuj `401`.

### Scenario B - get_user sa tokenom

1. Login.
2. Poziv `GET /users/me`.
3. Očekuj tačne podatke current user-a.
4. Potvrdi da nema `hashed_password` u response-u.

### Scenario C - change_password uspeh

1. Pošalji tačan `current_password`.
2. Pošalji validan `new_password`.
3. Očekuj uspeh.
4. Stari password više ne radi na `/auth/token`.
5. Novi password radi.

### Scenario D - change_password pogrešan current_password

1. Pošalji netačnu staru lozinku.
2. Očekuj grešku.

---

## 11) Najčešće greške u ovom rešenju

1. Vraćanje `hashed_password` u `get_user` odgovoru.
2. Upis plaintext nove lozinke umesto hash-a.
3. Preskočena provera stare lozinke.
4. Zaboravljen `db.commit()`.
5. Users router implementiran, ali nije uključen u `main.py`.

---

## 12) Kratak zaključak

Ovo rešenje uvodi "self-service user management" sloj:

1. korisnik vidi svoj profil,
2. korisnik bezbedno menja lozinku,
3. endpointi su oslonjeni na postojeći JWT auth tok.

Time dobijaš kompletniji auth modul i dobar temelj za sledeće korake (admin pravila i kasniji SQLAlchemy 2.0 refaktor).
