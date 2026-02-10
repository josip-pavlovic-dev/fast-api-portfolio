# FastAPI 6-Month Roadmap (25h+ nedeljno)

**Cilj:** Remote junior FastAPI backend developer. Fokus na Python + API dizajn + baze + testiranje + deploy. Minimalni JS/TS samo za API potrosnju i demo.

## Startni setup (prva 2 dana)

- Instaliraj Python 3.11+, Postgres, Docker, Git
- Napravi novi repo (ili folder) `fastapi-portfolio`
- Setuj `pre-commit` i `ruff`, `pytest`, `uvicorn`
- Napravi bazni `README` sa ciljevima i napretkom

## Osnovni princip rada

- 5 dana nedeljno, 4-6h dnevno (ukupno 25-30h)
- Svake nedelje: 1 mini feature, 1 test suite update, 1 deploy ili infra korak
- Dnevno: 1 commit, kratke belezke o naucenom

## 6-mesecni put (24 nedelje) - detaljan raspored

**Mesec 1 (nedelje 1-4): Python + Web/API osnove**

- **Nedelja 1:** Python refresher (typing, errors, struct), HTTP osnove
- **Nedelja 2:** FastAPI routing, Pydantic modeli, validation
- **Nedelja 3:** CRUD mini API (TODO/Notes), `pytest` osnove
- **Nedelja 4:** Refactor + error handling + OpenAPI pregled

**Mesec 2 (nedelje 5-8): Baze i ORM**

- **Nedelja 5:** SQL osnove + Postgres setup
- **Nedelja 6:** SQLAlchemy 2.0 + session patterns
- **Nedelja 7:** Alembic migracije + data layer pattern
- **Nedelja 8:** Search/filter + paginacija + indexi

**Mesec 3 (nedelje 9-12): Auth, sigurnost, testovi**

- **Nedelja 9:** Auth osnove (password hashing, JWT)
- **Nedelja 10:** Refresh flow + permissions + rate limit basics
- **Nedelja 11:** Pytest integration tests + fixtures
- **Nedelja 12:** OpenAPI polish + security checklist

**Mesec 4 (nedelje 13-16): Async + background tasks**

- **Nedelja 13:** Async FastAPI (await, lifespans)
- **Nedelja 14:** Background tasks + queue (Celery ili RQ)
- **Nedelja 15:** Redis cache + cache invalidation
- **Nedelja 16:** Observability (logs, health, metrics)

**Mesec 5 (nedelje 17-20): DevOps i deploy**

- **Nedelja 17:** Dockerfile + Compose lokalni setup
- **Nedelja 18:** GitHub Actions (lint + test)
- **Nedelja 19:** Deploy na Render/Fly.io/AWS free tier
- **Nedelja 20:** Secrets, env vars, monitoring basics

**Mesec 6 (nedelje 21-24): Portfolio i intervju**

- **Nedelja 21:** Case studies + README upgrade
- **Nedelja 22:** Test coverage + performance pass
- **Nedelja 23:** API design interview practice
- **Nedelja 24:** SQL practice + mock interviews

## Udemy plan po mesecima (izaberi 1-2 kursa mesecno)

Napomena: biraj 4.5+ ocenu i skorije update-ovan kurs. Ispod su konkretni linkovi koje si poslao.

- **Mesec 1 (FastAPI + Python osnove):**
  - FastAPI: <https://www.udemy.com/course/fastapi-the-complete-course/>
  - FastAPI (alternativa): <https://www.udemy.com/course/fastapi-course-python/>
  - FastAPI (alternativa): <https://www.udemy.com/course/completefastapi/>
  - FastAPI (alternativa): <https://www.udemy.com/course/fastapi-guide/>
  - Python baza: <https://www.udemy.com/course/complete-python-bootcamp/>
  - Python dublje: <https://www.udemy.com/course/python-3-deep-dive-part-1/>
- **Mesec 2 (SQLAlchemy + Postgres):**
  - SQLAlchemy + Alembic: <https://www.udemy.com/course/sqlalchemy-alembic-bootcamp/>
  - SQL + Postgres: <https://www.udemy.com/course/sql-and-postgresql/>
- **Mesec 3 (Auth + Pytest):**
  - Pytest (deo kursa): <https://www.udemy.com/course/playwright-python-automation-testing-pytest/>
  - TODO: posalji Udemy link za FastAPI JWT/Auth kurs (Spring Security nije relevantan za Python)
- **Mesec 4 (Async + Redis/Queue):**
  - Redis: <https://www.udemy.com/course/redis-the-complete-developers-guide-p/>
  - Celery (Django kurs, ali Celery koncept je upotrebljiv): <https://www.udemy.com/course/django-celery-mastery/>
  - TODO: posalji Udemy link za Async FastAPI ili Celery/RQ
