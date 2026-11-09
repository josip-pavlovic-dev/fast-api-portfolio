# Kontekst projekta

## Cilj

Napraviti desktop PDF Toolkit za portfolio, uz učenje kroz sopstvenu
implementaciju, korak po korak.

## Dogovoren način rada

- Objašnjenja i teorija su na srpskoj latinici.
- Svaki dan ima teoriju u `teorija.md` i praktičan rad u `zadaci.md`.
- Radimo samo trenutni mali cilj; ne preskačemo korake zbog brzine.
- Prvo pokušavaš zadatak, a pomoć i kompletno rešenje prilagođavamo onome gde
  zapneš.
- Za sada koristimo postojeće `.venv` okruženje iz korena repozitorijuma.
- Privatni PDF fajlovi i generisani izlazi ne pripadaju Git repozitorijumu.

## Trenutno stanje

- Napravljen je početni CustomTkinter prozor u `app.py`.
- Tkinter je proveren u aktivnom Python okruženju; dostupna je Tcl/Tk verzija 8.6.
- `self.pdf_paths` je lista string putanja; `choose_pdf_files()` DODAJE izbor
  dijaloga u listu (bez duplikata) i prikazuje imena fajlova u statusnoj labeli.
- `parsiranje_brojeva_stranica(tekst, total_pages)` je na nivou modula u `app.py`;
  proverava prazan unos, neispravne delove, pozitivnost, redosled opsega i
  granice PDF-a. Provereno sa 5 validnih i 15 nevalidnih slučajeva.
- U `cheatsheet/` postoji indeks i pet teorijskih vodiča: `tkinter`,
  `tkinter.filedialog`, `customtkinter`, `os` i `pypdf`. `pathlib` još ne koristimo;
  putanje su i dalje stringovi prema dogovoru.
- Dan 1 je završen: `merge_pdfs()` traži najmanje dva ulaza, pita za izlaznu
  putanju, sprečava izbor ulaznog fajla kao izlaza i čuva spojeni PDF.
- Spajanje testirano na tri uzorka: izlaz ima 7 stranica po redosledu ulaza, a
  izvorni PDF nije promenjen.
- U `sample_pdfs/` su tri sintetička PDF fajla sa 1, 2 i 4 stranicama.
- Sledeći korak: Dan 2 — povezati validirani parser sa `PdfReader` i GUI-jem;
  parser još nije pozvan iz aplikacionog toka.

## Tehničke odluke

- `CustomTkinter` koristimo za desktop interfejs.
- `pypdf` koristimo za čitanje, spajanje i izdvajanje stranica.
- Obrada se radi lokalno. Aplikacija ne šalje fajlove na internet.
