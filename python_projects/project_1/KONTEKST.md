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
- `self.pdf_paths` je lista string putanja, a `choose_pdf_files()` čuva izbor
  dijaloga u toj listi.
- U `sample_pdfs/` su tri sintetička PDF fajla sa 1, 2 i 4 stranicama.
- Spajanje i izdvajanje PDF stranica još nisu implementirani.
- Sledeći korak je proveriti izabrane putanje u terminalu i prikazati imena
  fajlova u prozoru; zatim ćemo implementirati spajanje.

## Tehničke odluke

- `CustomTkinter` koristimo za desktop interfejs.
- `pypdf` koristimo za čitanje, spajanje i izdvajanje stranica.
- Obrada se radi lokalno. Aplikacija ne šalje fajlove na internet.