- **Mesec 5 (Docker + CI/CD):**
  - Docker (izaberi jedan): <https://www.udemy.com/course/learn-docker/> ili <https://www.udemy.com/course/docker-mastery/>
  - GitHub Actions: <https://www.udemy.com/course/github-actions-the-complete-guide/>
- **Mesec 6 (System design + SQL):**
  - System design (izaberi jedan): <https://www.udemy.com/course/system-design-interview-prep/>
  - System design (alternativa): <https://www.udemy.com/course/software-architecture-design-of-modern-large-scale-systems/>
  - SQL practice: <https://www.udemy.com/course/the-complete-sql-bootcamp-30-hours-go-from-zero-to-hero/>

## Udemy -> Repo zadaci (direktno povezivanje)

**Mesec 1 (FastAPI fundamentals + Python typing)**

- **Teorija iz kursa:** routing, Pydantic, response modeli, status kodovi
- **Repo zadaci:** `app/main.py` osnovni CRUD, `tests/test_health.py`, `tests/test_items.py`, dokumentacija u `README`

**Mesec 2 (SQLAlchemy + Alembic + Postgres)**

- **Teorija iz kursa:** ORM modeli, session, migracije
- **Repo zadaci:** `app/db/base.py`, `app/db/session.py`, Alembic init, migracije za `Item`/`User`

**Mesec 3 (Auth + Pytest)**

- **Teorija iz kursa:** JWT, password hashing, refresh flow
- **Repo zadaci:** `app/core/security.py`, `app/api/routes/auth.py`, testovi login/refresh

**Mesec 4 (Async + Redis/Queue)**

- **Teorija iz kursa:** async endpoints, background tasks, caching
- **Repo zadaci:** `app/services/cache.py`, `app/workers/` (celery/rq), testovi za cache

**Mesec 5 (Docker + CI/CD)**

- **Teorija iz kursa:** Dockerfile, compose, GitHub Actions
- **Repo zadaci:** `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`

**Mesec 6 (System design + SQL)**

- **Teorija iz kursa:** API dizajn, query optimizacija
- **Repo zadaci:** README case study + SQL optimizacije + performance checklist

## Sprint taskovi - Mesec 2 (SQLAlchemy + Alembic)

**Nedelja 5: Postgres + SQL osnove**

- [ ] Postgres u Dockeru + health check
- [ ] Kreiraj `items` tabelu u SQL (ručno) za razumevanje
- [ ] Napravi `Item` model u SQLAlchemy
- [ ] 5 unit testova za CRUD bez migracija

**Nedelja 6: SQLAlchemy 2.0 session pattern**

- [ ] `SessionLocal` + dependency injection
- [ ] `crud.py` layer (create/read/update/delete)
- [ ] 5 dodatnih testova (update + delete)
- [ ] Dodaj `created_at`/`updated_at` polja

**Nedelja 7: Alembic migracije**

- [ ] Init Alembic + prva migracija
- [ ] Dodaj `users` tabelu
- [ ] Napiši seed skriptu za test data
- [ ] 5 testova za DB migracije

**Nedelja 8: Search + filter + indexi**

- [ ] Query param filter (status, created_at)
- [ ] Pagination (limit/offset)
- [ ] Dodaj index na `created_at`
- [ ] 3 integration testa za search/pagination

## Sprint taskovi - Mesec 3 (Auth + Testovi)

**Nedelja 9: Auth osnove**

- [ ] Password hashing (bcrypt/argon2)
- [ ] JWT access token
- [ ] Protected route primer
- [ ] 5 testova za auth flow

**Nedelja 10: Refresh + permissions**

- [ ] Refresh token flow
- [ ] Role/permission osnovno (user/admin)
- [ ] Rate limit osnovno (simple middleware)
- [ ] 5 testova (refresh + role)

**Nedelja 11: Integration tests**

- [ ] TestClient + DB fixture
- [ ] 8-10 integration testova
- [ ] Test coverage report (minimum 60%)
- [ ] Stabilizacija test suite

**Nedelja 12: OpenAPI + security checklist**

- [ ] OpenAPI primeri i opisi
- [ ] Security checklist u README
- [ ] Endpoint error standardizacija
- [ ] Finalni refactor

## Projekti (finalni portfolijo)

1. **Core CRUD API** (TODO/Notes)
   - Fokus: kvalitetan CRUD, testovi, dokumentacija
2. **Auth + Users API**
   - JWT, refresh, password reset flow
3. **Job Board API** (ili Inventory API)
   - Advanced: search, filter, cache, background tasks, deploy

## Milestones i checkliste

**Projekat 1 - Core CRUD API**

