# Dan 2: zadaci

## 1. Napravi funkciju za parsiranje

Napiši funkciju koja prima tekstualni unos i vraća listu brojeva stranica.
Za početak neka funkcija ne otvara prozor i ne čita PDF; bavi se samo tekstom.

Ručno proveri sledeće primere:

| Unos      | Očekivani rezultat |
| --------- | ------------------ |
| `1`       | `[1]`              |
| `1, 3, 5` | `[1, 3, 5]`        |
| `2-4`     | `[2, 3, 4]`        |
| `1, 3-5`  | `[1, 3, 4, 5]`     |

Za sada možeš koristiti nekoliko `assert` provera ili ispisati rezultat i
uporediti ga sa očekivanim. Automatizovane `pytest` testove dodavaćemo kada
osnovni tok bude jasniji.

Rešenje:

```python
def funkcija_za_parsiranje(tekst:str | None = None):
    tekst = tekst or ""
    brojevi_stranica = []
    for deo in tekst.split(","):
        deo = deo.strip()
        if deo.isdigit():
            brojevi_stranica.append(int(deo))
        elif '-' in deo:
            start, end = map(int, deo.split('-'))
            brojevi_stranica.extend(range(start, end + 1))
    return brojevi_stranica
```

## 2. Dodaj validaciju granica

Prosledi funkciji i ukupan broj stranica PDF-a. Odbij:

Prazan tekst nije dozvoljen

```python
if not tekst:
    raise ValueError("Prazan tekst nije dozvoljen")
```

Nulu ili negativan broj stranice

```python
if broj <= 0:
    raise ValueError("Broj stranice mora biti pozitivan")
```

Opseg u kome je početak veći od kraja

```python
if start > end:
    raise ValueError("Početna stranica ne može biti veća od krajnje")
```

Broj stranice veći od broja stranica u PDF-u;

```python
if broj > ukupan_broj_stranica:
    raise ValueError("Broj stranice ne može biti veći od broja stranica u PDF-u")
```

Tekst koji nije moguće protumačiti kao broj ili opseg.

```python
try:
    broj = int(deo)
except ValueError:
    raise ValueError(f"Neispravan unos: {deo}")
```

Grešku prijavi razumljivom porukom. Nemoj dopustiti da se neispravan tekst
pretvori u indeks stranice.

## 3. Poveži izdvajanje sa PDF-om

- Omogući izbor jednog ulaznog PDF fajla.
- Prikaži koliko stranica ima izabrani PDF.
- Dodaj polje za unos stranica.
- Dodaj dugme za izbor lokacije izlaznog fajla.
- Napravi novi PDF samo od proverenih stranica, redom kojim su unete.

## Provera završetka

Pojedinačni testni PDF fajlovi imaju najviše 4 stranice. Za proveru sa najmanje
5 stranica koristi spojeni PDF iz Dana 1, koji sa sva tri uzorka ima 7 stranica.

Na PDF-u od najmanje pet stranica proveri da `1, 3-4` napravi PDF od tri
stranice. Proveri i da neispravni unosi zaustavljaju obradu uz razumljivu poruku,
a ne uz traceback u terminalu.

## Dodatni izazov

Kada su osnovni slučajevi gotovi, dodaj unos `last` kao naziv za poslednju
stranicu. To nije obavezno za završetak dana.
