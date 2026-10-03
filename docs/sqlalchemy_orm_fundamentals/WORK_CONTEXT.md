# Kontekst za nastavak rada: SQLAlchemy ORM Fundamentals

Ovaj dokument je prenosivi kontekst za nastavak rada u novom razgovoru. Pošalji ga kada prelazimo na TodoApp ili na drugu oblast kursa. Pošto se stanje repozitorijuma i zavisnosti može promeniti, pre svake izmene ponovo proveri aktuelne fajlove i Git status.

## Cilj i način rada

- Korisnik prati SQLAlchemy Fundamentals, kurs od približno 11 sati, tokom oko dve nedelje zajedničkog rada.
- Cilj je da se SQLAlchemy ORM osnove savladaju pre prelaska na Alembic.
- TodoApp je praktični projekat koji se refaktoriše ka SQLAlchemy 2.0; korisnik će prilagoditi TodoApp kada kurs uvede API-je ili obrasce koje treba usvojiti.
- Za svaku poslatu lekciju koristi njen transkript i pripadajući `source_code` kao primarni izvor. Sačuvaj vernost transkriptu; dodatna objašnjenja, savremeni kontekst i razlike u odnosu na SQLAlchemy 2.0 označi kao dodatke.
- Priprema teorije je na srpskom jeziku, latinicom, uz pravilnu upotrebu č, ć, š, đ i ž.
- Piši u postojeći `.md` šablon odgovarajuće oblasti. Pre rada proveri tačan naziv fajla i trenutni sadržaj, jer nazivi i stanje mogu da se promene.
- Analiziraj primere pre objašnjavanja. Ako se primer iz transkripta, ERD-a i source koda ne slaže, označi razliku umesto da je prećutno ispravljaš.

## Jedno virtuelno okruženje

Korisnik izričito želi **jedan postojeći `.venv` u korenu repozitorijuma** za portfolio, TodoApp i SQLAlchemy kurs, kad god je to moguće.

- Ne predlaži niti kreiraj poseban `.venv` u `docs/`, `TodoApp/`, `Models/` ili pojedinačnoj oblasti bez konkretne nekompatibilnosti i dogovora sa korisnikom.
- Ne briši niti rekreiraj postojeći root `.venv`.
- Usklađuj zavisnosti u postojećem okruženju i prilagođavaj TodoApp, umesto da razdvajaš projekte u više okruženja.
- Nemoj pokretati `pip freeze` nad celim okruženjem da bi zamenio requirements fajlove; to može uneti zavisnosti nepovezanih projekata.
- Pre instalacije proveri aktuelne requirements fajlove, verzije u `.venv`-u i `pip check`. Nakon izmene ponovi proveru zavisnosti i ciljane testove.

### Poslednje provereno stanje zavisnosti

Na dan 2026-10-03 usklađeni su:

- [root `requirements.txt`](../../requirements.txt)
- [`fast-api-course-my-work/requirements.txt`](../../fast-api-course-my-work/requirements.txt)

Oba pin-uju SQLAlchemy `2.0.38`. Kursni primeri u prvoj oblasti i projektu za generisanje tabela takođe zahtevaju SQLAlchemy `2.0.38`.

Poslednje proverene verzije u root `.venv`-u bile su SQLAlchemy `2.0.38`, psycopg v3 `3.2.1`, psycopg2 `2.9.10` i `typing_extensions` `4.12.2`; `pip check` je prošao. Ovo je istorijski snapshot, ne pretpostavljaj da je i dalje aktuelan bez provere.

`psycopg` v3 i `psycopg2-binary` mogu koegzistirati. Kursni `db.py` koristi `postgresql://`, koji podrazumevano bira psycopg2; portfolio može koristiti psycopg v3 uz odgovarajući URL driver. Kursni `requirement.txt` fajlovi predstavljaju lokalne izvore/lekcije; nemoj instalirati svaki naslepo ako bi pin-ovi odstupali od zajedničkog okruženja. Uskladi ih sa root requirements-om kada je potrebno.

