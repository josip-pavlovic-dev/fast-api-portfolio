# Lekcija 02: ERD dijagram baze podataka

## Cilj lekcije

Pre nego što napišemo ORM modele, potrebno je da razumemo strukturu podataka koju želimo da predstavimo. ERD (Entity-Relationship Diagram) je vizuelni prikaz entiteta, njihovih polja i veza. U ovoj lekciji ERD služi kao nacrt za modele koji će se razvijati u narednim lekcijama.

Kurs koristi fajl [ERD-1.drawio](source_code/ERD-1.drawio), koji se otvara u diagrams.net, ranije poznatom kao draw.io. Fajl je čitljiv diagrams.net XML, pa nije potrebna dodatna ekstenzija samo da bi se proverila njegova struktura.

## Šta prikazuje ERD?

### Entitet

Entitet predstavlja vrstu stvari o kojoj sistem čuva podatke. U relacionoj bazi se najčešće preslikava u tabelu. Primeri iz kursnog dizajna su kategorija, proizvod, korisnik, porudžbina i događaj promocije.

### Atribut

Atribut opisuje osobinu entiteta. U tabeli se najčešće preslikava u kolonu. Na primer, proizvod može imati naziv, opis, cenu i datum kreiranja. ERD pored naziva polja može da prikaže tip, ključ, dozvolu za `NULL`, podrazumevanu vrednost i pravila jedinstvenosti.

### Veza

Veza opisuje kako su zapisi jednog entiteta povezani sa zapisima drugog entiteta. U relacionoj bazi se najčešće ostvaruje stranim ključem, a za vezu više-prema-više i dodatnom tabelom.

## Ključevi i opcionalnost

- **Primarni ključ (PK)** jednoznačno identifikuje svaki red tabele. Ne sme biti `NULL`, a vrednost mora biti jedinstvena.
- **Strani ključ (FK)** čuva referencu na red u drugoj tabeli, ili na drugi red iste tabele kod samoreferentne veze.
- **Nullable polje** može da ima vrednost `NULL`. Kod stranog ključa to često odlučuje da li je veza obavezna ili opciona.
- **Unique ograničenje** sprečava da se ista vrednost, ili ista kombinacija vrednosti, pojavi više puta.
- **Podrazumevana vrednost** se koristi kada unos ne obezbedi vrednost za kolonu, u skladu sa tim gde je default definisan.

Ključna razlika: `NULL` nije isto što i prazan tekst, nula ili `False`. Na primer, `name = ''` i `name IS NULL` predstavljaju različita stanja i zahtevaju različita pravila.

## Kardinalnost veza

Kardinalnost govori koliko zapisa jedne strane može biti povezano sa zapisima druge strane.

### Jedan-prema-više (1:N)

Jedan zapis roditeljske tabele može biti povezan sa više zapisa druge tabele, dok svaki zapis sa strane „više“ pripada jednom roditelju. Strani ključ se obično nalazi na strani „više“.

Primer: jedna kategorija sadrži više proizvoda, a svaki proizvod ima jednu kategoriju. `product.category_id` zato referencira `category.id`.

### Više-prema-više (N:M)

Više zapisa prve tabele može biti povezano sa više zapisa druge tabele. Relaciona baza takvu vezu obično predstavlja posrednom tabelom koja sadrži strane ključeve ka obe strane.

Primer: proizvod može učestvovati u više promocija, a promocija može obuhvatati više proizvoda. Tabela `product_promotion_event` povezuje te zapise.

Ako posredna tabela ima dodatne podatke, kao što je količina proizvoda u porudžbini, ona je više od tehničke veze: predstavlja asocijacioni entitet sa sopstvenim značenjem.

### Jedan-prema-jedan (1:1)

Jedan zapis sa jedne strane odgovara najviše jednom zapisu sa druge strane. U bazi se to obično obezbeđuje stranim ključem koji je ujedno jedinstven. Samo crtanje 1:1 veze nije dovoljno: ograničenje mora postojati i u šemi baze.

### Samoreferentna veza

Tabela može imati strani ključ koji pokazuje na njen sopstveni primarni ključ. Tako se, na primer, kategorija može povezati sa roditeljskom kategorijom iz iste tabele. Gornji nivo hijerarhije nema roditelja, pa je strani ključ roditelja obično opcion.

## Kursni ERD: inventar i porudžbine

Transkript opisuje dijagram kao generički sistem za upravljanje zalihama. Naglašeno je da dizajn služi za vežbu karakteristika baza i ne mora biti potpuno veran produkcionom sistemu zaliha.

Entiteti prikazani u dijagramu obuhvataju:

- `category` / `inventory_category`: kategorije sa samoreferentnim roditeljem;
- `product`: proizvode koji pripadaju kategorijama;
- `promotion_event`: vremenski ograničene promocije;
- `product_promotion_event`: vezu između proizvoda i promocija;
- `stock_management`: evidenciju stanja zaliha za proizvod;
- `user`: korisnike;
- `order`: porudžbine korisnika;
- `order_product`: proizvode i njihove količine u okviru porudžbine.

