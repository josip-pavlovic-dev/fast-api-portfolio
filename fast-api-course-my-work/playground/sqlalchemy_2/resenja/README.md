# SQLAlchemy 2.0: rešenja vežbi

Ovaj folder sadrži po jedan samostalni, pokretljivi primer za svaku od 10 lekcija. Skripte su rešenja za proveru nakon što samostalno prekucaš vežbu iz teorijske beleške; nisu zamena za pokušaj.

Sve skripte koriste postojeći root `.venv` i SQLite bazu u memoriji (`sqlite://`). Ne čitaju niti menjaju aplikacione ili projektne baze i ne traže novu instalaciju paketa.

## Kako da radiš

1. Otvori teorijsku belešku za lekciju i uradi zadatak bez gledanja rešenja.
2. Pokreni odgovarajući fajl iz root-a repozitorijuma.
3. Prekucaj rešenje i uporedi ga sa izlazom, SQL logom i `assert` proverama.
4. Menjaj vrednosti ili ukloni jedan uslov i predvidi rezultat pre ponovnog pokretanja.

Pokretanje pojedinačnog primera:

```bash
.venv/bin/python fast-api-course-my-work/playground/sqlalchemy_2/resenja/01_uvod_core_orm.py
```

## Mapa lekcija

| Lekcija                                  | Teorija                                                                      | Rešeni primer                                                  |
| ---------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 01: Uvod u SQLAlchemy                    | [Beleška 01](../../../teorija_sqlalchemy_2/01_introduction_to_SQLAlchemy.md) | [01_uvod_core_orm.py](01_uvod_core_orm.py)                     |
| 02: Engine i Connection                  | [Beleška 02](../../../teorija_sqlalchemy_2/02_working_with_the_engine.md)    | [02_engine_connection.py](02_engine_connection.py)             |
| 03: Transakcije i upravljanje konekcijom | [Beleška 03](../../../teorija_sqlalchemy_2/03_connection_management.md)      | [03_transakcije.py](03_transakcije.py)                         |
| 04: Table metadata i ORM model           | [Beleška 04](../../../teorija_sqlalchemy_2/04_table_metadata_model.md)       | [04_table_metadata.py](04_table_metadata.py)                   |
| 05: Kreiranje šeme i strani ključ        | [Beleška 05](../../../teorija_sqlalchemy_2/05_create_database_schema.md)     | [05_schema_i_foreign_key.py](05_schema_i_foreign_key.py)       |
| 06: Jedan INSERT i server default        | [Beleška 06](../../../teorija_sqlalchemy_2/06_insert_data.md)                | [06_insert_i_server_default.py](06_insert_i_server_default.py) |
| 07: Grupni INSERT                        | [Beleška 07](../../../teorija_sqlalchemy_2/07_bulk_data_insertion.md)        | [07_bulk_insert.py](07_bulk_insert.py)                         |
| 08: SELECT                               | [Beleška 08](../../../teorija_sqlalchemy_2/08_selecting_data.md)             | [08_select.py](08_select.py)                                   |
| 09: Filtriranje i JOIN tipovi            | [Beleška 09](../../../teorija_sqlalchemy_2/09_filtering_and_ordering.md)     | [09_filter_order_join.py](09_filter_order_join.py)             |
| 10: ORM Session i Unit of Work           | [Beleška 10](../../../teorija_sqlalchemy_2/10_ORM_session_and_work_unit.md)  | [10_session_unit_of_work.py](10_session_unit_of_work.py)       |
