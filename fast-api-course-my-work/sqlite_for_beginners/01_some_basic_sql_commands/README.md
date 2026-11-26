# Oblast 01 — Osnovne SQLite komande

Ova oblast uvodi `sqlite3` komandni alat i komande koje olakšavaju pregled baze, uvoz i izvoz podataka. Važno je razlikovati SQL naredbe od posebnih komandi SQLite CLI-ja koje počinju tačkom.

## Lekcije

1. [Šta je `sqlite3` alat](./01_what_is_sqlite3_tool.md)
2. [Često korišćene SQLite komande](./02_some_commonly_used_sqlite3_commands.md)
3. [SQLite `.dump` komanda](./03_sqlite_dump_command.md)

Lekcije obrađuju pokretanje CLI alata, pregled tabela i šeme, izvoz rezultata, čitanje SQL datoteke i razliku između tekstualnog dump-a i SQLite rezervne kopije.

## Na šta obrati pažnju

- `sqlite3` CLI je poseban program; nije sama SQLite baza niti Python modul `sqlite3`. SQL naredbe rade nad bazom, dok komande sa tačkom, kao `.tables`, `.schema` i `.dump`, pripadaju CLI-ju.
- Relativna putanja se računa od trenutnog direktorijuma. Otvaranje nepostojeće putanje bez `-readonly` može napraviti praznu bazu; proveri `.databases` pre nego što zaključiš da su podaci nestali.
- `.once` preusmerava izlaz sledeće komande, dok `.output` ostaje aktivan do `.output stdout`. Obe komande pišu odvojeni fajl, čak i kada je glavna baza otvorena samo za čitanje; izaberi novu putanju da ne bi prepisao raniji rezultat.
- `.dump` pravi SQL tekst, a `.backup` kopiju u SQLite formatu. Dump prazne tabele i dalje sadrži `CREATE TABLE`, ali nema `INSERT` naredbi.
- U proveri sa SQLite CLI 3.54.1, prazan upit uz `.headers on` u interaktivnoj sesiji napravio je prazan izlaz; kada je potrebno zaglavlje i bez redova, koristi `-header` pri pokretanju CLI-ja.

## Vežbe

Vežbe komandnog alata nalaze se u [playground/cli/](../playground/cli/). Za pregled Chinook-a koristi radnu kopiju i pokreni CLI iz korena repozitorijuma:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

`.txt` fajlovi `01`–`03` u `cli/` sadrže SQLite CLI komande za ovu oblast i mogu se učitati pomoću `.read`; fajl `04` pripada narednoj oblasti. Vežba za `.dump` prazne tabele radi se odvojeno u svežoj memorijskoj bazi, tako da ne menja Chinook. Detaljna dnevna vežba za dump nalazi se u [danu 04](../pitanja_i_odgovori/dan_04_sqlite_dump_command.md).

Nazad na [glavni README kursa](../README.md).
