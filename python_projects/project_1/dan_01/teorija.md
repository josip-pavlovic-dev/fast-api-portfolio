# Dan 1: početni prozor i spajanje PDF-ova

## Cilj dana

Razumećemo kako se pokreće desktop prozor, šta znači da je GUI program vođen
događajima i kako biblioteka `pypdf` može da spoji PDF fajlove. Ne očekuje se da
se sve zapamti iz prvog čitanja; važno je da se posle možeš vratiti objašnjenju i
povezati ga sa kodom.

## 1. Šta aplikacija treba da radi?

Korisnik izabere dva ili više PDF fajlova, odredi gde želi da sačuva rezultat i
dobije jedan novi PDF. Svaka izabrana datoteka dodaje svoje stranice u rezultat.
Zato je redosled izabranih fajlova važan.

Pojednostavljen tok izgleda ovako:

1. Aplikacija otvori prozor i čeka korisnika.
2. Korisnik izabere ulazne PDF fajlove.
3. Korisnik izabere ime i lokaciju izlaznog fajla.
4. `pypdf` pročita ulaze i upiše stranice u novi PDF.
5. Aplikacija prikaže da li je čuvanje uspelo.

Za sada čuvamo novi fajl umesto da menjamo originalne fajlove. To smanjuje
mogućnost da slučajno izgubimo ulazne podatke.

## 2. Običan skript i GUI aplikacija

Običan skript uglavnom izvršava naredbe redom, od početka do kraja, pa se
završava. GUI aplikacija prvo napravi prozor i kontrole, a zatim čeka događaje
kao što su klik ili izbor fajla.

U našem kodu `mainloop()` započinje čekanje na događaje:

```python
app = PdfToolkitApp()
app.mainloop()
```

Dok je `mainloop()` aktivan, prozor ostaje otvoren. Kada korisnik klikne na
dugme, GUI poziva funkciju koja je povezana sa tim dugmetom. Takav način rada
zovemo **vođen događajima** (event-driven).

## 3. Funkcija kao povratni poziv

Kada dugmetu prosleđujemo funkciju koja će se pokrenuti kasnije, prosleđujemo
funkciju bez zagrada:

```python
button = ctk.CTkButton(parent, text="Spoji PDF-ove", command=merge_pdfs)
```

`command=merge_pdfs` znači: „pozovi ovu funkciju kada se dugme klikne“.

Ako napišemo `command=merge_pdfs()`, Python bi pozvao funkciju odmah, dok pravi
dugme. To obično nije ono što želimo. Reč **povratni poziv** (callback) označava
funkciju koju prosledimo drugom delu programa da bi je pozvao kasnije.

## 4. Šta čuvamo dok aplikacija radi?

Aplikacija treba da zapamti putanje fajlova koje je korisnik izabrao. Putanja je
adresa fajla u sistemu, na primer `Dokumenti/izvestaj.pdf`; nije isto što i
sadržaj celog PDF-a.

Za to ćemo koristiti listu. Lista čuva više vrednosti i njihov redosled:

```python
pdf_paths = ["racun.pdf", "ugovor.pdf"]
```

Kasnije ćemo putanje predstavljati objektima `Path` iz modula `pathlib`. Za
početak je važno razumeti ideju: aplikacija čuva spisak izabranih fajlova, a
spajanje koristi taj spisak redom.

## 5. Spajanje pomoću `pypdf`

`PdfWriter` predstavlja PDF koji gradimo. `append()` dodaje stranice ulaznog
fajla na kraj, a `write()` upisuje gotov rezultat:

```python
from pypdf import PdfWriter

writer = PdfWriter()
for pdf_path in pdf_paths:
    writer.append(pdf_path)

writer.write(output_path)
```

Ako su ulazni fajlovi redom `racun.pdf`, pa `ugovor.pdf`, njihove stranice će se
u istom redosledu pojaviti u izlaznom fajlu. `output_path` je putanja koju je
korisnik izabrao za novi PDF.

Ovo je samo primer osnovne ideje, ne gotov deo aplikacije. U aplikaciji moramo
još da dodamo izbor fajlova, izbor lokacije za čuvanje i prikaz rezultata.

## 6. Gde se obrada dešava?

`CustomTkinter` pravi prozor, dugmad i drugačije stilizovane Tkinter kontrole.
`pypdf` obrađuje PDF sadržaj. Obe biblioteke rade u našem Python programu, pa
ova aplikacija ne mora da šalje dokumente na internet.

PDF dokumenti mogu sadržati osetljive podatke. Za vežbanje koristi testne ili
izmišljene dokumente, a stvarne privatne fajlove nemoj stavljati u Git repozitorijum.

## 7. Greške su deo rada sa fajlovima

Izabrani fajl može biti oštećen, zaštićen lozinkom, nedostupan zbog dozvola ili
možda nema dovoljno prostora za čuvanje rezultata. Zato aplikacija ne treba da
prijavi uspeh ako čuvanje nije prošlo.

Prvo ćemo napraviti i razumeti osnovni uspešan tok. Zatim ćemo dodavati obradu
otkazivanja dijaloga, pogrešnih PDF fajlova i drugih grešaka. Nećemo prikrivati
problem praznim `except:` blokom.

## Pojmovi za ponavljanje

- **GUI**: grafički korisnički interfejs, kao što su prozor i dugmad.
- **Događaj**: nešto što se desi u interfejsu, na primer klik.
- **Callback**: funkcija koju GUI poziva kada se dogodi odgovarajući događaj.
- **Putanja**: lokacija fajla u sistemu.
- **Ulazni fajl**: PDF koji korisnik daje aplikaciji.
- **Izlazni fajl**: novi PDF koji aplikacija napravi.
