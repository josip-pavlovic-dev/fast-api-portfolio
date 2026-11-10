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

- Kod veze 1:N, strani ključ se obično nalazi u tabeli koja predstavlja "više" strane, dok "jedan" deo veze sadrži primarni ključ koji se referencira. Kod N:M veza, strani ključevi se nalaze u posrednoj tabeli koja povezuje dve glavne tabele.

2. Da li je strani ključ obavezan ili može biti `NULL`?

- Strani ključ može biti obavezan (`NOT NULL`) ili opcionalan (`NULL`). Ako je veza obavezna, strani ključ se definiše sa `NOT NULL`, dok kod opcionalne veze može biti `NULL`. Kod N:M veza, strani ključevi u posrednoj tabeli su obično obavezni, jer posredna tabela ne bi imala smisla bez oba povezivanja reda. Dakle, obaveznost stranog ključa zavisi od prirode veze i poslovnih pravila koja se primenjuju.

- Kod veze 1:1, strani ključ može biti postavljen na bilo kojoj strani, ali se obično stavlja na stranu koja je opcionalna ili koja logički zavisi od druge strane. Kod veze 1:N, strani ključ je uvek na strani "više". Kod N:M veza, strani ključevi su u posrednoj tabeli i obično su obavezni.

- Kod veze 1:1, ponekad se koristi jedinstveno ograničenje (`UNIQUE`) na stranom ključu kako bi se osigurala jedinstvenost veze. Kod veze 1:N, strani ključ ne mora biti jedinstven, dok kod N:M veza, kombinacija stranih ključeva u posrednoj tabeli obično ima jedinstveno ograničenje kako bi se sprečilo dupliranje veza.

- Kod veze 1:1, ponekad se koristi i primarni ključ na strani koja sadrži strani ključ kako bi se dodatno osigurala jedinstvenost i integritet veze. Kod N:M veza, primarni ključ posredne tabele se često sastoji od kombinacije stranih ključeva, čime se garantuje da svaki par povezanih redova bude jedinstven.

3. Kako se sprečava da baza prihvati vezu ka nepostojećem redu?

- Da bi se sprečilo da baza prihvati vezu ka nepostojećem redu, koristi se ograničenje stranog ključa (`FOREIGN KEY`) sa referencijalnim integritetom. Ovo osigurava da vrednost stranog ključa mora postojati u primarnoj tabeli na koju se referencira. Takođe, mogu se definisati akcije kao što su `ON DELETE CASCADE` ili `ON UPDATE CASCADE` kako bi se automatski ažurirale ili brisale povezane vrednosti.

- Kod veze 1:1, referencijalni integritet se često koristi zajedno sa jedinstvenim ograničenjem ili primarnim ključem kako bi se osigurala jedinstvenost veze. Kod veze 1:N, referencijalni integritet garantuje da strani ključ u tabeli "više" uvek referencira postojeći red u tabeli "jedan". Kod N:M veza, referencijalni integritet u posrednoj tabeli osigurava da svaki strani ključ referencira validan red u odgovarajućoj glavnoj tabeli.

4. Da li je kardinalnost 1:1, 1:N ili N:M i kojim ograničenjem se sprovodi?

- Kardinalnost predstavlja broj veza koje jedan red u jednoj tabeli može imati sa redovima u drugoj tabeli. Na primer, u vezi 1:1, jedan red u tabeli "jedan" može biti povezan sa najviše jednim redom u tabeli "više", dok u vezi 1:N, jedan red u tabeli "jedan" može biti povezan sa više redova u tabeli "više". U N:M vezi, jedan red u jednoj tabeli može biti povezan sa više redova u drugoj tabeli i obrnuto.

- Kod veze 1:1, kardinalnost se obično sprovodi jedinstvenim ograničenjem ili primarnim ključem na strani koja sadrži strani ključ. Kod veze 1:N, kardinalnost se sprovodi tako što strani ključ u tabeli "više" referencira primarni ključ u tabeli "jedan". Kod N:M veza, kardinalnost se sprovodi kombinacijom stranih ključeva u posrednoj tabeli, često uz jedinstveno ograničenje kako bi se sprečilo dupliranje veza.

5. Da li posredna tabela sadrži dodatne poslovne podatke?

- Ako posredna tabela sadrži dodatne poslovne podatke, to obično znači da veza između glavnih tabela nije samo čista veza, već ima i svoje atribute. U tom slučaju, posredna tabela se tretira kao zaseban entitet sa sopstvenim primarnim ključem, pored stranih ključeva koji referenciraju glavne tabele. Ako posredna tabela ne sadrži dodatne podatke, ona se često koristi samo za implementaciju N:M veze i njen primarni ključ se obično sastoji od kombinacije stranih ključeva.

- Prilikom analize ERD-a, važno je obratiti pažnju na sve atribute i oznake ključeva kako bi se pravilno razumela priroda veza između tabela. Samo gledanje linija veza može biti nedovoljno, jer dodatni atributi u posrednoj tabeli mogu značiti da veza ima dodatnu poslovnu logiku koja se mora uzeti u obzir.

- Takođe, obratite pažnju na oznake primarnih i stranih ključeva, jer one često otkrivaju da li je veza 1:1, 1:N ili N:M, i da li posredna tabela ima sopstveni identitet ili samo implementira vezu između glavnih tabela.
