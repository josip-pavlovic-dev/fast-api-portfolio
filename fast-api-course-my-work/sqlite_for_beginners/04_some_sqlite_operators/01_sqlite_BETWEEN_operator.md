# 01 — SQLite `BETWEEN` operator

## Cilj lekcije

U ovoj lekciji naučićeš kako da pomoću operatora `BETWEEN` filtriraš vrednosti koje se nalaze unutar opsega. Koristićemo tabelu `invoices` iz Chinook baze, a zatim ćemo razmotriti tekstualne vrednosti, datume, `NOT BETWEEN` i česte granične slučajeve.

Prethodna lekcija: [Filtriranje redova pomoću `WHERE`](../02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.md).

Operatori poput `BETWEEN`, `IN`, `LIKE` i `GLOB` pojavljivali su se i u ranijim primerima. Ova oblast ih obrađuje sistematski, tako da možeš prvo da pređeš gradivo, a zatim da ga ponavljaš.

## Čemu služi `BETWEEN`

`BETWEEN` proverava da li se izraz nalazi između donje i gornje granice:

```sql
izraz BETWEEN donja_granica AND gornja_granica
```

Uobičajeno se koristi kao uslov u `WHERE` klauzuli:

```sql
SELECT kolone
FROM tabela
WHERE izraz BETWEEN donja_granica AND gornja_granica;
```

Važno: `BETWEEN` uključuje **obe granice**. Uslov:

```sql
vrednost BETWEEN 5 AND 10
```

znači isto što i:

```sql
vrednost >= 5 AND vrednost <= 10
```

Ovo objašnjenje važi za uobičajen stabilan izraz, kao što je kolona. SQLite kod `BETWEEN` procenjuje izraz sa leve strane jednom; ako ga ručno napišeš dva puta kao odvojena poređenja, izraz može biti procenjen dvaput. To je bitno samo za posebne ili nedeterminističke izraze, ne za običnu kolonu.

Zato su i `5` i `10` unutar opsega:

```sql
SELECT
    5 BETWEEN 5 AND 10 AS donja_granica_ukljucena,
    10 BETWEEN 5 AND 10 AS gornja_granica_ukljucena;
```

Oba izraza vraćaju `1` u SQLite-u, što predstavlja tačno (`TRUE`).

Reč `AND` između granica deo je sintakse operatora `BETWEEN`. Dodatne uslove navedi posle cele provere opsega; zagrade mogu učiniti grupisanje preglednijim:

```sql
SELECT InvoiceId, Total
FROM invoices
WHERE (Total BETWEEN 5 AND 10)
  AND BillingCountry = 'USA';
```

Ovaj upit traži račune čiji je `Total` između 5 i 10, uključujući granice, i koji su za kupce iz SAD.

## Primer iz Chinook baze

U transkriptu se operator demonstrira nad kolonom `Total` iz tabele `invoices`. Pošto transkript ne navodi konkretne granice iz upita, ovde koristimo opseg od 5 do 10:

```sql
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId;
```

Ovaj upit vraća račune čija je ukupna vrednost od `5` do `10`, uključujući oba iznosa. U priloženoj Chinook bazi uslov odgovara 115 redova. Zato se ovaj broj ne poklapa sa osam rezultata pomenutih u transkriptu: tamošnje granice nisu navedene, a broj redova zavisi od njih. Za pregled prvih pet, bez promene samog uslova:

```sql
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId
LIMIT 5;
```

Očekivani rezultat:

| InvoiceId | BillingAddress         | Total |
| --------: | ---------------------- | ----: |
|         3 | Grétrystraat 63        |  5.94 |
|        10 | 3 Chatham Street       |  5.94 |
|        17 | 319 N. Frances Street  |  5.94 |
|        24 | Ullevålsveien 14       |  5.94 |
|        31 | 9, Place Louis Barthou |  5.94 |

