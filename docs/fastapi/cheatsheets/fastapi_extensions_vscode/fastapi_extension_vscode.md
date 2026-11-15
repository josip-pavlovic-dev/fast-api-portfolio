# FastAPI ekstenzija za VS Code

Ovaj vodič objašnjava kako da instaliraš i koristiš namensku FastAPI ekstenziju u VS Code-u, uključujući rad u WSL-u.

## 1. Šta ekstenzija radi

Ekstenzija **FastAPI** (`FastAPILabs.fastapi-vscode`) dodaje alate za snalaženje u FastAPI kodu:

- **Path Operation Explorer** prikazuje pronađene rute i grupiše ih po router-ima. Klik na rutu vodi do njene definicije, a preko router-a možeš otvoriti mesto na kom je definisan.
- **Pretraga ruta** pronalazi rute po putanji, HTTP metodi ili imenu.
- **CodeLens** prikazuje veze između poziva test klijenta, kao što je `client.get("/items")`, i odgovarajuće rute. Kod ruta može prikazati i testove koji ih pozivaju.
- **FastAPI Cloud integracija** omogućava komande za objavljivanje aplikacije i pregled njenih logova. To je opcionalna funkcionalnost i nije potrebna za lokalni razvoj.

Ekstenzija ne zamenjuje Python ekstenziju, Pylance, pokretanje aplikacije ili testove. Ona olakšava navigaciju kroz FastAPI aplikaciju.

---

## 2. Instalacija u WSL: Ubuntu-24.04

Kada je folder projekta otvoren kroz WSL, statusna traka VS Code-a treba da prikazuje **WSL: Ubuntu-24.04**. To znači da je prozor povezan sa Linux okruženjem. Ekstenzija mora biti instalirana na tom udaljenom WSL hostu, a ne samo u lokalni VS Code za Windows.

### Instalacija kroz VS Code

1. Otvori projekat u WSL prozoru i proveri oznaku **WSL: Ubuntu-24.04**.
2. Otvori Extensions panel pomoću `Ctrl+Shift+X`.
3. Pretraži `FastAPI` i izaberi ekstenziju izdavača **FastAPI Labs**.
4. Klikni na dugme za instalaciju u WSL-u, obično označeno kao **Install in WSL: Ubuntu-24.04**.
5. Ako VS Code zatraži ponovno učitavanje prozora, izaberi **Reload Window**.

Ako vidiš samo da je ekstenzija instalirana lokalno, pronađi je u odeljku **Local - Installed** i izaberi instalaciju na WSL host.

---

### Proveri da li je instalirana u pravom prozoru

Instalaciju pokreni iz Extensions panela prozora u kom ćeš raditi:

1. Proveri da je prozor povezan sa **WSL: Ubuntu-24.04** i da je izabran profil koji koristiš.
2. Na stranici FastAPI ekstenzije klikni **Install** ili **Install in WSL: Ubuntu-24.04**, u zavisnosti od toga šta VS Code prikazuje.
3. Posle instalacije proveri da je ekstenzija navedena u odeljku **WSL: Ubuntu-24.04 - Installed**. Na Marketplace stranici dugme više ne bi trebalo da prikazuje **Install**.

Važno: uspešna CLI poruka za instalaciju nije dovoljna ako u aktivnom prozoru ekstenzija i dalje prikazuje **Install**. Profili i lokalni/udaljeni extension host mogu imati različite instalacije. U tom slučaju instaliraj je kroz Extensions panel upravo tog prozora.

---

## 3. Trenutno stanje u tvom setup-u

- U tvom aktivnom VS Code prozoru Marketplace trenutno prikazuje **Install** za FastAPI ekstenziju. To znači da je još treba instalirati u tom prozoru/profilu; prethodna CLI instalacija nije bila dostupna u prikazanom kontekstu.
- U tvom aktivnom VS Code profilu dodato je `fastapi.cloud.enabled: false`, pa su Cloud komande isključene.
- Dodato je i `fastapi.telemetry.enabled: false`, tako da je isključena telemetrija ekstenzije.
- Nije postavljen globalni `fastapi.entryPoint`; ekstenzija koristi automatsko otkrivanje aplikacije. U ovom repozitorijumu glavna aplikacija je `app.main:app`.
- CodeLens je podrazumevano uključen. Nije potrebno posebno podešavanje.
- Tvoja Python, Pylance i Ruff podešavanja ostaju u Windows profilu koji koristiš uz WSL; nisu menjana.

