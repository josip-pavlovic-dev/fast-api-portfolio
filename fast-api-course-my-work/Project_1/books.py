import asyncio  # Služi za izvođenje asinhronih funkcija i testiranje FastAPI ruta asinhrono.
from collections.abc import Awaitable, Callable

from fastapi import Body, FastAPI, HTTPException

app = FastAPI(
    title="FastAPI Books API",
    description="API za upravljanje knjigama koristeći FastAPI.",
    version="1.0",
)

BOOKS: list[dict[str, str]] = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


@app.get("/")
async def root() -> dict[str, str]:
    return {"Opis": "API za upravljanje knjigama koristeći FastAPI."}


@app.get("/books")
async def sve_knjige() -> list[dict[str, str]]:
    return BOOKS


@app.get("/books/{books_by_title}")
async def pretraga_po_nazivu_knjige(books_by_title: str) -> dict[str, str] | None:
    if not BOOKS:
        return None

    for book in BOOKS:
        book_title = book.get("title")
        if (
            book_title is not None
            and book_title.casefold() == books_by_title.casefold()
        ):
            return book

    return None


@app.get(
    "/books/"
)  # Putanja se mora završavati sa / ako se koristi query parametar umesto path parametra.
async def pretraga_knjiga_po_kategorijama(category: str) -> list[dict[str, str]]:
    if not BOOKS:
        return []

    lista_knjiga: list[dict[str, str]] = []

    for book in BOOKS:
        book_category = book.get("category")
        if (
            book_category is not None
            and book_category.casefold() == category.casefold()
        ):
            lista_knjiga.append(book)

    return lista_knjiga


@app.get("/books/author/")
async def pretraga_knjiga_po_autoru(author: str) -> list[dict[str, str]]:
    if not BOOKS:
        return []

    lista_knjiga: list[dict[str, str]] = []

    for book in BOOKS:
        book_author = book.get("author")
        if book_author is not None and book_author.casefold() == author.casefold():
            lista_knjiga.append(book)

    return lista_knjiga


@app.get("/books/author/{author}/")
async def pretraga_knjiga_po_autoru_i_kategoriji(
    author: str, category: str
) -> list[dict[str, str]]:

    if not BOOKS:
        return []

    lista_knjiga: list[dict[str, str]] = []

    for book in BOOKS:
        book_author = book.get("author")
        book_category = book.get("category")

        if (
            book_author is not None and book_author.casefold() == author.casefold()
        ) and (
            book_category is not None
            and book_category.casefold() == category.casefold()
        ):
            lista_knjiga.append(book)

    return lista_knjiga


@app.post("/books")
async def kreiraj_novu_knjigu_i_dodaj_je_u_listu(
    new_book: dict[str, str] = Body(),
) -> dict[str, str]:
    BOOKS.append(new_book)
    return new_book


