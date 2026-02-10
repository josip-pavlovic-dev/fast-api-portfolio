# FastAPI Portfolio

Cilj: 6 meseci fokusiran FastAPI backend put sa jasnim projektima, testovima i deploy-om.

## Brzi start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Testovi

```bash
pytest
```

## Endpoints

- GET /health
- POST /items/
- GET /items/
- GET /items/{item_id}
- PUT /items/{item_id}
- DELETE /items/{item_id}

## Struktura

- app/ - aplikacioni kod
- tests/ - testovi
- scripts/ - pomocne skripte
- docs/ - sprint plan i kursevi

## Roadmap

Vidi [django-portfolio/scratch/roadmap/fastapi_6_month_plan.md](../django-portfolio/scratch/roadmap/fastapi_6_month_plan.md)

## Sprint plan i kursevi

- [docs/SPRINT_01.md](docs/SPRINT_01.md)
- [docs/COURSES.md](docs/COURSES.md)