TodoApp koristi FastAPI, SQLAlchemy, SQLite, JWT i autentifikacione zavisnosti. Njegovi modeli koriste SQLAlchemy 2.0 `Mapped` / `mapped_column`; postojeći `Session.query()` API i dalje je podržan u SQLAlchemy 2.0, mada će kurs postepeno preći na savremeni `select()` stil.

## Razlika između `.venv` i `.vscode`

`.venv` je Python okruženje; `.vscode` sadrži podešavanja editora. Ugnježdeni `.vscode/settings.json` fajlovi uz kursne primere nisu dodatna okruženja i ne treba ih brisati zbog odluke o jednom `.venv`-u. Oni važe kada se odgovarajući folder otvori kao workspace. Repozitorijum ignoriše `.vscode/` i `.venv/` u Git-u.

## Bezbednost baza i destruktivnih skripti

- Jedan `.venv` ne znači jednu bazu podataka. Python okruženje je zajedničko, ali TodoApp i kursni primeri treba da koriste odvojene baze.
- TodoApp database konfiguracija koristi SQLite (`todosapp.db`). Kursna oblast za generisanje tabela koristi PostgreSQL bazu `inventory`.
- Kursni `reset_db.py` poziva `Base.metadata.drop_all()` pa zatim `create_all()`. `1_migration.py` poziva reset skriptu. To briše tabele koje pripadaju toj metadata konfiguraciji; ne pokreći ih dok ne proveriš connection string i ciljnu bazu.
- Kursni `docker-compose.yml` koristi fiksni container name `postgres_db`, port `5432` i `postgres:latest`; proveri da ne postoji konflikt sa već pokrenutim PostgreSQL servisom.
- TodoApp smoke test treba da koristi privremenu SQLite bazu ili eksplicitni dependency override, ne produkcione ili korisničke podatke.

## Git i postojeće izmene

- Korisnik radi na grani koja nije `main` i ima sačuvan backup. To omogućava kontrolisano testiranje dependency promena, ali nije dozvola za automatsko vraćanje ili odbacivanje fajlova.
- Pre izmene proveri `git status` i pročitaj trenutni sadržaj svakog fajla koji diraš.
- Ne prepisuj i ne odbacuj korisničke izmene. Na poslednjoj proveri postojale su izmene u `fast-api-course-my-work/TodoApp/db/base.py` i `fast-api-course-my-work/teorija_po_danima/dan_13_refactor_sqlalchemy_2_0.md`; proveri ponovo pre rada, jer se status menja.
- Ne radi commit niti stage-uj dodatne fajlove osim ako korisnik to zatraži ili je staging nužan za dogovoreni zadatak.

## Poslednja validacija TodoApp-a

Na dan 2026-10-03, nakon prelaska na SQLAlchemy 2.0.38:

- `pip check` je prošao bez neusaglašenih zavisnosti.
- Postojeći portfolio testovi: 8 prošli; prikazana su dva FastAPI `on_event` deprecation upozorenja.
- TodoApp smoke test je prošao nad privremenom SQLite bazom: aplikacija se pokrenula, ruta bez tokena vratila je 401, registracija i login su uspeli, JWT je dekodiran, a autorizovani korisnik je kreirao i izlistao todo.
- PostgreSQL/Docker integracioni test nije pokrenut.

Ove rezultate ponovi kada se promene zavisnosti ili TodoApp kod; nemoj ih predstavljati kao trenutnu validaciju bez novog pokretanja.

## Checklist pri prelasku na drugu oblast

1. Pročitaj transkript i tačan `.md` šablon te oblasti.
2. Pregledaj pripadajući `source_code`, requirements i, ako postoji, ERD ili setup guide.
3. Proveri Git status, root `.venv` verzije i dependency pin-ove; ne pravi novo okruženje po automatizmu.
4. Utvrdi da li kursni primer koristi stariji stil ili ponašanje specifično za određeni DB driver.
5. Napiši teoriju na srpskoj latinici, odvoji sadržaj transkripta od dodataka i popuni samo dogovorene lekcije.
6. Ako se menja kod ili dependency, validiraj prvo izmenjeni sloj, zatim relevantne TodoApp testove/smoke test i `pip check`.
