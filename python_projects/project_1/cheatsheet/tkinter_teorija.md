# Tkinter i CustomTkinter: teorija i brze reference

Ovaj dokument je tvoj lični cheatsheet za GUI deo PDF Toolkit projekta. Prati
tačno ono što smo do sada uradili u `app.py`, pa se vraćaj ovde kad god zapneš.
Svaki koncept ima: kratko objašnjenje, primer iz našeg koda i najčešće zamke.

## 1. Šta su Tkinter i CustomTkinter?

- **Tkinter** je standardna Python biblioteka za grafički interfejs (GUI). Dolazi
  uz Python instalaciju na većini sistema (na Linuxu ponekad kao poseban paket
  `python3-tk`). Pravi prozore, dugmad, polja za unos, dijaloge...
- **CustomTkinter** je dodatna biblioteka koja pruža stilizovane vidžete i prozor
  zasnovane na Tkinter/Tk tehnologiji. Detalji o njoj su u posebnom fajlu
  `customtkinter_teorija.md`.

U našoj aplikaciji prozor, dugmad i labele dolaze iz `customtkinter`, a dijalog za
fajlove iz `tkinter.filedialog`. Dijalozi su standardni Tkinter alati, kursevi
njihovog korišćenja su u `tkinter_filedialog_teorija.md`.

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

Dok `mainloop()` radi, Tk čeka događaje operativnog sistema: klik, unos sa
tastature, pomeranje prozora ili zatvaranje. Kada događaj stigne, poziva se
funkcija koja je za njega registrovana (npr. preko `command=`). Kada zatvoriš prozor,
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
- Ne mešaj `pack()` i `grid()` za decu istog roditeljskog vidžeta. Tkinter će
  prijaviti `TclError`, jer dva menadžera ne mogu istovremeno upravljati istim
  skupom dece.
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
znači „fajlovi sa nastavkom `.pdf`". U aktuelnom kodu koristimo taj obrazac.

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

## 12. Šta se dešava ispod Tkinter-a?

Tkinter je Python interfejs prema Tcl/Tk grafičkom sistemu. Python objekat
predstavlja prozor ili vidžet, a Tkinter šalje odgovarajuće naredbe grafičkom
sistemu. Zato neke greške iz rasporeda ili konfiguracije imaju naziv `TclError`:
problem je prijavio Tcl/Tk sloj, a ne nužno Python sintaksa.

U našoj aplikaciji:

- `ctk.CTk` kreira glavni prozor i pokreće isti Tk događajni model;
- `CTkLabel` i `CTkButton` prave vidžete;
- `tkinter.filedialog` traži od operativnog sistema dijalog za izbor ili čuvanje;
- `mainloop()` obrađuje događaje dok je prozor otvoren.

Tkinter aplikacija obično ima jedan glavni prozor. Ostale kontrole imaju
roditelja i žive unutar njega ili unutar nekog okvira. U našem kodu prvi argument
`self` u `CTkLabel(self, ...)` znači da je labela dete glavnog prozora.

## 13. Događaj, callback i vezana metoda

Kada napišemo:

```python
command=self.choose_pdf_files
```

Python dobija **vezanu metodu**: funkciju `choose_pdf_files` zajedno sa konkretnim
objektom aplikacije (`self`). Kada korisnik klikne, Tkinter poziva tu metodu na
tom objektu. Zato ona može da pristupi `self.pdf_paths` i `self.status_label`.

Callback funkcije u Tkinter-u izvršavaju se redom u GUI niti. Tkinter ne pokreće
automatski novu nit za svaki klik. To je razlog zašto callback ne treba da
obavlja dugo trajajući posao: dok se metoda izvršava, prozor ne može da obradi
ostale događaje i deluje zamrznuto.

`command=` je pogodan za uobičajenu akciju dugmeta i ne prosleđuje joj objekat
događaja. Za tastaturu, miš i druge događaje može se koristiti `bind()`:

```python
def on_key_press(event) -> None:
    print(event.keysym)

self.bind("<KeyPress>", on_key_press)
```

