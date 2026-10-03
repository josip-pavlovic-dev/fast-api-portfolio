# Lekcija 01: Uvod u oblast „Defining Database Tables“

## Cilj lekcije

Ova lekcija otvara oblast u kojoj se projektuje struktura baze i definišu SQLAlchemy modeli. Modeli predstavljaju Python opis tabela i njihovih veza. U narednim koracima taj opis će se iskoristiti za pravljenje tabela u relacionoj bazi, a zatim će aplikacija moći da upisuje i čita podatke.

Glavna ideja lekcije je redosled rada:

1. Osmisliti strukturu podataka i odnose između njih.
2. Opisati tu strukturu pomoću SQLAlchemy modela.
3. Na osnovu modela napraviti tabele u izabranom sistemu za upravljanje bazom podataka.
4. Upisivati, menjati, brisati i čitati podatke.

U ovoj prvoj oblasti fokus je na prva dva koraka: razumevanju dizajna i definisanju modela. Pravljenje tabela obrađuje se u sledećoj fazi kursa.

## Šta je SQLAlchemy ORM?

SQLAlchemy je Python alat za rad sa relacionim bazama podataka. Njegov ORM deo (Object Relational Mapper) povezuje Python klase i objekte sa tabelama i redovima u bazi.

U najjednostavnijem primeru:

- Python klasa opisuje tabelu;
- atribut klase opisuje kolonu;
- instanca klase predstavlja jedan zapis;
- veze između modela opisuju kako su podaci povezani.

ORM omogućava da se mnoge operacije izraze Python kodom umesto ručnim sastavljanjem svakog SQL iskaza. I dalje je važno razumeti relacione baze i SQL: ORM generiše SQL i šalje ga bazi, ne uklanja SQL iz sistema.

## Zašto se modeli koriste?

Modeli daju aplikaciji jedan organizovan opis strukture podataka. Kada se pravilno postave, oni mogu da učine kod:

- **čistijim**: definicije tabela nisu pomešane sa poslovnom logikom i HTTP rutama;
- **lakšim za održavanje**: struktura jedne tabele i njene veze pregledno su opisane na jednom mestu;
- **doslednijim**: ključevi, ograničenja i relacije mogu se deklarisati uz model;
- **prirodnijim za Python**: aplikacija može da radi sa objektima i atributima;
- **pogodnijim za razvoj većeg sistema**: modeli se mogu organizovati u module i koristiti kroz više delova aplikacije.

Model sam po sebi ne garantuje bezbednost, skalabilnost niti ispravnost podataka. Za to su i dalje potrebni dobra šema baze, validacija, pravilno upravljanje sesijama i transakcijama, odgovarajuća prava pristupa i pažljivo pisani upiti.

## Model još nije tabela

Važno je razlikovati opis šeme od same šeme u bazi:

- **Model** je Python deklaracija koju aplikacija može da učita.
- **Tabela** je objekat koji postoji u konkretnoj bazi podataka.
- **Kreiranje šeme** je korak kojim se definicije modela primenjuju na bazu.

Samo pisanje klase ne znači da je tabela već napravljena. Kurs zato prvo razvija modele, a zatim obrađuje povezivanje sa bazom i generisanje tabela.

### Terminološka napomena: generisanje tabela i migracije

Transkript sledeći korak opisuje kao korišćenje modela za izgradnju tabela, uz upotrebu reči „migrate“. Preciznije, direktno kreiranje tabela iz metadata modela i upravljanje verzionisanim promenama šeme pomoću alata kao što je Alembic nisu ista stvar. Ovaj kurs prvo obrađuje osnove modela i generisanje tabela; Alembic dolazi kasnije u tvom planu.

## Tok rada kroz kurs

Transkript postavlja tri šire faze:

1. Definisanje modela i strukture baze.
2. Korišćenje modela za kreiranje tabela u izabranom relacionom sistemu za upravljanje bazom.
3. Upiti i interakcija sa podacima.

Praktični primeri u ovoj oblasti oslanjaju se na unapred pripremljen dizajn baze. Na taj način koncepti kao što su tipovi kolona, strani ključevi, veze jedan-prema-više i više-prema-više mogu da se uče u okviru jednog povezanog primera.

## Baza koja se koristi u kursu

Kurs koristi generički dizajn sistema za upravljanje zalihama. Cilj dijagrama nije da bude potpuno razrađen poslovni sistem spreman za produkciju. Njegova svrha je da pruži primere uobičajenih elemenata relacionog modela:

- različitih entiteta i tipova kolona;
- primarnih i stranih ključeva;
- samoreferentnih veza;
- veza jedan-prema-više, jedan-prema-jedan i više-prema-više;
- ograničenja i automatizacije na nivou aplikacije ili baze.

Polaznik može da koristi sopstveni dizajn baze umesto kursnog, ali promene u dijagramu moraju da se odraze i u modelima i kodu koji se nad njima kasnije piše.

## Pojmovi za pamćenje

- **Relaciona baza** organizuje podatke u tabele koje mogu biti povezane ključevima.
- **Model** je Python opis tabele i njenih karakteristika.
- **Šema baze** obuhvata tabele, kolone, ključeve, ograničenja i druge objekte baze.
- **ORM** prevodi između Python objekata i relacionih podataka, kao i između ORM izraza i SQL-a.
- **ERD** je dijagram koji pomaže da se struktura i veze razumeju pre pisanja modela.

## Šta treba da bude jasno nakon lekcije

Možeš svojim rečima da objasniš:

1. Šta SQLAlchemy ORM povezuje.
2. Zašto se modeli definišu pre rada sa zapisima.
3. Zašto model u Python kodu nije isto što i tabela koja već postoji u bazi.
4. Kako se ova oblast uklapa u kasnije kreiranje tabela i upite.
5. Zašto kurs koristi jedan zajednički primer baze, ali dozvoljava i sopstveni dizajn.

## Dodatak: kontekst projekta TodoApp i SQLAlchemy 2.0

Ovaj dodatak dopunjuje transkript i povezuje ga sa tvojim praktičnim ciljem.

TodoApp se refaktoriše ka SQLAlchemy 2.0 pre prelaska na Alembic. Modeli su deo opisa šeme, dok će se kasnije posebno učiti engine, sesije, transakcije, upiti i migracije. Te teme su povezane, ali nisu zamenljive.

U kursnom `source_code/Models/` paketu verzija je fiksirana na SQLAlchemy 2.0.38. Primeri koriste `DeclarativeBase`, ali kolone većinom deklarišu starijim `Column(...)` stilom. Taj stil i dalje može biti validan u SQLAlchemy 2.0, ali savremeni tipizovani declarative stil obično koristi `Mapped[...]` uz `mapped_column(...)`. Dok napredujemo, razlikovaćemo:

- šta konkretna lekcija demonstrira;
- šta je kompatibilno sa SQLAlchemy 2.0;
- koji oblik je preporučljiv za novi, tipizovani kod.

Ovaj dodatak nije zamena za transkript, već orijentir za dalji rad.
