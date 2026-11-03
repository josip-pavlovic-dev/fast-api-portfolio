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

Projekat ima početni prozor. PDF-ove još ne otvara niti obrađuje.

## Pokretanje

Komande pokreni iz korena repozitorijuma. U ovom repozitorijumu koristi postojeće
virtuelno okruženje `.venv`:

```bash
source .venv/bin/activate
python -m pip install -r python_projects/project_1/requirements.txt
python python_projects/project_1/app.py
```

U ovom Linux okruženju Tkinter trenutno nije instaliran. Na Debian/Ubuntu
sistemima ga jednom instaliraj sistemskom komandom:

```bash
sudo apt install python3-tk
```

Ovo je sistemski preduslov i zato se ne nalazi u `requirements.txt`.

## Materijali za učenje

- [Plan rada](PLAN_RADA.md)
- [Kontekst i trenutni napredak](KONTEKST.md)
- [Dan 1: prozor aplikacije i spajanje PDF-ova](dan_01/teorija.md)
- [Dan 2: izdvajanje stranica](dan_02/teorija.md)
