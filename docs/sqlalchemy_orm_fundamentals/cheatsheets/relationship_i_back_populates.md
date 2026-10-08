# `relationship()` i `back_populates`: kako razumeti ORM veze

Ovaj vodič koristi SQLAlchemy 2.x stil (`Mapped`, `mapped_column` i `relationship`) i polazi od veze `Kategorija`–`Proizvod` iz projekta. Glavna ideja je da razdvojiš tri stvari koje se često pomešaju:

1. **strani ključ** čuva i ograničava vezu u šemi baze;
2. **`relationship()`** daje Python pristup povezanom ORM objektu ili objektima;
3. **`back_populates`** uparuje ta dva ORM atributa tako da predstavljaju dve strane iste veze.

---

## Najkraći mentalni model

Za jednu kategoriju i više proizvoda baza ima približno ovakav oblik:

```text
kategorija
    id (PRIMARY KEY)

proizvod
    id (PRIMARY KEY)
    kategorija_id (FOREIGN KEY -> kategorija.id)
```

Python objekti kroz `relationship()` mogu da se koriste ovako:

```text
Kategorija.proizvodi  <---- ista veza ---->  Proizvod.kategorija
       lista proizvoda                         jedna kategorija
```

To su dve Python putanje do iste relacije, a ne dve zasebne FK kolone.

---

## Tvoj primer, deo po deo

U modelu `Kategorija` nalazi se:

```python
proizvodi: Mapped[list[Proizvod]] = relationship(
    back_populates="kategorija"
)
```

Čitaj deklaraciju ovim redom:

- **`proizvodi`** je ime Python atributa na objektu `Kategorija`. Zato ćeš pisati `kategorija.proizvodi`.
- **`Mapped[list[Proizvod]]`** kaže da je to mapirani ORM atribut čija je vrednost kolekcija `Proizvod` objekata. Jedna kategorija može imati nula, jedan ili više proizvoda. Ako ih nema, kolekcija je prazna lista, a ne `None`.
- **`relationship(...)`** kaže SQLAlchemy ORM-u kako da izloži povezane objekte kroz taj atribut. To samo po sebi nije kolona u tabeli.
- **`back_populates="kategorija"`** navodi ime odgovarajućeg ORM atributa na drugoj strani veze: `Proizvod.kategorija`.

Druga strana veze u modelu `Proizvod` izgleda ovako:

```python
kategorija_id: Mapped[int] = mapped_column(
    ForeignKey("kategorija.id"),
    nullable=False,
)

kategorija: Mapped[Kategorija] = relationship(
    back_populates="proizvodi"
)
```

Povezivanje imena je uzajamno:

| Atribut koji definišeš | Vrednost `back_populates` | Atribut na drugom modelu |
| ---------------------- | ------------------------- | ------------------------ |
| `Kategorija.proizvodi` | `"kategorija"`            | `Proizvod.kategorija`    |
| `Proizvod.kategorija`  | `"proizvodi"`             | `Kategorija.proizvodi`   |

Vrednost je **ime Python atributa**, ne ime klase, tabele ili FK kolone. Na primer `back_populates="kategorija_id"` bi bilo pogrešno: `kategorija_id` je kolona, a `back_populates` treba da pokaže na `relationship()` atribut `kategorija` iz modela `Proizvod`.

U projektnom modelu `catalog.py` koristi `from __future__ import annotations`, pa `Proizvod` može da se navede u tipu pre nego što je njegova klasa definisana (npr. `kategorija: Mapped[Kategorija] = relationship(...)` nije još definisana u trenutku kada se anotacija tipa `Mapped[Kategorija]` procenjuje). Ovo je korisno za izbegavanje problema sa redosledom definisanja klasa u Pythonu. Funkcioniše tako što Python tretira anotacije tipova kao stringove dok se ne izvrši evaluacija tipova.

---

## Strani ključ nije isto što i `relationship()`

`Proizvod.kategorija_id` i `Proizvod.kategorija` često deluju kao dupliranje,
ali imaju različite poslove:

| Deklaracija                                                   | Uloga                                                           |
| ------------------------------------------------------------- | --------------------------------------------------------------- |
| `kategorija_id: Mapped[int] = mapped_column(ForeignKey(...))` | Vrednost kolone i FK pravilo koje baza može da sprovede.        |
| `kategorija: Mapped[Kategorija] = relationship(...)`          | ORM atribut za rad sa povezanim objektom `Kategorija`.          |
| `proizvodi: Mapped[list[Proizvod]] = relationship(...)`       | ORM atribut za rad sa kolekcijom povezanih objekata `Proizvod`. |

