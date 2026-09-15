# FastAPI praktikum za početnike

Ovaj folder je strukturiran kao praktični put od jednostavnih endpointa do kompletne CRUD aplikacije.

## Redosled učenja

1. [01_common_errors_fastapi_pydantic.md](01_common_errors_fastapi_pydantic.md)
   Najčešće greške i šta one zapravo znače.

2. [02_status_codes_and_http_exceptions.md](02_status_codes_and_http_exceptions.md)
   `status_code`, `HTTPException`, i HTTP odgovori.

3. [03_post_put_delete_and_crud.md](03_post_put_delete_and_crud.md)
   Osnovni CRUD pregled.

4. [04_crud_practice_01_get_and_post.md](04_crud_practice_01_get_and_post.md)
   Prvi praktični CRUD korak: `GET` i `POST`.

5. [05_crud_practice_02_get_by_id_and_404.md](05_crud_practice_02_get_by_id_and_404.md)
   `GET /books/{book_id}` i 404 greške.

6. [06_crud_practice_03_put_and_delete.md](06_crud_practice_03_put_and_delete.md)
   Ažuriranje i brisanje knjiga.

7. [07_crud_practice_04_final_project.md](07_crud_practice_04_final_project.md)
   Finalni kompletan CRUD projekat.

## Pravilo za učenje

Ne preskači redosled.

Svaki novi file gradi na prethodnom. Cilj nije da odmah sve naučiš, nego da progresivno dodaješ jednu novu sposobnost.

---

## Predlog rada

Za svaki file:

1. pročitaj teoriju
2. napiši kod u lokalnom projektu
3. testiraj endpoint
4. probaj i najmanje 3 inputa: normalan, pogrešan i edge case
5. zapiši šta si naučio u 3-5 rečenica

---

## Tematski fokus

Ovaj set je zasnovan na jednostavnom modelu knjiga, jer je to najbolji način da se razumeju:

- Pydantic modeli
- `response_model`
- `HTTPException`
- `status_code`
- CRUD endpointi
- request/response schemе

---

## Napomena

Ovo je “praktični” put, ne “teorijski” kurs.
Cilj je da znaš kako da već u prvoj fazi napišeš realan API, a ne samo da čitaš definicije.
