# Dan 12

## Pitanje 1

PITANJE: Zašto `if not user` i kada `if user is None`

---

## Odgovor 1

ODGOVOR: Kada koristimo `if not user`, proveravamo da li je `user` falsy vrednost (npr. `None`, `False`, `0`, `""`, `[]`). Kada koristimo `if user is None`, proveravamo da li je `user` tačno `None`. U kontekstu SQLAlchemy `first()` metode, preciznije je koristiti `if user is None`, jer `first()` vraća ili ORM objekat ili `None`.

### Detaljno objašnjenje

#### Šta vraća ovaj upit

Kod:

```python
user = db.query(Users).filter(Users.username == username).first()
```

`first()` u ovom slučaju vraća:

1. `Users` objekat ako je korisnik pronađen
2. `None` ako korisnik nije pronađen

Ne vraća prazan string `""`.

To je ključ svega.

---

#### Razlika između `if not user` i `if user is None`

A) `if not user`

Ovo je opšti "falsy" test. Ulazi u blok ako je vrednost falsy, npr:

- `None`
- `False`
- `0`
- `""`
- `[]`

B) `if user is None`

Ovo proverava samo jednu stvar:

- da li je vrednost baš `None` i ništa drugo.

---

#### Šta je bolje ovde nego u varijanti `if not user`

U `auth` upitu (gde proveravamo da li korisnik postoji) je preciznije i čitljivije:

```python
if user is None:
	return False
```

Zašto?

1. Tačno opisuje realan ishod `first()` metode koja vraća ili ORM objekat ili `None`.
2. Ne oslanja se na opšti falsy mehanizam koji bi mogao uključivati i druge vrednosti osim `None`.
3. Jasnije je drugom programeru koji čita kod šta se zapravo proverava.

`if not user` će takođe raditi u ovoj konkretnoj situaciji, ali je manje eksplicitno.

---

#### Tvoje pitanje: "Šta ako je string prazan?"

To je odlična intuitivna provera, ali ovde nije relevantna za promenljivu `user`, jer `user` nije string.

`user` je:

1. ORM objekat klase `Users`, ili
2. `None`

Prazan string može biti relevantan za `username` input, ali ne za rezultat upita `user`.

---

#### Praktično pravilo za tebe

Za ovakve DB lookup situacije koristi:

```python
if user is None:
	return False
```

Za opšte Python check-ove (npr. lista, string, broj) koristi `if not x` kada baš želiš "falsy" ponašanje.

---

#### Dodatna napomena za tvoj auth1.py

U tvom vežbanju imaš tipfeler:

```python
hashed_pasword = getattr(user, "hashed_pasword", None)
```

Treba:

```python
hashed_password = getattr(user, "hashed_password", None)
```

Ako ostane tipfeler, uvek će vraćati `None` i autentifikacija će padati.

---

### Kratak zaključak

1. Oba oblika mogu proći u ovom konkretnom slučaju ali `if user is None` je preciznije i jasnije.
2. Za SQLAlchemy `first()` rezultat je bolji `if user is None`.
3. Ne grešiš u razmišljanju - samo je tip promenljive `user` (objekat ili `None`) razlog zašto prazan string nije tema u tom delu.

---

## Pitanje 2

PITANJE: Kako da izvedem prvi korak Faze 1 (`snapshot` trenutnog stanja: branch + backup baze)?

---

## Odgovor 2

ODGOVOR: Snapshot je urađen i sastoji se iz dve stvari:

1. Napravljena je posebna `git grana` za bezbedan rad pre refaktora (snapshot grana),
2. Napravljena je SQL kopija SQLite baze.

To je pravi "safety net" pre većih promena.

### Šta je konkretno urađeno

#### Kreirana snapshot grana

Kreirana je i aktivirana grana:

```text
snapshot/todoapp-pre-sqlalchemy2-2026-10-02
```

Zašto je ovo važno:

1. Imaš izolovan prostor za refaktor.
2. Ako nešto krene loše, lako se vraćaš na prethodni tok rada.
3. Jasno se vidi od kog trenutka kreće SQLAlchemy 2.0 prelaz.

---

#### Napravljen backup baze kao SQL dump

Detektovana aktivna baza iz `TodoApp/db/database.py`:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

Kreiran je dump fajl:

```text
fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql
```

`dump` fajl sadrži SQL naredbe za rekreiranje baze. Njega možeš koristiti za vraćanje baze u prethodno stanje tako što ćeš izvršiti SQL naredbe iz fajla u SQLite konzoli ili kroz neki SQL alat. Primer:

```bash
sqlite3 fast-api-course-my-work/todosapp.db < fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql
```

`fast-api-course-my-work/todosapp.db` je trenutna aktivna SQLite baza koja se vraća u prethodno stanje korišćenjem SQL dump fajla.

`< >` je mesto gde se izvršava SQL naredba iz dump fajla u SQLite konzoli.

`fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql` je fajl koji sadrži SQL dump baze.

Zašto je ovo važno:

1. Ovo je "čitljiv" backup (SQL naredbe), ne samo binarni fajl.
2. Možeš da vidiš strukturu i podatke.
3. Možeš da vratiš stanje i na čistoj bazi ako zatreba.

---

### Teorija: zašto branch + SQL dump, a ne samo jedno od ta dva

1. Ako uradiš samo branch:

- Time ćeš sačuvati kod (snapshot grana), ali ne i realne podatke baze. (treba ti SQL dump za to)

2. Ako uradiš samo SQL dump:

- Ti ćeš sačuvati podatke, ali bez jasnog koda koji je te podatke koristio.

3. Kada imaš oba:

1. `branch` = `snapshot koda`,
1. `dump` = `snapshot podataka`,
1. zajedno daju tačku povratka koja je pouzdana.

---

### Komande koje treba da znaš (isti obrazac ubuduće)

Snapshot grana (git switch -c <branch_name>) se kreira i aktivira.

```bash
git switch -c snapshot/todoapp-pre-sqlalchemy2-2026-10-02
```

Ako grana već postoji i nema promena koje treba sačuvati, jednostavno se prebaci na tu granu.

```bash
git switch snapshot/todoapp-pre-sqlalchemy2-2026-10-02
```

Razlika između snapshot grane i SQL dump-a je u tome što grana čuva stanje koda, dok SQL dump čuva stanje baze podataka.

`git switch <branch_name>` se koristi za prebacivanje na postojeću granu.
`git switch -c <branch_name>` se koristi za kreiranje i prebacivanje na novu granu.
`git branch` se koristi za prikaz svih grana u repozitorijumu.
`git log` se koristi za prikaz istorije commit-a u trenutnoj grani.
`git branch --show-current` se koristi za prikaz trenutne aktivne grane.

Kreiranje foldera za backup

```bash
mkdir -p fast-api-course-my-work/backups/db_snapshots
```

SQL dump SQLite baze

```bash
sqlite3 fast-api-course-my-work/todosapp.db ".dump" > fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql
```

Brza provera da backup postoji

```bash
ls -lh fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql
```

---

### Kako da razmišljaš o ovom koraku u refaktoru

Pre svake veće faze (`modeli`, `query`-jevi, `migracije`), uradi mini-snapshot:

1. branch checkpoint ako grana još ne postoji (`git switch -c snapshot/<branch_name>`) ili prebacivanje na postojeću granu (`git switch snapshot/<branch_name>`)

2. backup baze (`sqlite3 fast-api-course-my-work/todosapp.db ".dump" > fast-api-course-my-work/backups/db_snapshots/todosapp_snapshot_2026-10-02.sql`),

3. Tek onda menjaj kod. (nakon što su branch i backup baze kreirani)

To značajno smanjuje stres u refaktoru i ubrzava oporavak kad god se pojavi problem.

---

