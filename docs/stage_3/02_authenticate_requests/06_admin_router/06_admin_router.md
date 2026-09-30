# Oblast 03 - Authenticate Requests

## Lekcija 06 - Admin router i role-based pristup

Ova lekcija uvodi ideju da postoje endpointi koji nisu dostupni svakom autentifikovanom korisniku, već samo korisniku sa admin ulogom.

To je prvi pravi primer role-based authorization pravila.

---

## 1) Šta je cilj lekcije

Do sada je cilj bio da korisnik pristupa samo svojim Todo zapisima.

U ovoj lekciji cilj se proširuje:

1. običan korisnik i dalje vidi/menja samo svoje zapise,
2. admin korisnik dobija dodatne endpointe za pregled svih Todo zapisa,
3. admin može obrisati i tuđi Todo zapis kada to poslovna pravila dozvoljavaju.

To znači da uvodimo razliku između:

1. user-scoped endpointa (`/todos/...`),
2. admin-scoped endpointa (`/admin/...`).

---

## 2) Usklađeno stanje tvog trenutnog projekta

Prema trenutnom kodu u `TodoApp`:

1. `Users` model ima kolonu `role`.
2. `api/routes/admin.py` postoji, ali je trenutno prazan.
3. `main.py` trenutno uključuje samo `auth.router` i `todos.router`.
4. JWT payload trenutno sadrži `sub`, `username`, `exp` (ne i `role`).
5. `get_current_user` trenutno vraća ORM `Users` objekat iz baze.

Važna posledica:

Admin funkcionalnost iz transkripta je konceptualno sledeći korak, ali u tvom aktivnom kodu još nije uključena.

---

## 3) Kako transcript rešava admin proveru

U transcriptu je ideja:

1. role se dodaje u JWT pri `create_access_token`,
2. role se čita pri decode,
3. admin endpoint proverava da je `user_role == "admin"`,
4. tek tada dozvoljava "super" operacije.

To je validan kursni pristup, ali postoji i još robusnija varijanta (ispod).

---

## 4) Dva moguća pristupa za admin proveru

### Pristup A - role u JWT payload-u

Prednosti:

1. Jednostavno i brzo za kursni primer.
2. Nema dodatnih DB čitanja za role ako je sve u tokenu.

Mane:

1. Ako se role promeni u bazi, stari token može nositi zastarelu role informaciju do isteka.

### Pristup B - role iz baze (preporučeno za održavanje)

Pošto tvoj `get_current_user` već vraća `Users` ORM objekat iz baze, admin proveru možeš raditi direktno nad `current_user.role`.

Prednosti:

1. Uvek čitaš svežu role vrednost.
2. Manji rizik od stale role podataka u tokenu.
3. Lepše se uklapa u tvoj trenutni kod.

Zaključak za tvoj projekat u ovom trenutku:

1. Role claim u tokenu nije obavezan da bi admin provera radila.
2. Dovoljno je da proveriš `current_user.role` posle `get_current_user`.

---

## 5) Predloženi dizajn admin routera (usklađen sa TodoApp)

Konceptualno, admin router treba da bude:

1. `prefix="/admin"`
2. `tags=["admin"]`

Tipične admin rute za ovu fazu:

1. `GET /admin/todos` - vraća sve Todo zapise
2. `DELETE /admin/todos/{todo_id}` - briše Todo po ID-u bez owner filtera, ali samo za admin korisnika

Ključna sigurnosna provera:

1. Ako `current_user.role != "admin"`, vraća se auth/authorization greška.

---

## 6) 401 ili 403 za "nije admin" slučaj

U transcriptu je korišćen `401` za "nije admin".

U REST praksi često je preciznije:

1. `401` kada korisnik nije autentifikovan ili je token nevalidan,
2. `403` kada je korisnik autentifikovan, ali nema dozvolu (npr. nije admin).

Za konzistentnost tvog projekta možeš:

1. zadržati `401` ako pratiš kurs 1:1,
2. ili preći na `403` za čistiju semantiku u kasnijem refaktoru.

---

## 7) Zašto je admin router odvojen od todos routera

Odvajanje je važno zbog čitljivosti i održavanja:

1. `/todos` rute ostaju user-scoped i ownership-orijentisane.
2. `/admin` rute nose globalne privilegije.
3. Lakše je testirati i auditovati privilegovane endpointe.

Time se smanjuje rizik da se admin logika "slučajno" pomeša sa običnim korisničkim tokovima.

---

## 8) Kako se ova lekcija naslanja na prethodne

Do lekcije 05 već imaš:

1. JWT auth,
2. current user dependency,
3. ownership filtere za create/read/update/delete.

Lekcija 06 dodaje:

1. role-based grananje prava pristupa,
2. admin endpointe za globalan pregled i globalan delete.

To je prirodan prelaz iz "resource ownership" ka "permission modelu".

---

## 9) Test scenariji kada implementiraš admin router

### Scenario A - običan korisnik na admin read-all

1. Login kao user role.
2. Pozovi `GET /admin/todos`.
3. Očekuj odbijanje (`401` ili `403`, po dogovoru projekta).

### Scenario B - admin korisnik na admin read-all

1. Login kao admin.
2. Pozovi `GET /admin/todos`.
3. Očekuj sve Todo zapise, uključujući zapise drugih korisnika.

### Scenario C - admin delete tuđeg zapisa

1. Login kao admin.
2. Pozovi `DELETE /admin/todos/{todo_id}` za zapis koji nije adminov.
3. Očekuj uspeh (`204`) ako zapis postoji.

### Scenario D - nepostojeći ID

1. Admin poziva delete za nepostojeći ID.
2. Očekuj `404`.

---

## 10) Najčešće greške u ovoj fazi

1. Admin router nije uključen u `main.py`.
2. Provera role je case-sensitive, a podaci nisu normalizovani (`Admin` vs `admin`).
3. Mešanje ownership filtera i admin filtera bez jasnih pravila.
4. Oslanjanje samo na token role bez razmišljanja o zastarelim tokenima.
5. Nedosledno vraćanje status kodova za "nije admin".

---

## 11) Kratak zaključak lekcije

Lekcija 06 uvodi ključni koncept: nije dovoljno znati ko je korisnik, već i koja ovlašćenja ima.

U tvom projektu ovo je sledeći logičan korak posle ownership CRUD zaštite:

1. postoje user endpointi (`/todos`) koji štite sopstvene podatke,
2. uvode se admin endpointi (`/admin`) za globalne operacije,
3. pristup se kontroliše preko role pravila.

Ovo je odlična priprema za narednu oblast i kasniji refaktor na SQLAlchemy 2.0, jer ćeš ući u refaktor sa jasno definisanim security granicama.
