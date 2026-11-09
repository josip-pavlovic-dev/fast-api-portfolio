# Tkinter i CustomTkinter: teorija i brze reference

Ovaj dokument je tvoj lični cheatsheet za GUI deo PDF Toolkit projekta. Prati
tačno ono što smo do sada uradili u `app.py`, pa se vraćaj ovde kad god zapneš.
Svaki koncept ima: kratko objašnjenje, primer iz našeg koda i najčešće zamke.

## 1. Šta su Tkinter i CustomTkinter?

- **Tkinter** je standardna Python biblioteka za grafički interfejs (GUI). Dolazi
  uz Python instalaciju na većini sistema (na Linuxu ponekad kao poseban paket
  `python3-tk`). Pravi prozore, dugmad, polja za unos, dijaloge...
- **CustomTkinter** je biblioteka koja „oblači" Tkinter vidžete u moderan izgled
  (tamna tema, zaobljeni uglovi). Koristi se skoro isto kao Tkinter — naša
  aplikacija je zato dobra prilika da naučiš oba.

Ključna ideja: CustomTkinter nije zamena, nego nadogradnja. Zato u kodu mešamo
obe: prozor i dugmad su iz `customtkinter`, a dijalog za fajlove iz
`tkinter.filedialog`.

## 2. Anatomija naše aplikacije

```python
import customtkinter as ctk

class PdfToolkitApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        # ... podešavanje prozora i vidžeta ...

def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()

if __name__ == "__main__":
    main()
```

Tri stvari su ovde važne:

1. **Klasa nasleđuje `ctk.CTk`** — `CTk` je glavni prozor. Naša klasa „jeste"
   prozor, samo sa dodatnim stvarima koje mi definišemo.
2. **`super().__init__()`** — poziva konstruktor roditeljske klase. Bez tog
   poziva prozor ne bi bio inicijalizovan i ništa drugo ne bi radilo. Pravilo:
   uvek prva linija u `__init__` kada nasleđuješ Tkinter/CustomTkinter klasu.
3. **`mainloop()`** — pokreće petlju događaja. Detaljnije u poglavlju 4.

## 3. Osnovna podešavanja prozora

```python
self.title("PDF Toolkit")     # tekst u naslovnoj traci prozora
self.geometry("720x480")      # početna veličina: ŠIRINA x VISINA u pikselima
self.minsize(560, 360)        # najmanja dozvoljena veličina (korisnik ne može ispod)
```

- `geometry()` prima string u formatu `"ŠxV"` — obrati pažnju da je to slovo
  `x` između brojeva, ne znak množenja. Zato pišemo `"720x480"`, a ne `"720*480"`.
- `minsize()` je korisno da korisnik ne smanji prozor toliko da se sadržaj
  „pokvari" ili postane nečitljiv.

## 4. Petlja događaja (`mainloop`)

Obična skripta se izvršava od prve do poslednje linije i završi se. GUI program
radi drugačije:

```python
app = PdfToolkitApp()   # 1. napravi se prozor i svi vidžeti
app.mainloop()          # 2. program ULAZI U PETLJU i čeka događaje
```

Dok `mainloop()` radi, Tkinter neprestano proverava: „da li je korisnik nešto
kliknuo, kucao, zatvorio prozor?" Kad se događaj desi, poziva se funkcija koja
je za njega registrovana (npr. preko `command=`). Kada zatvoriš prozor,
`mainloop()` se završava i program se gasi.

**Zamka:** sve što napišeš _posle_ `mainloop()` izvršiće se tek kad se prozor
zatvori. Zato se sva logika aplikacije piše unutar klasa i callback funkcija, a
ne posle poziva `mainloop()`.

Ovakav način rada zove se **programiranje vođeno događajima** (event-driven).

## 5. Vidžeti: labela i dugme

**Vidžet** (widget) je svaki element interfejsa: labela, dugme, polje za unos...

### Labela — `CTkLabel`

