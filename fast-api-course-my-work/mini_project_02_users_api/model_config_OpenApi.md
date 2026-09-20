# model_config u Pydantic-u za OpenAPI i SQLAlchemy

## OpenAPI primer u Pydantic-u

`model_config` iz kursa je potpuno tačan:

```python
model_config = {
    "json_schema_extra": {
        "example": {
            ...
        }
    }
}
```

On služi da Swagger dokumentacija (`docs`) prikaže primer JSON tela za `BookRequest`. Ne utiče na validaciju ni na `model_dump()`.

Postoje različita podešavanja unutar istog `model_config`:

```python
# Za Swagger/OpenAPI primer:
model_config = {
    "json_schema_extra": {
        "example": {...}
    }
}
```

---

## SQLAlchemy primer u Pydantic-u

```python
# Kasnije, uz SQLAlchemy:
model_config = ConfigDict(from_attributes=True)
```

`from_attributes=True` je posebno za response model, npr. `UserResponse`, da Pydantic može čitati SQLAlchemy objekat kroz atribute poput `user.id` i `user.email`.

Možeš ih i spojiti kada dođe vreme:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    # polja...

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {...}},
    )
```
