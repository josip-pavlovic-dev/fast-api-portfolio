# Oblast 06 — SQLite agregatne funkcije

Ova oblast obrađuje agregatne funkcije koje računaju vrednosti iz više redova, kao i klauzule koje formiraju grupe i filtriraju njihove rezultate. Lekcije idu od osnovnih agregata (`AVG`, `COUNT`, `SUM`, `MAX`, `MIN` i `GROUP_CONCAT`) do `GROUP BY` i `HAVING`.

## Lekcije

1. [Uvod u SQLite agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md)
2. [`AVG()`](./02_sqlite_AVG_function.md)
3. [`COUNT()`](./03_sqlite_COUNT_function.md)
4. [`SUM()`](./04_sqlite_SUM_function.md)
5. [`MAX()`](./05_sqlite_MAX_function.md)
6. [`MIN()`](./06_sqlite_MIN_function.md)
7. [`GROUP_CONCAT()`](./07_sqlite_GROUP_CONCAT_function.md)
8. [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md)
9. [`HAVING`](./09_sqlite_HAVING_clause.md)

## Cilj i prioritet

Posle oblasti treba da možeš da:

- izabereš agregat koji odgovara pitanju i razumeš koje vrednosti ulaze u njegov račun;
- razlikuješ `COUNT(*)`, `COUNT(izraz)` i `COUNT(DISTINCT izraz)`;
- objasniš kako `NULL`, nula, duplikati i prazan skup menjaju rezultate;
- grupišeš redove pomoću jednog ili više izraza i računaš agregate za svaku grupu;
- pravilno razdvojiš filtriranje ulaznih redova (`WHERE`) od filtriranja grupa (`HAVING`);
- pronađeš red ili redove koji odgovaraju maksimumu ili minimumu, uključujući izjednačene vrednosti;
- odrediš redosled u `GROUP_CONCAT()` i izbegneš neočekivano umnožavanje nakon `JOIN`-a;
- proveriš kako SQLite tipovi i kolacije utiču na numeričke i tekstualne agregate.

Pre računanja prvo utvrdi šta predstavlja jedan ulazni red. `JOIN` može umnožiti redove, pa agregat nad spojenim rezultatom može brojati parove ili događaje, a ne jedinstvene entitete koje si imao na umu.

## Na šta posebno da obratiš pažnju

### `NULL`, nula i prazan skup

- Većina agregata ignoriše `NULL`; `COUNT(*)` je izuzetak i broji sve ulazne redove.
- `COUNT(izraz)` broji nenulte vrednosti, uključujući `0` i prazan tekst `''`. Ne proverava da li vrednost ima smisla za tvoju aplikaciju.
- `AVG()` i `SUM()` uključuju nulu, a ignorišu `NULL`. Nemoj menjati `NULL` u nulu pomoću `COALESCE()` osim ako to odgovara pravilima podataka.
- Agregatni upit bez `GROUP BY` nad praznim ulazom i dalje vraća jedan rezultatni red. `COUNT()` vraća `0`, dok `SUM()`, `AVG()`, `MIN()`, `MAX()` i `GROUP_CONCAT()` vraćaju `NULL`; `TOTAL()` vraća `0.0`.
- `GROUP BY` nad praznim ulazom formira nula grupa i vraća nula redova. Grupa koja postoji, ali sadrži samo `NULL` vrednosti, i dalje se vraća.

### `AVG()` i `SUM()` — težine, tipovi i preciznost

- `AVG()` računa prosek nenultih vrednosti. Nula učestvuje u imeniocu; `NULL` ne.
- Prosek grupnih proseka nije nužno ukupni prosek. Kada grupe imaju različit broj uzoraka, koristi ponderisanje brojem nenultih vrednosti ili računaj ukupni prosek direktno nad izvornim redovima.
- Za konverzije poput milisekundi u minute podeli realnim brojem, npr. `Milliseconds / 60000.0`; celobrojno deljenje može skratiti svaku vrednost pre agregacije.
- `SUM()` nad celim brojevima može prijaviti integer overflow. Realne vrednosti koriste približnu floating-point aritmetiku. Za novac je često prikladnije sabirati najmanju novčanu jedinicu kao ceo broj i formatirati rezultat na kraju.
- SQLite je fleksibilno tipiziran. Tekst koji izgleda kao broj može učestvovati u numeričkom agregatu; tekst koji se ne može protumačiti numerički može doprineti kao nula. Agregati nisu validacija kvaliteta podataka.

### `COUNT()`, duplikati i `JOIN`

- `COUNT(DISTINCT izraz)` broji različite nenulte vrednosti jednog izraza. Za kombinacije više kolona koristi `SELECT DISTINCT` u podupitu, pa broji redove spoljašnjeg upita.
- Duplirane vrednosti ne znače nužno duplirane zapise. `SUM(DISTINCT Total)` sabira različite iznose, ne račune; `AVG(DISTINCT value)` računa prosek jedinstvenih vrednosti, ne svih događaja.
- Posle `LEFT JOIN`-a red bez poklapanja i dalje postoji. `COUNT(*)` ga broji, dok `COUNT(desni_ključ)` izostavlja njegovu `NULL` vrednost.
- Pre agregiranja proveri kardinalnost spojeva: više poklapanja može ponoviti istu vrednost u zbiru, proseku ili konkateniranoj listi.

### `MIN()` i `MAX()` — vrednost nije ceo red

