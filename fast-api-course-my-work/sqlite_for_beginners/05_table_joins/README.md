# Oblast 05 — SQLite spajanje tabela

Ova oblast obrađuje načine kombinovanja redova iz tabela. Naučićeš kako izbor vrste spoja određuje koji redovi ulaze u rezultat, kako uslov `ON` uspostavlja poklapanje i zašto broj redova posle spajanja može biti veći od broja redova bilo koje pojedinačne tabele.

## Lekcije

1. [`LEFT JOIN`](./01_sqlite_LEFT_join.md)
2. [`INNER JOIN`](./02_sqlite_INNER_join.md)
3. [`CROSS JOIN`](./03_sqlite_CROSS_join.md)
4. [`SELF JOIN`](./04_sqlite_SELF_join.md)

## Cilj i prioritet

Posle oblasti treba da možeš da:

- izabereš `LEFT JOIN` kada moraš sačuvati svaki red leve tabele, ili `INNER JOIN` kada želiš samo poklapanja;
- povežeš stvarni primarni i strani ključ u `ON` uslovu i objasniš kardinalnost veze;
- razlikuješ nepoklopljeni red od poklopljenog reda čija je opciona kolona `NULL`;
- pronađeš redove bez poklapanja bez slučajnog odbacivanja rezultata spoljnog spoja;
- proceniš broj redova `CROSS JOIN` proizvoda pre izvršavanja;
- koristiš istu tabelu u više uloga pomoću `SELF JOIN`-a i jasnih alias-a;
- prepoznaš kako dupliranje redova utiče na `COUNT`, `SUM` i druge naknadne agregate;
- dodaš `ORDER BY` sa dovoljnim kriterijumima kada je redosled rezultata važan.

Pre pisanja upita odredi šta treba da predstavlja jedan rezultatni red. Spoj može vratiti više redova za jedan red iz početne tabele; to je često ispravno ponašanje veze jedan-prema-više, a ne greška ili dupliranje koje treba sakriti pomoću `DISTINCT`.

## Provereni rezultati u Chinook kopiji

Brojevi su provereni nad trenutnom `chinook_practice.db` kopijom. Razlikovaće se ako se podaci promene, ali značenje join operatora ostaje isto.

| Provera                                                                        | Očekivani rezultat |
| ------------------------------------------------------------------------------ | -----------------: |
| `artists LEFT JOIN albums` — redovi / različiti izvođači / povezani albumi     |    418 / 275 / 347 |
| Izvođači bez albuma, pronađeni preko `IS NULL`                                 |                 71 |
| Filter `al.Title LIKE 'A%'` u `ON` — redovi / izvođači / NULL-prošireni redovi |    282 / 275 / 250 |
| Isti filter u `WHERE` — redovi / izvođači                                      |            32 / 25 |
| `tracks INNER JOIN albums` — redovi / različite numere / albumi                |  3503 / 3503 / 347 |
| Numere bez albuma u trenutnoj kopiji                                           |                  0 |
| Numere sa albuma `Greatest Hits`                                               |                 57 |
| `INNER JOIN` rezultati za naslove albuma koji počinju sa `A`                   |                369 |
| `albums CROSS JOIN media_types` — redovi u tabelama / kombinacije              |     347 × 5 = 1735 |
| `employees` / parovi zaposleni–rukovodilac / zaposleni bez rukovodioca         |          8 / 7 / 1 |

Ovi brojevi potvrđuju konkretne upite, ali nisu pravila SQL-a. Na primer, `INNER JOIN` nad `tracks` i `albums` vraća isti broj redova kao `tracks` samo zato što u ovoj kopiji svaka numera ima poklapanje.

## Na šta posebno da obratiš pažnju

### `LEFT JOIN` i `INNER JOIN` ne čuvaju iste redove

- `INNER JOIN` vraća kombinacije redova koje zadovoljavaju `ON`. Redovi bez poklapanja se izostavljaju.
- `LEFT JOIN` vraća sve redove leve tabele. Kada nema desnog poklapanja, izabrane kolone desne strane se popunjavaju sa `NULL`.
- `LEFT OUTER JOIN` je puniji naziv za `LEFT JOIN`.
- `LEFT JOIN` nije simetričan: tabela navedena pre operatora je leva strana i njeni redovi se čuvaju.
- `JOIN` bez reči `INNER` podrazumeva unutrašnje spajanje. Navedi `INNER JOIN` kada želiš da namera bude jasna.