```python
self.status_label = ctk.CTkLabel(
    self,                                # roditelj: kom prozoru pripada
    text="Početni prozor je spreman.",   # početni tekst
)
self.status_label.pack(padx=24, pady=12) # smeštanje u prozor (vidi poglavlje 6)
```

Labela služi za prikaz teksta. Kasnije tekst menjamo sa `configure()`:

```python
self.status_label.configure(text=f"Izabrano PDF fajlova: {len(self.pdf_paths)}")
```

**Zamka:** `configure` menja postojeći vidžet. Ne pravi novu labelu svaki put —
to bi nagomilavalo elemente jedan preko drugog.

### Dugme — `CTkButton`

```python
self.choose_pdf = ctk.CTkButton(
    self,
    text="Izaberi PDF-ove",
    command=self.choose_pdf_files,   # BEZ zagrada!
)
self.choose_pdf.pack(pady=10)
```

`command=` prima **funkciju koja će biti pozvana na klik**:

- `command=self.choose_pdf_files` — tačno. Prosleđuješ samu funkciju; Tkinter je
  poziva kasnije, kad se klikne.
- `command=self.choose_pdf_files()` — greška. Python bi pozvao funkciju **odmah**,
  dok pravi dugme, a `command` bi dobio njen rezultat (`None`). Dugme bi bilo
  „mrtvo".

Ako callback treba da primi argument, koristi se `lambda`:

```python
ctk.CTkButton(self, text="Gore", command=lambda: self.move(-1))
```

`lambda` pravi malu anonimnu funkciju koja će se izvršiti na klik i tek tada
pozvati `self.move(-1)` sa argumentom.

## 6. Smeštanje vidžeta: `pack()`

Samo pravljenje vidžeta ga **ne prikazuje**. Vidžet mora da se „smesti" u
prozor jednim od tri menadžera geometrije:

| Menadžer  | Kako radi                           | Kada koristiti                     |
| --------- | ----------------------------------- | ---------------------------------- |
| `pack()`  | slaže vidžete jedan uz/ispod drugog | jednostavni rasporedi (naš slučaj) |
| `grid()`  | tabela sa redovima i kolonama       | forme, složeniji rasporedi         |
| `place()` | tačne koordinate x, y               | retko; teško za održavanje         |

Mi koristimo `pack()`:

```python
self.status_label.pack(padx=24, pady=12)
```

- `padx` / `pady` — spoljašnji razmak (u pikselima) levo-desno / gore-dole.
- `pady=(32, 12)` — tuple koji definiše različit razmak gore i dole (32 piksela gore, 12 dole).
- `padx=(16, 8)` — isto važi za horizontalni razmak (16 piksela levo, 8 desno).

**Zamke:**

- Ako zaboraviš `pack()` (ili `grid()`), vidžet se neće videti — bez ikakve
  greške u terminalu.
- Ne mešaj `pack()` i `grid()` unutar istog roditelja — Tkinter će se „zaglaviti"
  pokušavajući da pomiri oba rasporeda.
- `pack()` vraća `None`, pa ovo ne radi što očekuješ:
  `self.label = ctk.CTkLabel(...).pack()` — `self.label` postaje `None`.
  Zato uvek dve linije: prvo pravljenje, pa `pack()`.

## 7. Stanje aplikacije: atributi instance

Aplikacija mora da „pamti" stvari između klikova. Za to služe atributi
instance — promenljive vezane za `self`:

```python
def __init__(self) -> None:
    super().__init__()
    self.pdf_paths: list[str] = []   # stanje: lista izabranih fajlova
```

- Kreiraju se u `__init__`, a koriste u svim metodama preko `self.`.
- Žive koliko i prozor. Kad se aplikacija zatvori, gube se.
- **Zamka:** promenljiva bez `self.` (npr. `pdf_paths = []` unutar metode) je
  lokalna — nestaje čim metoda završi. Zato ranije nije „pamtilo" fajlove.

Dodavanje bez duplikata (naš trenutni kod):

```python
for pdf_path in files:
    if pdf_path not in self.pdf_paths:
        self.pdf_paths.append(pdf_path)
```

