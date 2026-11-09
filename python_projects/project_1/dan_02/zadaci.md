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

## 2. Dodaj validaciju granica

Prosledi funkciji i ukupan broj stranica PDF-a. Odbij:

- prazan tekst;
- nulu ili negativan broj;
- opseg u kome je početak veći od kraja;
- broj stranice veći od broja stranica u PDF-u;
- tekst koji nije moguće protumačiti kao broj ili opseg.

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