Ovde Tkinter prosleđuje callback-u objekat `event` sa podacima o događaju. Ovo
još nije potrebno za naš PDF Toolkit; primer služi da razlikuje `bind()` od
`command=`.

## 14. Menadžeri rasporeda detaljnije

`pack()`, `grid()` i `place()` odgovaraju na pitanje gde će vidžet biti prikazan.
Svaki menadžer upravlja samo decom svog roditelja.

Za `pack()` su česti argumenti:

```python
widget.pack(side="top", fill="x", expand=True, padx=8, pady=8)
```

- `side` bira stranu uz koju se vidžet slaže (`"top"`, `"bottom"`, `"left"`,
  `"right"`).
- `fill` određuje da li se širi po širini (`"x"`), visini (`"y"`) ili oboje
  (`"both"`).
- `expand=True` dozvoljava vidžetu da dobije deo slobodnog prostora roditelja.
- `padx` i `pady` dodaju razmak izvan vidžeta.

Ne moraš dodati sve ove opcije odjednom. U našem trenutnom prozoru dovoljan je
jednostavan vertikalni `pack(pady=10)`.

Za forme je `grid()` često prirodniji jer pozicije određuje redovima i kolonama.
Možeš koristiti `grid()` u jednom okviru, a `pack()` u drugom okviru koji je
njegovo dete; pravilo da se geometrijski menadžeri ne mešaju odnosi se na vidžete
sa istim roditeljem.

## 15. Menjanje vidžeta i osvežavanje prikaza

`configure()` menja opcije postojećeg vidžeta:

```python
self.status_label.configure(text="Spajanje PDF-ova u toku...")
```

Promena Python objekta i prikaz promene na ekranu nisu uvek isti trenutak.
Tkinter obično osveži prozor kada se kontrola vrati glavnoj petlji. U aplikaciji
koristimo:

```python
self.update_idletasks()
```

Ovo obrađuje zadatke koje Tkinter čeka u stanju mirovanja, kao što su iscrtavanje
vidžeta i preračunavanje rasporeda. U našem slučaju poziv pomaže da se poruka o
statusu prikaže pre nastavka. On **ne** pokreće spajanje u pozadini i ne čini
dugačak posao asinhronim.

## 16. Tkinter promenljive

Tkinter nudi promenljive kao `StringVar`, `IntVar` i `BooleanVar`, koje mogu da
povežu Python vrednost sa kontrolom. Na primer, `textvariable=some_string_var`
omogućava da promena `StringVar` vrednosti ažurira polje ili labelu.

Trenutno naš program čuva izabrane fajlove u običnoj Python listi
`self.pdf_paths` i tekst statusa menja pomoću `configure()`. To je jednostavnije
za početni projekat. Tkinter promenljive možemo uvesti kada dodamo polje za unos
brojeva stranica.

## 17. Zatvaranje i čišćenje resursa

Kada korisnik zatvori glavni prozor, `mainloop()` se završi i aplikacija izlazi.
Ako program otvori fajl ručno, treba ga zatvoriti i kada se desi greška. Zato u
aplikaciji koristimo kontekstni menadžer:

```python
with open(output_path, "wb") as pdf_file:
    writer.write(pdf_file)
```

Python zatvara fajl pri izlasku iz `with` bloka, uključujući slučaj kada zapis
prijavi grešku. Upravljanje fajlom je Python mehanizam, ali je važno za GUI tok
koji pokreće čuvanje.

## 18. Pravilo za duge poslove

Tkinter callback-i rade u glavnoj GUI niti. Kratak posao kao izbor putanje ili
spajanje nekoliko malih testnih PDF-ova je u redu. Ako bi obrada trajala dugo,
prozor ne bi odgovarao dok se callback ne završi. Kasnije bismo za veće fajlove
mogli koristiti radnu nit ili `after()` za periodično izvršavanje malog dela
posla, ali ne treba uvoditi niti pre nego što postoji stvarna potreba.
