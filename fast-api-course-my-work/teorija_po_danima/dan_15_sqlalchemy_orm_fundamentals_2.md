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

U `catalog.py`:

- U klasi/tabeli `Kategorija` obavezni su `naziv` i `slug` kategorije, dok `aktivnost` i `nivo kategorije` ostaju `ne-nullable` i imaju početne vrednosti `default=False` i `0`.

- Klasa/tabela `Proizvod` sada zahteva `tekstualna polja` za `naziv` i `opis`, `boolean statuse` za `aktivan` i `digitalni`, `vremenske oznake` za `kreirano_u` i `izmenjeno_u` i `numerička polja` za `cenu`.

- U klasi/tabeli `StanjeZaliha` kolona `količina` ima default `0` i `nullable=False`, kao i `poslednja_provera` koja tako ima `nullable=False` i samim time kao i `količina` mora biti prosleđena. `poslednja_provera` za registrovanje vremena promene koristi `DateTime(timezone=True)` način definisanja kolone. Ovaj model osigurava da se svaka promena stanja zaliha beleži sa vremenskom oznakom.

U `models/promotions.py` imamo klasu/tabelu `PromotivniDogadjaj` gde su `naziv`, `datum_pocetka`, `datum_zavrsetka` i `umanjenja cene` promotivnog događaja postali obavezni.

Ne navodi se `Mapped[... | None]` za ova polja, već koristi `Mapped[...]` sa `nullable=False`. Napomena da `nullable=False` ne sprečava prazan string; to je samo ograničenje baze. Takođe, ne navođenje `None` u anotaciji automatski govori SQLAlchemy-ju da polje ne može biti `NULL` pa je `nullable=False` redundantno, i ne mora se eksplicitno navoditi osim radi jasnoće.

Takođe imamo i klasu/tabelu `VezaProizvodaIPromocije` koja povezuje proizvode sa promotivnim događajima. Оna je trenutno prazna u smislu da ima samo primarni ključ (kolona `id`) i još uvek nema dodatnih kolona za strane ključeve koji bi povezivali proizvode i promotivne događaje. Kasnija uloga ove tabele će biti da uspostavi mnogostruku vezu između proizvoda i promotivnih događaja, omogućavajući da jedan proizvod može biti deo više promocija (`one-to-many`), a jedna promocija može obuhvatiti više proizvoda (`many-to-one`).

U `models/orders.py` imamo klasu/tabelu `Korisnik` i `Porudzbina` gde su korisnicko_ime, email, lozinka i količina stavke već bili ne-nullable, pa su ostali neizmenjeni. Vremena kreiranja i izmene porudžbine sada su tipizovana kao obavezna.

---

### Zašto postoje dva signala

SQLAlchemy 2.x može da zaključi nullability iz `Mapped[T]` i `Mapped[T | None]`. Ipak, ovde navodimo `nullable=False` eksplicitno zato što je lekcija upravo o ograničenju baze.

`Anotacija` pomaže da se Python kod i alati za tipove slažu sa ograničenjem

`nullable metapodatak` definiše SQL kolonu.

`None` nije dozvoljen za `Mapped[T]` obavezno polje, a `nullable=False` će sprečiti bazu da sačuva SQL vrednost `NULL`.

Ovo `ne` odbija `prazan string niti tekst sastavljen od razmaka`. To je posebna validacija. U ovoj lekciji još ne dodajemo `Pydantic` validatore niti `CHECK` ograničenja.

---

### Praktična korekcija za `izmenjeno_u`

Kurski source postavlja `updated_at` kao `nullable=False` uz `onupdate=func.now()`, ali nema početni default. Sam `onupdate` ne daje vrednost pri `INSERT`, pa bi zapis bez eksplicitnog `updated_at` pao na `NOT NULL` ograničenju.

U praktičnim modelima sam zato postavio `default=func.now()` uz postojeći `onupdate=func.now()` za `Proizvod.izmenjeno_u` i `Porudzbina.izmenjeno_u`. Polje dobija početnu vrednost pri unosu, a kasniji SQLAlchemy `UPDATE` može da osveži vreme. Ovo je namerna praktična popravka, nije tvrdnja da je tako napisano u kurskom source-u. Kasnije ćemo kroz lekciju 09 detaljnije razdvojiti default ponašanja.

---

## Koraci implementacije

