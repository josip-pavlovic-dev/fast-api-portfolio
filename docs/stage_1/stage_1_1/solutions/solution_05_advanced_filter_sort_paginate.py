from fastapi import FastAPI, Query

app = FastAPI()

books: list[dict] = [
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
    results = books[:]

    if min_rating is not None:
        results = [book for book in results if book["rating"] >= min_rating]

    if max_rating is not None:
        results = [book for book in results if book["rating"] <= max_rating]

    if published_from is not None:
        results = [book for book in results if book["published_date"] >= published_from]

    if published_to is not None:
        results = [book for book in results if book["published_date"] <= published_to]

    reverse = sort_order == "desc"

    if sort_by == "title":
        results.sort(key=lambda b: b["title"].lower(), reverse=reverse)
    else:
        results.sort(key=lambda b: b[sort_by], reverse=reverse)

    paginated = results[skip : skip + limit]

    return {
        "total": len(results),
        "skip": skip,
        "limit": limit,
        "items": paginated,
    }
