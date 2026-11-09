# Dan 2: izdvajanje stranica

## Cilj dana

Naučićemo da iz jednog PDF fajla sačuvamo samo stranice koje korisnik traži.
Glavna stvar na koju treba paziti jeste razlika između načina na koji ljudi broje
stranice i načina na koji Python pristupa elementima liste.

## 1. Stranice u `pypdf`

PDF čitač može da otvori izabrani fajl i prikaže kolekciju stranica:

```python
from pypdf import PdfReader

reader = PdfReader(input_path)
page_count = len(reader.pages)
first_page = reader.pages[0]
```

Ljudi prvu stranicu zovu stranica 1. Python, kao i većina programskih jezika,
prvi element liste označava indeksom `0`. Zato je:

| Broj koji unosi korisnik | Indeks koji koristi Python |
| ------------------------ | -------------------------- |
| Stranica 1               | Indeks 0                   |
| Stranica 2               | Indeks 1                   |
| Stranica 3               | Indeks 2                   |

Prelaz sa korisničkog broja stranice na indeks radi se oduzimanjem 1. Taj
prelaz treba da bude jasan i da se obavi na jednom mestu u programu.

## 2. Dogovor o unosu stranica

Da unos bude jednostavan, aplikacija će prihvatati:

- `1` za jednu stranicu;
- `1, 4, 7` za nekoliko pojedinačnih stranica;
- `2-5` za neprekinuti opseg;
- `1, 3-5, 8` za kombinaciju.

Razmake oko brojeva možemo zanemariti. Ipak, `0`, negativni brojevi, prazan unos,
neispravan opseg kao `5-2` i broj veći od ukupnog broja stranica moraju biti
odbijeni jasnom porukom.

## 3. Pretvaranje teksta u brojeve

Unos iz polja GUI-ja je tekst, pa ga moramo razložiti i proveriti pre nego što
koristimo kao broj stranice. Korisna je podela odgovornosti:

1. Funkcija za parsiranje pretvara tekst, na primer `1, 3-5`, u listu
   korisničkih brojeva `[1, 3, 4, 5]`.
2. Provera potvrđuje da su svi brojevi u rasponu od 1 do broja stranica.
3. Deo koji pristupa `reader.pages` pretvara broj stranice u indeks oduzimanjem 1.

Ovako logiku parsiranja možemo proveriti bez otvaranja prozora. Ako se pojavi
greška, lakše ćemo utvrditi da li je problem u tekstu, proveri granica ili PDF-u.

## 4. Napraviti PDF od izabranih stranica

Kada je lista stranica proverena, svaku traženu stranicu možemo dodati u novi
`PdfWriter`:

```python
from pypdf import PdfWriter

writer = PdfWriter()
for page_number in page_numbers:
    writer.add_page(reader.pages[page_number - 1])

writer.write(output_path)
```

U ovom primeru `page_numbers` sadrži brojeve koje je uneo korisnik, počevši od

1. Zato se `- 1` nalazi baš pri pristupu `reader.pages`. Redosled u izlaznom
   fajlu prati redosled brojeva u unosu.

## 5. Provera unosa pre rada

Za PDF od 6 stranica, `1, 3-5` je dozvoljen unos, a `1, 7` nije: stranica 7 ne
postoji. Opseg `4-2` takođe odbijamo, jer početak ne može biti posle kraja.

Ove provere nisu samo dodatna pogodnost. One sprečavaju da aplikacija pokuša da
čita stranicu koja ne postoji i omogućavaju joj da korisniku kaže šta treba da
ispravi.

## 6. Kako tekst postaje lista stranica?

Korisnik unosi tekst, ali program ne može da koristi tekst kao broj stranice bez
pretvaranja i provere. Za unos `1, 3-5` možemo zamisliti sledeće korake:

1. Podeli tekst po zarezu: `"1, 3-5"` postaje `"1"` i `"3-5"`.
2. Ukloni razmake oko svakog dela.
3. Deo bez crtice predstavlja jednu stranicu; deo sa crticom predstavlja opseg.
4. Pretvori krajeve opsega u cele brojeve.
5. Napravi broj za svaku stranicu u opsegu.
6. Proveri da li su svi brojevi dozvoljeni za izabrani PDF.

Za razlaganje teksta postojeće Python string metode su dovoljne:

```python
selection = "1, 3-5"
parts = selection.split(",")
print(parts)  # ['1', ' 3-5']
```

`split(",")` deli string na mestu svakog zareza. Razmak ispred `3-5` ostaje,
pa se svaki deo očisti pomoću `strip()`:

```python
part = " 3-5 ".strip()
print(part)  # 3-5
```

Nemoj pretpostaviti da je unos već čist. Korisnik može uneti `1,3-5`,
`1, 3-5` ili `1 , 3 - 5`.

## 7. Pojedinačni brojevi, opsezi i `range()`

Ako je deo unosa `"3"`, funkcija `int()` može da ga pretvori u ceo broj:

```python
page_number = int("3")
```

Za opseg kao što je `"3-5"`, najpre razdvojimo početak i kraj:

```python
start_text, end_text = "3-5".split("-", maxsplit=1)
```

`maxsplit=1` znači da delimo najviše jednom. Zatim svaki tekst možemo očistiti
od razmaka i pretvoriti u ceo broj.

Python funkcija `range(start, stop)` uključuje početak, ali **ne uključuje**
`stop`:

```python
list(range(3, 5))      # [3, 4]
list(range(3, 5 + 1))  # [3, 4, 5]
```

Zato pri pretvaranju ljudski inkluzivnog opsega `3-5` koristimo `end + 1` kao
granice `range()` poziva. Bez toga bi se poslednja tražena stranica izostavila.

Za opseg možemo dodati više brojeva u listu, dok pojedinačni broj dodajemo samo
jednom. Lista čuva redosled dodavanja, pa unos `3, 1` treba da napravi izlaz sa
stranicom 3, pa stranicom 1. U prvoj verziji i ponovljeni broj znači ponovljenu
stranicu u izlaznom PDF-u.

## 8. Parsiranje i validacija su različiti koraci

**Parsiranje** odgovara na pitanje: „Koje brojeve stranica korisnik traži?"
Na primer, `"1, 3-5"` postaje `[1, 3, 4, 5]`.

**Validacija** odgovara na pitanje: „Da li su ti brojevi dozvoljeni za ovaj PDF?"
Za dokument od 7 stranica dozvoljeni korisnički brojevi su od 1 do 7.

Provere treba da pokriju bar sledeće slučajeve:

- prazan unos i prazne delove kao u `1,,3`;
- tekst koji nije ceo broj, kao `abc`;
- `0` i negativne brojeve;
- opseg u obrnutom redosledu, kao `5-2`;
- traženu stranicu veću od `total_pages`;
- opseg koji počinje ili se završava izvan granica PDF-a.

Korisnička greška ne bi trebalo da izazove traceback i prekine aplikaciju. Parser
može da odbaci unos izuzetkom `ValueError`, a GUI će kasnije uhvatiti taj
konkretan izuzetak i prikazati razumljivu poruku. Izbegavaj prazan `except:` ili
`except Exception` koji sakrije uzrok problema.

## 9. Provera granica pre indeksiranja

Proveru radimo nad korisničkim brojevima pre nego što pristupimo `reader.pages`.
Ovo je naročito važno zato što Python dozvoljava negativne indekse:

```python
reader.pages[-1]  # poslednja stranica, a ne greška
```

Ako korisnik unese `0`, a program odmah oduzme jedan, dobija indeks `-1` i
slučajno bira poslednju stranicu. Zato je redosled obavezan:

1. Parsiraj tekst u korisničke brojeve.
2. Proveri da su brojevi u rasponu `1..total_pages`.
3. Tek pri čitanju stranice pretvori broj u indeks oduzimanjem 1.

Tako konverzija sa ljudskog brojanja na Python indeks ostaje na jednom jasnom
mestu u kodu.

## 10. Testiraj parser bez prozora

Parser je najlakše razumeti ako ga prvo testiramo bez GUI-ja i bez otvaranja PDF-a.
`assert` poredi stvarni i očekivani rezultat i prekida proveru ako se razlikuju:

```python
assert parse_pages("1") == [1]
assert parse_pages("2-4") == [2, 3, 4]
assert parse_pages("1, 3-5") == [1, 3, 4, 5]
```

Zatim proveri pogrešne unose: prazan tekst, `abc`, `0`, `5-2` i broj veći od
ukupnog broja stranica. U zadatku prvo možeš samo ispisati rezultate i
uporediti ih; `pytest` ćemo uvoditi postepeno.

PDF uzorci pojedinačno imaju 1, 2 i 4 stranice. Za proveru PDF-a od najmanje
5 stranica koristi izlaz od 7 stranica koji si napravio spajanjem sva tri
uzorka u Danu 1.

## Pojmovi za ponavljanje

- **Indeks**: pozicija elementa u Python listi; prvi indeks je `0`.
- **Broj stranice**: ljudsko brojanje, počevši od `1`.
- **Parsiranje**: pretvaranje unosa iz jednog oblika, na primer teksta, u
  vrednosti koje program može da proveri i obradi.
- **Validacija**: provera da li je unos ispravan i dozvoljen.
- **Opseg**: niz uzastopnih stranica, na primer `2-5`.
- **Inkluzivan opseg**: opseg kod kog su uključeni i početak i kraj.
- **`range()`**: pravi brojeve od početka do vrednosti pre gornje granice.
- **`ValueError`**: izuzetak koji se, između ostalog, javlja kad tekst ne može
  da se pretvori u ceo broj pomoću `int()`.
- **Čista funkcija**: funkcija čiji rezultat zavisi od ulaza i koja ne menja
  prozor niti fajl-sistem; parser stranica možemo napisati na ovaj način.