1. **Kategorija:** naziv i slug su postali `Mapped[str]` sa `nullable=False`; `aktivna` i `nivo` su obavezni, uz `default=False` i `default=0`.
2. **Proizvod:** naziv, slug, opis, digitalni status, aktivnost, vreme kreiranja, vreme izmene i cena su nenullable. Statusi imaju `False` default, vreme kreiranja `func.now()`, a vreme izmene i početni default i `onupdate`.
3. **Stanje zaliha:** količina je obavezna sa default-om `0`; vreme poslednje provere je obavezno i nema default, pa aplikacija mora da ga prosledi.
4. **Promotivni događaj:** naziv, početni i završni datum i iznos umanjenja cene su obavezni.
5. **Korisnik i stavka porudžbine:** njihova postojeća `nullable=False` pravila već su odgovarala lekciji; nisu menjana.
6. **Porudžbina:** `kreirano_u` je obavezno sa `default=func.now()`. `izmenjeno_u` je obavezno i dobija praktični početni default uz `onupdate`.
7. **README:** ažuriran je pregled implementiranih lekcija i zabeležena korekcija za `izmenjeno_u`.

Nismo unapred dodavali `unique=True`, `nove primarne ključeve`, `strane ključeve`, `roditeljski ID` niti `ORM relacije`. To pripada narednim lekcijama; postojeći `id` ključevi ostaju tehnički preduslov za ORM modele.

---

## Provera

Provereno je da se paket modela uvozi i da sva polja osim primarnih ključeva imaju `nullable=False` u SQLAlchemy metapodacima. Ovo proverava mapiranje, ali još ne izvršava INSERT nad bazom; engine i sesije nisu deo ovog projekta u ovoj fazi.

---

## Beleške i pitanja

Odgovore na pitanja iz lekcije 08 dodaćemo ovde nakon provere razumevanja. Sledeća tema je lekcija 09: kada SQLAlchemy primenjuje `default`, kada bazu koristi `server_default` i kako callable default utiče na vrednost.

## Lekcija 09: Podrazumevane vrednosti

### Šta smo naučili

Default određuje vrednost za INSERT koji ne navede vrednost kolone. `nullable=False` i dalje zasebno zabranjuje `NULL`; default ne zamenjuje to ograničenje niti predstavlja poslovno obrazloženje za izabranu vrednost.

- `default=False` i `default=0` prosleđuju Python vrednost kroz SQLAlchemy-generisani upit.
- `default=func.now()` je SQLAlchemy client-side default koji ubacuje SQL izraz u INSERT; bazni server izvršava `now()`.
- Python callable, na primer `default=lambda: str(uuid.uuid4())`, poziva se u Python-u kada SQLAlchemy-u zatreba vrednost. Prosleđuje se funkcija, ne rezultat njenog poziva pri učitavanju modula.
- `server_default=...` opisuje `DEFAULT` u DDL-u; baza ga koristi i za klijente koji ne koriste ovaj SQLAlchemy model, ako izostave kolonu.

SQLAlchemy `default` važi za SQLAlchemy ORM i Core iskaze, ali ne i za SQL koji direktno izvršava drugi klijent. `server_default` važi na nivou baze. Ako se šema već kreira, dodavanje ili promena serverskog default-a zahteva migraciju; promena modela sama ne prepravlja postojeću tabelu.

### Kako se to odnosi na naše modele

Default-i za ovu lekciju već su bili prisutni u modelima posle prethodne implementacije, pa nije bilo potrebno ponovo menjati njihove deklaracije. Sada smo proverili njihovo značenje i zabeležili ih uz odgovarajuće kursne primere:

| Praktično polje                                  | Default                              | Razlog                                                                                 |
| ------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------- |
| `Kategorija.aktivna`                             | `False`                              | nova kategorija počinje neaktivna                                                      |
| `Kategorija.nivo`                                | `0`                                  | početni nivo kategorije                                                                |
| `Proizvod.digitalni`, `Proizvod.aktivan`         | `False`                              | početni boolean statusi                                                                |
| `StanjeZaliha.kolicina`                          | `0`                                  | početno stanje je nula evidentiranih komada                                            |
| `Proizvod.kreirano_u`, `Porudzbina.kreirano_u`   | `func.now()`                         | vreme unosa računa baza kroz SQL izraz u SQLAlchemy INSERT-u                           |
| `Proizvod.izmenjeno_u`, `Porudzbina.izmenjeno_u` | `func.now()` i `onupdate=func.now()` | obavezno polje dobija početno vreme i može da se osveži pri narednoj SQLAlchemy izmeni |