Izaberi levu tabelu prema tome koji entiteti moraju ostati u rezultatu. Ako zameniš strane u `LEFT JOIN`-u, promenićeš koje redove čuvaš.

### `ON`, `WHERE` i traženje nepoklopljenih redova

- `ON` određuje koje redove se smatraju poklapanjem.
- Kod `LEFT JOIN`-a filter desne tabele u `ON` ograničava poklapanja, ali čuva redove leve tabele i kada nema odgovarajućeg desnog reda.
- Isti filter desne tabele u `WHERE` može ukloniti NULL-proširene redove i time promeniti efekat spoljnog spoja.
- Da bi pronašao redove bez poklapanja, proveri ključ desne strane koji je garantovano nenult kada desni red postoji, najčešće primarni ključ: `WHERE r.Id IS NULL`.
- Za proveru `NULL` koristi `IS NULL` ili `IS NOT NULL`, nikada `= NULL`.

Nemoj proveravati opcionu kolonu desne tabele ako želiš da dokažeš da desni red ne postoji: postojeći red može imati `NULL` baš u toj koloni. Izaberi ključ koji razlikuje stvarni red od NULL-proširenog rezultata.

Kod `INNER JOIN`-a uslov koji ograničava rezultat može često biti izražen kroz `ON` ili `WHERE`. Nemoj tu intuiciju prenositi na `LEFT JOIN`: za spoljni spoj lokacija filtera može promeniti koje redove čuvaš.

### Ključevi, kardinalnost i broj redova

- Poveži kolone koje predstavljaju stvarnu relaciju, obično strani ključ sa primarnim ili jedinstvenim ključem. Isto ime kolone samo po sebi nije dokaz da su kolone povezane.
- Jedan red može imati nula, jedno ili više poklapanja. Više poklapanja daje više rezultatnih redova.
- Više redova sa istim nazivom u rezultatu ne znači nužno duplirane zapise. Na primer, svaki album može ponavljati naslov uz svaku svoju numeru.
- `DISTINCT` menja oblik rezultata uklanjanjem ponovljenih izlaznih vrednosti; ne popravlja pogrešan uslov `ON` niti umnožavanje izazvano neočekivanom kardinalnošću.
- Ako agregiraš posle spajanja, utvrdi šta jedan rezultatni red predstavlja. `COUNT(*)` može brojati parove, a ne jedinstvene objekte.
- U `LEFT JOIN`-u `COUNT(*)` broji i NULL-prošireni red, dok `COUNT(r.Id)` broji samo poklopljene redove ako `r.Id` ne može biti `NULL`.

Poređenje `NULL` join ključeva pomoću `=` ne stvara poklapanje, čak ni kada su oba ključa `NULL`: rezultat poređenja je nepoznat, a ne `TRUE`.

### `CROSS JOIN` — proceni proizvod pre izvršavanja

- `CROSS JOIN` kombinuje svaki red leve tabele sa svakim redom desne tabele; ne traži poklapanje ključeva.
- Za `m` redova i `n` redova rezultat ima `m × n` kombinacija. Ako je jedna tabela prazna, rezultat je prazan.
- Izračunaj očekivanu veličinu pre spajanja velikih tabela. Proizvod može brzo narasti na milione redova i potrošiti mnogo vremena i memorije.
- Sve kombinacije nisu dokaz poslovne veze između zapisa. U primeru albuma i tipova medija, upit pravi sve parove; ne potvrđuje da je svaki album dostupan u svakom tipu.
- Ako želiš samo povezane redove, koristi `INNER JOIN` i smislen uslov `ON`. Ne koristi `CROSS JOIN` kada je uslov povezivanja slučajno izostavljen.
- Kao i kod drugih upita, redosled nije garantovan bez `ORDER BY`.

### `SELF JOIN` — ista tabela, različite uloge