Glavne relacije koje se vide u ERD-u i kasnijim modelima su:

| Veza                                | Značenje                                   | Uobičajeno preslikavanje                       |
| ----------------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Kategorija → proizvodi              | Jedna kategorija ima više proizvoda        | Strani ključ `product.category_id`             |
| Kategorija → roditeljska kategorija | Hijerarhija kategorija                     | Samostrani ključ, npr. `parent_id`             |
| Proizvodi ↔ promocije               | Proizvod može biti u više promocija        | Posredna tabela `product_promotion_event`      |
| Proizvod ↔ stanje zaliha            | Jedan zapis zaliha za jedan proizvod       | FK `stock_management.product_id` uz `UNIQUE`   |
| Korisnik → porudžbine               | Jedan korisnik može imati više porudžbina  | Strani ključ `order.user_id`                   |
| Porudžbine ↔ proizvodi              | Porudžbina sadrži više proizvoda i obrnuto | Posredni entitet `order_product`, sa količinom |

U ERD-u se pojavljuju i ograničenja za kategorije: neprazan naziv, format sluga, jedinstvena kombinacija naziva i nivoa, kao i granice za nivo. Kasniji kod demonstrira kako se deo takvih pravila može izraziti ograničenjima i automatizacijom.

## Osnovno snalaženje u diagrams.net

Transkript prikazuje sledeći radni tok:

1. Otvori postojeći `.drawio` dijagram, umesto da crtaš model od nule.
2. Sačuvaj kopiju ili izmene na izabrano mesto. Dijagram ne treba smatrati automatski sačuvanim; čuvaj izmene tokom rada.
3. Uvećavaj i umanjuj prikaz kontrolama za zumiranje. Za pomeranje po platnu koristi prevlačenje ili taster Space uz prevlačenje, zavisno od rasporeda i podešavanja aplikacije.
4. Pažljivo izaberi red ili ćeliju tabele pre nego što je menjaš. Dvoklikom menjaš tekst; opcije rasporeda omogućavaju dodavanje ili uklanjanje redova i kolona.
5. Vezu povuci sa tačke povezivanja jedne tabele do druge. Poveži je sa samim entitetom kako bi ostala zakačena kada se tabela pomeri.
6. Izaberi liniju veze i podesi oznake kardinalnosti na njenim krajevima. Stilovi kao jedna crta i „crow's foot“ predstavljaju različite krajeve veze.
7. Po potrebi dodaj tekst uz vezu, na primer naziv odnosa, i kopiraj postojeći entitet kada praviš sličnu novu tabelu.

Tačan položaj komandi može da se promeni između verzija diagrams.net, ali cilj je isti: tabela predstavlja entitet, a povezana linija predstavlja relaciju i njenu kardinalnost.

## Kako se dijagram preslikava u SQLAlchemy modele

ERD je projektni prikaz, ne Python kod. Pri pravljenju modela svaka odluka mora da se prevede u odgovarajući deo šeme:

- entitet postaje klasa nasleđena iz deklarativne baze;
- polje postaje kolona sa odgovarajućim tipom;
- PK postaje primarni ključ;
- FK čuva vezu i referencu na ciljnu tabelu;
- kardinalnost se sprovodi kombinacijom stranih ključeva, jedinstvenosti i ORM `relationship()` konfiguracije;
- pravila kao što su opseg vrednosti ili dozvoljeni format mogu postati ograničenja baze.

`relationship()` i `ForeignKey` nisu isto. Strani ključ je deo šeme baze i obezbeđuje referencijalni integritet. `relationship()` je ORM konfiguracija koja omogućava da se povezani Python objekti učitavaju i povezuju kroz atribute. Često se koriste zajedno, ali jedno ne zamenjuje drugo.

## Mapa source_code fajlova

Priloženi izvori počinju da se primenjuju od lekcije 03, „Starting a New SQLAlchemy Project“. Modeli su prikazani kao niz progresivnih primera koji dodaju osobine korak po korak:

| Fajl                            | Glavna tema                                               |
| ------------------------------- | --------------------------------------------------------- |
| `1_declarative_mapping.py`      | Deklarativna baza i `DeclarativeBase`                     |
| `2_defining_database_models.py` | Klase koje predstavljaju tabele                           |
| `3_common_field_types.py`       | Tipovi kolona: tekst, brojevi, logičke vrednosti i slično |
| `4_time_date_field.py`          | Datumska i vremenska polja                                |
| `5_Required.py`                 | Obavezne kolone i `nullable`                              |
| `6_default_values.py`           | Podrazumevane vrednosti i vremenski izrazi                |
| `7_unique_column.py`            | Jedinstvenost kolona                                      |
| `8_primary_key.py`              | Primarni ključevi                                         |
| `9_foreign_key.py`              | Strani ključevi i ORM veze                                |
| `10_self_referencing_fk.py`     | Samoreferentna veza kategorija                            |
| `11_on_delete.py`               | Ponašanje stranog ključa pri brisanju                     |
| `12_many_to_many.py`            | Veza proizvoda i promocija preko posredne tabele          |
| `13_one_to_one.py`              | Jedan-na-jedan veza proizvoda i zaliha                    |
| `14_constraints.py`             | Ograničenja `CHECK` i `UNIQUE`                            |
| `15_event_listener.py`          | SQLAlchemy mapper događaji pre upisa i izmene             |
| `16_trigger.py`                 | PostgreSQL trigger napravljen uz DDL događaj              |