- [ ] CRUD endpoints + validacija
- [ ] 10+ unit testova
- [ ] OpenAPI opis + primeri
- [ ] Minimalni deploy (Render/Fly)

**Projekat 2 - Auth + Users API**

- [ ] Registracija + login + refresh
- [ ] Password hashing + reset flow
- [ ] 15+ integration testova
- [ ] Rate limit osnovno + security checklist

**Projekat 3 - Job Board API**

- [ ] Search, filter, pagination
- [ ] Redis cache + invalidation
- [ ] Background task (email/cleanup)
- [ ] CI/CD + Docker + live deploy

## Minimalni JS/TS

- Samo za potrosnju API-ja (fetch, error handling, osnovni UI)
- Alternativa: Postman + Swagger demo

## Preporuceni output po projektu

- README: opis, setup, env, test, endpoints
- OpenAPI link + Postman collection
- CI badge + deploy link
- Minimalni demo UI (opciono)

## Provera napretka (svakih 2 nedelje)

- Da li mozes objasniti API tok bez gledanja u kod?
- Da li imas barem 10-20 testova po projektu?
- Da li je deploy stabilan i reproducibilan?

## Prvi korak (danas)

1. Kreiraj repo `fastapi-portfolio`
2. Pokreni FastAPI "hello" endpoint
3. Napravi prvi test sa `pytest`
4. Zabelezi plan rada (dnevni ritam)

## Dnevni plan (prve 4 nedelje)

**Ritam:** 5 dana rada + 1 dan laganog review + 1 dan odmora

**Nedelja 1 (Python + HTTP osnove)**

- **Dan 1:** Python typing + error handling (2h) + HTTP status kodovi (1h) + mini zadaci (1-2h)
- **Dan 2:** Requests/response primeri + JSON parsing (2h) + mini projekat (1-2h)
- **Dan 3:** Struktura projekta + `venv` + `ruff` + `pytest` setup (3-4h)
- **Dan 4:** FastAPI uvod: app, routing, response modeli (3-4h)
- **Dan 5:** Prvi endpointi + basic validation (3-4h)
- **Dan 6 (review):** ponavljanje + kratka dokumentacija + 1 refactor

**Nedelja 2 (FastAPI + Pydantic)**

- **Dan 1:** Pydantic modeli + validation errori
- **Dan 2:** CRUD logika u memoriji + response modeli
- **Dan 3:** Error handling + status kodovi
- **Dan 4:** OpenAPI/Swagger pregled + docstrings
- **Dan 5:** Mini projekat: TODO API bez baze
- **Dan 6 (review):** cleanup + README update

**Nedelja 3 (Pytest + CRUD)**

- **Dan 1:** Pytest osnove + test struktura
- **Dan 2:** Unit testovi za CRUD
- **Dan 3:** Integration testovi (TestClient)
- **Dan 4:** Refactor + test coverage provera
- **Dan 5:** Mini deploy (lokalno) + demo endpointi
- **Dan 6 (review):** stabilizacija testova

**Nedelja 4 (Polish + OpenAPI)**

- **Dan 1:** Standardizuj response modele
- **Dan 2:** Error handling konvencije
- **Dan 3:** OpenAPI opis + primeri
- **Dan 4:** Finalni refactor + cleanup
- **Dan 5:** Dokumentacija i mini case study
- **Dan 6 (review):** checklist + plan za mesec 2

## Nedeljni deliverables (svaka nedelja)

- 1 mala funkcionalnost (feature)
- 5-10 testova
- 1 kratka beleka sta si naucio
- 1 mini refactor ili cleanup

## Udemy izbor - kako da biras kurs (bez lutanja)

- Minimalno 4.5 ocena i 2024+ update
- 50-70% reviewa iz poslednjih 12 meseci
- Kurs mora imati sekciju za testove i deploy (ili bar za tooling)
- Ako kurs nema projekte, preskoci

**Preporuka:** biraj 1 "core" kurs + 1 "support" kurs po mesecu

**Primer search query-ja:**

- "FastAPI complete course 2025"
- "SQLAlchemy 2.0 Alembic"
- "Pytest testing python"
- "Docker for developers"
- "GitHub Actions CI/CD"

## Job search priprema (od meseca 4)

- Mesec 4: zapocni LinkedIn/GitHub polishing
- Mesec 5: 10-15 ciljanih prijava nedeljno
- Mesec 6: mock intervjui + case study pisanje

**Portfolio minimum:** 2 deployed API-ja + 1 advanced API

## Dan 0 - setup checklist (ako krecemo od nule)

- [ ] Python 3.11+ instaliran
- [ ] Postgres lokalno ili u Dockeru
- [ ] GitHub nalog + SSH key
- [ ] `pre-commit`, `ruff`, `pytest` rade
- [ ] Repo `fastapi-portfolio` spreman