@app.put("/books/{book_title}")
async def azuriraj_knjigu_po_naslovu(
    book_title: str, updated_book: dict[str, str] = Body()
) -> dict[str, str]:
    for index, book in enumerate(BOOKS):
        current_title = book.get("title")
        if (
            current_title is not None
            and current_title.casefold() == book_title.casefold()
        ):
            BOOKS[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")


@app.delete("/books/delete_book/{book_title}")
async def obrisi_knjigu(book_title: str) -> dict[str, str]:
    for index, book in enumerate(BOOKS):
        current_title = book.get("title")
        if (
            current_title is not None
            and current_title.casefold() == book_title.casefold()
        ):
            del BOOKS[index]
            return {"detail": "Knjiga je obrisana"}

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")


async def run_get_assert_tests() -> None:
    original_books = BOOKS.copy()

    try:
        assert await root() == {
            "Opis": "API za upravljanje knjigama koristeći FastAPI."
        }
        assert await sve_knjige() == original_books
        assert await pretraga_po_nazivu_knjige("title one") == original_books[0]
        assert await pretraga_po_nazivu_knjige("unknown title") is None
        assert await pretraga_knjiga_po_kategorijama("SCIENCE") == original_books[:2]
        assert await pretraga_knjiga_po_kategorijama("unknown") == []
        assert await pretraga_knjiga_po_autoru("AUTHOR TWO") == [
            original_books[1],
            original_books[5],
        ]
        assert await pretraga_knjiga_po_autoru("unknown") == []
        assert await pretraga_knjiga_po_autoru_i_kategoriji(
            "author one", "SCIENCE"
        ) == [original_books[0]]
        assert await pretraga_knjiga_po_autoru_i_kategoriji("author one", "math") == []

        books_with_missing_fields = [
            {"title": "First", "category": "science"},
            {"author": "Author One", "category": "science"},
            {"title": "Third", "author": "Author One"},
            {"title": "Fourth", "author": "Author One", "category": "science"},
        ]
        BOOKS[:] = books_with_missing_fields

        assert await pretraga_po_nazivu_knjige("FIRST") == books_with_missing_fields[0]
        assert await pretraga_knjiga_po_kategorijama("science") == [
            books_with_missing_fields[0],
            books_with_missing_fields[1],
            books_with_missing_fields[3],
        ]
        assert await pretraga_knjiga_po_autoru("author one") == [
            books_with_missing_fields[1],
            books_with_missing_fields[2],
            books_with_missing_fields[3],
        ]
        assert await pretraga_knjiga_po_autoru_i_kategoriji(
            "author one", "science"
        ) == [books_with_missing_fields[1], books_with_missing_fields[3]]

        BOOKS.clear()
        assert await sve_knjige() == []
        assert await pretraga_po_nazivu_knjige("anything") is None
        assert await pretraga_knjiga_po_kategorijama("science") == []
        assert await pretraga_knjiga_po_autoru("Author One") == []
        assert (
            await pretraga_knjiga_po_autoru_i_kategoriji("Author One", "science") == []
        )
    finally:
        BOOKS[:] = original_books


async def assert_http_404(operation: Callable[[], Awaitable[object]]) -> None:
    try:
        await operation()
    except HTTPException as error:
        assert error.status_code == 404
        assert error.detail == "Knjiga nije pronađena"
    else:
        raise AssertionError("Očekivan je HTTP 404 za nepostojeću knjigu.")


async def run_post_put_delete_assert_tests() -> None:
    original_books = [book.copy() for book in BOOKS]

    first_book = {
        "title": "Title One",
        "author": "Author One",
        "category": "science",
    }
    second_book = {
        "title": "Title Two",
        "author": "Author Two",
        "category": "history",
    }
    new_book = {
        "title": "Title Three",
        "author": "Author Three",
        "category": "math",
    }
    updated_book = {
        "title": "Updated Title One",
        "author": "Updated Author",
        "category": "history",
    }

    try:
        BOOKS[:] = [first_book.copy(), second_book.copy()]

        created_book = await kreiraj_novu_knjigu_i_dodaj_je_u_listu(new_book)
        assert created_book == new_book
        assert BOOKS == [first_book, second_book, new_book]

        replaced_book = await azuriraj_knjigu_po_naslovu("TITLE ONE", updated_book)
        assert replaced_book == updated_book
        assert BOOKS == [updated_book, second_book, new_book]

        books_before_missing_update = BOOKS.copy()
        await assert_http_404(
            lambda: azuriraj_knjigu_po_naslovu("Unknown Title", updated_book)
        )
        assert BOOKS == books_before_missing_update

        delete_result = await obrisi_knjigu("title two")
        assert delete_result == {"detail": "Knjiga je obrisana"}
        assert BOOKS == [updated_book, new_book]

        books_before_missing_delete = BOOKS.copy()
        await assert_http_404(lambda: obrisi_knjigu("Unknown Title"))
        assert BOOKS == books_before_missing_delete

        BOOKS.clear()
        await assert_http_404(
            lambda: azuriraj_knjigu_po_naslovu("Unknown Title", updated_book)
        )
        await assert_http_404(lambda: obrisi_knjigu("Unknown Title"))

        empty_list_book = {
            "title": "First Book",
            "author": "First Author",
            "category": "science",
        }
        assert (
            await kreiraj_novu_knjigu_i_dodaj_je_u_listu(empty_list_book)
            == empty_list_book
        )
        assert BOOKS == [empty_list_book]
    finally:
        BOOKS[:] = original_books


if __name__ == "__main__":
    asyncio.run(run_get_assert_tests())
    asyncio.run(run_post_put_delete_assert_tests())
    print("Svi assert testovi su prosli.")
