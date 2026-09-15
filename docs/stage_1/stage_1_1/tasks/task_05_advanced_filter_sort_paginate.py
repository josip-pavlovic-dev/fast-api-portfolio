from fastapi import FastAPI, Query

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "FastAPI in Action",
        "author": "Bob",
        "description": "Practical API building",
        "rating": 5,
        "published_date": 2026,
    },
    {
        "id": 2,
        "title": "FastAPI for Beginners",
        "author": "John",
        "description": "Beginner roadmap",
        "rating": 4,
        "published_date": 2024,
    },
    {
        "id": 3,
        "title": "Mastering FastAPI",
        "author": "Alice",
        "description": "Advanced techniques",
        "rating": 5,
        "published_date": 2025,
    },
    {
        "id": 4,
        "title": "Python API Design",
        "author": "Ana",
        "description": "Design patterns",
        "rating": 3,
        "published_date": 2023,
    },
]


@app.get("/books/advanced")
async def advanced_books(
    min_rating: int | None = Query(default=None, ge=1, le=5),
    max_rating: int | None = Query(default=None, ge=1, le=5),
    published_from: int | None = Query(default=None, ge=2000, le=2100),
    published_to: int | None = Query(default=None, ge=2000, le=2100),
    sort_by: str = Query(default="id", pattern="^(id|title|rating|published_date)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    # TODO 1: Primeni sve filtere ako su zadati.
    # TODO 2: Dodaj sortiranje po sort_by i sort_order.
    # TODO 3: Primeni paginaciju sa skip i limit.
    # TODO 4: Vrati dict: total, skip, limit, items.
    pass
