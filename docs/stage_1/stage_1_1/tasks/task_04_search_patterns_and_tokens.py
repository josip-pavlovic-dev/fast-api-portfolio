from fastapi import FastAPI, Query

app = FastAPI()

books = [
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
    # TODO 1: Implementiraj startswith i endswith pretragu po title.
    # TODO 2: Pretraga treba da bude case-insensitive.
    pass


@app.get("/books/search/fulltext-lite")
async def search_fulltext_lite(q: str = Query(min_length=2)):
    # TODO 3: podeli q na reci (tokens), normalizuj lower().
    # TODO 4: Vrati knjige gde SVAKA rec iz q postoji u title+author+description.
    pass
