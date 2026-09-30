# 12 - Plan 7 dana: SQLAlchemy 2.0 + Alembic prelaz za tvoj TodoApp

Ovo je praktican, vremenski ogranicen plan koji te vodi od trenutnog stanja (legacy SQLAlchemy stil) do stabilnog SQLAlchemy 2.0 + Alembic workflow-a pre oblasti 12.

Plan je dizajniran da minimizira rizik: mali koraci, cesti checkpoint-i, bez "big-bang" refaktora.

## Pravilo rada za svih 7 dana

- Svaki dan: 90 do 120 minuta fokusa.
- Prvo uradi mini teoriju, pa odmah primeni na svom kodu.
- Menjaj jedan podsistem po sesiji (modeli ili query ili migracije), ne sve odjednom.
- Na kraju svakog dana imas jasan "exit kriterijum".

---

## Dan 1 - Mentalni model SQLAlchemy 2.0

Cilj:

- Razumeti sta je novo u 2.0 i zasto se prelazi sa `query()` stila na `select()` stil.

Sta ucis:

- [01_sta_je_novo_u_sqlalchemy_2_0.md](../01_osnove/01_sta_je_novo_u_sqlalchemy_2_0.md)
- [02_engine_sessionmaker_i_session.md](../01_osnove/02_engine_sessionmaker_i_session.md)

Prakticni zadatak:

- Napravi licnu mapu "legacy -> 2.0" za 5 najcescih obrazaca iz svog projekta.
- Primeri koje mapiras:
  - `db.query(Model).all()` -> `select(Model)` + `execute()` + `scalars().all()`
  - `db.query(Model).filter(...).first()` -> `select(Model).where(...)` + `scalars().first()`

Exit kriterijum:

- Mozes usmeno objasniti putanju: `select()` -> `execute()` -> `scalars()` bez gledanja u belezke.

---

## Dan 2 - Modeli u 2.0 stilu

Cilj:

- Prebaciti bar jedan model na `Mapped` i `mapped_column` bez menjanja biznis logike.

Sta ucis:

- [01_mapped_i_mapped_column.md](../02_modeli_i_tipovi/01_mapped_i_mapped_column.md)
- [02_relacije_i_foreign_key_u_2_0.md](../02_modeli_i_tipovi/02_relacije_i_foreign_key_u_2_0.md)

Prakticni zadatak:

- Refaktorisi `Todos` model u 2.0 tipizovani stil.
- Ako si stabilan, refaktorisi i `Users` model.
- Ne diraj jos query deo u routerima.

Exit kriterijum:

- Model(i) koriste `Mapped[...]` i `mapped_column(...)`.
- Aplikacija se i dalje pokrece bez regresije na osnovnom health check-u.

---

## Dan 3 - SELECT upiti u 2.0

Cilj:

- Prevesti read operacije u auth/todo toku sa legacy query API-ja na 2.0 stil.

Sta ucis:

- [01_select_where_execute_scalars.md](../03_upiti_u_2_0/01_select_where_execute_scalars.md)

Prakticni zadatak:

- Kreni od najmanjeg rizika:
  - get all todos za current user
  - get todo by id + owner filter

- Odrzi istu HTTP semantiku (401/403/404) kao pre refaktora.

Exit kriterijum:

- Najmanje 2 read endpoint-a rade u 2.0 stilu sa istim ponasanjem kao pre.

---

## Dan 4 - UPDATE/DELETE i transakcije

Cilj:

- Stabilno prevesti write tokove i ucvrstiti transakcioni obrazac.

Sta ucis:

- [02_update_delete_i_transakcije.md](../03_upiti_u_2_0/02_update_delete_i_transakcije.md)

Prakticni zadatak:

- Refaktorisi PUT/DELETE todo endpoint-e na 2.0 stil.
- Potvrdi da `commit()` ostaje na pravom mestu i da nema "silent fail" slucajeva.

Exit kriterijum:

- PUT i DELETE rade sa vlasnickim filterom (`owner_id`) i bez promene API ugovora.

---

## Dan 5 - FastAPI integracija i clean session pattern

Cilj:

- Ucvrstiti dependency/session pattern da bude cist i predvidiv pre migracija.

Sta ucis:

- [01_depends_session_pattern_2_0.md](../04_fastapi_integracija/01_depends_session_pattern_2_0.md)
- [02_auth_todo_upiti_pre_posle.md](../04_fastapi_integracija/02_auth_todo_upiti_pre_posle.md)

Prakticni zadatak:

- Proveri da svi routeri koriste isti session dependency pristup.
- Ujednaci stil u auth i todo route-ovima (bez mesanja legacy i 2.0 sintakse u istoj funkciji).

Exit kriterijum:

- Nemas endpoint koji mesa `query()` i `select()` u istoj logickoj celini.

---

## Dan 6 - Alembic setup na postojecem projektu

Cilj:

- Uvesti Alembic kao izvor istine za evoluciju seme.

Sta ucis:

- [06_alembic_migracije_detaljno.md](../../baze/06_alembic_migracije_detaljno.md)
- [02_alembic_i_sqlalchemy_2_0_veza.md](02_alembic_i_sqlalchemy_2_0_veza.md)

Prakticni zadatak:

- Inicijalizuj Alembic.
- Podesi `target_metadata` na tvoj `Base.metadata`.
- Napravi prvu reviziju i pokreni upgrade na lokalnoj bazi.
- Dokumentuj tacan redosled komandi koje su radile kod tebe.

Exit kriterijum:

- Imas validnu migraciju i uspesan upgrade bez rucnog menjanja tabela direktno u DB.

---

## Dan 7 - Verifikacija i "pre-oblast-12" gate

Cilj:

- Potvrditi da je refaktor stabilan i da mozes bezbedno dalje.

Sta prolazis:

- [03_checklista_pre_oblasti_12.md](03_checklista_pre_oblasti_12.md)
- [01_korak_po_korak_refaktor_plan.md](01_korak_po_korak_refaktor_plan.md)

Prakticni zadatak:

- Uradi finalni smoke test:
  - auth registracija/login
  - create/get/update/delete todo
  - ownership zastita

- Potvrdi da su migracije reproducibilne na cistoj bazi.

Exit kriterijum:

- Svi kljucni endpoint-i rade.
- Migracije rade deterministicki.
- Spreman si za oblast 12 bez dugova koji bi kasnije eksplodirali.

---

## Anti-haos pravila (obavezno)

- Ne refaktorisi i modele i sve rute i migracije u istom commitu.
- Ako endpoint promeni ponasanje, vrati korak nazad i izoluj uzrok.
- Svaki dan zatvori kratkim zapisom: "sta radi", "sta ne radi", "sta je sledece".

## Predlog tempa posle ovih 7 dana

Ako zavrsis svih 7 dana sa zelenim checkpoint-ima, odmah nakon toga kreni na oblast 12, ali:

- i dalje radi inkrementalno,
- svaku novu DB promenu vodi kroz Alembic,
- i odrzavaj 2.0 stil kao jedini standard u novom kodu.
