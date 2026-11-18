# 02 — Otvaranje i priključivanje Chinook baze

## Cilj lekcije

U ovoj lekciji otvorićeš Chinook bazu koja se nalazi u repozitorijumu i proverićeš da možeš da pristupiš njenim tabelama. Transkript koristi izraz „priključivanje baze“, ali je važno razlikovati otvaranje glavne baze u SQLite CLI-ju od SQL naredbe `ATTACH DATABASE`, kojom se dodatna baza priključuje postojećoj konekciji.

## Chinook baza je već u projektu

U folderu [chinook/](../chinook/) nalaze se baza `chinook.db` i dijagram šeme. Pošto je arhiva već raspakovana i fajl se nalazi u projektu, nije potrebno da ga ponovo preuzimaš niti da ga kopiraš u koren diska kao u video-lekciji.

Ovakav raspored čuva bazu uz materijale kursa i izbegava putanje specifične za jedan računar, poput `C:\SQLite\DB\Chinook.db`. Koristi putanju koja odgovara tvom repozitorijumu i proveri da naziv fajla `chinook.db` ispravan.

## Otvori Chinook kao glavnu bazu

Otvori integrisani terminal u VS Code-u i postavi trenutni direktorijum na koren repozitorijuma. Zatim pokreni:

```bash
sqlite3 "fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db"
```

Ova putanja je relativna u odnosu na trenutni direktorijum terminala. Ako se već nalaziš u folderu `fast-api-course-my-work/sqlite_for_beginners/chinook`, dovoljna je kraća komanda:

```bash
sqlite3 chinook.db
```

Pokretanje `sqlite3 putanja/do/baze.db` otvara tu bazu kao glavnu bazu trenutne SQLite CLI konekcije. U SQLite CLI-jevoj terminologiji glavna baza dostupna je pod imenom `main`.

Proveri da li je otvoren pravi fajl:

```text
.databases
```

Zatim prikaži tabele:

```text
.tables
```

U Chinook bazi treba da vidiš tabele kao što su `artists`, `albums`, `tracks`, `customers`, `invoices` i `invoice_items`. Za pregled definicije pojedinačne tabele koristi, na primer:

```text
.schema albums
```

Ako ne vidiš očekivane tabele, prvo proveri putanju u `.databases`. Kada SQLite CLI otvori nepostojeći fajl, može napraviti novu praznu bazu, pa pogrešna putanja često izgleda kao „prazna Chinook baza“.

## Otvaranje baze nije isto što i `ATTACH DATABASE`

U svakodnevnom govoru možeš čuti da se baza „priključuje“ u SQLite, ali postoje dva različita postupka:

- **Otvaranje baze kao glavne:** pokreneš `sqlite3 putanja/do/baze.db` ili u CLI-ju izvršiš `.open putanja/do/baze.db`. Time se glavna baza te konekcije otvara ili menja.
- **Priključivanje dodatne baze SQL naredbom:** dok je jedna baza već otvorena, izvršiš `ATTACH DATABASE ... AS ime;`. Time se dodatna baza dodaje istoj konekciji pod posebnim imenom, bez zamene glavne baze.

Video-lekcija pokazuje prvi postupak: pokretanjem CLI-ja sa putanjom do `Chinook.db` otvara se glavna baza. To nije SQL naredba `ATTACH DATABASE`.

## Priključi Chinook kao dodatnu bazu

Pravi `ATTACH DATABASE` možeš da isprobaš bez menjanja fajla Chinook baze. Pokreni privremenu bazu u memoriji iz korena repozitorijuma:

```bash
sqlite3 :memory:
```

U SQLite CLI-ju izvrši SQL naredbu:

```sql
ATTACH DATABASE 'fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db' AS chinook;
```

Putanja u SQL stringu računa se u odnosu na direktorijum iz kog je pokrenut SQLite proces. Ako si CLI pokrenuo iz drugog foldera, prilagodi putanju ili koristi apsolutnu putanju.

Proveri obe baze u konekciji:

```text
.databases
```

Privremena baza je dostupna pod imenom `main`, a priključena Chinook baza pod imenom `chinook`. Tabele iz priključene baze možeš da kvalifikuješ imenom šeme:

```sql
SELECT Name
FROM chinook.artists
ORDER BY Name
LIMIT 5;
```

Ovde `chinook` nije novo ime fajla, već alias koji si zadao u `ATTACH DATABASE` naredbi. Kvalifikovano ime `chinook.artists` znači tabelu `artists` u priključenoj bazi. Imena kao što su `main`, `temp` i aliasi priključenih baza predstavljaju šeme dostupne u toj konekciji.

Kada završiš, možeš da ukloniš priključenu bazu iz konekcije:

```sql
DETACH DATABASE chinook;
```

`DETACH DATABASE` prekida vezu sa tom bazom u trenutnoj konekciji. Ne briše fajl `chinook.db`. Kada izađeš iz CLI-ja, konekcija se zatvara; sledeći put kada želiš dodatnu bazu, moraš je ponovo priključiti.

## Važne napomene za aplikacije

`ATTACH DATABASE` ne kopira podatke i ne spaja dve baze u jednu. Omogućava jednoj konekciji da pristupi tabelama iz više baza, na primer radi čitanja ili upita koji spajaju podatke. Samo priključivanje baze ne menja njene redove.

Priključena baza dostupna je samo u konekciji u kojoj je izvršena naredba `ATTACH`. U SQLAlchemy aplikaciji sa pool-om konekcija ne treba pretpostaviti da je svaka nova konekcija automatski priključila istu bazu. Takvo podešavanje mora se namerno uraditi za svaku konekciju kojoj je potrebno.

Strani ključevi ne povezuju tabele preko fajlova baze. Relacione tabele koje treba da garantuju referencijalni integritet obično treba držati u istoj SQLite bazi. `ATTACH` je koristan alat za određene scenarije, ali nije zamena za pažljivo modeliranje podataka niti za klijent-server bazu kada aplikaciji treba centralizovan višekorisnički rad.

Za ovu lekciju koristi Chinook samo za pregled i upite. Nemoj menjati ili brisati njene podatke; vežbaj izmene na posebnoj bazi koju napraviš za vežbe.

## Česte nedoumice

- **`.tables` ne prikazuje Chinook tabele:** proveri da li si otvorio ili priključio pravi fajl i da li `.databases` prikazuje očekivanu putanju.
- **CLI kaže da tabela ne postoji:** kod priključene baze koristi prefiks aliasa, na primer `chinook.artists`.
- **`ATTACH` prijavljuje grešku pri otvaranju fajla:** proveri relativnu putanju, dozvole za čitanje i da li fajl zaista postoji.
- **Ne možeš da pronađeš bazu:** trenutni direktorijum terminala možda nije koren repozitorijuma. Putanje iz primera nisu relativne u odnosu na Markdown fajl.
- **Pogrešno si otvorio praznu bazu:** izađi iz CLI-ja, vrati se u terminal i ponovi komandu sa tačnom putanjom do `chinook.db`.

## Provera razumevanja

1. Koja je razlika između pokretanja `sqlite3 chinook.db` i SQL naredbe `ATTACH DATABASE`?
2. Šta predstavlja alias `chinook` u primeru i kako se koristi u imenu `chinook.artists`?
3. Da li `DETACH DATABASE chinook` briše fajl baze?
4. Zašto priključivanje baze u jednoj konekciji ne znači da će ona biti priključena u svakoj SQLAlchemy konekciji?
5. Zašto je važno proveriti `.databases` pre nego što zaključiš da je baza prazna?

## Vežbe

### Vežba 1 — Otvori Chinook

1. Iz VS Code terminala, koristeći putanju iz korena repozitorijuma, otvori `chinook.db` kao glavnu bazu.
2. U CLI-ju pokreni `.databases`, `.tables` i `.schema albums`.
3. Pronađi u izlazu `albums` strani ključ ka tabeli `artists`.
4. Izađi iz CLI-ja komandom `.quit` i ponovo otvori istu bazu.

### Vežba 2 — Priključi dodatnu bazu

1. Iz korena repozitorijuma pokreni `sqlite3 :memory:`.
2. Priključi Chinook bazu pod aliasom `chinook`.
3. Izvrši `.databases` i objasni razliku između `main` i `chinook`.
4. Pokreni `SELECT Name FROM chinook.artists ORDER BY Name LIMIT 5;`.
5. Izvrši `DETACH DATABASE chinook;` i proveri `.databases`.

### Vežba 3 — Istraži radne direktorijume

1. Pokreni `sqlite3` iz korena repozitorijuma i priključi Chinook putanjom iz lekcije.
2. Izađi iz CLI-ja, promeni trenutni direktorijum u folder `chinook` i ponovi postupak sa kraćom putanjom.
3. Objasni zašto ista relativna putanja ne mora da radi iz oba direktorijuma.

### Vežba 4 — Nacrtaj tok otvaranja

Nacrtaj dva kratka toka:

1. Terminal pokreće SQLite CLI, a `chinook.db` postaje glavna baza (`main`).
2. Terminal pokreće CLI nad `:memory:`, a Chinook se dodaje pod aliasom `chinook`.

U svakom toku označi kada se putanja razrešava i koliko dugo baza ostaje dostupna.
