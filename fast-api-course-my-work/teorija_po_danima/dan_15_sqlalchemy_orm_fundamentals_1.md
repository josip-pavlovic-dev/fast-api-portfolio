# Dan 15: SQLAlchemy ORM Fundamentals 1

## Cilj rada

Danas nastavljamo modelovanje tabela kroz lekcije 08–13. Cilj je da do samoreferencirajuće veze razumemo kako se nullable pravilo, podrazumevane vrednosti, jedinstvenost, primarni ključevi i strani ključevi nadovezuju jedan na drugi. Radimo postepeno: implementiramo samo obrađenu lekciju, proverimo modele, pa tek onda prelazimo dalje.

Kurski snapshot-i ostaju neizmenjeni. U praktičnom paketu koristimo SQLAlchemy 2.x stil (`Mapped[...]`, `mapped_column()`), srpske ASCII nazive i postojeći root `.venv`. Ako praktični model namerno odstupi od source primera, razlog beležimo ovde.

## Plan za danas

1. **Lekcija 08 – Obavezna polja:** uskladiti `Mapped` anotacije i `nullable=False`; razlikovati `NULL` od praznog teksta.
2. **Lekcija 09 – Default vrednosti:** proći Python/SQLAlchemy default i `server_default`; proveriti kada se vrednosti zaista dodeljuju.
3. **Lekcija 10 – Jedinstvene vrednosti:** dodati ograničenja `unique` prema pravilima kursa i razlikovati ih od `NOT NULL`.
4. **Lekcija 11 – Primarni ključevi:** povezati već postojeći tehnički `id` sa pravilima i dopuniti razumevanje PK-a bez ponovnog dodavanja kolona.
5. **Lekcija 12 – Strani ključevi:** povezati odgovarajuće modele i razdvojiti FK kolonu od ORM `relationship()` atributa.
6. **Lekcija 13 – Samoreferencirajući FK:** dodati vezu kategorije sa roditeljskom kategorijom i razrešiti zašto root kategorija zahteva nullable FK.

Redosled može da se pomeri ako neka provera pokaže da treba dodatno utvrditi prethodni pojam. Kriterijum za završetak nije samo da se kod učita: treba umeti objasniti koje pravilo sprovodi anotacija, koje SQLAlchemy metapodatak, a koje baza.

## Lekcija 08: Obaveznost i `NULL`

### Šta smo promenili

U `models/catalog.py` i `models/promotions.py` polja koja su u lekciji obavezna više ne koriste opcione anotacije poput `Mapped[str | None]`. Prešla su na `Mapped[str]`, `Mapped[date]`, `Mapped[int]`, `Mapped[bool]` ili `Mapped[datetime]`, a deklaracije navode i `nullable=False`. Time Python tip i ograničenje kolone opisuju isto pravilo.

U `catalog.py` su obavezni naziv i slug kategorije; aktivnost i nivo kategorije ostaju nenullable i imaju početne vrednosti `False` i `0`. Proizvod sada zahteva tekstualna polja, boolean statuse, cenu i vremenske oznake. Količina zaliha ima default `0`, dok `poslednja_provera` mora biti prosleđena. U `promotions.py` naziv, datumi i iznos umanjenja cene promotivnog događaja postali su obavezni.

U `models/orders.py` korisničko ime, email, lozinka i količina stavke već su bili nenullable, pa su ostali neizmenjeni. Vremena kreiranja i izmene porudžbine sada su tipizovana kao obavezna.

### Zašto postoje dva signala

SQLAlchemy 2.x može da zaključi nullability iz `Mapped[T]` i `Mapped[T | None]`. Ipak, ovde navodimo `nullable=False` eksplicitno zato što je lekcija upravo o ograničenju baze. Anotacija pomaže da se Python kod i alati za tipove slažu sa ograničenjem; nullable metapodatak definiše SQL kolonu. `None` nije dozvoljen za `Mapped[T]` obavezno polje, a `nullable=False` će sprečiti bazu da sačuva SQL `NULL`.

Ovo ne odbija prazan string niti tekst sastavljen od razmaka. To je posebna validacija; u ovoj lekciji još ne dodajemo Pydantic validatore niti `CHECK` ograničenja.

### Praktična korekcija za `izmenjeno_u`

Kurski source postavlja `updated_at` kao `nullable=False` uz `onupdate=func.now()`, ali nema početni default. Sam `onupdate` ne daje vrednost pri `INSERT`, pa bi zapis bez eksplicitnog `updated_at` pao na `NOT NULL` ograničenju.

U praktičnim modelima sam zato postavio `default=func.now()` uz postojeći `onupdate=func.now()` za `Proizvod.izmenjeno_u` i `Porudzbina.izmenjeno_u`. Polje dobija početnu vrednost pri unosu, a kasniji SQLAlchemy `UPDATE` može da osveži vreme. Ovo je namerna praktična popravka, nije tvrdnja da je tako napisano u kurskom source-u. Kasnije ćemo kroz lekciju 09 detaljnije razdvojiti default ponašanja.

## Koraci implementacije

1. **Kategorija:** naziv i slug su postali `Mapped[str]` sa `nullable=False`; `aktivna` i `nivo` su obavezni, uz `default=False` i `default=0`.
2. **Proizvod:** naziv, slug, opis, digitalni status, aktivnost, vreme kreiranja, vreme izmene i cena su nenullable. Statusi imaju `False` default, vreme kreiranja `func.now()`, a vreme izmene i početni default i `onupdate`.
3. **Stanje zaliha:** količina je obavezna sa default-om `0`; vreme poslednje provere je obavezno i nema default, pa aplikacija mora da ga prosledi.
4. **Promotivni događaj:** naziv, početni i završni datum i iznos umanjenja cene su obavezni.
5. **Korisnik i stavka porudžbine:** njihova postojeća `nullable=False` pravila već su odgovarala lekciji; nisu menjana.
6. **Porudžbina:** `kreirano_u` je obavezno sa `default=func.now()`. `izmenjeno_u` je obavezno i dobija praktični početni default uz `onupdate`.
7. **README:** ažuriran je pregled implementiranih lekcija i zabeležena korekcija za `izmenjeno_u`.

Nismo unapred dodavali `unique=True`, nove primarne ključeve, strane ključeve, roditeljski ID niti ORM relacije. To pripada narednim lekcijama; postojeći `id` ključevi ostaju tehnički preduslov za ORM modele.

## Provera

Provereno je da se paket modela uvozi i da sva polja osim primarnih ključeva imaju `nullable=False` u SQLAlchemy metapodacima. Ovo proverava mapiranje, ali još ne izvršava INSERT nad bazom; engine i sesije nisu deo ovog projekta u ovoj fazi.

## Beleške i pitanja

Odgovore na pitanja iz lekcije 08 dodaćemo ovde nakon provere razumevanja. Sledeća tema je lekcija 09: kada SQLAlchemy primenjuje `default`, kada bazu koristi `server_default` i kako callable default utiče na vrednost.
