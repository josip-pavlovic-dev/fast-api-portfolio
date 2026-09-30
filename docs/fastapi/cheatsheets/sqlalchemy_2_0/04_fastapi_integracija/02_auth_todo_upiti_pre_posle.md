# 08 - Auth/Todo upiti: pre i posle (konkretno za tvoj kod)

## A) get_current_user

Pre:

```python
user = db.query(Users).filter(Users.id == user_id).first()
```

Posle:

```python
from sqlalchemy import select

stmt = select(Users).where(Users.id == user_id)
user = db.execute(stmt).scalars().first()
```

## B) get_all todos

Pre:

```python
todo_models = db.query(Todos).filter(Todos.owner_id == current_user.id).all()
```

Posle:

```python
stmt = select(Todos).where(Todos.owner_id == current_user.id)
todo_models = db.execute(stmt).scalars().all()
```

## C) read_todo ownership

Pre:

```python
db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == current_user.id).first()
```

Posle:

```python
stmt = select(Todos).where(Todos.id == todo_id, Todos.owner_id == current_user.id)
todo_model = db.execute(stmt).scalars().first()
```

Poenta: auth i ownership logika ostaju iste, menja se SQLAlchemy jezik kojim to izrazavas.
