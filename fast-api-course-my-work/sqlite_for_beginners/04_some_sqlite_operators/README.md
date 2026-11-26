# Oblast 04 — Neki SQLite operatori

Ova oblast sistematski obrađuje operatore koji su se već pojavljivali u ranijim lekcijama i vežbama: `BETWEEN`, `IN`, `LIKE`, `GLOB` i `LIMIT`. Prođi lekcije redom i upoređuj slične operatore — naročito `LIKE` i `GLOB`, kao i `IN` i `NOT IN`.

## Lekcije

1. [`BETWEEN`](./01_sqlite_BETWEEN_operator.md)
2. [`IN`](./02_sqlite_IN_operator.md)
3. [`LIKE`](./03_sqlite_LIKE_operator.md)
4. [`GLOB`](./04_sqlite_GLOB_operator.md)
5. [`LIMIT` i `OFFSET`](./05_sqlite_LIMIT_clause.md)

## Cilj i prioritet

Posle oblasti treba da možeš da:

- izabereš odgovarajući operator za opseg, skup vrednosti ili tekstualni obrazac;
- objasniš kako granice, `NULL`, kolacija i džokeri utiču na rezultat;
- koristiš `ORDER BY` sa jedinstvenim dodatnim kriterijumom pre nego što ograničiš rezultat ili ga podeliš na stranice;
- validiraš korisničke filtere, veličinu stranice i pomeraj u aplikaciji;
- razlikuješ prenosive SQL obrasce od SQLite specifičnog ponašanja.

Temeljno nauči značenje uslova i logiku `NULL`; ne oslanjaj se samo na to da upit „izgleda kao da radi“. Plan učenja preporučuje da prvenstveno savladaš prenosive SQL veštine, a SQLite posebnosti razumeš dovoljno da znaš kada su važne — pogledaj [plan učenja](../plan_ucenja/sta_je_vazno.md).

## Na šta posebno da obratiš pažnju

### `BETWEEN` — uključive granice i vremenski opsezi

- `BETWEEN` uključuje i donju i gornju granicu. `NOT BETWEEN` ih isključuje iz skupa vrednosti koje vraća.
- Obrnute granice, kao `BETWEEN 10 AND 5`, ne znače da će se redosled automatski ispraviti; za uobičajene numeričke vrednosti neće biti poklapanja.
- Ako je vrednost ili granica `NULL`, uslov je `UNKNOWN`, ne `TRUE`. `NOT BETWEEN` ne pronalazi `NULL`; za to koristi `IS NULL`.
- Tekstualni opseg zavisi od kolacije. Datumi i vreme u SQLite-u nemaju zasebnu storage klasu; za timestampove koristi dosledan format i često poluotvoren opseg `>= početak AND < početak_sledećeg_perioda`, da obuhvatiš ceo dan ili mesec.
- Ne mešaj `BETWEEN`-ov `AND` između granica sa dodatnim `AND` uslovom u `WHERE`.

### `IN` i `NOT IN` — skupovi, podupiti i `NULL`

- `IN` proverava članstvo u listi ili rezultatu podupita; duplikati u listi/podupitu ne dupliraju redove spoljnog upita. Podupit za obično poređenje treba da vrati jednu kolonu.
- `NOT IN` može dati `UNKNOWN` za nepoklapajuću vrednost ako lista ili podupit sadrži `NULL`. Filtriraj `NULL` iz podupita ili razmotri `NOT EXISTS`.
- Ako je leva vrednost `NULL`, poređenje sa nepraznom listom uglavnom je `UNKNOWN`; dodaj zaseban `IS NULL` uslov ako želiš da uključiš takve redove.
- SQLite prihvata praznu listu `IN ()` i ima definisano ponašanje za nju, ali ta sintaksa nije prenosiva na sve baze. U aplikaciji unapred odredi šta prazan spisak filtera treba da znači.

### `LIKE` i `GLOB` — obrasci nisu zamenljivi

