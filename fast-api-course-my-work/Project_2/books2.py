from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: str,
        rating: int,
        published_date: int,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: int | None = Field(
        description="The ID of the book is not needed on creation", default=None
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Nova Knjiga",
                "author": "Marko Vidojkovic",
                "description": "Opis knjige",
                "rating": 5,
                "published_date": 2026,
            }
        }
    }


# Poredjenja brojeva:
# lt - less than (manje od)
# gt - greater than (veće od)
# le - less than or equal to (manje ili jednako)
# ge - greater than or equal to (veće ili jednako)

BOOKS: list[Book] = [
    Book(
        id=1,
        title="FastAPI for Beginners",
        author="John Doe",
        description="A comprehensive guide to FastAPI.",
        rating=5,
        published_date=2023,
    ),
    Book(
        id=2,
        title="Advanced FastAPI",
        author="Jane Smith",
        description="Deep dive into FastAPI features.",
        rating=4,
        published_date=2024,
    ),
    Book(
        id=3,
        title="Mastering FastAPI",
        author="Alice Johnson",
        description="Expert techniques for building APIs with FastAPI.",
        rating=5,
        published_date=2025,
    ),
    Book(
        id=4,
        title="FastAPI in Action",
        author="Bob Brown",
        description="Practical guide to building APIs with FastAPI.",
        rating=4,
        published_date=2026,
    ),
    Book(
        id=5,
        title="The FastAPI Cookbook",
        author="Charlie Davis",
        description="Recipes for common FastAPI tasks.",
        rating=5,
        published_date=2027,
    ),
    Book(
        id=6,
        title="FastAPI Patterns",
        author="Diana Evans",
        description="Design patterns and best practices for FastAPI.",
        rating=4,
        published_date=2028,
    ),
]


# Čitanje svih knjiga:
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


# Čitanje pojedinačne knjige po ID-u:
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

# Čitanje knjige po rejtingu:
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=0, le=5)):
    if not 1 <= book_rating <= 5:
        return {"error": "Rating must be between 1 and 5"}
    # Ako je rejting validan, nastavljamo sa filtriranjem knjiga po rejtingu.
    books_by_rating = [book for book in BOOKS if book.rating == book_rating]

    return books_by_rating

    # books_to_return = []
    # for book in BOOKS:
    #     if book.rating == book_rating:
    #         books_to_return.append(book)
    # return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_publish_date(publish_date: int = Query(gt=1999, lt=2100)):
    books_to_return = [book for book in BOOKS if book.published_date == publish_date]

    # books_to_return = []
    # for book in BOOKS:
    #     if book.published_date == publish_date:
    #         books_to_return.append(book)

    return books_to_return


# Kreiranje nove knjige:
@app.post("/create-book/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(
        **book_request.model_dump()
    )  # konvertuje zahtev u objekat klase Book
    BOOKS.append(find_book_id(new_book))  # type: ignore
    return status.HTTP_201_CREATED


# Funkcija koja omogućava da id knjige ide redom kako ih registrujemo u listi BOOKS
def find_book_id(book: Book):

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    return book


# Deo po deo `new_book= Book(**book_request.model_dump())`:
# 1. `book_request.model_dump()` konvertuje Pydantic model u rečnik.
# 2. `**book_request.model_dump()` raspakuje rečnik u ključne (keyword arguments naprimer `id=1, title="FastAPI for Beginners", ...`) argumente za konstruktor klase Book.
# 3. `Book(**book_request.model_dump())` kreira novi objekat klase Book sa podacima iz zahteva.

# Šta tačno radi funkcija `model_dump()`:
# `model_dump()` je metoda Pydantic modela koja vraća podatke modela kao rečnik.
# Ovo omogućava jednostavno kreiranje novih `objekata` koristeći te podatke.


@app.put("/books/update_book/", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book  # type: ignore
            book_changed = True
            return BOOKS[i]
    if not book_changed:
        raise HTTPException(status_code=404, detail="Knjiga nije pronađena")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_deleted = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break
    if not book_deleted:
        raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