- `SELF JOIN` nije poseban join operator: ista tabela se navodi više puta uz različite alias-e.
- Svaki alias predstavlja zasebnu ulogu. U primeru zaposlenih `e` je zaposleni, a `m` njegov rukovodilac.
- Ako `employees.ReportsTo` upućuje na `employees.EmployeeId`, uslov je `m.EmployeeId = e.ReportsTo`.
- `INNER JOIN` izostavlja zaposlenog čiji je `ReportsTo` `NULL`; `LEFT JOIN` sa `employees AS e` na levoj strani čuva sve zaposlene i daje `NULL` za rukovodioca koji ne postoji.
- Jedan self join prikazuje direktnu vezu na jednom nivou, ne celu hijerarhiju. Za proizvoljan broj nivoa potreban je rekurzivni CTE.
- Uslov spajanja je jasniji u eksplicitnom obliku `JOIN ... ON` nego kada se isti uslov meša sa filtrima u `WHERE`.

### Redosled i prikaz rezultata

- Bez `ORDER BY` ne postoji garantovan redosled rezultata. Ako vrednosti sortiranja mogu da se ponavljaju, dodaj jedinstveni tie-breaker, najčešće primarni ključ.
- Kvalifikuj kolone alias-ima tabela, na primer `e.EmployeeId` i `m.EmployeeId`, naročito kada obe tabele imaju istoimene kolone.
- Alias-uj izlazne kolone kada ista tabela ili isto ime kolone imaju različite uloge, na primer `Manager` i `DirectReport`.
- `LIMIT` ograničava broj prikazanih redova; ne menja pravila poklapanja niti ukupan broj kombinacija.

Temeljno nauči kardinalnost i ulogu `NULL`; nemoj se oslanjati samo na to da rezultat „izgleda kao da radi“. Plan učenja preporučuje da prvenstveno savladaš prenosive SQL veštine, a SQLite posebnosti razumeš dovoljno da znaš kada su važne — pogledaj [plan učenja](../plan_ucenja/sta_je_vazno.md).

## Vežbe i bezbedan način rada

Četiri SQL skripte nalaze se u [playground/sql/05_table_joins/](../playground/sql/05_table_joins/). One su samo za čitanje i namenjene su Chinook kopiji, ne bazi FastAPI aplikacije. U SQLite CLI-ju, iz korena repozitorijuma, otvori kopiju u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj jednu skriptu iz SQLite CLI prompta, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/01_sqlite_LEFT_join.sql
```

U SQLTools-u izaberi `ChinookPractice`, proveri da pokazuje na `playground/databases/chinook_practice.db` i pokreći pojedinačne `-- @block` odeljke. `.read` je SQLite CLI meta-komanda, a ne SQL upit.

### Proverene vežbe

Sve četiri SQL skripte uspešno su izvršene u read-only režimu nad `chinook_practice.db`. Provereni su i očekivani brojevi u tabeli iznad. Oni važe za trenutnu kopiju i razlikovaće se ako se podaci promene.

Detaljna objašnjenja, rešenja vežbi i kratki odgovori nalaze se u [danu 09 — SQLite JOIN](../pitanja_i_odgovori/dan_09_table_joins.md). Oznaka „Dan 09“ obuhvata ceo sadržaj oblasti 05 i ne znači da sav materijal treba završiti za jedan dan. Za opšta pravila rada u Playground-u pogledaj [Playground README](../playground/README.md).

### Prenosivo znanje i SQLite specifičnosti

`INNER JOIN`, `LEFT JOIN`, `CROSS JOIN`, `ON`, `WHERE`, alias-i i pažljivo rukovanje sa `NULL` predstavljaju korisne relacione SQL veštine. Ipak, proveri sintaksu i podršku ciljne baze pri prelasku na drugi DBMS:

- SQLite dozvoljava neke oblike `CROSS JOIN` sa uslovom koje nije potrebno koristiti za uobičajenu nameru; za povezivanje redova jasnije je napisati `INNER JOIN ... ON`.
- Sintaksa spajanja, dostupne vrste spojeva i plan izvršavanja mogu se razlikovati među bazama.
- SQLAlchemy ne uklanja razlike u kardinalnosti, `NULL` semantici ili podršci ciljne baze. ORM upit i dalje treba da izražava ispravan join uslov.

Nazad na [glavni README kursa](../README.md).
