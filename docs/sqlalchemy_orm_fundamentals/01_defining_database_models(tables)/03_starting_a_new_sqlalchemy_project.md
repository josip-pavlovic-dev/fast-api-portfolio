# Lekcija 03: Pokretanje novog SQLAlchemy projekta

## Cilj lekcije

Pre nego što Python skripta može da uvozi SQLAlchemy, potrebno je da projekat ima dostupnu biblioteku i da se zna u kom Python okruženju se kod izvršava. Ova lekcija postavlja osnovni razvojni setup: virtuelno okruženje, instalaciju zavisnosti, `requirements` fajl i Ruff podešavanja za VS Code.

## Šta je virtuelno okruženje?

Virtuelno okruženje je zasebna Python instalaciona lokacija za zavisnosti jednog projekta. Ono omogućava da različiti projekti koriste različite verzije biblioteka bez međusobnog ometanja.

Na primer, jedan projekat može zahtevati SQLAlchemy 2.0.36, a drugi 2.0.38. Ako oba koriste isto globalno okruženje, instalacija jedne verzije može promeniti verziju dostupnu drugom projektu. Virtuelna okruženja izoluju njihove instalirane pakete.

Virtuelno okruženje ne kopira ceo Python interpreter; ono obezbeđuje projektnu lokaciju za pakete i komande koje koriste izabranu Python instalaciju.

## Kreiranje i aktiviranje okruženja

Na macOS-u i Linux-u uobičajeno je da se okruženje napravi komandom `python3 -m venv`, a aktivira skriptom `activate`. Na Windows-u se često koristi `py -m venv`, a aktivacija zavisi od terminala.

Primer za Linux/macOS, kada se komande izvršavaju iz korena repozitorijuma. Prvu komandu pokreni samo ako root `.venv` još ne postoji:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

PowerShell primer za isti cilj:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Kada je okruženje aktivno, terminal obično prikazuje njegovo ime u promptu. To je koristan znak, ali nije konačna potvrda koji se interpreter koristi. Pouzdanije je proveriti `python --version` i putanju aktivnog interpreter-a.

Za izlazak iz aktivnog okruženja koristi:

```bash
deactivate
```

## Instaliranje zavisnosti

Biblioteke za Python projekte najčešće se instaliraju iz Python Package Index-a (PyPI), koristeći `pip`. Instalaciju je najbolje pokrenuti kroz aktivni interpreter:

```bash
python -m pip install SQLAlchemy
```

Oblik `python -m pip` smanjuje rizik da se pozove `pip` povezan sa drugim Python interpreter-om.

Kursni primeri u `source_code/Models/requirement.txt` fiksiraju verziju:

```text
SQLAlchemy==2.0.38
```

U ovom repozitorijumu zavisnosti se instaliraju iz zajedničkog root `requirements.txt`, koji usklađuje FastAPI/TodoApp i SQLAlchemy kurs. Kursni fajlovi `requirement.txt` dokumentuju zavisnosti source-code paketa; pre njihove samostalne instalacije uporedi pin-ove sa zajedničkim fajlom:

```bash
python -m pip install -r requirements.txt
```

Opcija `-r` govori `pip`-u da pročita listu zavisnosti iz fajla.

Verziju možeš proveriti ovako:

