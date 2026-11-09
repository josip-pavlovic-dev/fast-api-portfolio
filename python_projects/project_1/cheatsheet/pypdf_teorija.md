# `pypdf`: čitanje i pravljenje PDF fajlova

`pypdf` je spoljna Python biblioteka za rad sa PDF dokumentima. Za razliku od
`tkinter` i `os`, ne dolazi uz Python; zavisnost je navedena u
`requirements.txt`. PDF Toolkit je koristi za spajanje ulaznih PDF-ova. U Danu 2
koristićemo je i za čitanje broja stranica i izdvajanje odabranih stranica.

## 1. Uvoz potrebnog objekta

U aplikaciji se klasa uvozi unutar metode koja je koristi:

```python
from pypdf import PdfWriter
```

`PdfWriter` je klasa iz paketa `pypdf`, a ne poseban Python modul koji mi
napravimo. Lokalni uvoz znači da se ovaj import izvrši kada se pozove
`merge_pdfs()`. Možemo ga staviti i na vrh fajla; lokalni uvoz je trenutni izbor
aplikacije i olakšava da se vidi koja metoda koristi PDF writer.

## 2. Šta je writer?

Writer je objekat koji skuplja stranice namenjene novom PDF fajlu:

```python
writer = PdfWriter()
```

Odmah nakon pravljenja nema dodanih stranica. Sledeći koraci pune writer, a tek
potom ga upisujemo u izlaznu datoteku.

## 3. Dodavanje celih PDF-ova pomoću `append()`

```python
for pdf_path in self.pdf_paths:
    writer.append(pdf_path)
```

`self.pdf_paths` je lista string putanja koju puni dijalog. `append()` otvori
PDF na putanji i doda njegove stranice na kraj writer-a.

- Svaki ulaz dodaje se redom iz liste.
- Stranice unutar jednog ulaza zadržavaju svoj redosled.
- Sledeći PDF dodaje se posle stranica prethodnog PDF-a.
- Izvorni fajlovi se čitaju; writer priprema odvojeni izlaz.

Ako ulazni fajlovi imaju redom 1, 2 i 4 stranice, spojeni PDF treba da ima
`1 + 2 + 4 = 7` stranica.

## 4. Upis rezultata

U našoj aplikaciji izlazni fajl se otvara ovako:

```python
with open(output_path, "wb") as pdf_file:
    writer.write(pdf_file)
```

- `output_path` je string putanje koji je vratio „Sačuvaj kao" dijalog.
- `"w"` znači upisivanje.
- `"b"` znači binarni režim, koji je potreban za PDF bajtove.
- `with` zatvara fajl nakon završetka bloka, i kada dođe do greške.
- `writer.write(pdf_file)` upisuje PDF koji je writer sastavio.

Otvori izlazni fajl tek nakon što su ulazne putanje dodate writer-u i provereno je
da izlaz nije jedan od ulaza. Otvaranje postojećeg fajla sa `"wb"` može da
obriše njegov stari sadržaj.

## 5. Čitanje PDF-a pomoću `PdfReader`

Dan 2 koristiće `PdfReader`:

```python
from pypdf import PdfReader

reader = PdfReader(input_path)
page_count = len(reader.pages)
first_page = reader.pages[0]
```

`reader.pages` je kolekcija stranica. Njena dužina daje broj stranica, a prvi
indeks je `0`, kao kod Python lista. Ljudi obično broje stranice od `1`, zato
unos korisnika mora da se pretvori u indeks pomoću `page_number - 1` tek pošto
je broj proveren.

Kolekcija stranica se može čitati i proslediti u `PdfWriter.add_page()`:

```python
writer.add_page(reader.pages[page_number - 1])
```

U `pypdf_teorija.md` obrađujemo i `PdfReader`, iako trenutni `app.py` još koristi
samo `PdfWriter`.

## 6. `append()` naspram `add_page()`

- `writer.append(pdf_path)` dodaje stranice iz čitavog ulaznog PDF-a.
- `writer.add_page(page)` dodaje jednu stranicu koju smo prethodno izabrali.

Spajanje celih fajlova u Danu 1 prirodno koristi `append()`. Izdvajanje stranica
u Danu 2 koristiće `PdfReader` zajedno sa `add_page()`.

## 7. Odgovornosti biblioteka

`pypdf` obrađuje PDF strukturu; ne otvara GUI dijaloge i ne prikazuje statusne
poruke. Za to koristimo `tkinter.filedialog` i `customtkinter`.

Tok trenutnog spajanja:

1. Tkinter dijalog vrati putanje.
2. Python proveri listu i zaštiti ulazne putanje od prepisivanja.
3. `PdfWriter` i `append()` sastave stranice.
4. Python `open()` otvori izlaz u binarnom režimu.
5. `pypdf` upiše rezultat.
6. CustomTkinter labela prikaže status.

Svaki deo ima jednu odgovornost, što olakšava pronalaženje greške.

## 8. Greške i ograničenja

PDF može nedostajati, biti oštećen, biti zaključan lozinkom ili imati strukturu
koju biblioteka ne može da pročita. Naš trenutni kod još ne prikazuje prilagođenu
poruku za sve te slučajeve; to je kasnija dorada, a ne razlog da sakrijemo greške
praznim `except:` blokom.

Testiraj prvo sa malim, poznatim fajlovima iz `sample_pdfs/`. Nemoj menjati
originalne uzorke; izlaz čuvaj pod drugim imenom.

## Pojmovi za ponavljanje

- **Writer**: objekat koji gradi i upisuje PDF rezultat.
- **Reader**: objekat koji otvara PDF za čitanje.
- **Stranica (`page`)**: jedna PDF stranica predstavljena objektom.
- **Binarni režim**: režim fajla za bajtove, označen slovom `b` u `"wb"`.
- **Izuzetak**: objekat greške koji Python podiže kada operacija ne uspe.
