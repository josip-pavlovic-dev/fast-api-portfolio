# `tkinter.filedialog`: dijalozi za izbor i čuvanje fajlova

`tkinter.filedialog` je standardni Python podmodul za sistemske dijaloge (otvaranje i čuvanje) fajlova.
PDF Toolkit ga koristi da korisnik odabere ulazne PDF-ove i mesto na kom će
sačuvati spojeni rezultat.

## 1. Uvoz podmodula

U aplikaciji koristimo:

```python
from tkinter import filedialog
```

`tkinter` je standardni GUI modul, a `filedialog` je njegov podmodul. Ovo ne
otvara dijalog; samo učitava funkcije koje možemo pozvati kasnije.

## 2. Dijalog za izbor jednog fajla

```python
file_path = filedialog.askopenfilename(
    parent=self,
    title="Izaberi PDF",
    filetypes=(("PDF fajlovi", "*.pdf"),),
)
```

`askopenfilename()` vraća putanju izabranog fajla kao string. Ako korisnik
otkaže, vraća prazan string `""`.

## 3. Dijalog za izbor više fajlova

Naš `choose_pdf_files()` koristi `askopenfilenames()`:

```python
files = filedialog.askopenfilenames(
    parent=self,
    title="Izaberi PDF-ove",
    filetypes=(("PDF fajlovi", "*.pdf"),),
)
```

Ova funkcija vraća kolekciju string putanja (u Tkinter-u je to tuple), na primer:

```python
(
    "/home/student/PDF-ovi/racun.pdf",
    "/home/student/PDF-ovi/ugovor.pdf",
)
```

To su putanje koje je dijalog vratio; ne treba ih ručno sastavljati. U aplikaciji
pretvaramo tuple u listu jer želimo da dodajemo izbore iz više otvaranja dijaloga:

```python
for pdf_path in files:
    if pdf_path not in self.pdf_paths:
        self.pdf_paths.append(pdf_path)
```

## 4. Otkazivanje dijaloga

Pri otkazivanju `askopenfilenames()` vraća praznu kolekciju, a `askopenfilename()`
ili `asksaveasfilename()` vraćaju prazan string. Provera `if not ...` radi za oba
slučaja:

```python
if not files:
    return
```

To sprečava da program nastavi bez putanje. U `choose_pdf_files()` čuvamo postojeći
izbor ako korisnik otkaže; u `merge_pdfs()` prikazujemo poruku da je čuvanje
otkazano.

## 5. Dijalog „Sačuvaj kao"

```python
output_path = filedialog.asksaveasfilename(
    parent=self,
    title="Sačuvaj spojeni PDF",
    defaultextension=".pdf",
    filetypes=(("PDF fajlovi", "*.pdf"),),
)
```

- `parent=self` vezuje dijalog za prozor aplikacije.
- `title` postavlja naslov dijaloga.
- `defaultextension=".pdf"` dodaje nastavak ako korisnik ne unese nastavak fajla.
- `filetypes` prikaže odgovarajući tip fajlova u dijalogu.

**Važno:** `asksaveasfilename()` samo vraća putanju kao string. Ne pravi PDF i ne
upisuje sadržaj. Upis obavljaju `open()` i `PdfWriter.write()` u `merge_pdfs()`.

## 6. Filter nije validacija

Obrazac `"*.pdf"` pomaže korisniku da lakše pronađe PDF fajlove, ali sam po sebi
ne dokazuje da je izabrani fajl ispravan PDF. Fajl može imati nastavak `.pdf`, a
biti oštećen ili imati neki drugi sadržaj. Biblioteka koja čita PDF mora da
proveri sadržaj i može prijaviti grešku.

## 7. Zašto koristimo `parent`?

`parent=self` govori sistemu kom prozoru dijalog pripada. To pomaže da dijalog
bude pravilno postavljen i da se ponaša kao deo naše aplikacije. U grafičkoj
aplikaciji je bolje proslediti roditeljski prozor nego otvoriti nevezan dijalog.

## 8. `askopenfile()` naspram `askopenfilename()`

Postoje i `askopenfile()` i `askopenfiles()`, koji otvaraju fajl i vraćaju Python
file objekte. Mi koristimo varijante čija imena završavaju sa `filename(s)`, jer
želimo samo putanje. Zatim `pypdf` otvara ulazne fajlove, a aplikacija bira kada
će ih obrađivati.

Pravilo za ovaj projekat:

- `askopenfilenames()` — vrati više ulaznih putanja;
- `asksaveasfilename()` — vrati izlaznu putanju;
- `pypdf` — čita PDF-ove i zapisuje rezultat.

## 9. Dijalog i GUI događaj

Poziv dijaloga se događa iz callback-a dugmeta. Dok je dijalog otvoren, korisnik
prvo završi izbor ili ga otkaže; tek onda se naredna linija Python koda izvršava.
To pojednostavljuje tok: prikaži dijalog, proveri rezultat, pa nastavi.

U aplikaciji je statusna labela osvežena sa `update_idletasks()` pre otvaranja
„Sačuvaj kao" dijaloga, kako bi poruka o statusu bila prikazana pre nego što
kontrola pređe na dijalog.

## Pojmovi za ponavljanje

- **Podmodul**: modul koji pripada većem paketu, kao `tkinter.filedialog`.
- **Putanja**: tekst koji označava lokaciju fajla.
- **Prazan rezultat**: znak da je korisnik otkazao dijalog.
- **Filter fajlova**: obrazac koji olakšava pronalaženje fajlova, ali ne proverava
  njihov sadržaj.
