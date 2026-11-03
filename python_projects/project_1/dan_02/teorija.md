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

## Pojmovi za ponavljanje

- **Indeks**: pozicija elementa u Python listi; prvi indeks je `0`.
- **Parsiranje**: pretvaranje unosa iz jednog oblika, na primer teksta, u
  vrednosti koje program može da proveri i obradi.
- **Validacija**: provera da li je unos ispravan i dozvoljen.
- **Opseg**: niz uzastopnih stranica, na primer `2-5`.
- **Čista funkcija**: funkcija čiji rezultat zavisi od ulaza i koja ne menja
  prozor niti fajl-sistem; parser stranica možemo napisati na ovaj način.
