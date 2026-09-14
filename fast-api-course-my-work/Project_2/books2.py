from fastapi import Body, FastAPI

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


BOOKS: list[Book] = [
    Book(
        id=1,
        title="FastAPI for Beginners",
        author="John Doe",
        description="A comprehensive guide to FastAPI.",
        rating=5,
    ),
    Book(
        id=2,
        title="Advanced FastAPI",
        author="Jane Smith",
        description="Deep dive into FastAPI features.",
        rating=4,
    ),
    Book(
        id=3,
        title="Mastering FastAPI",
        author="Alice Johnson",
        description="Expert techniques for building APIs with FastAPI.",
        rating=5,
    ),
    Book(
        id=4,
        title="FastAPI in Action",
        author="Bob Brown",
        description="Practical guide to building APIs with FastAPI.",
        rating=4,
    ),
    Book(
        id=5,
        title="The FastAPI Cookbook",
        author="Charlie Davis",
        description="Recipes for common FastAPI tasks.",
        rating=5,
    ),
    Book(
        id=6,
        title="FastAPI Patterns",
        author="Diana Evans",
        description="Design patterns and best practices for FastAPI.",
        rating=4,
    ),
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.post("/books/create-book")
async def create_book(book: Book = Body()):
    BOOKS.append(book)
    return book
