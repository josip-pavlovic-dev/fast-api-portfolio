# VS Code: Podesavanje Formatera i Importa (Black + Ruff)

Ovaj dokument opisuje sta je provereno u tvom trenutnom `settings.json`, sta je potencijalno usporavalo `save`, i koja konfiguracija je izabrana da radi bez konflikta.

## 1) Sta je provereno

U tvom `settings.json` glavne Python stavke su bile:

- `editor.formatOnSave` za Python = `true` (Black formatter)
- `source.organizeImports.ruff` = `always`
- `source.fixAll.ruff` = `explicit`
- `files.autoSave` = `afterDelay`
- deprecated `python.linting.*` kljucevi su jos prisutni

Zakljucak:

- Nema "hard" konflikta koji lomi editor.
- Ali postoji realan izvor sporijeg cuvanja fajla:
  - Black radi na `save`
  - Ruff organize imports radi na `save`
  - Auto-save cesto okida `save`

To znaci da jedan Python fajl moze biti obradjen vise puta dok kucas, pa subjektivno deluje sporije.

---

## 2) Problem 1: `python.linting.*` je zastareo

U novijim verzijama Python ekstenzije stari linting prekidaci vise nisu preporucen nacin konfiguracije.

Primer starih kljuceva:

```json
"python.linting.enabled": true,
"python.linting.mypyEnabled": true,
"python.linting.ruffEnabled": true,
"python.linting.pylintEnabled": false
```

Sta je bolje danas:

- Ruff se vodi preko Ruff ekstenzije i/ili `pyproject.toml`
- Mypy se obicno vodi kroz task/CLI ili mypy ekstenziju
- Pylance radi analizu tipova odvojeno (`python.analysis.*`)

Prakticno: uklanjanje starih `python.linting.*` kljuceva smanjuje konfuziju i buduce nejasnoce.

---

## 3) Problem 2: Black + Ruff na svakom save

Black i Ruff mogu raditi zajedno bez problema, ali je pitanje kada da se pokrecu.

Ako je:

```json
"editor.formatOnSave": true,
"source.organizeImports.ruff": "always"
```

onda na svakom save-u imas:

- Black format
- Ruff organize imports

Ako je ukljucen i auto-save (`afterDelay`), ovaj ciklus se desava cesto i zato save moze delovati sporije.

---

## 4) Izabrano resenje (bez konflikta, brzi save)

Cilj: da zadrzis Black na save, ali da Ruff import organizaciju pokreces eksplicitno kad zelis.

### Finalna preporuka

```json
"[python]": {
  "editor.defaultFormatter": "ms-python.black-formatter",
  "editor.formatOnSave": true,
  "editor.formatOnSaveMode": "modificationsIfAvailable",
  "editor.codeActionsOnSave": {
    "source.organizeImports.pylance": "never",
    "source.fixAll.pylance": "never",
    "source.organizeImports.ruff": "explicit",
    "source.fixAll.ruff": "explicit"
  }
}
```

I globalno:

```json
"python.analysis.autoImportCompletions": true,
"files.autoSave": "afterDelay",
"files.autoSaveDelay": 1500
```

Napomena:

- `source.organizeImports.ruff: "explicit"` znaci da se ne pokrece automatski na svakom save-u.
- `formatOnSaveMode: "modificationsIfAvailable"` smanjuje obim formatiranja na izmenjene delove kada je moguce.

---

## 5) Konkretne izmene koje treba uraditi u `settings.json`

1. Ukloni deprecated kljuceve:

```json
"python.linting.enabled",
"python.linting.mypyEnabled",
"python.linting.ruffEnabled",
"python.linting.pylintEnabled"
```

1. U `[python]` promeni:

```json
"source.organizeImports.ruff": "always"
```

u:

```json
"source.organizeImports.ruff": "explicit"
```

1. Dodaj (ako vec nije prisutno):

```json
"editor.formatOnSaveMode": "modificationsIfAvailable"
```

1. Opcionalno uspori auto-save okidanje (manje prekida dok kucas):

```json
"files.autoSaveDelay": 1500
```

---

## 6) Da li je ovo konflikt-free?

Sa gore navedenim podesavanjem:

- Black radi na save-u (stabilno)
- Ruff import/fix radi samo kada ga eksplicitno pozoves
- Pylance import organizer je iskljucen da ne duplira posao

To je cist i predvidiv flow bez duplih automatskih izmena istog fajla pri svakom save-u.

---

## 7) Kako rucno pokretati Ruff kada zatreba

Kada zelis da sredis importe ili fixeve:

1. `Ctrl + Shift + P`
1. `Ruff: Organize Imports`
1. ili `Ruff: Fix All`

Ako zelis, mozes vezati i poseban keybinding samo za ove komande.

---

## 8) Brz test posle izmene

Posle azuriranja `settings.json` proveri sledece:

1. Otvori Python fajl.
1. Namerno promeni stil (npr. razmake).
1. `Ctrl + S`:
   - Black treba da formatira.
   - Importi ne treba da se reorganizuju automatski.
1. Sacekaj auto-save tokom kucanja:
   - Ne bi trebalo da osetis isto usporenje kao ranije.
1. Pokreni rucno `Ruff: Organize Imports` i potvrdi da radi.

Ako ovo prolazi, konfiguracija je stabilna i bez konflikta za svakodnevni rad.

---

## 9) Praktican test koji smo upravo uradili

