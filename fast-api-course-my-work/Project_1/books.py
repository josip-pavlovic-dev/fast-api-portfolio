from fastapi import FastAPI

app = FastAPI()


BOOKS: list[dict[str, str]] = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/mybook")
async def read_my_book():
    return {"book_title": "My favourite book!"}


@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():  # type: ignore
            return book


@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = list()
    for book in BOOKS:
        if book["category"].casefold() == category.casefold():  # type: ignore
            books_to_return.append(book)
    return books_to_return


# NAPOMENA: FastAPI automatski parsira query parametre iz URL-a. Na primer, /books/?category=science će pozvati read_category_by_query sa category="science".


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return: list[str] = list()
    for book in BOOKS:
        if (
            book.get("author").casefold() == book_author.casefold()  # type: ignore
            and book.get("category").casefold() == category.casefold()  # type: ignore
        ):
            books_to_return.append(book)  # type: ignore
    return books_to_return
