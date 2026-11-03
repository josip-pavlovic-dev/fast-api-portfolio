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
- GUI pokretanje još nije provereno: Linux okruženju nedostaje sistemski paket
  `python3-tk`.
- Spajanje i izdvajanje PDF stranica još nisu implementirani.
- Sledeći korak je Dan 1: pokrenuti prozor i proći kroz njegov kod, pa dodavati
  izbor i spajanje PDF fajlova.

## Tehničke odluke

- `CustomTkinter` koristimo za desktop interfejs.
- `pypdf` koristimo za čitanje, spajanje i izdvajanje stranica.
- Obrada se radi lokalno. Aplikacija ne šalje fajlove na internet.
