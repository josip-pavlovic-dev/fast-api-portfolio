from fastapi import FastAPI, HTTPException, Path

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
async def get_book_by_id(book_id: int = Path(ge=1)):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Knjiga nije pronadjena")
