# Oblast 2: Generisanje tabela iz modela

## Uvod u oblast

U prvoj oblasti napravili smo SQLAlchemy modele koji opisuju tabele i njihove veze. Sada prelazimo sa definisanja modela na njihovo povezivanje sa stvarnom relacionom bazom: PostgreSQL-om.

Model je Python opis strukture podataka. Da bi aplikacija mogla da radi sa PostgreSQL bazom, potrebni su joj baza koja je pokrenuta, SQLAlchemy engine koji zna kako da se poveže sa njom, ORM sesije za rad sa podacima i postupak kojim se definicije modela pretvaraju u tabele u bazi.

Ova oblast uvodi te osnovne korake kroz pet lekcija. Fokus je na razumevanju toka od konfiguracije baze do tabela, ne na iscrpnom pokrivanju svih mogućnosti PostgreSQL-a ili SQLAlchemy-ja.

## Šta ćemo obraditi

1. **Uvod u oblast**: kako se nova faza nadovezuje na modele iz prve oblasti i šta ćemo izgraditi.
2. **PostgreSQL i Docker**: pokretanje baze u kontejneru i upoznavanje sa alatima za njen pregled i upravljanje, uključujući pgAdmin i DataGrip.
3. **SQLAlchemy engine**: kreiranje engine-a koji predstavlja aplikacionu vezu prema bazi i koristi konfigurisan URL i drajver.
4. **ORM sesije**: otvaranje, korišćenje i zatvaranje sesije, kao i osnovna odgovornost za commit i rollback.
5. **Kreiranje i uklanjanje tabela**: korišćenje modela i metapodataka da se tabele naprave u bazi i razumevanje uklanjanja tabela.

Posle pete lekcije završavamo ovu oblast i pravimo pauzu. Ne širimo se na sledeće kurske teme dok se ne vratimo na početak i ne prođemo svaku lekciju ponovo, praktično, uz poređenje starog `Column` pristupa i SQLAlchemy 2.x tipizovanog `Mapped`/`mapped_column` pristupa.

## Veza sa prethodnom oblasti

Prva oblast se bavila deklaracijom modela, kolonama, relacijama i pravilima integriteta. U ovoj oblasti ti modeli postaju deo stvarne baze. Korisno je zadržati sledeće razlike:

- Klasa modela je Python deklaracija; tabela je objekat koji postoji u DBMS-u.
- `create_engine()` konfiguriše povezivanje, ali sam po sebi ne kreira tabele.
- ORM sesija upravlja operacijama sa ORM objektima; ona nije isto što i engine.
- Kreiranje tabela iz modela je poseban korak i ne treba ga mešati sa migracijama koje menjaju već postojeću šemu.

Ove razlike ćemo razraditi u odgovarajućim lekcijama, pa ih sada koristimo samo kao mapu za naredni deo kursa.

## Alati iz kurskog materijala

Priloženi paket sadrži Docker Compose konfiguraciju za PostgreSQL i pgAdmin, kao i primere za engine, sesije, modele i reset baze. Kurs koristi PostgreSQL; SQLAlchemy komunicira s njim preko odgovarajućeg drajvera.

pgAdmin i DataGrip su klijentski alati za pregled i upravljanje bazom. Oni nisu zamena za PostgreSQL server: aplikacija i dalje komunicira sa DBMS-om, dok GUI alat olakšava pregled objekata i podataka.

Konkretna podešavanja, komande i upozorenja za Docker, URL konekcije i rad nad bazom obrađivaćemo u lekcijama koje su za to namenjene. Nećemo unapred pokretati destruktivne reset skripte iz source paketa.

## Dogovor za rad u ovom repozitorijumu

Ovaj odeljak je naš radni dogovor, a ne sadržaj predavanja:

- Koristimo jedan postojeći `.venv` iz root-a repozitorijuma. Ne pravimo drugo virtuelno okruženje unutar kurskog source paketa i ne instaliramo tamo zasebne zavisnosti.
- Izvorne fajlove kursa čuvamo kao snapshot i ne menjamo ih radi prilagođavanja. Kada je primer napisan starom `Column` sintaksom, objasnićemo ga kao izvorni kurski zapis.
- U sopstvenom praktičnom kodu, kada dođe vreme za ponovno praktično prolaženje, koristićemo SQLAlchemy 2.x tipizovani stil sa `Mapped[...]` i `mapped_column()`. Poređenje sa starim `Column` zapisom biće eksplicitno, korak po korak.
- Sada prolazimo teoriju svih pet lekcija. Tek nakon završetka oblasti vraćamo se od prve lekcije na praktičan rad i poređenje stilova.

## Ishod oblasti

Po završetku ovih pet lekcija treba da možeš da objasniš kako PostgreSQL server, engine, ORM sesija i modeli sarađuju; da prepoznaš gde se nalaze konfiguracija i lifecycle sesije; i da razumeš kako se iz modela prave tabele i zašto postojeću šemu treba menjati kontrolisano.

Ovaj uvod daje mapu puta. Sledeća lekcija počinje podešavanjem PostgreSQL baze u Docker-u.
