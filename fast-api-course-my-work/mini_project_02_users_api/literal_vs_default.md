# Literal tip u UserResponse klasi

## Korišćenje Literal tipa u response modelu

U `UserResponse` klasi stavi:

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Literal["admin", "user"]
    is_active: bool

```

Dakle, **ne** `Literal["admin", "users"]`, jer su dozvoljene vrednosti `"admin"` i `"user"` u jednini.

Tvoja klasa je ispravna:

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Literal["admin", "user"]
    is_active: bool
```

Rečenica iz dokumenta znači da treba ukloniti **default vrednosti**:

```python
role: Literal["admin", "user"] = "user"  # nije potrebno u response modelu
is_active: bool = True                   # nije potrebno
```

`Literal` i default vrednost nisu ista stvar:

- `Literal["admin", "user"]` određuje koje vrednosti su dozvoljene.
- `= "user"` određuje podrazumevanu vrednost ako podatak nije prosleđen.

`UserCreate` treba default vrednosti, jer korisnik može izostaviti ta polja:

```python
role: Literal["admin", "user"] = "user"
is_active: bool = True
```

`UserResponse` treba samo da opiše stvarne podatke koje server vraća, bez defaulta. `str` bi radio, ali `Literal` je precizniji i sprečava da API vrati neispravnu ulogu.
