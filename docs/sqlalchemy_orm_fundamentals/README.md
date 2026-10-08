# SQLAlchemy ORM Fundamentals

## O kursu

Ovaj kurs pruža praktičan i teorijski uvod u SQLAlchemy ORM i rad sa relacionim bazama podataka iz Pythona. Kroz definisanje modela, pravljenje tabela, upravljanje podacima i sastavljanje upita, cilj je da se razume kako ORM povezuje Python objekte sa tabelama i kako se SQLAlchemy koristi u stvarnim aplikacijama.

Kurs je namenjen Python programerima, backend inženjerima, analitičarima podataka i svima koji žele da savladaju ORM pristup radu sa bazama.

## Ciljevi učenja

Po završetku kursa trebalo bi da možeš da:

- objasniš svrhu ORM-a i prednosti SQLAlchemy-ja;
- podesiš Python razvojno okruženje, VS Code i virtuelno okruženje;
- definišeš modele, kolone, tipove podataka, ključeve, ograničenja i veze;
- generišeš šemu baze iz ORM modela;
- upravljaš sesijama, transakcijama i promenama ORM objekata;
- umećeš, menjaš i brišeš podatke;
- pišeš i kombinuješ upite, filtere i spojeve tabela;
- grupišeš podatke i računaš agregate;
- prepoznaš SQL koji SQLAlchemy generiše i proceniš kako upit utiče na bazu.

## Sadržaj kursa

### 1. Uvod

- Pregled sadržaja, ciljeva i ishoda kursa.
- Šta je ORM i kakav problem rešava.
- Prednosti i ograničenja korišćenja SQLAlchemy ORM-a.

### 2. Priprema razvojnog okruženja

- Instalacija i podešavanje Pythona na Windows-u i macOS-u.
- Podešavanje VS Code-a za SQLAlchemy razvoj.
- Kreiranje i upravljanje virtuelnim okruženjima.
- Instalacija i upravljanje projektnim zavisnostima.

### 3. Osnove: definisanje modela i tabela

- Razumevanje strukture baze kroz ERD dijagram.
- Početna struktura SQLAlchemy projekta i deklarativna baza.
- Definisanje tabela pomoću ORM modela.
- Tipovi kolona, uključujući datumske i vremenske vrednosti.
- Obavezne i nullable kolone, podrazumevane vrednosti i jedinstvenost.
- Primarni i strani ključevi.
- Samoreferentne veze i ponašanje stranih ključeva pri brisanju.
- Veze jedan-prema-jedan i više-prema-više.
- Ograničenja na nivou baze podataka.
- Event listeners i automatizacija događaja u bazi.
- Python tipizacija modela i njena korist za čitljivost i održavanje.

Materijali za ovu oblast nalaze se u [01_defining_database_models(tables)](<01_defining_database_models(tables)/>).

Dopunski vodič za čitanje ORM veza nalazi se u
[cheatsheet-u za `relationship()` i `back_populates`](cheatsheets/relationship_i_back_populates.md).

### 4. Osnove: generisanje tabela iz modela

- Pokretanje PostgreSQL-a pomoću Docker-a.
- Kreiranje SQLAlchemy engine-a.
- Kreiranje i upravljanje ORM sesijama.
- Generisanje tabela na osnovu modela.
- Brisanje i ponovno kreiranje tabela tokom razvoja.

Materijali za ovu oblast nalaze se u [02_generating_tables_from_models](02_generating_tables_from_models/).

### 5. Osnove: unos, izmena i brisanje podataka

- Unos zapisa pomoću `add()` i potvrđivanje pomoću `commit()`.
- Višestruki unos kroz `add_all()` i bulk API-je.
- Izmena postojećih zapisa i praćenje promena ORM objekata.
- Rad sa stranim ključevima i ORM vezama.
- Uloga `flush()` u toku transakcije.
- Brisanje zapisa i postupanje sa povezanim zapisima.
- Zaštita osetljivih polja enkripcijom.
- Podrazumevane vrednosti koje postavlja server baze.
- Unos i izmena podataka kroz PostgreSQL i DataGrip.

### 6. Osnove: upiti nad bazom

- Popunjavanje baze početnim podacima.
- Dohvatanje zapisa pomoću SELECT upita.
- Filtriranje pomoću WHERE uslova.
- Pregled SQL-a koji SQLAlchemy generiše.
- Korišćenje `first()`, `count()`, `limit()`, `exists()` i `order_by()`.
- Ponovna upotreba upitne logike kroz `@classmethod` u modelima.

### 7. Napredno filtriranje

- Filtriranje metodom `where()`.
- Kombinovanje uslova pomoću AND i OR logike.
- Poređenja i osnovni operatori u upitima.
- Funkcije `like()`, `in_()` i `between()`.
- Uklanjanje duplikata pomoću `distinct()`.
- Sastavljanje kompozitnih upita koji se mogu dalje nadograđivati.

### 8. Spojevi tabela (joins)

- Inner join za relacije definisane stranim ključevima.
- Inner join za veze jedan-prema-jedan i više-prema-više.
- Left join za iste tipove relacija.
- Full outer join.
- Izdvajanje ili isključivanje određenih rezultata iz spojenih skupova.

### 9. Agregacije i grupisanje

- Agregatne funkcije `count()`, `sum()`, `avg()`, `min()` i `max()`.
- Grupisanje rezultata pomoću `group_by()`.
- Filtriranje grupisanih rezultata pomoću `having()`.

## Veza sa TodoApp projektom

Paralelno sa kursom radi se refaktor mini projekta TodoApp sa starijeg SQLAlchemy stila na SQLAlchemy 2.0. Cilj je da se osnove ORM-a razumeju pre prelaska na Alembic i migracije.

Primeri iz kursa mogu koristiti drugačiju verziju ili stil API-ja. Tokom izrade beleški obratićemo pažnju na razliku između prikazanog koda i preporučenog SQLAlchemy 2.0 pristupa, uz objašnjenje kada je neka razlika važna za TodoApp.

## Napomena o materijalima

Teorijski materijali se pripremaju na srpskom jeziku, latinicom, uz pažljivu upotrebu slova č, ć, š, đ i ž. Osnovna objašnjenja prate sadržaj transkripta; dopunska objašnjenja i savremeni kontekst biće jasno izdvojeni kada prevazilaze ono što je obrađeno u lekciji.