`append()` dodaje na kraj postojeće liste, za razliku od
`self.pdf_paths = list(files)` koji **zamenjuje** celu listu.

## 8. Dijalozi za fajlove: `tkinter.filedialog`

Dijalog za izbor fajla je sistemski prozor koji Tkinter otvara za nas.
Uvozimo ga lokalno u metodi (ili na vrhu fajla — obe varijante su validne):

```python
from tkinter import filedialog

files = filedialog.askopenfilenames(
    parent=self,
    title="Izaberi PDF-ove",
    filetypes=(("PDF fajlovi", "*.pdf"),),
)
```

Najčešće funkcije:

| Funkcija              | Šta vraća                       | Kada                  |
| --------------------- | ------------------------------- | --------------------- |
| `askopenfilename()`   | jedna putanja (string) ili `""` | biranje jednog fajla  |
| `askopenfilenames()`  | tuple string putanja ili `()`   | biranje više fajlova  |
| `asksaveasfilename()` | putanja (string) ili `""`       | „Sačuvaj kao" dijalog |

**Važno za naš projekat:** ako korisnik klikne „Otkaži", rezultat je prazan tuple `()` (ili prazan string). Zato uvek proveravamo pre upotrebe:

```python
if not files:
    return   # korisnik je otkazao; ne diraj postojeće stanje
```

Bez ove provere, otkazivanje bi obrisalo prethodno izabrane fajlove ili
srušilo aplikaciju.

Argument `filetypes` prima tuple (torku) parova `(opis, obrazac)`. Obrazac `"*.pdf"`
znači „svi fajlovi koji se završavaju na .pdf". U našem kodu trenutno piše
`"*pdf"` — radi, ali preciznije je `"*.pdf"` jer uključuje tačku.

## 9. Kako sve funkcioniše zajedno (tok jednog klika)

1. `mainloop()` čeka.
2. Klikneš „Izaberi PDF-ove".
3. Tkinter poziva `self.choose_pdf_files()` (jer je registrovana preko `command=`).
4. Metoda otvori dijalog; dijalog vrati putanje kao tuple stringova.
5. Putanje dodajemo u `self.pdf_paths` (bez duplikata).
6. `self.status_label.configure(...)` ažurira tekst u prozoru.
7. Metoda se završava; `mainloop()` nastavlja da čeka sledeći događaj.

Ovo je obrazac koji ćeš videti u svakoj GUI aplikaciji: **događaj → callback →
promena stanja → osvežavanje prikaza**.

## 10. Mini rečnik pojmova

- **Vidžet** — element interfejsa (dugme, labela, polje...).
- **Roditelj (parent)** — prozor/okvir u koji vidžet pripada; prvi argument
  pri pravljenju vidžeta.
- **Callback** — funkcija koju prosledimo da je neko drugi pozove kasnije
  (ovde: Tkinter na klik).
- **Petlja događaja** — `mainloop()`; beskonačno čekanje i obrada događaja.
- **Stanje (state)** — podaci koje aplikacija pamti između događaja
  (`self.pdf_paths`).
- **Dijalog** — sistemski prozor za izbor fajla, čuvanje, potvrdu...
- **`configure()`** — metoda koja menja postojeći vidžet (tekst, boju...).

## 11. Brza dijagnostika kad nešto ne radi

| Simptom                                  | Verovatno uzrok                                         |
| ---------------------------------------- | ------------------------------------------------------- |
| Vidžet se ne vidi                        | zaboravljen `pack()`/`grid()`                           |
| Dugme odmah „uradi nešto" pri pokretanju | zagrade u `command=func()`                              |
| Klik ne radi ništa                       | `command` dobio `None` (isti uzrok iznad)               |
| „Ne pamti" podatke                       | lokalna promenljiva umesto `self.` atributa             |
| Otkazivanje dijaloga ruši/briše          | nedostaje `if not files: return`                        |
| `AttributeError: ... no attribute ...`   | atribut nije napravljen u `__init__` pre upotrebe       |
| Aplikacija se „smrzne"                   | duga operacija direktno u callback-u (naprednije: niti) |