Podešavanja FastAPI ekstenzije su u **User Settings aktivnog profila**, a ne u `.vscode/settings.json` projekta. Tako se Cloud/telemetrija podešavanja primenjuju kroz tvoj profil, dok se entry point ostavlja automatskom otkrivanju za različite projekte. Ova podešavanja će važiti čim instaliraš i aktiviraš ekstenziju u tom profilu/prozoru.

---

## 4. Otvaranje pregleda ruta

1. Otvori FastAPI projekat kao workspace u VS Code-u.
2. U Activity Bar-u pronađi **Path Operation Explorer**.
3. Proširi aplikaciju i router-e da pregledaš pronađene endpoint-e.
4. Klikni na endpoint da pređeš do definicije u Python fajlu.
5. Desnim klikom na router možeš preći do njegove definicije.

Ovo je naročito korisno kada su endpoint-i raspoređeni po više fajlova, a glavni `main.py` uključuje router-e pomoću `include_router(...)`.

### Pretraga ruta

Klikni na dugme za pretragu u Path Operation Explorer-u ili otvori Command Palette pomoću `Ctrl+Shift+P` i pokreni:

```text
FastAPI: Search Path Operations...
```

Pretragu možeš koristiti za pronalaženje rute po putanji, metodi kao što su `GET` ili `POST`, ili imenu operacije.

---

## 5. CodeLens za rute i testove

CodeLens su dodatne veze koje se prikazuju iznad relevantnih linija koda:

- iznad poziva test klijenta možeš otvoriti odgovarajuću rutu;
- iznad rute možeš videti i otvoriti testove koji je pozivaju.

Na primer, ekstenzija može povezati poziv `client.get("/items")` u testu sa FastAPI handler-om koji obrađuje `GET /items`. To ubrzava navigaciju, ali samo po sebi ne pokreće test i ne potvrđuje da endpoint ispravno radi.

CodeLens je podrazumevano uključen i u tvom profilu nije menjan. Ako ga nekad želiš isključiti samo za jedan projekat, možeš to uraditi u tom projektu:

```json
{
  "fastapi.codeLens.enabled": false
}
```

Ako se CodeLens ne pojavljuje, proveri da li je Python fajl sa testom sačuvan, da li test poziva endpoint preko test klijenta i da li je `fastapi.codeLens.enabled` uključen. Podrška za CodeLens ne znači da će svaki proizvoljan HTTP poziv biti prepoznat kao test klijenta.

---

## 6. Podešavanje FastAPI entry point-a

Ekstenzija pokušava automatski da pronađe aplikaciju pregledom Python fajlova koji prave `FastAPI()` instancu. U većim projektima može postojati više aplikacija ili nestandardna struktura foldera; tada je korisno navesti entry point ručno.

Entry point se piše u formatu:

```text
paket.modul:promenljiva_aplikacije
```

Na primer, ako je promenljiva `app` definisana u `app/main.py`:

```text
app.main:app
```

Ako automatsko otkrivanje u nekom projektu ne pronađe pravu aplikaciju, podesi entry point samo u tom projektu, kroz **Workspace Settings (JSON)**:

```json
{
  "fastapi.entryPoint": "app.main:app"
}
```

Zameni vrednost ako je aplikacija u drugom modulu ili se ASGI promenljiva zove drugačije. Nemoj postavljati `app.main:app` u globalni User Settings profil ako koristiš više projekata: ta putanja može biti pogrešna za ostale. Entry point samo kaže ekstenziji koju aplikaciju da analizira; ne pokreće je.

---

## 7. Podešavanja, privatnost i FastAPI Cloud

| Podešavanje                 | Značenje                                                                        | Podrazumevano         |
| --------------------------- | ------------------------------------------------------------------------------- | --------------------- |
| `fastapi.entryPoint`        | Modul i ASGI promenljiva glavne aplikacije; prazno znači automatsko otkrivanje. | Automatsko otkrivanje |
| `fastapi.codeLens.enabled`  | Prikaz veza između ruta i test klijentskih poziva.                              | `true`                |
| `fastapi.cloud.enabled`     | Uključuje FastAPI Cloud komande i integraciju u statusnoj traci.                | `true`                |
| `fastapi.telemetry.enabled` | Dozvoljava slanje anonimnih podataka o korišćenju radi poboljšanja ekstenzije.  | `true`                |

Podešavanja možeš pronaći u VS Code Settings pretragom `fastapi`. Za izmenu aktivnog profila otvori Command Palette (`Ctrl+Shift+P`) i izaberi **Preferences: Open User Settings (JSON)**. Proveri da menjaš profil koji koristiš u WSL-u, a ne Workspace Settings.

Tvoj profil sada sadrži sledeća podešavanja:

```jsonc
{
  "fastapi.cloud.enabled": false,
  "fastapi.telemetry.enabled": false,
}
```

