# 03 — SQLite `CROSS JOIN`

## Cilj lekcije

U ovoj lekciji naučićeš kako `CROSS JOIN` pravi sve moguće kombinacije redova iz dve tabele. Za razliku od `INNER JOIN`-a i `LEFT JOIN`-a, ne traži poklapanje vrednosti u join ključevima: svaki red leve tabele kombinuje se sa svakim redom desne tabele.

Koristićemo `albums` i `media_types` iz Chinook baze. Njihove kolone ne moraju da imaju međusobno povezane vrednosti da bi se napravio `CROSS JOIN`.

Prethodne lekcije: [`LEFT JOIN`](./01_sqlite_LEFT_join.md) i [`INNER JOIN`](./02_sqlite_INNER_join.md). Izvor za ovu lekciju: [transkript `CROSS JOIN`-a](../transcripts/05_table_joins/03_sqlite_CEOSS_join_transcript.txt).

## Šta je `CROSS JOIN`

`CROSS JOIN` vraća Dekartov proizvod dve tabele: svaki red iz prve tabele uparuje sa svakim redom iz druge.

```sql
SELECT kolone
FROM prva_tabela
CROSS JOIN druga_tabela;
```

Za ovaj uobičajeni oblik ne piše se `ON` uslov, jer ne tražimo poklapanja. U rezultatu se nalaze sve kombinacije, čak i kada tabele nemaju zajedničke kolone ili relaciju.

Ako prva tabela ima `m` redova, a druga `n` redova, broj kombinacija je:

```text
m × n
```

Na primer, 4 reda spojena sa 3 reda daju 12 redova. Ako je jedna tabela prazna, rezultat ima 0 redova.

## Primer iz transkripta: albumi i tipovi medija

Tabela `albums` u priloženoj Chinook kopiji ima 347 redova, a `media_types` ima 5 redova. Njihov `CROSS JOIN` zato daje `347 × 5 = 1735` kombinacija:

```sql
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    a.ArtistId,
    m.MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId
LIMIT 10;
```

Prvi album se u rezultatu pojavljuje pet puta — jednom uz svaki tip medija:

| AlbumId | AlbumTitle                            | ArtistId | MediaTypeId | MediaTypeName               |
| ------: | ------------------------------------- | -------: | ----------: | --------------------------- |
|       1 | For Those About To Rock We Salute You |        1 |           1 | MPEG audio file             |
|       1 | For Those About To Rock We Salute You |        1 |           2 | Protected AAC audio file    |
|       1 | For Those About To Rock We Salute You |        1 |           3 | Protected MPEG-4 video file |
|       1 | For Those About To Rock We Salute You |        1 |           4 | Purchased AAC audio file    |
|       1 | For Those About To Rock We Salute You |        1 |           5 | AAC audio file              |
|       2 | Balls to the Wall                     |        2 |           1 | MPEG audio file             |
|       2 | Balls to the Wall                     |        2 |           2 | Protected AAC audio file    |
|       2 | Balls to the Wall                     |        2 |           3 | Protected MPEG-4 video file |
|       2 | Balls to the Wall                     |        2 |           4 | Purchased AAC audio file    |
|       2 | Balls to the Wall                     |        2 |           5 | AAC audio file              |

Ovo je primer kombinovanja podataka, ne tvrdnja da je svaki album zaista dostupan u svakom tipu medija. Upit ne proverava takvu poslovnu vezu.

Možeš da proveriš ukupan broj kombinacija direktno:

```sql
SELECT COUNT(*) AS combinations
FROM albums AS a
CROSS JOIN media_types AS m;
```

U priloženoj bazi rezultat je `1735`. Broj će biti drugačiji ako se promene redovi u bilo kojoj od tabela.

## Kolone u rezultatu

`SELECT *` vraća kolone obe tabele. U ovom primeru to su kolone iz `albums`, a zatim kolone iz `media_types`:

```sql
SELECT *
FROM albums
CROSS JOIN media_types
LIMIT 5;
```

Za veće tabele je obično bolje navesti samo potrebne kolone i dati im jasne alias-e. Tako izbegavaš suvišne podatke i lakše razlikuješ istoimene kolone:

```sql
SELECT
    a.AlbumId AS AlbumId,
    a.Title AS AlbumTitle,
    m.MediaTypeId AS MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m;
```

`CROSS JOIN` ne uklanja duplikate. Ako tabela sadrži ponovljene vrednosti, svaka njena pojava učestvuje u kombinacijama. `DISTINCT` dodaj samo kada zaista želiš da ukloniš ponovljene izlazne redove, ne da bi menjao značenje spajanja.

## `CROSS JOIN` naspram `INNER JOIN`

| Ponašanje           | `CROSS JOIN`                         | `INNER JOIN`                          |
| ------------------- | ------------------------------------ | ------------------------------------- |
| Uslov za uparivanje | Ne zahteva poklapanje kolona         | Obično ga definišeš u `ON`            |
| Kombinacije         | Svaki red sa svakim redom            | Samo kombinacije koje zadovolje uslov |
| Broj redova         | Proizvod broja redova obe tabele     | Zavisi od broja poklapanja            |
| Tipična namena      | Namerno generisanje svih kombinacija | Povezivanje povezanih zapisa          |