```bash
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

## Šta radi `pip freeze`?

`pip freeze` ispisuje pakete instalirane u trenutno aktivnom okruženju u formatu koji `pip` može ponovo da instalira. Preusmeravanje izlaza u fajl, na primer `pip freeze > requirements.txt`, čuva snimak zavisnosti tog okruženja.

Ovo je korisno kada je okruženje čisto i predstavlja tačno projekat koji želiš da reprodukuješ. Ako okruženje sadrži biblioteke od više nepovezanih projekata, `pip freeze` može da zabeleži mnogo nepotrebnih paketa. U tom slučaju je bolji eksplicitan requirements fajl koji navodi samo stvarne zavisnosti.

U ovom repozitorijumu kursni fajl se zove `requirement.txt` u jednini i trenutno sadrži samo SQLAlchemy 2.0.38. Prilikom rada koristi postojeći pin; nemoj ga prepisivati izlazom `pip freeze` iz portfolio okruženja.

## Ruff: formatiranje i provera koda

Transkript preporučuje Ruff kao alat za formatiranje, proveru koda i organizovanje import-a. U VS Code-u se Ruff može koristiti preko ekstenzije i projekta-specifičnih podešavanja u `.vscode/settings.json`.

Podešavanja iz `source_code/Models/.vscode/settings.json` pokazuju:

- formatiranje Python koda pri čuvanju fajla;
- Ruff kao podrazumevani formatter za Python;
- organizovanje import-a pri eksplicitnom pokretanju code action-a;
- ruler na 88 karaktera.

Podešavanje `source.fixAll` u tom fajlu je zakomentarisano, dakle nije uključeno. Kada se automatsko popravljanje uključi, formatter ili linter mogu ukloniti neiskorišćene importe i primeniti druga pravila. Zato treba razumeti šta se menja pri čuvanju, a ne pretpostaviti da formatiranje menja samo razmake.

Ruff ekstenzija za VS Code i Python paket Ruff nisu isto: ekstenzija integriše alat u editor, dok Python paket omogućava pozivanje alata iz okruženja ili CI sistema. Kursni `requirement.txt` ne navodi Ruff, pa se ne može zaključiti da je Ruff instaliran u tom virtuelnom okruženju samo na osnovu ovog fajla.

## Rad sa kursnim primerima

Transkript navodi da preuzeti primeri ne sadrže virtuelno okruženje. To je očekivano: okruženje sadrži lokalne izvršne fajlove i pakete specifične za računar, pa se obično ne deli u repozitorijumu. Umesto njega projekat deli spisak zavisnosti; svako lokalno napravi svoje okruženje i instalira te zavisnosti.

Tipičan tok rada je:

1. Izaberi odgovarajući Python interpreter.
2. Kreiraj ili aktiviraj okruženje projekta.
3. Instaliraj pakete iz njegovog requirements fajla.
4. Proveri verziju biblioteke.
5. Otvori kod u editoru i poveži ga sa istim interpreter-om.
6. Tek tada pokreni Python skriptu.

Ako VS Code koristi drugi interpreter od terminala, paket može biti instaliran, a da editor i dalje prijavljuje da ne može da ga pronađe. Zato interpreter izabran u VS Code-u treba da bude isti kao interpreter okruženja u kom se instaliraju zavisnosti.

## Dodatak: preporuka za ovaj repozitorijum

### Dogovor za ovaj repozitorijum: jedan root `.venv`

Koristimo postojeći `.venv` u korenu `fast-api-portfolio` repozitorijuma za portfolio, TodoApp i SQLAlchemy kurs. Ne pravimo zasebno okruženje unutar `docs/`, `TodoApp/`, `Models/` ili pojedinačnih source-code foldera. TodoApp se prilagođava zajedničkoj verziji SQLAlchemy-ja.

Koren `requirements.txt` i `fast-api-course-my-work/requirements.txt` usklađeni su na SQLAlchemy 2.0.38. Kursni source-code zahtevi mogu imati dodatne pakete, pa ih prvo uporedi sa zajedničkim fajlom umesto da ih naslepo instaliraš.

Portfolio/TodoApp koriste psycopg v3, a kursni primer sa `postgresql://` podrazumevano koristi psycopg2. Oba drivera su instalirana u istom `.venv`-u; jedan ne zahteva zasebno Python okruženje.

Raspored okruženja:

```text
fast-api-portfolio/
├── .venv/                              # jedino zajedničko Python okruženje
├── requirements.txt                    # usklađeni dependency pin-ovi
├── fast-api-course-my-work/
│   └── TodoApp/
└── docs/
	└── sqlalchemy_orm_fundamentals/
```

Ako je `.venv` već napravljen, aktiviraj ga iz korena repozitorijuma i instaliraj usklađene zavisnosti:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Očekivani ispis verzije je `2.0.38`. U VS Code-u izaberi interpreter iz root `.venv`-a. Nemoj pokretati `python3 -m venv .venv` ako okruženje već postoji.

Repozitorijum već ignoriše `.venv/`, tako da virtuelno okruženje ne bi trebalo da se pojavi među fajlovima za commit. Zavisnosti koje treba deliti ostaju u `requirement.txt`.

### Gde važi `.vscode/settings.json`?

VS Code primenjuje workspace podešavanja iz `.vscode/settings.json` na korenu otvorenog workspace-a. Pošto se kursni fajl nalazi u `source_code/Models/.vscode/settings.json`, ta podešavanja važe kada se `Models/` otvori kao workspace folder; ne treba pretpostaviti da će se automatski primeniti dok je otvoren koren celog `fast-api-portfolio` repozitorijuma. Bez obzira na Ruff podešavanja, interpreter treba da bude root `.venv`.

## Rezime

- U ovom repozitorijumu portfolio, TodoApp i kurs koriste jedan postojeći root `.venv`.
- Root i TodoApp requirements usklađeni su na SQLAlchemy 2.0.38.
- Kursni requirements uporedi sa zajedničkim pin-ovima pre instaliranja; ne pravi novi `.venv` po oblasti.
- Proveri aktivnu verziju nakon instalacije i koristi isti interpreter u terminalu i VS Code-u.
- Poveži VS Code sa istim interpreter-om koji koristi terminal.
- Ruff podešavanja ugnježdena u `Models/.vscode/` važe kada se taj folder otvori kao workspace.