`ORDER BY` daje predvidiv redosled prikaza. `LIMIT 5` prikazuje samo pet redova; ne menja to koji redovi ispunjavaju uslov `BETWEEN`.

Ako želiš samo da proveriš koliko računa ispunjava uslov, možeš koristiti agregat `COUNT`:

```sql
SELECT COUNT(*) AS broj_racuna
FROM invoices
WHERE Total BETWEEN 5 AND 10;
```

Rezultat u istoj bazi je `115`.

## Isključivanje opsega pomoću `NOT BETWEEN`

Dodavanjem `NOT` tražiš vrednosti koje nisu unutar opsega:

```sql
SELECT InvoiceId, Total
FROM invoices
WHERE Total NOT BETWEEN 5 AND 10
ORDER BY Total, InvoiceId
LIMIT 10;
```

Za običan izraz, ovo je ekvivalentno uslovu:

```sql
Total < 5 OR Total > 10
```

Pošto je `BETWEEN` uključivao granice, `NOT BETWEEN` ih isključuje iz rezultata: vrednosti `5` i `10` nisu „izvan“ opsega od 5 do 10.

Ako je donja granica veća od gornje, na primer `Total BETWEEN 10 AND 5`, nijedna obična numerička vrednost ne može istovremeno biti bar 10 i najviše 5. Nemoj zameniti granice nasumično; prvo odluči koji opseg želiš da predstaviš.

## Opsezi brojeva, teksta i datuma

`BETWEEN` može porediti brojeve, tekst i datume, ali poređenje mora odgovarati načinu na koji su vrednosti sačuvane.

### Brojevi

Brojevi su najčešći i najlakši primer:

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
WHERE Milliseconds BETWEEN 180000 AND 240000
ORDER BY Milliseconds, TrackId;
```

Ovaj uslov uključuje i numere koje traju tačno `180000` ili `240000` milisekundi. Brojeve piši bez navodnika kada želiš numeričko poređenje.

SQLite koristi dinamički sistem tipova. U običnoj tabeli kolona može sadržati vrednosti različitih klasa skladištenja, a afinitet kolone može uticati na konverzije pri poređenju. Za pouzdane numeričke opsege čuvaj i poredi numeričke vrednosti dosledno; nemoj se oslanjati na slučajno mešanje brojeva i tekstualnih zapisa brojeva. Pogledaj i lekciju [Tipovi podataka i klase skladištenja u SQLite-u](../02_retriving_data_and_manipulating_data/08_sqllite_data_types.md).

### Tekst

Tekst se poredi prema pravilima kolacije, najčešće leksikografskim pravilima `BINARY`, a ne prema značenju reči:

```sql
SELECT 'pear' BETWEEN 'apple' AND 'plum' AS tekst_je_u_opsegu;
```

U podrazumevanoj `BINARY` kolaciji ovaj izraz vraća `1`. Poređenje teksta može zavisiti od velikih i malih slova, kolacije i znakova u tekstu. To nije isto što i pretraga prefiksa: za obrasce teksta koristi `LIKE` ili `GLOB`, u zavisnosti od obrasca koji želiš.

### Datumi i vremena

SQLite nema posebnu klasu skladištenja za datume i vremena. Često se čuvaju kao tekst u doslednom, sortirljivom ISO 8601 formatu ili kao numeričke vrednosti. Poređenje je pouzdanije kada su vrednosti istog formata i koriste doslednu vremensku zonu.

Za kolonu koja čuva samo datume u obliku `YYYY-MM-DD`, `BETWEEN` može jasno izraziti uključiv opseg:

```sql
WHERE invoice_date BETWEEN '2025-01-01' AND '2025-01-31'
```

Kod vremenskih oznaka sa satima, minutima i sekundama postoji važna zamka. Ako su vrednosti, na primer, `2025-01-31 14:30:00`, gornja granica `'2025-01-31'` označava početak tog dana kao tekstualne granice; ona ne obuhvata automatski ceo 31. januar. Takođe, granica `'23:59:59'` može propustiti vrednosti sa delićima sekunde.

Za ceo kalendarski mesec koristi poluotvoreni opseg: uključi početak prvog dana, a isključi početak sledećeg meseca:

```sql
SELECT InvoiceId, InvoiceDate
FROM invoices
WHERE InvoiceDate >= '2009-01-01 00:00:00'
  AND InvoiceDate <  '2009-02-01 00:00:00'
