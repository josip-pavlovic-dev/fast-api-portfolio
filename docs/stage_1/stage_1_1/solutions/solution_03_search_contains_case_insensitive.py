from fastapi import FastAPI, Query

app = FastAPI()

books: list[dict] = [
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
    results = books

    if title:
        title_norm = title.strip().lower()
        results = [book for book in results if title_norm in book["title"].lower()]

    if author:
        author_norm = author.strip().lower()
        results = [book for book in results if author_norm in book["author"].lower()]

    return results
