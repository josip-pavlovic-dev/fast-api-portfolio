from fastapi import FastAPI, Query

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "FastAPI for Beginners",
        "author": "John Doe",
        "description": "Practical intro",
    },
    {
        "id": 2,
        "title": "Advanced FastAPI",
        "author": "Jane Smith",
        "description": "Deep dive",
    },
    {
        "id": 3,
        "title": "Python Patterns",
        "author": "Ana Nikolic",
        "description": "Design ideas",
    },
]


@app.get("/books/search")
async def search_books(
    title: str | None = Query(default=None, min_length=1),
    author: str | None = Query(default=None, min_length=1),
):
    # TODO 1: Kreni od cele liste books.
    # TODO 2: Ako postoji title, uradi contains pretragu po title (case-insensitive).
    # TODO 3: Ako postoji author, uradi contains pretragu po author (case-insensitive).
    # TODO 4: Vrati filtrirane rezultate.
    pass
