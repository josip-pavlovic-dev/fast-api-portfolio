# `os`: rad sa putanjama u PDF Toolkit-u

`os` je Python standard library modul koji pruža funkcije vezane za operativni
sistem. Naš projekat ga koristi za dve stvari: da prikaže samo ime fajla i da
proveri da li je izlazna putanja ista kao neka ulazna putanja.

## 1. Uvoz modula

```python
import os
```

`os` dolazi uz Python. Ne treba ga instalirati preko `pip`-a. U trenutnom kodu
koristimo njegov podmodul `os.path`.

## 2. Putanja je string

U projektu smo odlučili da za sada putanje čuvamo kao stringove:

```python
self.pdf_paths: list[str] = []
```

Vrednost poput `"/home/user/PDF/racun.pdf"` je običan Python string koji sadrži
ime i lokaciju fajla. Pozivi iz `os.path` primaju string i vraćaju string; oni ne
pretvaraju našu listu u neku drugu strukturu podataka.

## 3. Prikaz imena fajla: `basename()`

Aplikacija prikazuje imena PDF fajlova, ne pune putanje:

```python
file_names = [os.path.basename(path) for path in self.pdf_paths]
```

`os.path.basename(path)` vrati poslednji deo putanje:

```python
os.path.basename("/home/user/PDF/racun.pdf")  # "racun.pdf"
```

List comprehension primenjuje `basename()` na svaku putanju i napravi novu
listu stringova. Originalna lista `self.pdf_paths` se ne menja.

## 4. Zašto proveravamo da li se izlaz poklapa sa ulazom?

Ako korisnik izabere ulazni PDF kao destinaciju, zapisivanje rezultata preko tog
fajla može da uništi original. U aplikaciji prvo oblikujemo izlaznu putanju:

```python
output_realpath = os.path.normcase(os.path.realpath(output_path))
```

- `os.path.realpath(path)` razrešava simboličke linkove i nepotrebne segmente
  putanje, kao što je `..`, i vraća putanju pogodnu za poređenje.
- `os.path.normcase(path)` normalizuje velika/mala slova i separatore prema
  operativnom sistemu. Na POSIX sistemima kao što je Linux obično ne menja ništa;
  na Windowsu može normalizovati razlike u velikim slovima i separatore.

Rezultat je i dalje string. Promenljiva `output_realpath` je samo lokalna vrednost
za ovu proveru; ne zamenjuje `output_path` i ne menja `self.pdf_paths`.

## 5. Set comprehension za ulazne putanje

```python
input_realpaths = {
    os.path.normcase(os.path.realpath(pdf_path))
    for pdf_path in self.pdf_paths
}
```

Ovo je **set comprehension**. Za svaki `pdf_path` iz liste:

1. `os.path.realpath()` normalizuje putanju;
2. `os.path.normcase()` primenjuje poređenje primereno sistemu;
3. rezultat se dodaje u skup.

Primer oblika rezultata:

```python
{
    "/home/user/PDF/racun.pdf",
    "/home/user/PDF/ugovor.pdf",
}
```

Skup je praktičan za proveru članstva, a duplikati bi se ionako pojavili samo
jednom. Ovaj izraz ne menja listu `self.pdf_paths`.

Razlika u odnosu na dict comprehension:

```python
{value for value in values}             # set comprehension: samo vrednosti
{key: value for key, value in pairs}    # dict comprehension: ključ i vrednost
```

## 6. Provera članstva

```python
if output_realpath in input_realpaths:
    self.status_label.configure(
        text="Izaberite izlazni fajl koji nije jedan od ulaznih PDF-ova."
    )
    return
```

Operator `in` proverava da li je string `output_realpath` element skupa
`input_realpaths`. Ako jeste, blokiramo nastavak metode. Provera je pre otvaranja
izlaza u režimu `"wb"`, koji bi postojeći fajl otvorio za upis i skratio njegov
sadržaj.

## 7. Zašto `realpath()` radi i kada izlaz još ne postoji?

Dijalog „Sačuvaj kao" često vraća putanju novog fajla koji još nije napravljen.
`realpath()` može da normalizuje i takvu putanju: u ovoj upotrebi nam treba
uporediv oblik imena, a ne da `os` otvara fajl. Stvarni izlaz se kreira kasnije,
kada aplikacija pozove `open()` i `writer.write()`.

Ova provera sprečava podudaranje putanja, uključujući uobičajene razlike kao
`folder/../ulaz.pdf`. Ona ne proverava da li je izabrana datoteka zaista validan
PDF; to je posao biblioteke `pypdf`.

## 8. `os.path` i `pathlib`

Trenutno koristimo stringove i `os.path`, kao što smo dogovorili. U Python-u
postoji i `pathlib.Path`, objekatni način rada sa putanjama. On nije upotrebljen
u trenutnom kodu i ne treba mešati `Path` objekte sa stringovima nasumično.

Kada budemo prešli na `pathlib`, ponovićemo istu zaštitu koristeći `Path` metode.
Za sada je važno da razumeš: `realpath()` i `normcase()` služe samo za poređenje,
a sačuvane putanje ostaju stringovi.

## Pojmovi za ponavljanje

- **Modul**: Python kod koji uvezemo i čije funkcije možemo koristiti.
- **Podmodul**: deo većeg modula/paketa; ovde `os.path`.
- **Bazno ime**: poslednji deo putanje, na primer `racun.pdf`.
- **Normalizacija putanje**: svođenje više zapisa iste lokacije u uporediv oblik.
- **Skup (`set`)**: kolekcija jedinstvenih elemenata, pogodna za proveru `in`.
- **Comprehension**: sažet zapis za pravljenje kolekcije iz postojeće kolekcije.
