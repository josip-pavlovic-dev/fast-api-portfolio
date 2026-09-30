# 11 - Checklista pre oblasti 12 (Large Production Database Setup)

Pre nego sto predjes na oblast 12, potvrdi:

1. Razumes `Mapped` i `mapped_column`.
2. Umes da prevedes `query().filter().first()` u `select().where().execute().scalars().first()`.
3. Auth i todo tok rade posle refaktora.
4. `get_current_user` i ownership filter su netaknuti po logici.
5. Znacenje 401/403/404 je ostalo konzistentno.
6. Imas plan za Alembic (init, env.py, target_metadata, revision, upgrade/downgrade).
7. Ne oslanjas se na `create_all()` za evoluciju seme kada krenu realne promene tabela.

Ako je sve cekirano, spreman si za oblast 12 bez haosa u bazi.