FK kolona je na strani **više**: u tabeli `proizvod`. Više proizvoda može da sadrži isti `kategorija_id`. `Kategorija.proizvodi` ne stvara dodatnu FK kolonu u tabeli `kategorija` već samo omogućava navigaciju sa strane **jedan** (`Kategorija`).

`relationship()` se oslanja na FK mapiranje da bi ORM znao kako su tabele povezane. FK može da postoji i bez `relationship()`; tada baza i dalje ima referencijalno pravilo, ali nemaš taj praktičan Python atribut za navigaciju (`Kategorija.proizvodi` ili `Proizvod.kategorija`).

Obrnuto, `relationship()` nije zamena za FK ograničenje baze.

---

## Šta `back_populates` radi u Pythonu

Upareni atributi odražavaju izmene veze sa obe strane u smislu Python objekata. Kada su objekti u memoriji, dodela sa jedne strane ažurira drugu:

```python
proizvod.kategorija = kategorija
assert proizvod in kategorija.proizvodi

drugi_proizvod = Proizvod(...)
kategorija.proizvodi.append(drugi_proizvod)
assert drugi_proizvod.kategorija is kategorija
```

Provera `is` potvrđuje da obe putanje vode do iste Python instance. Nije potrebno prvo upisati objekte u bazu da bi njihovi upareni ORM atributi bili povezani.

Ovo povezivanje atributa u memoriji nije isto što i upis u bazu:

- dodela objekta ne izvršava odmah `INSERT` ili `UPDATE`;
- SQLAlchemy upisuje promene kada su objekti uključeni u ORM sesiju i sesija
  izvrši `flush()` (što se dešava i tokom `commit()`);
- ako je veza postojećeg objekta još neučitana, pristup atributu može da
  pokrene učitavanje iz baze. To je ponašanje učitavanja, a ne značenje
  `back_populates`.

---

## Kako tip `Mapped[...]` pomaže da prepoznaš oblik veze

U tipizovanom deklarativnom mapiranju, tip veze obično prati broj objekata
dostupnih preko atributa:

| Python atribut                 | Tip                      | Šta ćeš dobiti            |
| ------------------------------ | ------------------------ | ------------------------- |
| `Kategorija.proizvodi`         | `Mapped[list[Proizvod]]` | Kolekciju, možda praznu.  |
| `Proizvod.kategorija`          | `Mapped[Kategorija]`     | Jedan objekat kategorije. |
| Opciona veza ka jednom objektu | `Mapped[Model \| None]`  | Objekat ili `None`.       |

Tip govori ORM-u i čitaocu da li je atribut kolekcija ili skalar. On ne zamenjuje pravila baze kao što su `ForeignKey`, `nullable=False` ili `unique=True`.

Za vezu `Kategorija`–`Proizvod`:

- `Mapped[list[Proizvod]]` znači da kategorija može da se kreće kroz više proizvoda;
- `Mapped[Kategorija]` znači da pojedinačni proizvod ima jedan objekat kategorije (ne može imati više kategorija).
- `nullable=False` na `kategorija_id` zahteva da svaki red proizvoda ima kategoriju;
- to **ne** zahteva da svaka kategorija već ima proizvod. Kategorija bez proizvoda i dalje je dozvoljena.

Ako dete sme da nema roditelja, FK kolona i Python tip treba da izraze tu opcionalnost, na primer `Mapped[int | None]` uz `nullable=True`, i `Mapped[Kategorija | None]` za odgovarajući ORM atribut. Uskladi tipove i ograničenja sa pravilom koje želiš u domenu.

---

## Jedan-prema-više i više-prema-jedan

Ovo nisu dve različite veze. To su dva ugla gledanja na istu FK vezu:

```text
jedna Kategorija  <---->  nula ili više Proizvoda
jedan Proizvod    <---->  jedna Kategorija
```

Primer iz projekta:

```python
class Kategorija(Base):
    proizvodi: Mapped[list[Proizvod]] = relationship(
        back_populates="kategorija"
    )


class Proizvod(Base):
    kategorija_id: Mapped[int] = mapped_column(
        ForeignKey("kategorija.id"),
        nullable=False,
    )
    kategorija: Mapped[Kategorija] = relationship(
        back_populates="proizvodi"
    )
```

NAPOMENA: Uvek razmišljaj o vezi iz oba ugla – FK kolona određuje stranu „više“, a `relationship` atributi povezuju ORM objekte. `scalar` tipovi su tipovi koji predstavljaju pojedinačne objekte (`Mapped[Model]` ili `Mapped[Model | None]`), dok `kolekcije` predstavljaju više povezanih objekata (`Mapped[list[Model]]`).

