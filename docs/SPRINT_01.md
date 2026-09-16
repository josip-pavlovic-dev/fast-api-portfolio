# Sprint 01 (Nedelje 1-2) - FastAPI osnove

Cilj: Stabilan FastAPI skeleton + osnovni CRUD + testovi.

## Checklist (uraditi redom)

- [x] Pokreni app lokalno (`uvicorn app.main:app --reload`)
- [x] Proveri `GET /health`
- [x] CRUD za `items` radi (POST + GET)
- [x] Dodaj `PUT /items/{id}`
- [x] Dodaj `DELETE /items/{id}`
- [x] Dodaj 6-8 testova (update + delete + not found)
- [x] Dokumentuj endpoints u README
- [x] Refactor strukturu (`schemas.py` ako zelis)

## Dnevni fokus

- Dan 1-2: razumevanje FastAPI routing + Pydantic
- Dan 3-4: dodaj update/delete + testovi
- Dan 5: README + cleanup

## Definition of done

- Svi testovi prolaze
- `ruff check app tests` prolazi
- README ima quickstart + endpoints listu