Ovo nije teorija, nego realan test pokrenut u terminalu.

### 9.1. Potvrda konfiguracije

Provereno je da je `settings.json` za Python sada zaista na:

```json
"editor.formatOnSaveMode": "modificationsIfAvailable",
"source.organizeImports.ruff": "explicit",
"source.fixAll.ruff": "explicit"
```

I da su deprecated kljucevi uklonjeni:

```text
python.linting.enabled
python.linting.mypyEnabled
python.linting.ruffEnabled
python.linting.pylintEnabled
```

Takodje je potvrdeno:

```json
"files.autoSaveDelay": 1500
```

### 9.2. Test Ruff organize imports (real output)

Napravljen je privremeni fajl sa namerno neuredjenim importima:

```python
import os
import json



def demo( ):
  return  {"ok":True}
```

Pokrenuta je provera:

```bash
ruff check --select I /tmp/vscode_format_test.py
```

Ruff je prijavio:

```text
I001 Import block is un-sorted or un-formatted
```

Zatim je pokrenut eksplicitni fix:

```bash
ruff check --select I --fix /tmp/vscode_format_test.py
```

Rezultat posle fix-a:

```python
import json
import os


def demo( ):
  return  {"ok":True}
```

Zakljucak testa:

- Ruff import organizacija radi ispravno kada je eksplicitno pokrenes.
- To je u skladu sa ciljem konfiguracije: bez automatskog import prepakivanja na svakom save-u.

### 9.3. Napomena za Black

U istom test okruzenju CLI paket `black` nije bio instaliran u `.venv`, pa Black nije mogao da se proveri preko terminal komande `black --version`.

To ne znaci da VS Code Black formatter ne radi, jer VS Code koristi `ms-python.black-formatter` ekstenziju.

Prakticna provera u editoru:

1. Otvori Python fajl.
1. Namerno poremeti format (npr. razmake).
1. `Ctrl + S`.
1. Ako se stil vrati u Black format, formatter radi kako treba.

Ako zelis i CLI Black verifikaciju u terminalu, instaliraj ga u venv:

```bash
pip install black
```

---

## 10) Potvrda iz realnog rada (tvoj feedback)

Posle primenjenih izmena potvrdeno je u editoru:

- importi koji nisu iskorisceni se ciste kako treba kada se pokrene odgovarajuca Ruff akcija
- auto-import predlozi rade tokom kucanja (primer: `timedelta` nudi import)

Prakticno, to znaci da je kombinacija uspesna:

```text
Black -> stabilan format na save
Ruff -> kontrolisan import/fix tok (explicit)
Pylance -> auto-import UX tokom kucanja
```

Ovo je upravo cilj profesionalnog podesavanja: predvidiv save bez konflikta i sa dobrim IntelliSense iskustvom.

---

## 11) Kako iskljuciti linter za `.md` fajlove

Ako mislis na `markdownlint` ekstenziju, danas postoje dva cista pristupa.

### Opcija A: Potpuno iskljuci markdownlint (najjednostavnije)

U `settings.json`:

```json
"markdownlint.enable": false
```

Time dobijas:

```text
nema markdownlint upozorenja ni na save ni tokom kucanja
```

### Opcija B: Ostavis markdownlint, ali bez automatskog okidanja

U `settings.json`:

```json
"markdownlint.enable": true,
"markdownlint.run": "onSave"
```

ili ako hoces manje agresivno:

```json
"markdownlint.run": "onType"
```

Ako zelis da ga prakticno ne osetis tokom rada, koristi Opciju A.

---

## 12) Da li je `markdownlint.config` zastareo?

Nije zastareo, i dalje je podrzan:

```json
"markdownlint.config": {
  "MD024": false,
  "MD013": false
}
```

Ali za ozbiljnije projekte je cesto bolji moderniji obrazac:

- drzi pravila u projektu, npr. `.markdownlint.jsonc`
- ne gomilaj ih u globalnom user `settings.json`

Prednost projektnog fajla:

```text
pravila putuju sa repozitorijumom
svi u timu imaju isto ponasanje
manje "skrivenih" globalnih pravila
```

Primer `.markdownlint.jsonc` u korenu projekta:

```jsonc
{
  "default": true,
  "MD024": false,
  "MD013": false,
}
```

Ako hoces potpuno bez markdown lint upozorenja, i dalje je najkrace:

```json
"markdownlint.enable": false
```

---

## 13) Warning za schema URL (`untrusted location`)

U jednom trenutku se pojavilo narandzasto upozorenje:

```text
Unable to load schema ... is untrusted
```

Uzrok:

- `.markdownlint.jsonc` je imao `$schema` koji pokazuje na GitHub raw URL
- VS Code/JSON validator je tretirao tu lokaciju kao nepoverljivu

Primer problem linije:

```jsonc
"$schema": "https://raw.githubusercontent.com/DavidAnson/markdownlint/main/schema/markdownlint-config-schema.json"
```

Primenjeno resenje:

- uklonjena je `$schema` linija iz `.markdownlint.jsonc`

Zasto je ovo bezbedno i ispravno:

- markdownlint pravila rade potpuno isto i bez `$schema`
- gasi se warning o nepoverljivoj lokaciji
- konfiguracija ostaje jednostavna i stabilna

Drugim recima, `$schema` je pomoc za autocomplete/validaciju JSONC strukture, ali nije obavezan za rad markdownlint pravila.