Razmišljaj ovako:

1. FK je u redu proizvoda, zato je proizvod strana „više“.
2. Jedna FK vrednost pokazuje ka jednom redu kategorije, zato je `Proizvod.kategorija` skalar.
3. Više redova proizvoda smeju da pokažu ka istoj kategoriji, zato je `Kategorija.proizvodi` kolekcija.
4. `back_populates` spaja ta dva ORM atributa u par i omogućava navigaciju između povezanih objekata sa obe strane veze.

---

## Jedan-prema-jedan

Za primer koristimo `korisnika` i `profil`. `FK` se nalazi u tabeli `profil`, a `unique=True` sprečava da dva profila pripadaju istom korisniku:

```python
class Korisnik(Base):
    profil: Mapped[Profil | None] = relationship(
        back_populates="korisnik"
    )


class Profil(Base):
    korisnik_id: Mapped[int] = mapped_column(
        ForeignKey("korisnik.id"),
        nullable=False,
        unique=True,
    )
    korisnik: Mapped[Korisnik] = relationship(
        back_populates="profil"
    )
```

Ovde važi:

- `Profil.korisnik_id` je obavezan, pa svaki profil mora da pripada korisniku;
- `unique=True` dozvoljava najviše jedan profil za istog korisnika;
- `Korisnik.profil` je skalar, ali može biti `None` ako profil još ne postoji.

Zato je pravilo preciznije `Korisnik 1 ---- 0..1 Profil`, a ne obavezno „svaki korisnik ima profil“. Skalarni `Mapped[Profil | None]` sam po sebi **ne** kreira `UNIQUE` ograničenje. Jedinstvenost mora da postoji i u šemi baze.

---

## Više-prema-više direktno preko `secondary`

Kada je vezna tabela samo tehnički most i ne treba ti ORM objekat za svaki njen red, `relationship()` može da koristi `secondary`. U ovom primeru student može da pohađa više predmeta, a predmet može da ima više studenata:

```python
student_predmet = Table(
    "student_predmet",
    Base.metadata,
    Column("student_id", ForeignKey("student.id"), primary_key=True),
    Column("predmet_id", ForeignKey("predmet.id"), primary_key=True),
)


class Student(Base):
    predmeti: Mapped[list[Predmet]] = relationship(
        secondary=student_predmet,
        back_populates="studenti",
    )


class Predmet(Base):
    studenti: Mapped[list[Student]] = relationship(
        secondary=student_predmet,
        back_populates="predmeti",
    )
```

Obe strane su kolekcije. `secondary` kaže ORM-u koju veznu tabelu da koristi; `back_populates` i dalje navodi ime atributa na suprotnom modelu. Primarni ključ nad obe FK kolone sprečava da se isti par studenta i predmeta unese više puta.

---

## Više-prema-više kroz eksplicitni asocijativni model

Ako želiš da pristupaš samom redu vezne tabele kao ORM objektu, mapiraj je kao klasu. U projektu tu ulogu imaju `VezaProizvodaIPromocije` i `StavkaPorudzbine`.

Kod proizvoda i promocija postoje dva para:

| Asocijativni model                  | Atribut na drugom modelu                      |
| ----------------------------------- | --------------------------------------------- |
| `Proizvod.veze_promocija`           | `VezaProizvodaIPromocije.proizvod`            |
| `PromotivniDogadjaj.veze_proizvoda` | `VezaProizvodaIPromocije.promotivni_dogadjaj` |

Svaki par koristi `back_populates`. Veza između proizvoda i promotivnih događaja prolazi kroz objekte veze:

```text
Proizvod -> VezaProizvodaIPromocije -> PromotivniDogadjaj
```

Zato se do događaja može doći preko asocijativnog objekta:

```python
for veza in proizvod.veze_promocija:
    dogadjaj = veza.promotivni_dogadjaj
```

Slično tome, `Porudzbina.stavke` je upareno sa `StavkaPorudzbine.porudzbina`, a `Proizvod.stavke_porudzbine` sa `StavkaPorudzbine.proizvod`. Stavka nosi i poslovni podatak `kolicina`, pa je važno da se njome može upravljati kao posebnim ORM objektom.

Kod direktne veze preko `secondary` aplikacija radi sa proizvodima i promocijama, a ORM održava redove vezne tabele. Kod asocijativnog modela aplikacija radi i sa objektima veze. Izaberi jedan jasan obrazac za konkretan par modela; nemoj bez razloga nuditi dva nezavisna puta za menjanje istih veznih redova.