ORDER BY InvoiceDate, InvoiceId;
```

Ovaj obrazac obuhvata sve vrednosti iz januara, uključujući bilo koje vreme tokom poslednjeg dana, bez potrebe da pogađaš poslednju moguću sekundu ili preciznost baze.

## `NULL` i `BETWEEN`

Ako je izraz ili neka granica `NULL`, poređenje uglavnom daje `NULL` — u logici SQL-a to je nepoznat rezultat (`UNKNOWN`), a ne `TRUE` ili `FALSE`:

```sql
SELECT
    NULL BETWEEN 1 AND 10 AS u_opsegu,
    NULL NOT BETWEEN 1 AND 10 AS van_opsega;
```

Oba rezultata su `NULL`. `WHERE` zadržava samo redove čiji uslov je `TRUE`, pa se red sa `NULL` vrednošću neće pojaviti ni uz `BETWEEN` ni uz `NOT BETWEEN`. Ako želiš posebno da pronađeš nedostajuće vrednosti, koristi `IS NULL`:

```sql
SELECT InvoiceId, Total
FROM invoices
WHERE Total IS NULL;
```

U Chinook tabeli `invoices` kolona `Total` je obavezna, ali u drugim tabelama ili projektima vrednost koja se poredi može biti `NULL`.

## Redosled klauzula

Kada `BETWEEN` kombinuješ sa sortiranjem i ograničavanjem rezultata, klauzule pišeš u ovom redosledu:

```sql
SELECT kolone
FROM tabela
WHERE izraz BETWEEN donja_granica AND gornja_granica
ORDER BY kolona
LIMIT broj_redova;
```

`WHERE` filtrira redove, `ORDER BY` određuje redosled, a `LIMIT` ograničava koliko redova se vraća.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 `ColumnElement.between()` gradi isti uključivi opseg:

```python
from decimal import Decimal

from sqlalchemy import select

minimum = Decimal("5.00")
maximum = Decimal("10.00")