- `LIKE` koristi `%` za nula ili više znakova i `_` za tačno jedan znak. `GLOB` koristi `*` i `?`; takođe podržava skupove znakova poput `[a-z]` i `[Mm]`.
- U SQLite-u ugrađeni `LIKE` podrazumevano zanemaruje razliku velikih i malih ASCII slova, ali nije puna Unicode ili lokalizovana pretraga. `GLOB` je podrazumevano osetljiv na velika i mala slova.
- Za doslovne `%` i `_` u `LIKE` obrascu koristi `ESCAPE`. `GLOB` nema `ESCAPE` klauzulu; doslovni `*` ili `?` može se navesti kao `[*]` ili `[?]`.
- `NULL LIKE ...`, `NULL NOT LIKE ...`, `NULL GLOB ...` i `NULL NOT GLOB ...` daju `NULL`, pa ih `WHERE` ne bira kao tačne.
- Vezani SQL parametri štite strukturu upita, ali `%`, `_`, `*`, `?` i skupovi i dalje imaju značenje obrasca. Escapuj ih kada korisnik očekuje doslovnu pretragu.
- `GLOB` je SQLite specifičan. `PRAGMA case_sensitive_like` je zastareo način menjanja `LIKE` ponašanja i ne treba ga uvoditi kao novo rešenje. Za Unicode pretragu ili drugu bazu ponovo proveri kolaciju i ponašanje operatora.
- Običan indeks ponekad može pomoći obrascu sa fiksnim prefiksom, ali obrazac koji počinje džokerom, kao `'%pojam%'` ili `'*pojam'`, uglavnom nije obična pretraga prefiksa. Za veće tabele proveri plan upita i stvarne podatke.

### `LIMIT` i `OFFSET` — predvidivi rezultati i straničenje

- Bez `ORDER BY` ne postoji garantovan redosled. Ako se vrednost sortiranja ponavlja, dodaj jedinstveni tie-breaker, obično primarni ključ.
- `OFFSET 12` preskače 12 redova, pa prvi vraćeni red je 13. u sortiranom nizu. U SQLite obliku `LIMIT offset, count` redosled brojeva je drugačiji; u ovom kursu koristi čitljiviji `LIMIT count OFFSET offset`.
- SQLite `LIMIT 0` vraća nula redova; negativan `LIMIT` može ukloniti gornju granicu, a negativan `OFFSET` se tretira kao nula. Aplikacija treba da validira veličinu stranice i pomeraj, umesto da se oslanja na ove SQLite posebnosti.
- `OFFSET` veći od broja pogodaka vraća prazan rezultat. `LIMIT` ograničava prikaz, ne daje ukupan broj pogodaka — za ukupan broj koristi `COUNT(*)`.
- Ako se podaci menjaju između zahteva, offset straničenje može preskočiti ili ponoviti redove. Za neke velike ili često menjane skupove razmotri keyset straničenje.

## Vežbe i bezbedan način rada

Svih pet SQL skripti nalazi se u [playground/sql/04_some_sqlite_operators/](../playground/sql/04_some_sqlite_operators/). One su samo za čitanje i namenjene su Chinook kopiji, ne bazi FastAPI aplikacije. U SQLite CLI-ju, iz korena repozitorijuma, otvori kopiju u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj jednu skriptu iz SQLite CLI prompta, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/01_sqlite_BETWEEN_operator.sql
```

Sledeće skripte možeš učitati u istoj read-only konekciji jer ne prave niti menjaju tabele i podatke. U SQLTools-u izaberi `ChinookPractice`, proveri da pokazuje na `playground/databases/chinook_practice.db` i pokreći pojedinačne `-- @block` odeljke. `.read` je SQLite CLI meta-komanda, a ne SQL upit.

Očekivani brojevi u komentarima i vodiču odnose se na priloženu Chinook kopiju; razlikovaće se ako su podaci promenjeni. Detaljna objašnjenja, očekivani rezultati i provera razumevanja nalaze se u [danu 08](../pitanja_i_odgovori/dan_08_some_sqlite_operators.md). Oznaka „Dan 08“ obuhvata vežbe iz cele oblasti 04 i ne znači da sav materijal treba završiti za jedan dan. Za opšta pravila rada u Playground-u pogledaj [Playground README](../playground/README.md).

### Proverene vežbe

Svih pet SQL skripti uspešno je izvršeno u read-only režimu nad `chinook_practice.db`. Provereni su i očekivani brojevi pogodaka za primere sa `BETWEEN`, `IN`, `LIKE`, `GLOB` i `LIMIT`; njihove vrednosti važe za trenutnu kopiju baze.

### Prenosivo znanje i SQLite specifičnosti

`BETWEEN`, `IN`, `LIKE`, `LIMIT`, sortiranje i pažljivo rukovanje sa `NULL` predstavljaju korisne SQL obrasce i u drugim bazama. Prazna `IN` lista, `GLOB`, podrazumevana osetljivost na velika i mala slova, ponašanje negativnog `LIMIT`/`OFFSET` i datum/vreme poređenja zavise od SQLite-a ili konkretne baze. Pri promeni DBMS-a ponovo proveri ponašanje, kolacije, sintaksu i straničenje; SQLAlchemy ne uklanja te razlike.

Nazad na [glavni README kursa](../README.md).