---

## Samoreferentna veza

Kod hijerarhije kategorija oba ORM atributa nalaze se na istoj klasi:

```python
roditelj_id: Mapped[int | None] = mapped_column(
    ForeignKey("kategorija.id"),
    nullable=True,
)

roditelj: Mapped[Kategorija | None] = relationship(
    back_populates="deca",
    remote_side=lambda: [Kategorija.id],
)

deca: Mapped[list[Kategorija]] = relationship(
    back_populates="roditelj"
)
```

Ovde `roditelj` pokazuje na jedan roditeljski objekat ili `None`, a `deca` je kolekcija potkategorija. `back_populates` uparuje `roditelj` sa `deca` kao i u prethodnim primerima. `remote_side` je dodatno podešavanje za samoreferentni slučaj: pomaže SQLAlchemy-ju da razlikuje roditeljski `id` od ID-ja deteta kada obe strane koriste istu tabelu. `roditelj_id` je nullable da bi korenska kategorija mogla da nema roditelja.

---

## Česte greške i kako da ih prepoznaš

1. **`back_populates` sadrži naziv klase ili kolone.** Treba da sadrži ime
   suprotnog `relationship()` atributa.
2. **Imena nisu uzajamna.** Ako jedna strana navodi `back_populates="kategorija"`, druga treba da navede `back_populates="proizvodi"`.
3. **Kolekcija je pogrešno shvaćena kao skalar.** `Mapped[list[T]]` predstavlja kolekciju, a `Mapped[T]` jedan objekat.
4. **Pretpostavlja se da je `relationship()` napravio FK.** FK mora biti definisan zasebno, osim ako je veza namerno podešena nekim drugim konfigurisanjem spajanja.
5. **Pretpostavlja se da tip pravi ograničenja baze.** Za veze 1:1 i dalje je potreban `UNIQUE`; za obaveznu vezu potreban je odgovarajući `NOT NULL`.
6. **Pretpostavlja se da `back_populates` podešava brisanje ili učitavanje.** Kaskade i FK `ondelete` pravila, kao i strategije učitavanja, podešavaju se odvojeno.

---

## `back_populates` naspram `backref`

`back_populates` je eksplicitni stil: definišeš oba ORM atributa i na svakom
navedeš ime odgovarajućeg atributa na suprotnoj strani. Tako se jasno vidi
oblik veze i lakše se tipizuju oba atributa pomoću `Mapped[...]`.

`backref` je kraći stil koji iz jedne deklaracije automatski pravi atribut na
drugoj strani. U novom tipizovanom kodu eksplicitni `back_populates` obično je
lakši za čitanje i održavanje. Ako postojeći model već koristi `backref`, ne
treba dodavati još jednu nezavisnu definiciju iste suprotne veze bez provere
postojećeg mapiranja.

---

## Brza metoda za čitanje bilo koje veze i razumevanje njenog oblika

Kada naiđeš na novu deklaraciju, odgovori redom na ova pitanja:

1. **Koje tabele su povezane?** Nađi njihove `__tablename__` vrednosti.
2. **Gde je FK?** Ta tabela je obično strana „više“ u vezi jedan-prema-više.
3. **Koliko objekata vraća ovaj atribut?** Pogledaj `Mapped[T]`, `Mapped[list[T]]` ili `Mapped[T | None]`.
4. **Koji je atribut sa druge strane?** Prati string u `back_populates`.
5. **Da li su imena uzajamno ispravna?** Proveri da li druga strana navodi početni atribut.
6. **Šta zaista garantuje baza?** Proveri FK, `nullable`, `unique` i eventualnu veznu tabelu; nemoj zaključivati samo iz Python tipa.

Za izdvojeni red:

```python
class Kategorija(Base):
    __tablename__ = "kategorija"

    proizvodi: Mapped[list[Proizvod]] = relationship(
        back_populates="kategorija"
    )
```

Odgovor je: „Na objektu tabele `kategorija`, atribut `proizvodi` je ORM kolekcija koja sadrži sve povezane objekte iz tabele `proizvod`. Suprotna strana je `Proizvod.kategorija`.

`FK` koji fizički povezuje tabele `kategorija` i `proizvod` je `Proizvod.kategorija_id`. `Proizvod` je klasa koja predstavlja tabelu `proizvod`. `kategorija_id` je kolona u tabeli `proizvod` koja referencira tabelu `kategorija`. Zato kategorija može imati više proizvoda, a svaki proizvod u ovom modelu mora pripadati jednoj kategoriji.“

---