statement = (
    select(Invoice.invoice_id, Invoice.total)
    .where(Invoice.total.between(minimum, maximum))
    .order_by(Invoice.total, Invoice.invoice_id)
)
```

Primer pretpostavlja da ORM model `Invoice` ima atribute `invoice_id` i `total`. `between()` uključuje obe granice, kao i SQL `BETWEEN`. SQLAlchemy izrazi prosleđuju vrednosti kao parametre umesto da ih lepe u SQL tekst. U FastAPI endpointu proveri da su granice ispravnog formata i da je donja granica manja ili jednaka gornjoj.

Za opseg datuma i vremena koji treba da uključi ceo dan ili mesec koristi isti poluotvoreni obrazac: `>= početak` i `< početak_narednog_perioda`. U SQLAlchemy-ju se to može zapisati kao dva `.where()` uslova.

## Indeksi i opsežno filtriranje

Ako često filtriraš veliku tabelu prema istoj koloni, indeks na toj koloni ponekad može pomoći i upitima sa `BETWEEN`. To ne znači da svaki `BETWEEN` automatski koristi indeks ili da je indeks uvek koristan. Indeksiranje zavisi od šeme, podataka i plana upita; kada budeš učio indekse, proveravaj ga pomoću `EXPLAIN QUERY PLAN` i stvarnih podataka.

## Česte greške

- **Pretpostaviš da su granice isključene:** `BETWEEN` uključuje i donju i gornju granicu.
- **Koristiš pogrešan `AND`:** `AND` između granica pripada sintaksi `BETWEEN`; dodatni uslovi idu posle cele provere opsega.
- **Očekuješ da `NOT BETWEEN` pronađe `NULL`:** `NULL` ne postaje obična vrednost van opsega; koristi `IS NULL`.
- **Navedeš granice obrnutim redosledom:** numerički opseg od 10 do 5 ne predstavlja opseg od 5 do 10.
- **Porediš brojeve kao tekst:** mešanje klasa skladištenja može dati neočekivano poređenje; koristi dosledne tipove vrednosti.
- **Koristiš `BETWEEN` sa tekstom kao da je pretraga prefiksa:** tekst se poredi prema kolaciji; za obrasce koristi `LIKE` ili `GLOB`.
- **Koristiš datum bez vremena kao krajnju granicu za timestamp:** `'2025-01-31'` ne obuhvata automatski ostatak tog dana; koristi `>= početak AND < početak_sledećeg_perioda`.
- **Očekuješ da `LIMIT` menja kriterijum opsega:** `LIMIT` samo skraćuje prikazani rezultat.

## Provera razumevanja

1. Šta proverava operator `BETWEEN`?
2. Da li su donja i gornja granica uključene?
3. Koji uslov je ekvivalentan izrazu `Total BETWEEN 5 AND 10`?
4. Šta vraća `NOT BETWEEN` za vrednosti na samim granicama?
5. Zašto `NULL NOT BETWEEN 1 AND 10` nije isto što i `TRUE`?
6. Zašto je opseg `BETWEEN 10 AND 5` problematičan za uobičajene numeričke vrednosti?
7. Zašto opseg tekstualnih vrednosti zavisi od kolacije?
8. Zašto `InvoiceDate BETWEEN '2025-01-01' AND '2025-01-31'` može propustiti timestampove tokom 31. januara?
9. Kada je korisno koristiti `>= početak AND < početak_narednog_perioda` umesto `BETWEEN`?
10. Da li `LIMIT` menja koje vrednosti ispunjavaju `BETWEEN` uslov?

## Vežbe

### Vežba 1 — Filtriraj račune po iznosu

1. U tabeli `invoices` prikaži `InvoiceId`, `BillingAddress` i `Total` za račune čiji je `Total` između 5 i 10.
2. Uključi `ORDER BY Total, InvoiceId`.
3. Koliko redova odgovara uslovu? Proveri broj pomoću `COUNT(*)`.
4. Dodaj `LIMIT 5` i uporedi prikazan broj redova sa ukupnim brojem koji odgovara uslovu.

### Vežba 2 — Proveri uključive granice

Pokreni upit koji poredi vrednosti `5` i `10` sa opsegom `BETWEEN 5 AND 10`. Objasni zašto obe vrednosti prolaze, a vrednosti `4.99` i `10.01` ne prolaze.

### Vežba 3 — Izdvoji vrednosti izvan opsega

Prikaži `InvoiceId` i `Total` za račune čiji iznos nije između 5 i 10. U prvih deset rezultata proveri da li svaki iznos zadovoljava `Total < 5 OR Total > 10`.

### Vežba 4 — Kombinuj opseg sa dodatnim uslovom

Prikaži račune sa `Total` između 5 i 10 koji imaju `BillingCountry = 'USA'`. Uveri se da su granice deo jednog `BETWEEN` uslova, a država dodatni uslov.

### Vežba 5 — Opseg trajanja numera

Iz tabele `tracks` prikaži `TrackId`, `Name` i `Milliseconds` za numere koje traju između 180.000 i 240.000 milisekundi. Uključi granice, sortiraj po trajanju i zatim po `TrackId`.

### Vežba 6 — Opseg datuma sa vremenom

Napiši upit za sve račune iz januara 2009. Ako koristiš kolonu sa datumom i vremenom, izaberi oblik koji obuhvata ceo januar, uključujući poslednji dan, bez oslanjanja na pretpostavku da je poslednja moguća sekunda `23:59:59`.