Cloud komande i telemetrija su isključene. Ostale mogućnosti za lokalni rad, kao što su pregled i pretraga ruta i CodeLens navigacija, ostaju dostupne.

---

## 8. Korak po korak: korišćenje u fast-api-portfolio

1. **Otvori repo u WSL prozoru.** U statusnoj traci proveri da piše `WSL: Ubuntu-24.04`, a da je otvoren root folder `fast-api-portfolio`.
2. **Otvori Path Operation Explorer.** Pronađi njegovu ikonu u Activity Bar-u. Ekstenzija treba da otkrije aplikaciju napravljenu u `app/main.py`.
3. **Pregledaj rute po router-u.** U ovom projektu `main.py` uključuje health i items router-e. Očekivane rute su:

   | Metoda   | Putanja            | Šta možeš otvoriti     |
   | -------- | ------------------ | ---------------------- |
   | `GET`    | `/health`          | Health handler         |
   | `POST`   | `/items/`          | Kreiranje item-a       |
   | `GET`    | `/items/`          | Lista item-a           |
   | `GET`    | `/items/{item_id}` | Čitanje item-a po ID-u |
   | `PUT`    | `/items/{item_id}` | Izmena item-a          |
   | `DELETE` | `/items/{item_id}` | Brisanje item-a        |

4. **Pređi od rute do koda.** Klikni, na primer, na `GET /health` da otvoriš handler u `app/api/routes/health.py`. Proširi items router i klikni na `GET /items/{item_id}` da odeš do odgovarajuće funkcije u `app/api/routes/items.py`.
5. **Pronađi rutu po imenu ili putanji.** U Path Operation Explorer-u klikni na pretragu ili pokreni `FastAPI: Search Path Operations...` iz Command Palette-a. Probaj `GET /items/{item_id}` ili `/health`.
6. **Prati vezu između testa i rute.** U `tests/test_health.py` poziv `client.get("/health")` proverava health handler. U `tests/test_items.py` pozivi poput `client.post("/items/")` i `client.get("/items/")` vode do odgovarajućih items ruta preko CodeLens-a. Klik na vezu služi za navigaciju; test i dalje pokrećeš odvojeno.

### U čemu ti sada konkretno pomaže

- Brže razumeš kako su `app/main.py`, router-i i handler funkcije povezani.
- Ne moraš ručno da tražiš definiciju rute kroz više fajlova.
- Možeš lakše da pratiš postojeće testove do endpoint-a koji proveravaju.
- Search je koristan kada znaš HTTP metodu ili URL, ali ne znaš ime Python funkcije.
- Pošto su Cloud komande isključene, ekstenziju koristiš za lokalno snalaženje u kodu, ne za objavljivanje aplikacije ili pregled Cloud logova.

Ekstenzija je alat za navigaciju. Ne šalje HTTP zahteve, ne pokreće pytest i ne potvrđuje da ruta radi. Za to nastavi da koristiš postojeće testove i lokalni FastAPI run workflow.

---

## 9. Česti problemi

### Explorer ne prikazuje aplikaciju ili rute

1. Proveri da je workspace otvoren u WSL prozoru i da je ekstenzija instalirana u **WSL: Ubuntu-24.04**.
2. Proveri da li VS Code otvara root folder u kome se nalazi aplikacija.
3. Ako automatsko otkrivanje ne uspe ili postoji više aplikacija, podesi `fastapi.entryPoint`.
4. Sačuvaj fajlove, pa po potrebi pokreni **Developer: Reload Window** iz Command Palette-a.

---

### Ekstenzija radi u Windows-u, ali ne i u WSL-u

To obično znači da je instalirana samo lokalno. U Extensions panelu otvori odeljak **Local - Installed** i instaliraj je u WSL host. Proveri da statusna traka prikazuje **WSL: Ubuntu-24.04**.

---

### Ruta se ne povezuje sa testom

Proveri da test koristi prepoznatljiv poziv test klijenta i da URL/metoda odgovaraju definisanoj ruti. CodeLens služi za navigaciju i nije zamena za izvršavanje testova.

---

## 10. Brza lista za početak

- [ ] VS Code prozor je povezan sa **WSL: Ubuntu-24.04**.
- [ ] `FastAPILabs.fastapi-vscode` je instaliran u WSL-u.
- [ ] Otvoren je pravi root folder FastAPI projekta.
- [ ] Path Operation Explorer prikazuje aplikaciju i njene rute.
- [ ] Ako je potrebno, podešen je `fastapi.entryPoint`.
- [ ] Proverena su podešavanja telemetrije i FastAPI Cloud integracije.

---
