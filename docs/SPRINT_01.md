# Sprint 01 (Nedelje 1-2) - FastAPI osnove

Cilj: Stabilan FastAPI skeleton + osnovni CRUD + testovi.

## Checklist (uraditi redom)

- [x] Pokreni app lokalno (`uvicorn app.main:app --reload`)
- [x] Proveri `GET /health`
- [x] CRUD za `items` radi (POST + GET)
- [x] Dodaj `PUT /items/{id}` u fajl `app/main.py`
- [x] Dodaj `DELETE /items/{id}` u fajl `app/main.py`
- [ ] Dodaj 6-8 testova (update + delete + not found)
- [ ] Dokumentuj endpoints u README
- [ ] Refactor strukturu (`schemas.py` ako želiš)

---

## Dnevni fokus

- Dan 1-2: razumevanje FastAPI routing + Pydantic
- Dan 3-4: dodaj update/delete + testovi
- Dan 5: README + cleanup

---

## Definition of done

- Svi testovi prolaze
- `ruff check app tests` prolazi
- README ima quickstart + endpoints listu
