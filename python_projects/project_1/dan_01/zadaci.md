# Dan 1: zadaci

Radi zadatke redom. Cilj nije da prepišeš ceo program, nego da razumeš po jedan
deo i proveriš ga pre nego što pređeš na sledeći.

## 1. Pokreni početni prozor

Iz korena repozitorijuma aktiviraj postojeće `.venv` okruženje, instaliraj
zavisnosti prema uputstvu iz glavnog `README.md` fajla i pokreni aplikaciju.

Proveri da li se otvara prozor sa naslovom „PDF Toolkit“ i porukom da je početni
prozor spreman.

---

## 2. Objasni početni kod

Pre nego što menjaš `app.py`, pokušaj svojim rečima da objasniš:

1. Zašto `PdfToolkitApp` nasleđuje `ctk.CTk`?

- ODG: `PdfToolkitApp` nasleđuje `ctk.CTk` jer želi da koristi sve funkcionalnosti i izgled prilagođenog Tkinter prozora koji `ctk.CTk` pruža.

2. Šta radi `super().__init__()`?

- ODG: `super().__init__()` poziva konstruktor roditeljske klase `ctk.CTk`, čime se inicijalizuje ceo prozor i sve njegove funkcionalnosti pre nego što se dodaju dodatni elementi specifični za `PdfToolkitApp`.

3. Šta se podešava pozivima `title()`, `geometry()` i `minsize()`?

- ODG: `title()` postavlja naslov prozora, `geometry()` definiše početnu veličinu prozora, a `minsize()` postavlja minimalne dimenzije prozora ispod kojih korisnik ne može da ga smanji.

4. Zašto se `mainloop()` poziva tek pošto je prozor napravljen?

- ODG: `mainloop()` pokreće glavnu petlju događaja Tkinter prozora, koja čeka i obrađuje korisničke akcije. Ako se pozove pre nego što je prozor potpuno napravljen, događaji ne bi mogli pravilno da se obrađuju i prozor možda ne bi bio prikazan ispravno.

Ne moraš imati savršene definicije. Važno je da otkriješ koji deo ti još nije
jasan.

---

## 3. Dodaj izbor PDF fajlova

Dodaj dugme „Izaberi PDF-ove“.

```python
self.choose_button = ctk.CTkButton(
    self, text="Izaberi PDF-ove", command=self.choose_pdf_files
)
self.choose_button.pack(pady=10)
```

Poveži dugme sa metodom koja otvara dijalog za izbor više fajlova.

```python
def choose_pdf_files(self) -> None:
    from tkinter import filedialog

    file_paths = filedialog.askopenfilenames(
        title="Izaberi PDF fajlove",
        filetypes=[("PDF fajlovi", "*.pdf")],
    )
    if not file_paths:
        return

    for file_path in file_paths:
        if file_path not in self.pdf_paths:
            self.pdf_paths.append(file_path)
```

Sačuvaj izabrane putanje u stanju aplikacije.

```python
self.pdf_paths = []
```

Prikaži imena izabranih fajlova u prozoru.

```python
if self.pdf_paths:
    file_names = [os.path.basename(path) for path in self.pdf_paths]
    self.status_label.configure(text="\n".join(file_names))
```

Proveri da otkazivanje dijaloga ne obriše prethodni izbor i ne sruši aplikaciju.

```python
if not file_paths:
    return  # Otkazivanje dijaloga ne menja prethodni izbor
```

Za izbor koristi se dijalog iz `tkinter.filedialog`. Pokušaj prvo samostalno da
otkriješ potrebne argumente; ako zapneš, tražićemo ih zajedno.

---

## 4. Dodaj spajanje

- Dodaj dugme za spajanje izabranih fajlova.

```python
self.merge_button = ctk.CTkButton(
    self, text="Spoji PDF-ove", command=self.merge_pdfs
)
self.merge_button.pack(pady=10)
```

- Omogući korisniku da izabere lokaciju i ime novog PDF fajla.

```python
def merge_pdfs(self) -> None:
    from tkinter import filedialog

    output_path = filedialog.asksaveasfilename(
        title="Sačuvaj spojeni PDF",
        defaultextension=".pdf",
        filetypes=[("PDF fajlovi", "*.pdf")],
    )
    if not output_path:
        return  # Otkazivanje dijaloga ne nastavlja spajanje
```

- Koristi `PdfWriter` i `append()` da dodaš izabrane fajlove redom.

```python
from pypdf import PdfWriter

    writer = PdfWriter()
    for pdf_path in self.pdf_paths:
        writer.append(pdf_path)
```

- Sačuvaj rezultat u novi fajl, a ne preko jednog od ulaza.

```python
    writer.write(output_path)
```

- Prikaži poruku o uspešnom čuvanju.

```python
    self.status_label.configure(text=f"Spojeni PDF sačuvan: {output_path}")
```

---

## Provera završetka

Dan 1 je završen kada možeš da:

- pokreneš aplikaciju i objasniš šta radi `mainloop()`;
- izabereš najmanje dva PDF fajla;
- napraviš novi PDF čije su stranice spojene redom;
- potvrdiš da ulazni fajlovi nisu promenjeni;
- objasniš zašto se funkcija dugmetu prosleđuje bez zagrada.

Ako naiđeš na grešku, sačuvaj celu poruku i deo koda koji si poslednji menjao.
Rešićemo jednu stvar odjednom.
