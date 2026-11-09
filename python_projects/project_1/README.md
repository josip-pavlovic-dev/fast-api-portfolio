# PDF Toolkit

Desktop aplikacija za rad sa PDF fajlovima. Fajlovi se obrađuju lokalno na
računaru; ne šalju se na veb-sajt.

## Cilj projekta

Počećemo od spajanja PDF fajlova i izdvajanja izabranih stranica. Kasnije ćemo
dodati rotiranje, istražiti kompresiju, obraditi PDF fajlove zaštićene lozinkom,
a zatim pripremiti testove i uputstvo za portfolio.

Projekat je inspirisan objavom „Build PDF Toolkit with Python and CustomTkinter:
Day 1“, ali ćemo kod pisati i razumeti sami, u malim koracima.

## Trenutno stanje

Izbor i spajanje više PDF fajlova su implementirani. Aplikacija sprečava da se
ulazni PDF izabere kao izlazni fajl. Izdvajanje stranica je sledeći cilj Dana 2.

## Testni PDF fajlovi

Folder `sample_pdfs/` sadrži tri sintetička dokumenta: jedan sa jednom, jedan sa
dve i jedan sa četiri stranice. Ako ih spojiš tim redom, rezultat treba da ima
sedam stranica. Dokumenti su napravljeni za vežbanje i ne sadrže privatne podatke.

## Pokretanje

Komande pokreni iz korena repozitorijuma. U ovom repozitorijumu koristi postojeće
virtuelno okruženje `.venv`:

```bash
source .venv/bin/activate
python -m pip install -r python_projects/project_1/requirements.txt
python python_projects/project_1/app.py
```

Tkinter je proveren u razvojnom okruženju (Tcl/Tk 8.6). Ako ga na drugom
Debian/Ubuntu računaru nema, instaliraj sistemski paket:

```bash
sudo apt install python3-tk
```

Ovo je sistemski preduslov i zato se ne nalazi u `requirements.txt`.

## Materijali za učenje

- [Plan rada](PLAN_RADA.md)
- [Kontekst i trenutni napredak](KONTEKST.md)
- [Teorija modula i biblioteka](cheatsheet/README.md)
- [Dan 1: prozor aplikacije i spajanje PDF-ova](dan_01/teorija.md)
- [Dan 2: izdvajanje stranica](dan_02/teorija.md)
