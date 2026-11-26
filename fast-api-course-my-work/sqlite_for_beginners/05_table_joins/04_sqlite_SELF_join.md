# 04 — SQLite `SELF JOIN`

## Cilj lekcije

U ovoj lekciji naučićeš kako da spojiš tabelu sa samom sobom. `SELF JOIN` je obrazac, a ne posebna vrsta join operatora: istu tabelu navedeš dva puta u upitu, daš joj različite alias-e i izabereš odgovarajući join, na primer `INNER JOIN` ili `LEFT JOIN`.

Kao primer koristićemo tabelu `employees` iz Chinook baze. Kolona `ReportsTo` čuva ID rukovodioca zaposlenog, a taj ID odgovara koloni `EmployeeId` drugog reda u istoj tabeli.

Prethodne lekcije: [`LEFT JOIN`](./01_sqlite_LEFT_join.md), [`INNER JOIN`](./02_sqlite_INNER_join.md) i [`CROSS JOIN`](./03_sqlite_CROSS_join.md). Izvor za ovu lekciju: [transkript `SELF JOIN`-a](../transcripts/05_table_joins/04_sqlite_SELF_join_transcript.txt).

## Zašto je potreban `SELF JOIN`

Jedan red u `employees` može da predstavlja zaposlenog, a drugi red iz iste tabele njegovog rukovodioca. Za prikaz obe uloge u istom rezultatu, tabelu koristimo dva puta:

```sql
SELECT kolone
FROM tabela AS prvi_alias
INNER JOIN tabela AS drugi_alias
    ON uslov_povezivanja;
```

Alias-i su neophodni da bi se jasno razlikovale dve uloge iste tabele. U sledećem primeru:

- `e` označava zaposlenog, odnosno osobu koja neposredno odgovara rukovodiocu;
- `m` označava njegovog rukovodioca.

## Primer iz transkripta: rukovodioci i direktni izveštaji

`employees.ReportsTo` upućuje na `employees.EmployeeId` rukovodioca. Uslov spajanja zato ide od reda zaposlenog ka redu rukovodioca:

```sql
SELECT
    m.EmployeeId AS ManagerId,
    m.FirstName || ' ' || m.LastName AS Manager,
    e.EmployeeId AS DirectReportId,
    e.FirstName || ' ' || e.LastName AS DirectReport,
    e.Title AS DirectReportTitle
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY
    m.LastName,
    m.FirstName,
    e.LastName,
    e.FirstName;
```

Ista tabela se pojavljuje u `FROM` i `JOIN`, ali alias `e` predstavlja zaposlenog, a alias `m` njegovog rukovodioca. Uslov `m.EmployeeId = e.ReportsTo` pronalazi red rukovodioca za svakog zaposlenog koji ima vrednost `ReportsTo`.

U priloženoj Chinook kopiji ovaj upit vraća 7 parova. Na primer:

| ManagerId | Manager       | DirectReportId | DirectReport     | DirectReportTitle   |
| --------: | ------------- | -------------: | ---------------- | ------------------- |
|         1 | Andrew Adams  |              2 | Nancy Edwards    | Sales Manager       |
|         1 | Andrew Adams  |              6 | Michael Mitchell | IT Manager          |
|         2 | Nancy Edwards |              5 | Steve Johnson    | Sales Support Agent |

Redosled rezultata određuju kolone u `ORDER BY`; bez njih nije garantovan. Imena kolona u `SELECT` delu imaju alias-e zato što obe reference na tabelu sadrže `FirstName`, `LastName` i `EmployeeId`, ali predstavljaju različite uloge.

## Zašto `INNER JOIN` izostavlja neke zaposlene

U tabeli je `ReportsTo` dozvoljeno da bude `NULL`. Zaposleni koji nema rukovodioca nema odgovarajući red za spajanje kroz `m.EmployeeId = e.ReportsTo`, pa ga `INNER JOIN` izostavlja. U ovoj bazi Andrew Adams je jedini zaposleni bez rukovodioca; zato se 8 zaposlenih svodi na 7 parova rukovodilac–zaposleni.

Ako želiš da prikažeš sve zaposlene i rukovodioca samo kada postoji, koristi `LEFT JOIN`, pri čemu `employees AS e` ostaje leva strana:

```sql
SELECT
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS Employee,
    m.FirstName || ' ' || m.LastName AS Manager
FROM employees AS e
LEFT JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY e.EmployeeId;
```

Ovaj upit vraća svih 8 zaposlenih. Za Andrewa kolona `Manager` je `NULL`. `LEFT JOIN` čuva sve redove sa leve strane; ako promeniš redosled uloga u `FROM` i `JOIN`, promenićeš i to čiji se redovi čuvaju.

## `ON` naspram starijeg oblika sa `WHERE`

