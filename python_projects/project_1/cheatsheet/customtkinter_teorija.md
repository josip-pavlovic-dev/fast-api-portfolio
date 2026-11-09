# `customtkinter`: prozor i stilizovani vidžeti

`customtkinter` je treća strana Python biblioteka za izradu desktop GUI-ja.
PDF Toolkit ga koristi za glavni prozor, tekstualne labele i dugmad. Ona se
oslanja na Tkinter/Tk, ali obezbeđuje sopstvene stilizovane vidžete.

## 1. Instalacija i uvoz

Zavisnost je deklarisana u `requirements.txt` i instalira se u postojećem
virtuelnom okruženju:

```bash
python -m pip install -r python_projects/project_1/requirements.txt
```

Uvozimo paket pod kraćim imenom `ctk`:

```python
import customtkinter as ctk
```

`as ctk` je alias. On menja samo ime koje koristimo u ovom Python fajlu; ne
menja instalirani paket.

## 2. Glavni prozor `CTk`

```python
class PdfToolkitApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
```

`ctk.CTk` je glavni prozor CustomTkinter aplikacije. Nasleđivanjem možemo da
organizujemo stanje i ponašanje prozora u sopstvenoj klasi `PdfToolkitApp`.

`super().__init__()` poziva konstruktor `CTk` roditeljske klase. To inicijalizuje
osnovni prozor pre nego što mu dodamo naslov, dimenzije i vidžete.

Prozor koristi metode poznate iz Tkinter-a:

```python
self.title("PDF Toolkit")
self.geometry("720x480")
self.minsize(560, 360)
```

Ove metode podešavaju naslov, početnu veličinu i najmanju dozvoljenu veličinu.
Za dublje objašnjenje prozora, događaja i rasporeda pogledaj
`tkinter_teorija.md`.

## 3. Pravljenje vidžeta

CustomTkinter ima svoje widget klase, čija imena počinju sa `CTk`.

### `CTkLabel`

Labela prikazuje tekst:

```python
self.status_label = ctk.CTkLabel(
    self,
    text="Početni prozor je spreman.",
)
self.status_label.pack(padx=24, pady=12)
```

Prvi argument `self` je roditelj, odnosno prozor u koji labela pripada.
`pack()` je Tkinter geometrijski menadžer koji je postavlja unutar roditelja.

Tekst postojeće labele može da se promeni:

```python
self.status_label.configure(text="Spajanje je završeno.")
```

### `CTkButton`

Dugme prikazuje komandu i povezuje klik sa callback funkcijom:

```python
self.choose_pdf = ctk.CTkButton(
    self,
    text="Izaberi PDF-ove",
    command=self.choose_pdf_files,
)
self.choose_pdf.pack(pady=10)
```

Funkciju prosleđujemo bez zagrada. `command=self.choose_pdf_files` znači da
CustomTkinter poziva metodu na klik. Sa zagradama bi se ona pokrenula odmah
prilikom pravljenja dugmeta. Isti princip objašnjen je u Tkinter cheatsheet-u.

## 4. CustomTkinter nije `tkinter`

U aplikaciji se koriste oba:

| Potreba                      | Korišćena biblioteka      |
| ---------------------------- | ------------------------- |
| Glavni prozor                | `customtkinter.CTk`       |
| Labela                       | `customtkinter.CTkLabel`  |
| Dugme                        | `customtkinter.CTkButton` |
| Dijalog izbora/čuvanja fajla | `tkinter.filedialog`      |

CustomTkinter pruža sopstvene kontrole, dok standardni `tkinter.filedialog`
otvara ugrađene sistemske dijaloge. Tkinter callback-i, `mainloop()` i osnovni
menadžeri rasporeda i dalje su važan deo mentalnog modela.

## 5. Fontovi

U prozoru trenutno koristimo `CTkFont`:

```python
font=ctk.CTkFont(size=24, weight="bold")
```

- `size` je veličina fonta.
- `weight="bold"` traži podebljan stil.

Font se prosleđuje vidžetu kao vrednost podešavanja. `CTkFont` nije vidžet i
zato se na njega ne poziva `pack()`.

## 6. Tema i izgled

CustomTkinter omogućava podešavanje izgleda, na primer:

```python
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
```

`set_appearance_mode()` bira svetli, tamni ili sistemski režim, a
`set_default_color_theme()` bira ugrađenu paletu. Ovo su opcije, ne deo
trenutnog projekta. Dodavaćemo izgled tek kada osnovni tok aplikacije radi.

Pojedini vidžeti imaju opcije kao `fg_color`, `text_color`, `corner_radius` i
`hover_color`. Njihova konkretna podrška zavisi od vidžeta i verzije biblioteke.
Za vrednosti koje projekat koristi, prati instaliranu verziju i dokumentaciju.

## 7. Raspored i promena sadržaja

CustomTkinter vidžeti podržavaju Tkinter geometrijske menadžere, kao što su
`pack()` i `grid()`. I dalje važi pravilo: nemoj koristiti `pack()` i `grid()` za
decu istog roditelja. Zašto i kako ovi menadžeri rade objašnjeno je u
`tkinter_teorija.md`.

Kada se klikne dugme za izbor PDF-ova, program čuva putanje u `self.pdf_paths`,
pa tekst prikaza ažurira pomoću `self.status_label.configure(...)`. Vidžeti su
objekti, pa labelu možemo menjati i iz druge metode iste aplikacije.

## 8. Dugotrajan posao i responzivnost

CustomTkinter deli Tkinter-ov model događaja. Callback radi u GUI niti. Ako dugo
spajanje PDF-ova blokira tu nit, prozor ne može da obradi ostale klikove i
osvežavanja. Za male vežbene fajlove to nije problem; pozadinske niti ćemo
razmatrati samo ako stvarna upotreba aplikacije pokaže da su potrebne.

## Pojmovi za ponavljanje

- **Alias**: alternativno ime za uvezeni modul, ovde `ctk`.
- **Klasa `CTk`**: glavni prozor CustomTkinter aplikacije.
- **Vidžet**: kontrola u prozoru, kao labela ili dugme.
- **Callback**: funkcija koju dugme pozove nakon klika.
- **Tema**: skup podrazumevanih boja i stilova.