- `MIN()` i `MAX()` vraćaju ekstremnu vrednost, ne automatski ceo red koji je sadrži.
- Da bi dobio redove sa minimumom ili maksimumom, izračunaj ekstrem u podupitu ili CTE-u pa ga spoji nazad sa tabelom. Takav pristup zadržava sve redove koji dele istu ekstremnu vrednost.
- Ponavljanje vrednosti ne menja minimum ili maksimum, pa je `MIN(DISTINCT ...)` ili `MAX(DISTINCT ...)` najčešće suvišan.
- SQLite poredi tekst prema kolaciji i redosledu storage klasa. Broj zapisan kao tekst ne mora se porediti kao broj; mešanje tekstualnih i numeričkih vrednosti može dati neočekivan rezultat.
- SQLite ima i skalarne `min(a, b, ...)` i `max(a, b, ...)`. Oni porede argumente jednog reda i imaju drugačija pravila za `NULL` od agregatnih oblika.

### `GROUP_CONCAT()` — lista u jednom tekstu

- `GROUP_CONCAT()` ignoriše `NULL`, ali zadržava prazan tekst i ponovljene vrednosti. Ako nema nijedne nenulte vrednosti, vraća `NULL`.
- Podrazumevani separator je zarez; drugi argument zadaje prilagođeni separator. Separator se umeće samo između stavki.
- Bez unutrašnjeg `ORDER BY` redosled vrednosti nije garantovan. Spoljašnji `ORDER BY` sortira rezultatne redove, ne stavke unutar konkateniranog teksta.
- SQLite podržava `ORDER BY` unutar agregata od verzije 3.44.0. Sintaksa `GROUP_CONCAT(DISTINCT value, separator)` nije podržana; izdvoji jedinstvene vrednosti u podupitu pa ih konkateniraj spolja.
- Rezultat je jedan tekst, ne strukturisana lista. Separatori koji se pojavljuju i u podacima mogu otežati razdvajanje, a veoma dugačak rezultat podleže SQLite ograničenju dužine stringa.

### `GROUP BY` i `HAVING`

- `WHERE` filtrira pojedinačne redove pre grupisanja; agregati rade nad preostalim redovima.
- `GROUP BY` formira grupe, ali ne garantuje redosled rezultata. Koristi `ORDER BY` i dodaj tie-breaker kada je stabilan poredak važan.
- Redovi sa `NULL` grupnim ključem pripadaju istoj grupi. Ako želiš da ih ukloniš, filtriraj ih pre grupisanja.
- U agregatnom upitu biraj grupne izraze i agregate. SQLite dozvoljava negrupisane „bare columns“, ali njihova vrednost može doći iz neodređenog reda i ponašanje nije prenosivo.
- `HAVING` odbacuje ili zadržava cele grupe nakon agregacije. Uslov poput `COUNT(*) >= 10` pripada u `HAVING`, ne u `WHERE`.
- U agregatnom upitu bez `GROUP BY`, svi ulazni redovi čine jednu implicitnu grupu; `HAVING` može da je zadrži ili odbaci. To nije zamena za `WHERE`.

Temeljno nauči značenje uslova i ponašanje `NULL`; nemoj se oslanjati samo na to da upit „izgleda kao da radi“. Plan učenja preporučuje da prvenstveno savladaš prenosive SQL veštine, a SQLite posebnosti razumeš dovoljno da znaš kada su važne — pogledaj [plan učenja](../plan_ucenja/sta_je_vazno.md).

## Vežbe i bezbedan način rada

Svih devet SQL skripti nalazi se u [playground/sql/06_sqlite_aggregate_functions/](../playground/sql/06_sqlite_aggregate_functions/). One su namenjene čitanju Chinook kopije i sadrže CTE primere nad privremenim vrednostima; ne menjaju tabele niti podatke. Ipak, koristi lokalnu kopiju, ne bazu FastAPI aplikacije. U SQLite CLI-ju, iz korena repozitorijuma, otvori kopiju u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj jednu skriptu iz prompta, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.sql
```

U SQLTools-u izaberi `ChinookPractice`, proveri da pokazuje na `playground/databases/chinook_practice.db` i pokreći pojedinačne `-- @block` odeljke. `.read` je SQLite CLI meta-komanda, a ne SQL upit.

### Proverene vežbe

Svih devet SQL skripti uspešno je izvršeno u read-only režimu nad `chinook_practice.db`. Provereni su i očekivani rezultati u [danu 10](../pitanja_i_odgovori/dan_10_sqlite_aggregate_functions.md). Brojevi u vodiču odnose se na trenutnu kopiju i razlikovaće se ako su podaci promenjeni.

### Prenosivo znanje i SQLite specifičnosti

Agregati, `GROUP BY`, `HAVING`, `NULL` pravila i razlika između filtriranja redova i grupa predstavljaju osnovne SQL koncepte. Ipak, proveri ponašanje pri prelasku na drugu bazu:

- `GROUP_CONCAT()`, `TOTAL()`, SQLite-ovo fleksibilno tipiziranje i dozvoljene „bare columns“ specifični su za SQLite ili se razlikuju među DBMS-ovima.
- Sintaksa za redosled unutar agregata i `DISTINCT` agregat sa prilagođenim separatorom zavisi od implementacije. SQLite podržava agregatni `ORDER BY` od verzije 3.44.0.
- Poređenje tekstualnih vrednosti zavisi od kolacije. Ugrađeni `NOCASE` nije potpuno Unicode case-folding pravilo.
- SQLAlchemy ne uklanja razlike u funkcijama, kolacijama, tipovima ili ponašanju ciljne baze.

Nazad na [glavni README kursa](../README.md).
