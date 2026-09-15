from fastapi import FastAPI

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Python Basics",
        "author": "Marko",
        "description": "Uvod u Python",
        "rating": 5,
        "published_date": 2024,
    },
    {
        "id": 2,
        "title": "FastAPI Intro",
        "author": "Ana",
        "description": "Uvod u FastAPI",
        "rating": 4,
        "published_date": 2025,
    },
]


@app.get("/books/{book_id}")
async def get_book_by_id(
    # TODO 1: Dodaj Path validaciju: ge=1
    book_id: int,
):
    # TODO 2: Vrati knjigu ako postoji.
    # TODO 3: Ako ne postoji, podigni HTTPException 404 sa porukom "Knjiga nije pronadjena".
    pass