Nismo dodali `server_default` modelima: ova lekcija/source koristi SQLAlchemy `default`, a server default bi promenio ugovor tako da direktni upisi drugih klijenata dobijaju vrednost iz šeme. Teorija sada prikazuje i SQLAlchemy 2.x `mapped_column()` oblik za obe opcije, ali primer server default-a ostaje objašnjavajući i ne menja praktični model.

### Provera ponašanja

U memorijskoj SQLite bazi proveravamo da se ORM objekti mogu upisati bez ručnog zadavanja polja koja imaju default, da se boolean/integer vrednosti popune i da `func.now()` obezbedi vreme. Ova provera pokriva ponašanje SQLAlchemy default-a u testnoj bazi; ne dokazuje da isti SQL literal ili tip radi identično u svakoj produkcionoj bazi.

Lekcija 10 o jedinstvenim vrednostima obrađena je u nastavku. Sledeća je lekcija 11: primarni ključevi, koje naši modeli već imaju kao tehnički preduslov.

## Lekcija 10: Jedinstvene vrednosti

### Šta znači `unique=True`

Unique ograničenje sprečava bazu da sačuva ponovljenu vrednost u koloni. To je pravilo integriteta koje baza proverava pri INSERT-u i UPDATE-u. Aplikaciona provera može ranije da pronađe zauzet slug ili email i prikaže bolju poruku, ali ne zamenjuje ograničenje: dva paralelna zahteva mogu istovremeno proći proveru, dok baza garantuje da samo jedan može da sačuva istu vrednost.

`unique=True` na jednoj koloni pravi pravilo za tu kolonu. Ako su dve kolone svaka zasebno unique, kao `naziv` i `slug`, njihove vrednosti se proveravaju odvojeno; ne radi se o jedinstvenosti samo njihovog para. Za jedinstvenu kombinaciju više kolona koristi se `UniqueConstraint`.

### Izmene u praktičnim modelima

1. `Kategorija.naziv` i `Kategorija.slug` su dobili `unique=True` jer naziv i URL slug kategorije treba pojedinačno da identifikuju jednu kategoriju.
2. `Proizvod.naziv` i `Proizvod.slug` su dobili `unique=True` prema pravilima priloženog source primera.
3. `PromotivniDogadjaj.naziv` je dobio `unique=True` da bi nazivi promocija bili jedinstveni.
4. `Korisnik.korisnicko_ime` i `Korisnik.email` već su bili unique i ostali su takvi. Lozinka nije unique: različiti korisnici smeju imati istu lozinku.
5. Nismo dodali unique ograničenja na druge kolone, složeni `UniqueConstraint` ili poseban unique indeks; source ove lekcije ne traži takva pravila.

Sva navedena polja su već `nullable=False`, pa sada istovremeno važe dva nezavisna pravila: vrednost mora postojati i ne sme se ponoviti. Jedinstvenost ne normalizuje tekst. Da li su, na primer, `"TV"` i `"tv"` jednaki zavisi od baze i kolacije; normalizaciju slug-a/email-a treba definisati odvojeno.

### Ograničenje naspram indeksa i migracije

`unique=True` izražava pravilo integriteta. Unique indeks takođe može da sprovodi jedinstvenost i koristiti se za pretragu, ali ga ne treba dodavati redundantno uz već postojeće ograničenje. Za poslovno pravilo nad više kolona koristi se `UniqueConstraint`; u teoriji je prikazan imenovan SQLAlchemy 2.x primer.

Pošto se modeli trenutno ne koriste za održavanje postojeće baze kroz migracije, menjali smo samo SQLAlchemy metapodatke. Kada uvedemo migracije, unique ograničenje moraće da se primeni na šemu, a postojeći duplikati moraju prvo da se razreše. Samo promenjen Python model ne menja već kreiranu tabelu.

### Provera ponašanja

U privremenoj SQLite bazi proveriću da li duplikate odbijaju sva nova unique polja, kao i već postojeći `Korisnik.korisnicko_ime` i `Korisnik.email`. Takva provera potvrđuje ograničenja u tom testnom dijalektu; poređenje velikih/malih slova i kolacije ostaje zavisno od produkcione baze.

---

## Kako da razmišljamo o SQLAlchemy-ju: klijent ili server?

Da, kao početni mentalni model možeš da kažeš da se `SQLAlchemy nalazi na strani aplikacije i ponaša se kao deo klijentskog sloja koji pristupa bazi`. SQLAlchemy nije sam server baze i obično nije zaseban proces: to je Python biblioteka koju koristi naša aplikacija.