## Pitanja za proveru razumevanja

1. Da li `back_populates="kategorija"` imenuje FK kolonu ili ORM atribut?

- **Odgovor:** `back_populates` imenuje ORM atribut, a ne FK kolonu. On povezuje dva `relationship()` atributa, omogućavajući ORM-u da održi konzistentnost između njih. Na primer, kada se doda `Proizvod` u `kategorija.proizvodi`, ORM automatski postavlja `Proizvod.kategorija` na odgovarajuću kategoriju.

2. Zašto je FK `kategorija_id` u tabeli `proizvod`, a ne u tabeli `kategorija`?

- **Odgovor:** FK `kategorija_id` je u tabeli `proizvod` jer jedan proizvod pripada jednoj kategoriji, dok jedna kategorija može imati više proizvoda. Dakle, veza je jedan-prema-više, i FK se postavlja na stranu „više“. Ovo omogućava da baza garantuje referencijalni integritet i pravilno mapiranje u ORM-u.

3. Šta je vrednost `kategorija.proizvodi` kada nema proizvoda?

- **Odgovor:** Kada kategorija nema proizvoda, `kategorija.proizvodi` je prazna lista (`[]`). ORM automatski inicijalizuje kolekciju, tako da uvek možeš iterirati preko nje bez provere da li je `None`.

4. Da li `nullable=False` na FK-u zahteva da svaka kategorija ima proizvod?

- **Odgovor:** Ne, `nullable=False` na FK-u `Proizvod.kategorija_id` zahteva da svaki proizvod ima kategoriju, ali ne zahteva da svaka kategorija ima proizvod. Kategorija može postojati bez proizvoda, ali svaki proizvod mora pripadati nekoj kategoriji.

5. Šta je potrebno dodati u šemu baze da skalarni odnos zaista bude 1:1?

- **Odgovor:** Da bi skalarni odnos zaista bio 1:1, potrebno je dodati jedinstveni indeks (`unique=True`) na FK kolonu u tabeli koja predstavlja „više“ stranu veze. Ovo osigurava da svaki red u tabeli „više“ može biti povezan sa najviše jednim redom u tabeli „jedan“. Bez ovog ograničenja, veza bi tehnički bila 1:N, čak i ako ORM atributi sugerišu 1:1.

6. Kada je praktičnije mapirati veznu tabelu kao klasu umesto koristiti `secondary`?

- **Odgovor:** Praktičnije je mapirati veznu tabelu kao klasu kada vezna tabela ima dodatne kolone osim FK-ova, ili kada želiš da imaš pristup ORM objektima vezne tabele direktno. Korišćenje `secondary` je jednostavnije kada vezna tabela služi samo za povezivanje dve tabele i nema dodatne podatke.

7. U samoreferentnom primeru, zašto su potrebni i `back_populates` i `remote_side`?

- **Odgovor:** `back_populates` omogućava ORM-u da održi konzistentnost između dva atributa u samoreferentnoj vezi, dok `remote_side` pomaže ORM-u da razlikuje „daleki“ kraj veze od „lokalnog“ kraja. Ovo je neophodno da bi ORM pravilno upravljao samoreferentnim odnosima i izbegao konfuziju prilikom učitavanja i ažuriranja objekata.

---

## Sažetak

- `ForeignKey` opisuje vezu na nivou šeme baze.
- `relationship()` daje pristup povezanim ORM objektima.
- `back_populates` uparuje dva `relationship()` atributa po njihovim imenima i
  održava ih usklađenim u Python objektima.
- Tip u `Mapped[...]` pomaže da prepoznaš kolekciju, skalar ili opcioni skalar,
  ali ne zamenjuje ograničenja baze.
- Oblik veze 1:1, 1:N ili M:N određuju FK raspored, jedinstvenost, opcionalnost
  i eventualna vezna tabela, a ne samo ime Python atributa.

---

## Povezane beleške i primeri iz projekta

- [Strani ključevi i `relationship()`](<../01_defining_database_models(tables)/12_creating_foreign_keys.md>)
- [Samoreferentne veze](<../01_defining_database_models(tables)/13_self_referencing_relationships.md>)
- [Veze više-prema-više](<../01_defining_database_models(tables)/15_defining_many_to_many_relationships.md>)
- [Veza jedan-prema-jedan](<../01_defining_database_models(tables)/16_creating_a_one_to_one_relationship.md>)
- [Praktični model `catalog.py`](../../../fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/catalog.py)
- [Praktični model `orders.py`](../../../fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/orders.py)
- [Praktični model `promotions.py`](../../../fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/promotions.py)