Fajlovi ponavljaju mnoge iste modele, pa ih treba čitati kao uzastopne snimke razvoja, a ne kao module koje treba sve istovremeno uvesti u jednu aplikaciju. Verzija navedena u `requirement.txt` je SQLAlchemy 2.0.38.

## Važne razlike između ERD-a i demonstracionog koda

Ovaj pregled je dopuna uz transkript. Služi da se u narednim lekcijama primeri pravilno razumeju, a ne da se neprimećeno prihvate nedoslednosti.

- **Naziv kategorije:** ERD koristi `inventory_category` i prikazuje roditeljsko polje `parent` / `parent_id`; modeli koriste tabelu `category` i naziv `category_id`.
- **Opcionalnost roditelja:** ERD dozvoljava kategoriju bez roditelja. U `10_self_referencing_fk.py` argument `nullable=False` prosleđen je unutar `ForeignKey(...)`, umesto koloni. Opcionalnost pripada koloni; uz to, neobavezna vrednost je potrebna za korenske kategorije.
- **Različiti opisi polja:** ERD i modeli se ne poklapaju u svim dužinama stringova, tipovima datuma, imenima i skupovima kolona. Kod se razvija postepeno i nije u svakom fajlu potpuno usklađen sa svakim detaljem dijagrama.
- **Brisanje roditelja:** ERD koristi termin `PROTECT`, dok model koristi SQL `RESTRICT`. Oba izražavaju zabranu brisanja roditelja dok postoje zavisni zapisi, ali su nazivi i tačna semantika vezani za ORM/bazu; nisu univerzalno zamenljivi u svakom ORM-u.
- **Jedan-na-jedan:** model stanja zaliha kombinuje jedinstven strani ključ sa `uselist=False`. Jedinstveni FK obezbeđuje kardinalnost u bazi; `uselist=False` podešava ORM prikaz odnosa.
- **Veza porudžbine i proizvoda:** `order_product` sadrži i `quantity`, pa predstavlja asocijacioni entitet sa sopstvenim podatkom, a ne samo bezličnu veznu tabelu.
- **Lozinka korisnika:** ERD prikazuje polje `password` radi primera. U stvarnoj aplikaciji lozinka se ne čuva kao čisti tekst; čuva se bezbedan hash.
- **Ograničenja:** `14_constraints.py` postavlja neke `CHECK` uslove na `Product`, dok imena ograničenja pominju kategoriju. ERD opisuje i dodatna pravila za kategoriju koja taj fajl ne implementira sva.
- **Regex:** operator `~` u `CHECK` izrazu je PostgreSQL specifičan. SQL izrazi i podrška za regex razlikuju se između dijalekata baze.
- **Vremenske vrednosti:** `default=func.now()` i `onupdate=func.now()` nisu isto što i `server_default` ili trigger koji izvršava baza za svaki klijent. Takođe, `onupdate` ne obezbeđuje automatski početnu vrednost pri INSERT-u.
- **Događaji i triggeri:** listener iz `15_event_listener.py` izvršava Python kod kada se upis radi kroz SQLAlchemy. Trigger iz `16_trigger.py` izvršava PostgreSQL kod na nivou baze. Trigger može obuhvatiti i druge klijente baze, dok ORM listener ne može; trigger primer je zato vezan za PostgreSQL.

Ove razlike ćemo detaljno obrađivati kada stignemo do odgovarajućih lekcija, umesto da ih sve pokušamo rešiti u ovoj uvodnoj lekciji.

## Dodatak: praktična provera razumevanja

Za svaku vezu sa ERD-a pokušaj da odgovoriš:

1. Koja strana veze sadrži strani ključ?
2. Da li je strani ključ obavezan ili može biti `NULL`?
3. Kako se sprečava da baza prihvati vezu ka nepostojećem redu?
4. Da li je kardinalnost 1:1, 1:N ili N:M i kojim ograničenjem se sprovodi?
5. Da li posredna tabela sadrži dodatne poslovne podatke?

Ako ne možeš da odgovoriš samo gledajući liniju veze, pregledaj atribute entiteta i oznake ključeva. ERD se čita kao celina, a ne samo kao skup kutija.
