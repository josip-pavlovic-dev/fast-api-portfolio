# Objašnjenje funkcije `get_users` u FastAPI aplikaciji

> Ovaj dokument objašnjava funkciju `get_users` u FastAPI aplikaciji liniju po liniju. Posle svakog koda sledi objašnjenje šta taj deo radi.

## Funkcija `get_users`

```python
@app.get("/users", response_model=list[UserResponse])
```

- `@app.get("/users", ...)` — dekorator koji kaže FastAPI-ju: "kad neko pošalje GET zahtev na `/users`, pozovi funkciju ispod".

- `response_model=list[UserResponse]` — kaže FastAPI-ju da odgovor treba da bude **lista** objekata oblika `UserResponse` (definisan gore u fajlu). FastAPI će automatski filtrirati/validirati polja tako da odgovor uvek ima tačno tu strukturu (id, name, email, role, is_active), bez obzira šta interno vratiš.

```python
def get_users(
    role: str | None = Query(default=None, description="Filter korisnika po roli."),
    is_active: bool | None = Query(
        default=None, description="Filter po aktivnom statusu."
    ),
):
```

---

## Query parametri `role` i `is_active`

- Ovo su **query parametri** — dolaze iz URL-a posle `?`, npr. `/users?role=admin&is_active=true`.

- `role: str | None = Query(...)`:
  - `role: str | None` — tip parametra: string ili `None` (nije obavezan).

  - `= Query(default=None, description="...")` — umesto običnog `= None`, koristi se `Query(...)` da bi mogao da dodaš metapodatke (npr. `description`) koji se prikazuju u automatskoj dokumentaciji (`docs`). `default=None` znači: ako korisnik ne pošalje `?role=...`, vrednost će biti `None`.

  - Da je napisano samo `role: str | None = None`, radilo bi identično funkcionalno, samo bez opisa u Swagger dokumentaciji.

- Isto važi za `is_active: bool | None = Query(default=None, ...)` — FastAPI automatski konvertuje string iz URL-a (`"true"`/`"false"`) u pravi `bool`.

Dakle, u praksi: ako pozoveš `GET /users` bez ičega, `role` i `is_active` su `None`. Ako pozoveš `GET /users?role=admin`, `role` postaje `"admin"`.

## Filtriranje korisnika po query parametrima

```python
    filtered_users = users
```

- Kreira novu promenljivu koja **referencira istu listu** kao globalni `users` (ne pravi kopiju). Ovde to nije problem jer se dalje ne modifikuje in-place, već se pravi nova lista kroz list comprehension.

- PITANJE: Zašto ne koristimodirektno `users` umesto `filtered_users`?
  - Odgovor: Ako bismo filtrirali direktno `users`, izgubili bismo originalnu listu i svaki sledeći poziv funkcije bi radio sa već filtriranom listom. Korišćenjem `filtered_users` pravimo novu listu za svaki zahtev, a originalna lista `users` ostaje netaknuta.

```python
    if role is not None:
        filtered_users = [user for user in filtered_users if user["role"] == role]
```

- Ako je korisnik poslao `role` u query-ju (nije `None`), napravi novu listu koja sadrži samo korisnike čiji `user["role"]` odgovara traženoj vrednosti.
- List comprehension `[x for x in lista if uslov]` je kraći zapis za for-petlju koja filtrira elemente.

```python
    if is_active is not None:
        filtered_users = [
            user for user in filtered_users if user["is_active"] == is_active
        ]
```

- Isto, ali za `is_active` — dodatno filtrira (nad već filtriranom listom od prethodnog filtriranja po `role`) po statusu aktivnosti. To znači da se oba filtera kombinuju: prvo po `role`, pa po `is_active` statusu. Konačna lista sadrži samo korisnike koji zadovoljavaju oba kriterijuma.

```python
    return filtered_users
```

---

## Zaključak

- Vraća finalnu listu. FastAPI je zatim serijalizuje prema `response_model=list[UserResponse]`.

**Zašto je `is not None` bitno, a ne samo `if role:`** — jer prazan string `""` ili `False` bi bili "falsy" u Pythonu, pa bi `if role:` pogrešno preskočio filtriranje za takve vrednosti. `is not None` proverava striktno da li je parametar uopšte poslat.
