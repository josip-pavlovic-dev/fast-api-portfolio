# Teorija modula i biblioteka

Ovi vodiči prate module koje `app.py` koristi ili koje već obrađuju zadaci Dana 1 i Dana 2.

| Vodič                                                 | Šta pokriva                                             | Gde se koristi                                          |
| ----------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| [Tkinter](tkinter_teorija.md)                         | GUI osnove, vidžeti, događaji, raspored i glavni prozor | `CTk` aplikacija je izgrađena na Tk događajnom modelu   |
| [Tkinter file dialogs](tkinter_filedialog_teorija.md) | Izbor i čuvanje putanja kroz sistemske dijaloge         | `filedialog.askopenfilenames()` i `asksaveasfilename()` |
| [CustomTkinter](customtkinter_teorija.md)             | Glavni prozor, labele i dugmad                          | `CTk`, `CTkLabel`, `CTkButton`, `CTkFont`               |
| [os](os_teorija.md)                                   | Prikaz imena i bezbedno poređenje string putanja        | `os.path.basename()`, `realpath()`, `normcase()`        |
| [pypdf](pypdf_teorija.md)                             | Spajanje, čitanje i izdvajanje PDF stranica             | `PdfWriter`; `PdfReader` u Danu 2                       |

`pathlib` još nije deo aplikacije. Putanje za sada ostaju stringovi, prema
našem dogovoru; o `pathlib` ćemo napraviti vodič kada pređemo na taj modul.
