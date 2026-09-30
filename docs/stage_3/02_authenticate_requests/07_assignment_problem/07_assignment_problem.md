# Oblast 03 - Authenticate Requests

## Lekcija 07 - Assignment: Users ruta, get_user i change_password

Ova lekcija je assignment checkpoint: cilj je da samostalno spojiš sve do sada naučeno iz autentifikacije i ownership rada.

Transcript je kratak, ali suština je veoma važna jer uvodi "my account" funkcionalnost.

---

## 1) Šta assignment traži

Potrebno je:

1. Kreirati novu `users` rutu.
2. Dodati endpoint `get_user`:
   - vraća podatke trenutno ulogovanog korisnika.
3. Dodati endpoint `change_password`:
   - menja lozinku trenutno ulogovanom korisniku.

---

## 2) Usklađeno stanje tvog trenutnog projekta

Prema trenutnom kodu:

1. `TodoApp/api/routes/users.py` postoji, ali je prazan.
2. `main.py` trenutno uključuje samo `auth.router` i `todos.router`.
3. `get_current_user` već postoji u `core/security.py` i vraća validan `Users` ORM objekat.
4. Hashing/verifikacija lozinke postoje u `auth.py` kroz `bcrypt_context`.

To znači da je baza za assignment spremna, a treba dopuniti users sloj i uključiti ga u app.

---

## 3) Predlog strukture users routera

Konceptualno:

1. `prefix="/users"`
2. `tags=["users"]`
3. dependency na `get_current_user`

Predložene rute:

1. `GET /users/me` ili `GET /users/` za current user podatke
2. `PUT /users/password` za promenu lozinke

Napomena:

`/users/me` je često čitljivije od `/users/` jer jasno govori da je endpoint vezan za trenutno ulogovanog korisnika.

---

## 4) Endpoint 1: get_user (trenutni korisnik)

Cilj endpointa:

1. Ne traži `user_id` iz URL-a.
2. Uzimа korisnika iz tokena kroz dependency.
3. Vraća bezbedan response model bez `hashed_password`.

Šta vraća:

1. `id`
2. `email`
3. `username`
4. `first_name`
5. `last_name`
6. `is_active`
7. `role`

Praktično, tvoj postojeći `UserResponse` schema je već dobar kandidat.

---

## 5) Endpoint 2: change_password

Cilj endpointa:

1. Korisnik menja sopstvenu lozinku.
2. Mora da pošalje trenutnu (old) lozinku.
3. Mora da pošalje novu (new) lozinku.
4. Server verifikuje staru lozinku pre promene.
5. Nova lozinka se hash-uje pre upisa u bazu.

Preporučen request model:

1. `current_password`
2. `new_password`

Preporučene validacije:

1. `new_password` minimalna dužina.
2. `new_password` ne sme biti ista kao `current_password`.

---

## 6) Security tok za change_password

Korak po korak:

1. `get_current_user` potvrdi identitet preko JWT-a.
2. U bazi se uzima korisnik tog identiteta.
3. `bcrypt_context.verify(current_password, user.hashed_password)` proveri staru lozinku.
4. Ako provera padne, vrati grešku (npr. `401` ili `400`, po dogovoru projekta).
5. Ako prođe, izračunaj hash nove lozinke.
6. Upiši hash u `user.hashed_password`.
7. `db.commit()` i po potrebi `db.refresh(user)`.

Važno:

Nikada ne čuvaj niti vraćaj plaintext lozinku.

---

## 7) Status kodovi i semantika

Predlog:

1. `200` za uspešno čitanje current user podataka.
2. `204` ili `200` za uspešnu promenu lozinke.
3. `401` ako korisnik nije autentifikovan.
4. `400` za loše unete password podatke (npr. pogrešna stara lozinka).

Ovo možeš uskladiti sa stilom koji već koristiš u `auth.py` i `todos.py`.

---

## 8) Šta obavezno treba uključiti u main.py

Nakon kreiranja users routera, moraš ga registrovati:

1. import users router modula
2. `app.include_router(users.router)`

Bez ovoga endpointi postoje u fajlu, ali nisu javno dostupni u API-ju.

---

## 9) Veza sa dosadašnjim lekcijama

Ovaj assignment je prirodan nastavak:

1. Auth već ume da prijavi korisnika i izda JWT.
2. Security već ume da iz JWT-a vrati current user.
3. Todo rute već koriste ownership.
4. Sada users ruta dodaje "self-service" profil i password management.

Time zatvaraš krug osnovne korisničke funkcionalnosti pre admin i naprednijih dozvola.

---

## 10) Test scenariji koje treba proći

### Scenario A - get_user bez tokena

1. Pozovi users endpoint bez Authorization header-a.
2. Očekuj `401`.

### Scenario B - get_user sa validnim tokenom

1. Login korisnika.
2. Pozovi get_user endpoint.
3. Očekuj tačne podatke tog korisnika.

### Scenario C - change_password pogrešna stara lozinka

1. Pošalji netačan `current_password`.
2. Očekuj odbijanje.

### Scenario D - change_password uspeh

1. Pošalji tačan `current_password` i validan `new_password`.
2. Očekuj uspeh.
3. Proveri da stara lozinka više ne radi.
4. Proveri da nova lozinka radi pri `/auth/token` login-u.

---

## 11) Najčešće greške

1. Vraćanje `hashed_password` u response-u.
2. Upis plaintext lozinke umesto hash-a.
3. Zaboravljen `db.commit()` posle promene lozinke.
4. Korišćenje URL `user_id` umesto current user dependency-ja.
5. Users router nije uključen u `main.py`.

---

## 12) Kratak zaključak

Iako je transcript kratak, assignment je važan jer povezuje:

1. autentifikaciju,
2. current user dependency,
3. bezbedno rukovanje lozinkama,
4. API dizajn za "profil trenutno ulogovanog korisnika".

Ova lekcija je odličan most ka sledećem videu sa rešenjem i ka stabilnom prelazu na narednu oblast.
