# Udemy Kursi i mapiranje na repo zadatke

Ovo je prakticna mapa: teorija iz kursa -> direktni zadaci u ovom repo-u.

## Mesec 1 (FastAPI + Python osnove)

- FastAPI: <https://www.udemy.com/course/fastapi-the-complete-course/>
- FastAPI (alternativa): <https://www.udemy.com/course/fastapi-course-python/>
- FastAPI (alternativa): <https://www.udemy.com/course/completefastapi/>
- FastAPI (alternativa): <https://www.udemy.com/course/fastapi-guide/>
- Python baza: <https://www.udemy.com/course/complete-python-bootcamp/>
- Python dublje: <https://www.udemy.com/course/python-3-deep-dive-part-1/>

Repo zadaci:

- `app/main.py` CRUD + response modeli
- `app/api/routes/items.py` validacija i error handling
- `tests/test_health.py` + `tests/test_items.py`

## Mesec 2 (SQLAlchemy + Postgres)

- SQLAlchemy + Alembic: <https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/>
- SQL + Postgres: <https://www.udemy.com/course/sql-and-postgresql/>

Repo zadaci:

- `app/db/base.py`, `app/db/session.py`
- Alembic init + migracije
- `crud.py` layer + testovi

## Mesec 3 (Auth + Pytest)

- Pytest (deo kursa): <https://www.udemy.com/course/playwright-python-automation-testing-pytest/>
- TODO: posalji Udemy link za FastAPI JWT/Auth kurs (Spring Security nije relevantan za Python)

Repo zadaci:

- `app/core/security.py`
- `app/api/routes/auth.py`
- testovi login/refresh

## Mesec 4 (Async + Redis/Queue)

- Redis: <https://www.udemy.com/course/redis-the-complete-developers-guide-p/>
- Celery (Django kurs, ali Celery koncept je upotrebljiv): <https://www.udemy.com/course/django-celery-mastery/>
- TODO: posalji Udemy link za Async FastAPI ili Celery/RQ

Repo zadaci:

- `app/services/cache.py`
- `app/workers/` (celery/rq)

## Mesec 5 (Docker + CI/CD)

- Docker (izaberi jedan): <https://www.udemy.com/course/learn-docker/> ili <https://www.udemy.com/course/docker-mastery/>
- GitHub Actions: <https://www.udemy.com/course/github-actions-the-complete-guide/>

Repo zadaci:

- `Dockerfile`, `docker-compose.yml`
- `.github/workflows/ci.yml`

## Mesec 6 (System design + SQL)

- System design (izaberi jedan): <https://www.udemy.com/course/system-design-interview-prep/>
- System design (alternativa): <https://www.udemy.com/course/software-architecture-design-of-modern-large-scale-systems/>
- SQL practice: <https://www.udemy.com/course/the-complete-sql-bootcamp-30-hours-go-from-zero-to-hero/>

Repo zadaci:

- README case study
- SQL optimizacije + performance checklist
