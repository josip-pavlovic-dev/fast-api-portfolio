# SQLAlchemy 2.0 - Putanja ucenja (od nule do tvog refaktora)

Ovaj mini-kurs je napravljen za tvoj trenutni nivo: završio si auth deo, razumeš klasičan SQLAlchemy stil (`Column`, `query()`, `filter()`, `first()`), i sledeći korak ti je prelazak na SQLAlchemy 2.0 pre ozbiljnog production DB setup-a.

## Redosled rada

1. `01_osnove/01_sta_je_novo_u_sqlalchemy_2_0.md`
2. `01_osnove/02_engine_sessionmaker_i_session.md`
3. `02_modeli_i_tipovi/01_mapped_i_mapped_column.md`
4. `02_modeli_i_tipovi/02_relacije_i_foreign_key_u_2_0.md`
5. `03_upiti_u_2_0/01_select_where_execute_scalars.md`
6. `03_upiti_u_2_0/02_update_delete_i_transakcije.md`
7. `04_fastapi_integracija/01_depends_session_pattern_2_0.md`
8. `04_fastapi_integracija/02_auth_todo_upiti_pre_posle.md`
9. `05_refaktor_todoapp/01_korak_po_korak_refaktor_plan.md`
10. `05_refaktor_todoapp/02_alembic_i_sqlalchemy_2_0_veza.md`
11. `05_refaktor_todoapp/03_checklista_pre_oblasti_12.md`
12. `05_refaktor_todoapp/04_plan_7_dana_sqlalchemy2_alembic.md`

---

## Kako koristiti ovaj materijal

- Prvo pročitaj lekciju, pa odmah uporedi sa svojim trenutnim kodom u `TodoApp`.
- Ne refaktorisi sve odjednom.
- Radi male, proverljive korake: `modeli` -> `query stil` -> `routeri` -> `test smoke` -> `Alembic`.
- Ako neki korak nije jasan, vrati se jednu lekciju nazad i napravi mini vežbu.

---

## Krajnji cilj

Da pre oblasti 12 imaš:

- SQLAlchemy 2.0 modele (`Mapped`, `mapped_column`),
- 2.0 query stil (`select`, `Session.execute`, `scalars`),
- jasan plan migracije na `Alembic` bez gubitka podataka,
- i stabilan FastAPI `auth/todo` tok na novom stilu.

---
