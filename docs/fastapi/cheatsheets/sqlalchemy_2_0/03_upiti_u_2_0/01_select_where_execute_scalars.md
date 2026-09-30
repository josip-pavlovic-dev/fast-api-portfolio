# 05 - 2.0 upiti: select, where, execute, scalars

## Osnovni obrazac

```python
from sqlalchemy import select

stmt = select(Users).where(Users.id == user_id)
user = db.execute(stmt).scalars().first()
```

## Mapiranje sa tvog koda

Trenutno:

```python
db.query(Users).filter(Users.id == user_id).first()
```

2.0:

```python
stmt = select(Users).where(Users.id == user_id)
user = db.execute(stmt).scalars().first()
```

## Lista rezultata

Trenutno:

```python
db.query(Todos).filter(Todos.owner_id == current_user.id).all()
```

2.0:

```python
stmt = select(Todos).where(Todos.owner_id == current_user.id)
todos = db.execute(stmt).scalars().all()
```

## Mentalni model

- `select(...)` = gradis SQL izraz
- `execute(...)` = pokreces izraz
- `scalars()` = uzimas ORM instance
- `first()/all()` = finalni shape rezultata
