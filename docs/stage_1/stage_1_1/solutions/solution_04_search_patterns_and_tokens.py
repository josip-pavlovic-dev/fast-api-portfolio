from fastapi import FastAPI, Query

app = FastAPI()

books: list[dict] = [
    {
        "id": 1,
        "title": "FastAPI in Action",
        "author": "Bob Brown",
        "description": "Practical API building guide",
    },
    {
        "id": 2,
        "title": "Mastering FastAPI",
        "author": "Alice Johnson",
        "description": "Advanced API techniques",
    },
    {
        "id": 3,
        "title": "Python Fundamentals",
        "author": "Marko V",
        "description": "Core language concepts",
    },
]


@app.get("/books/search/pattern")
async def search_books_pattern(
    starts_with: str | None = None,
    ends_with: str | None = None,
):
    results = books

    if starts_with:
        sw = starts_with.strip().lower()
        results = [b for b in results if b["title"].lower().startswith(sw)]

    if ends_with:
        ew = ends_with.strip().lower()
        results = [b for b in results if b["title"].lower().endswith(ew)]

    return results


@app.get("/books/search/fulltext-lite")
async def search_fulltext_lite(q: str = Query(min_length=2)):
    tokens = [token.lower() for token in q.strip().split() if token.strip()]

    def match(book: dict) -> bool:
        haystack = f"{book['title']} {book['author']} {book['description']}".lower()
        return all(token in haystack for token in tokens)

    return [book for book in books if match(book)]