Preciznije, SQLAlchemy ORM/Core pravi i prati rad sa SQL iskazima. `Engine` povezuje SQLAlchemy sa konkretnom bazom: koristi dijalekt da SQL i vrednosti prilagodi bazi, a DBAPI drajver obavlja konkretno izvršavanje kroz odgovarajući interfejs (npr. `psycopg2` za PostgreSQL, `mysqlclient` za MySQL, `sqlite3` za SQLite). Kod PostgreSQL-a ili MySQL-a drajver komunicira sa odvojenim serverom baze. Kod SQLite-a baza je obično ugrađena u aplikacioni proces, pa nema nužno odvojenog serverskog procesa.

Pojednostavljen tok upisa:

1. Python aplikacija napravi ORM objekat i doda ga u `Session`.
2. Pri `flush()` ili `commit()`, ORM pripremi potrebne INSERT/UPDATE iskaze.
3. `Engine` i njegov dijalekt kompajliraju iskaz za izabranu bazu, a DBAPI drajver ga izvršava.
4. Baza izvršava SQL i sprovodi ograničenja kao što su `NOT NULL` i `UNIQUE`.
5. SQLAlchemy preuzima vraćene vrednosti i sinhronizuje stanje objekta u sesiji.

### Client-side i server-side default

U ovom primeru:

```python
aktivna: Mapped[bool] = mapped_column(
	Boolean,
	default=False,
	nullable=False,
)
```

- `aktivna` je ime Python atributa u ORM klasi.
- `Mapped[bool]` označava da se atribut mapira kao ORM polje sa Python vrednošću tipa `bool`; SQLAlchemy može iz anotacije da zaključi tip i nullable pravilo.
- `mapped_column(...)` zadaje SQLAlchemy konfiguraciju kolone.
- `Boolean` je tip kolone.
- `default=False` je SQLAlchemy client-side default podešavanje: SQLAlchemy ga primenjuje pri svom INSERT-u kada upis ne navede vrednost.
- `nullable=False` je pravilo kolone u šemi baze; bazu treba migrirati ili kreirati iz ažuriranih metapodataka da bi se pravilo stvarno sprovelo.

Zato se ne kaže da je cela desna strana „client-side default“. Konkretno, `default=False` jeste client-side default, dok `Boolean` i `nullable=False` opisuju druge osobine kolone.

Client-side govori gde je default definisan i ko ga primenjuje; ne mora da govori gde se vrednost izračunava. Na primer, `default=func.now()` je podešen kao SQLAlchemy default, ali SQLAlchemy ubacuje SQL izraz `now()` u INSERT, a bazni server izvršava tu funkciju. Nasuprot tome, `default=False` je obična Python vrednost koju SQLAlchemy prosleđuje u upitu.

`server_default=...` definiše `DEFAULT` u DDL-u baze. Tada bazni server obezbeđuje vrednost i klijentima koji ne koriste SQLAlchemy, pod uslovom da izostave kolonu ili navedu `DEFAULT`. Ako upit eksplicitno pošalje `NULL`, default se ne koristi; odlučujuće je da li kolona dozvoljava `NULL`.

### Python tip u `Mapped[...]` i SQL tip kolone

U deklaraciji:

```python
aktivna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

`Mapped[bool]` opisuje Python vrednost atributa. SQLAlchemy može iz `bool` da zaključi SQLAlchemy tip `Boolean`, pa je u ovom primeru eksplicitni `Boolean` delom radi jasnoće. `mapped_column(...) zadaje kolonu i njene postavke`, kao što su `tip`, `default`, `nullability`, `primary key` i `unique` ograničenja.

U anotiranom declarative modelu kolona se u mnogim slučajevima može zaključiti i samo iz `Mapped[...]`, ali `mapped_column()` nam omogućava da njenu SQLAlchemy konfiguraciju navedemo neposredno.

Razlika je važnija kod celih brojeva:

```python
nivo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
```

Python vrednost je i dalje `int`; Python nema poseban ugrađeni tip `SmallInteger`. SQLAlchemy `SmallInteger` precizira SQL tip kolone, dok bi `Mapped[int]` bez eksplicitnog SQL tipa obično vodio do SQLAlchemy `Integer` tipa. Dijalekt zatim prevodi SQLAlchemy tip u odgovarajući DDL tip za izabranu bazu.

Ukratko: `Mapped[T]` govori koji Python tip vrednosti očekujemo i mapiramo; `mapped_column(SQLAlchemyType, ...)` eksplicitno zadaje tip i pravila SQL kolone. Nisu suvišni jedan drugom, iako SQLAlchemy često može da zaključi deo konfiguracije iz anotacije.
