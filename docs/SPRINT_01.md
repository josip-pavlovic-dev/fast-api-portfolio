# Sprint 01 (Nedelje 1-2) - FastAPI osnove

Cilj: Stabilan FastAPI skeleton + osnovni CRUD + testovi.

## Checklist (uraditi redom)

- [ ] Pokreni app lokalno (`uvicorn app.main:app --reload`)
- [ ] Proveri `GET /health`
- [ ] CRUD za `items` radi (POST + GET)
- [ ] Dodaj `PUT /items/{id}`
- [ ] Dodaj `DELETE /items/{id}`
- [ ] Dodaj 6-8 testova (update + delete + not found)
- [ ] Dokumentuj endpoints u README
- [ ] Refactor strukturu (`schemas.py` ako zelis)

## Dnevni fokus

- Dan 1-2: razumevanje FastAPI routing + Pydantic
- Dan 3-4: dodaj update/delete + testovi
- Dan 5: README + cleanup

## Definition of done

- Svi testovi prolaze
- `ruff check app tests` prolazi
- README ima quickstart + endpoints listu
