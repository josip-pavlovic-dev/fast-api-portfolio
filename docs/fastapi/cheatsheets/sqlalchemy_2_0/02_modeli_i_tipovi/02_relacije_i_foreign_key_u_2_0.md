# 04 - Foreign key i relacije u 2.0

## Tvoj trenutni slucaj

Imas:

- `Users.id`
- `Todos.owner_id -> ForeignKey("users.id")`

To ostaje isto i u 2.0, samo sintaksa prelazi na `mapped_column`.

## Primer u 2.0 stilu

```python
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

## Kada uvoditi relationship

Moze odmah, ali nije obavezno za prvi korak refaktora.

Za tvoj plan je pametno:

1. prvo prebaciti kolone + query stil,
2. zatim eventualno dodati `relationship()` ako bude trebalo.

Tako smanjujes rizik i lakse debagujes.