### Git commit/push, povratak na main i virtuelno okruženje

Trenutno si na grani:

```text
snapshot/todoapp-pre-sqlalchemy2-2026-10-02
```

Provera Git stanja pokazala je izmenjene fajlove, novi `dan_12.md` i neupraćeni folder sa SQL backup-om. Zato nemoj naslepo koristiti `git add .`: prvo proveri šta će ući u commit.

#### Da li `venv` mora biti aktivan pri promeni grane?

Ne. Git grana i Python virtuelno okruženje su odvojene stvari:

1. Git grana određuje verziju fajlova u projektu.
2. `venv` određuje Python interpreter i pakete koje terminal koristi.

Sama komanda `git switch` ne zahteva aktivan `venv`. Ako je okruženje već aktivno u istom terminalu, promena grane ga obično neće deaktivirati. Pošto je sada neaktivno, aktiviraj ga kada pokrećeš aplikaciju, testove ili Python komande.

U korenu ovog repozitorijuma postoji `.venv`. Aktiviraj ga iz korena projekta:

```bash
source .venv/bin/activate
```

Prompt obično prikaže `(.venv)`. Možeš proveriti interpreter ovako:

```bash
python --version
which python
```

Ne moraš ponovo da napraviš `.venv` samo zato što si promenio granu. Međutim, ako grana promeni `requirements.txt` ili druge fajlove zavisnosti, postojeći paketi možda neće odgovarati i treba ih proveriti ili instalirati ponovo.

#### Bezbedan redosled za commit snapshot grane

Iz korena repozitorijuma:

1. Proveri aktivnu granu i promene:

```bash
git status --short --branch
```

2. Pregledaj izmene u praćenim fajlovima:

```bash
git diff
```

3. Dodaj samo fajlove čije izmene želiš da sačuvaš. Putanje pronađene u `git status` dodaju se ovako:

```bash
git add putanja/do/fajla
```

Možeš dodati više željenih putanja istoj komandi. Nemoj dodavati niti push-ovati SQL dump ako sadrži stvarne korisničke ili druge privatne podatke; čuvaj ga lokalno ili na privatnom, zaštićenom mestu.

4. Proveri šta je staged pre commita:

```bash
git status --short
git diff --cached --stat
git diff --cached
```

5. Ako su samo željene promene staged, napravi commit:

```bash
git commit -m "Save TodoApp state before SQLAlchemy 2.0 refactor"
```

6. Push snapshot granu na remote. Ova komanda pretpostavlja da se remote zove `origin`:

```bash
git push -u origin snapshot/todoapp-pre-sqlalchemy2-2026-10-02
```

Ako `origin` ne postoji, proveri remote nazive komandom `git remote -v` i koristi odgovarajući naziv.

#### Povratak na main i početak refaktora

Posle uspešnog commita, vrati se na main:

```bash
git switch main
```

Ako koristiš remote, ažuriraj main:

```bash
git pull --ff-only origin main
```

Preporučujem da ne radiš refaktor direktno na `main`. Napravi zasebnu radnu granu iz ažurnog `main`-a:

```bash
git switch -c refactor/sqlalchemy-2.0-todoapp
```

Tako `main` ostaje stabilna, snapshot grana čuva prethodno stanje, a SQLAlchemy 2.0 izmene su izolovane u svojoj grani.

Ako Git odbije promenu grane zbog necommitovanih izmena, nemoj koristiti `git reset --hard` da ih odbaciš. Prvo pregledaj `git status`, pa commit-uj željene izmene ili ih bezbedno sačuvaj na drugi način.

### Kratak zaključak

Prvi korak Faze 1 je sada uspešno odrađen:

1. `snapshot grana` postoji.
2. `SQL backup baze` postoji.
3. `venv` nije potreban za Git komande, ali je potreban za pokretanje aplikacije i testova.
4. Nakon što sačuvaš željene izmene, možeš se vratiti na `main` i napraviti posebnu refactor granu za Fazu 2.

---