U starijem implicitnom obliku, uslov spajanja može se napisati u `WHERE` klauzuli:

```sql
SELECT
    m.FirstName || ' ' || m.LastName AS Manager,
    e.FirstName || ' ' || e.LastName AS DirectReport
FROM employees AS e, employees AS m
WHERE m.EmployeeId = e.ReportsTo;
```

Ovaj upit pravi unutrašnje spajanje u ovom primeru, ali meša navođenje tabela i uslov povezivanja. Preporučen je eksplicitni oblik `INNER JOIN ... ON`: odmah pokazuje kako su redovi povezani i olakšava razlikovanje join uslova od dodatnih filtera u `WHERE`.

## Šta jedan `SELF JOIN` može da pokaže

Ovaj primer prikazuje samo neposredni odnos zaposlenog i rukovodioca. Ako je potreban ceo lanac rukovodilaca kroz više nivoa, jedan `SELF JOIN` nije dovoljan; za obilazak hijerarhije koristi se rekurzivni CTE.

Self join može se koristiti i za poređenje redova iste tabele, na primer za pronalaženje parova proizvoda sa istom kategorijom. U svakom takvom upitu jasno odredi šta predstavljaju oba alias-a i da li treba ukloniti obrnuti par ili poređenje reda sa samim sobom.

Iako se self join-i mogu koristiti i za neke proračune, kao što su running totals, u savremenom SQLite-u su za kumulativne proračune obično jasnije funkcije prozora. Izaberi pristup prema cilju i podršci verzije baze.

## Česte greške

- **Zaboraviš da tabelu navedeš dva puta:** svaka uloga mora biti zasebna referenca u `FROM`/`JOIN`.
- **Ne daš različite alias-e:** koristi, na primer, `e` za zaposlenog i `m` za rukovodioca.
- **Zameniš smer veze:** uslov za ovaj model je `m.EmployeeId = e.ReportsTo`, ne obrnuto.
- **Pomešaš alias i naziv kolone:** `employees AS e` je alias tabele; `e.FirstName AS EmployeeName` je alias izlazne kolone.
- **Očekuješ da `INNER JOIN` prikaže zaposlenog bez rukovodioca:** `NULL` u `ReportsTo` nema poklapanje; koristi `LEFT JOIN` ako želiš da zadržiš sve zaposlene.
- **Zaboraviš da je veza hijerarhijska:** jedan self join prikazuje neposrednog roditelja, ne proizvoljan broj nivoa.
- **Koristiš implicitni join bez uslova:** kombinovaćeš svaki red sa svakim; napiši odgovarajući `ON`.
- **Osloniš se na slučajni redosled:** dodaj `ORDER BY` sa dovoljnim kriterijumima za stabilan rezultat.

## Vežbe

1. Prikaži ID i ime svakog zaposlenog uz ID i ime njegovog rukovodioca pomoću `INNER JOIN`.
2. Dodaj alias-e `Manager` i `DirectReport` za imena i sortiraj po rukovodiocu, pa po zaposlenom.
3. Uporedi broj redova u `employees` sa brojem parova koje vraća `INNER JOIN`. Objasni razliku.
4. Prepravi upit u `LEFT JOIN` i pronađi zaposlenog bez rukovodioca.
5. Dodaj titule zaposlenog i rukovodioca. Jasno imenuj izlazne kolone da se njihove uloge ne pomešaju.
6. Prepiši upit iz implicitnog oblika sa `WHERE` u eksplicitni `INNER JOIN ... ON`.
7. Promeni uslov spajanja na `e.EmployeeId = m.ReportsTo`. Uporedi rezultate i objasni koju ulogu sada predstavlja svaki red.
8. Objasni zašto ovaj upit prikazuje samo neposrednog rukovodioca, a ne sve nivoe organizacione hijerarhije.

## Provera razumevanja

1. Da li je `SELF JOIN` poseban SQL join operator ili obrazac koji koristi istu tabelu više puta?
2. Zašto se za dve reference na `employees` koriste različiti alias-i?
3. Šta predstavljaju `e` i `m` u primeru?
4. Zašto se `m.EmployeeId` poredi sa `e.ReportsTo`?
5. Zašto rezultat `INNER JOIN`-a sadrži 7 parova, a ne svih 8 zaposlenih?
6. Kako se menja rezultat kada se koristi `LEFT JOIN` sa `e` na levoj strani?
7. Koja je prednost `JOIN ... ON` u odnosu na implicitni join sa uslovom u `WHERE`?
8. Da li jedan self join vraća celu hijerarhiju? Zašto?
9. Zašto je korisno alias-ovati kolone u `SELECT` delu?
10. Koju klauzulu dodaš da bi rezultat imao predvidiv redosled?

## Izvori za dalje čitanje

- [SQLite: SELECT — JOIN syntax and processing](https://www.sqlite.org/lang_select.html)