Za `albums` i `media_types`, `CROSS JOIN` daje 1735 kombinacija. `INNER JOIN` bi trebalo koristiti kada postoji smislen uslov povezivanja između redova; bez takvog uslova, ne pretpostavljaj da bi rezultat predstavljao relaciju između albuma i tipova medija.

U SQLite-u se može napisati `CROSS JOIN ... ON uslov`, ali tada uslov ograničava skup kombinacija. To više nije puni Dekartov proizvod. Ako je namera da se povežu redovi koji zadovoljavaju uslov, jasnije je napisati `INNER JOIN ... ON uslov`.

## Kada je `CROSS JOIN` koristan

Koristi ga kada su ti potrebne sve moguće kombinacije, na primer:

- svaka veličina sa svakom bojom proizvoda, radi prikaza mogućih varijanti;
- svaki dan iz kalendara sa svakom kategorijom, radi izveštaja koji treba da prikaže i kombinacije bez aktivnosti;
- sve vrednosti iz dve male pomoćne liste, radi generisanja testnih kombinacija.

Pre upotrebe izračunaj očekivani broj redova. Na primer, 10.000 redova ukrštenih sa 2.000 redova daje 20 miliona kombinacija. Veliki rezultat može potrošiti mnogo vremena i memorije, a često ukazuje na slučajno izostavljen join uslov.

## Redosled rezultata

SQL ne garantuje redosled redova bez `ORDER BY`. Iako primer rezultata grupiše tipove medija po albumu, taj redosled treba eksplicitno tražiti:

```sql
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    m.MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId;
```

Za stabilno sortiranje koristi kolone koje zajedno jednoznačno određuju redove — ovde `AlbumId` i `MediaTypeId`.

## Česte greške

- **Očekuješ samo povezane redove:** `CROSS JOIN` ne proverava relaciju; koristi `INNER JOIN` uz odgovarajući `ON` ako želiš poklapanja.
- **Zaboraviš na množenje broja redova:** izračunaj `m × n` pre pokretanja upita.
- **Koristiš ga nad velikim tabelama bez potrebe:** rezultat može narasti na milione ili milijarde kombinacija.
- **Pretpostaviš da kombinacije predstavljaju stvarne veze:** upit pravi parove, ali ne potvrđuje da takva veza postoji u poslovnim podacima.
- **Izostaviš uslov u namernom `INNER JOIN`-u:** možeš dobiti sve moguće parove i pogrešan broj redova; proveri `ON` klauzulu.
- **Osloniš se na redosled bez `ORDER BY`:** rezultat nema garantovan redosled.
- **Koristiš `SELECT *` nad širokim tabelama:** izaberi samo potrebne kolone.
- **Dodaješ `DISTINCT` samo zato što vidiš ponovljene vrednosti:** različite kombinacije mogu deliti iste vrednosti kolona; prvo proveri šta jedan red rezultata treba da predstavlja.

## Vežbe

1. Prikaži sve kolone iz `albums` i `media_types` pomoću `CROSS JOIN`.
2. Prikaži samo `AlbumId`, `Title`, `MediaTypeId` i `Name`, uz jasne alias-e.
3. Izbroj redove u obe tabele, izračunaj njihov proizvod i uporedi ga sa `COUNT(*)` nad `CROSS JOIN` rezultatom.
4. Dodaj `ORDER BY AlbumId, MediaTypeId` i `LIMIT 10`. Uporedi rezultat sa primerom u lekciji.
5. Napravi dve male pomoćne tabele sa po nekoliko redova i proveri da li rezultat ima očekivani broj kombinacija.
6. Isprazni jednu pomoćnu tabelu i proveri koliko redova vraća `CROSS JOIN`.
7. Razmisli o slučaju kada imaš 5.000 redova u prvoj tabeli i 3.000 u drugoj. Koliko bi redova imao proizvod i da li je takav upit opravdan?
8. Napiši upit koji povezuje stvarno povezane redove dve tabele. Objasni zašto je za taj zadatak `INNER JOIN ... ON` jasniji od `CROSS JOIN`.

## Provera razumevanja

1. Šta je Dekartov proizvod?
2. Koliko redova vraća `CROSS JOIN` ako prva tabela ima 6 redova, a druga 4?
3. Koliko redova vraća ako je jedna od tabela prazna?
4. Da li kolone dveju tabela moraju imati isto ime ili iste vrednosti?
5. Zašto se album u primeru pojavljuje po pet puta?
6. Da li rezultat dokazuje da je album dostupan u svakom tipu medija?
7. Koja je razlika između `CROSS JOIN`-a i `INNER JOIN`-a sa uslovom poklapanja?
8. Zašto je važno proceniti veličinu rezultata pre izvršavanja?
9. Zašto `ORDER BY` treba dodati kada očekuješ određen redosled?
10. Zašto ponovljene vrednosti u rezultatu ne znače nužno da su redovi duplikati?

## Izvori za dalje čitanje

- [SQLite: SELECT — JOIN syntax and processing](https://www.sqlite.org/lang_select.html)
