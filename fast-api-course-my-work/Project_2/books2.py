from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI(
    title="FastAPI Books API",
    description="API za upravljanje knjigama koristeći FastAPI.",
    version="2.0",
)

# Book predstavlja model(Python objekat klase Book) koji sadrži informacije o knjizi
# uključujući id, naslov, autora, opis i ocenu.
# BOOKS je lista instanci klase Book koja sadrži nekoliko primera knjiga sa različitim
# vrednostima atributa.


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int | None = None

    def __init__(
        self, id, title, author, description, rating, published_date=None
    ) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# Body() se koristi za definisanje tela zahteva u FastAPI-ju, omogućavajući slanje podataka u JSON formatu prilikom kreiranja ili ažuriranja resursa. Problem koji se javlja kod korišćenja Body() je što nema automatsku validaciju podataka, pa je potrebno ručno proveravati ispravnost unetih vrednosti. Zbog toga se uvodi Pydantic, koji omogućava definisanje modela sa automatskom validacijom podataka.


class BookRequest(BaseModel):
    id: int | None = Field(
        description="Polje ID nije potrebno prilikom kreiranja knjige", default=None
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int | None = Field(gt=1999, lt=2100, default=None)

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "title": "Nova Knjiga",
                "author": "Autor",
                "description": "Opis",
                "rating": 1,
                "published_date": None,
            }
        },
    }


BOOKS: list[Book] = [
    Book(
        id=1,
        title="FastAPI for Beginners",
        author="John Doe",
        description="A comprehensive guide to FastAPI.",
        rating=5,
        published_date=2024,
    ),
    Book(
        id=2,
        title="Advanced FastAPI",
        author="Jane Smith",
        description="Deep dive into FastAPI features.",
        rating=4,
        published_date=2023,
    ),
    Book(
        id=3,
        title="Mastering FastAPI",
        author="Alice Johnson",
        description="Expert techniques for building APIs with FastAPI.",
        rating=5,
        published_date=2027,
    ),
    Book(
        id=4,
        title="FastAPI in Action",
        author="Bob Brown",
        description="Practical guide to building APIs with FastAPI.",
        rating=4,
        published_date=2014,
    ),
    Book(
        id=5,
        title="The FastAPI Cookbook",
        author="Charlie Davis",
        description="Recipes for common FastAPI tasks.",
        rating=5,
        published_date=2022,
    ),
    Book(
        id=6,
        title="FastAPI Patterns",
        author="Diana Evans",
        description="Design patterns and best practices for FastAPI.",
        rating=4,
        published_date=2022,
    ),
]


# NAPOMENA
# Svi endpoint-i vraćaju odgovarajuće HTTP status kodove koristeći status modul iz FastAPI-ja.
# Koristi se Path za validaciju parametara puta, Query za validaciju parametara upita, i Body za validaciju tela zahteva.
# Pydantic modeli (BookRequest) omogućavaju automatsku validaciju podataka i generisanje JSON šema za dokumentaciju.
# Funkcija automatski_id dodeljuje jedinstveni ID novokreiranoj knjizi, osiguravajući da svaki unos u listi BOOKS ima jedinstven identifikator.
# Ako lista BOOKS još uvek nema nijednu knjigu, ID počinje od 1.
# Status HTTP 200 OK se ne mora eksplicitno navoditi jer je podrazumevani za GET zahteve ali ga navodimo radi jasnoće.


@app.get("/")
async def root() -> dict[str, str]:
    """Funkcija koja vraća osnovne informacije o API-ju, uključujući opis i svrhu API-ja."""
    return {"Opis": "API za upravljanje knjigama koristeći FastAPI."}


@app.get("/books", status_code=status.HTTP_200_OK)
async def sve_knjige():
    """Funkcija koja vraća (prikazuje) sve knjige.

    Returns:
        list[Book]: Lista svih knjiga.
    """
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def pronadji_knjigu_po_id(
    book_id: int = Path(gt=0, description="ID knjige mora biti veći od 0.")
):
    """Funkcija koja pronalazi knjigu po njenom ID-u.

    Args:
        book_id (int): ID knjige koju želimo da pronađemo.

    Returns:
        Book: Objekat knjige sa odgovarajućim ID-em.

    Raises:
        HTTPException: Ako knjiga sa datim ID-em ne postoji.
    """

    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def pronadji_knjigu_po_rejtingu(
    book_rating: int = Query(
        ge=1,
        le=5,
        description="Rejting knjige mora biti između 1 i 5.",
    ),
):
    books_by_rating = [book for book in BOOKS if book.rating == book_rating]
    return books_by_rating


@app.get("/books/bypublished/", status_code=status.HTTP_200_OK)
async def pretraga_knjiga_po_godini_izdavanja(
    published_date: int | None = Query(
        default=None,
        gt=1999,
        lt=2100,
        description="Ako je navedena, godina mora biti između 2000. i 2099.",
    )
):
    """Funkcija koja pretražuje knjige po godini izdavanja.

    Args:
        published_date (int | None): Godina izdavanja knjige koju želimo da pronađemo. Ako nije navedena, vraćaju se sve knjige.

    Returns:
        list[Book]: Lista knjiga koje su objavljene u datoj godini.
    """
    if (
        published_date is None
    ):  # Ako godina izdavanja nije navedena, vraćaju se sve knjige.
        return BOOKS

    published_books = [book for book in BOOKS if book.published_date == published_date]

    return published_books


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def kreiraj_novu_knjigu(book_request: BookRequest):
    """Funkcija koja kreira novu knjigu i vraća njen ID.

    Args:
        book_request (BookRequest): Podaci o knjizi koju želimo da kreiramo.

    Returns:
        dict[str, int]: Rečnik sa ID-em novokreirane knjige.
    """
    new_book = Book(**book_request.model_dump())
    new_book = automatski_id(new_book)
    BOOKS.append(new_book)

    return {"Kreirana knjiga": {"id": new_book.id, "title": new_book.title}}


def automatski_id(book: Book) -> Book:
    """Funkcija koja dodeljuje automatski ID knjizi.

    Args:
        book (Book): Knjiga kojoj želimo dodeliti ID.

    Returns:
        Book: Knjiga sa dodeljenim ID-em.
    """

    # Ternarni izraz za dodeljivanje ID-a: ako je lista prazna, ID je 1, inače je ID poslednje knjige + 1.

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

    # if len(BOOKS) == 0:
    #     book.id = 1
    # else:
    #     book.id = BOOKS[-1].id + 1

    return book


@app.put("/books/update_book", status_code=status.HTTP_200_OK)
async def azuriraj_knjigu(update_book: BookRequest):
    """Funkcija koja ažurira postojeću knjigu na osnovu njenog ID-a.

    Args:
        update_book (BookRequest): Podaci o knjizi koju želimo da ažuriramo.

    Returns:
        dict[str, Any]: Rečnik sa porukom o uspehu i ažuriranim podacima knjige.
    """
    if update_book.id is None:
        raise HTTPException(
            status_code=400, detail="ID knjige je obavezan za ažuriranje."
        )
    for index, book in enumerate(BOOKS):
        if book.id == update_book.id:
            updated_book = Book(**update_book.model_dump())
            updated_book.id = BOOKS[index].id
            BOOKS[index] = updated_book

            return {"message": "Knjiga je ažurirana.", "book": BOOKS[index]}

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def ukloni_knjigu_iz_liste(
    book_id: int = Path(gt=0, description="ID knjige mora biti veći od 0.")
) -> None:
    for index, book in enumerate(BOOKS):
        if book.id == book_id:
            BOOKS.pop(index)
            return  # HTTP 204 No Content ne vraća telo odgovora

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")


def run_assert_tests() -> None:
    from fastapi.testclient import TestClient

    original_books = BOOKS.copy()
    new_book_request = {
        "title": "Test Book Seven",
        "author": "Test Author",
        "description": "A book created by an assert test.",
        "rating": 5,
        "published_date": 2025,
    }
    updated_book_request = {
        "id": 1,
        "title": "Updated Test Book",
        "author": "Updated Author",
        "description": "An updated book for an assert test.",
        "rating": 4,
        "published_date": 2026,
    }

    try:
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {
                "Opis": "API za upravljanje knjigama koristeći FastAPI."
            }

            response = client.get("/books")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()) == len(original_books)
            assert response.json()[0]["id"] == 1

            response = client.get("/books/1")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["title"] == "FastAPI for Beginners"
            assert (
                client.get("/books/0").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert (
                client.get("/books/not-an-id").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert client.get("/books/9999").status_code == status.HTTP_404_NOT_FOUND

            response = client.get("/books/?book_rating=5")
            assert response.status_code == status.HTTP_200_OK
            assert [book["id"] for book in response.json()] == [1, 3, 5]
            assert (
                client.get("/books/?book_rating=0").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert (
                client.get("/books/?book_rating=6").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert (
                client.get("/books/").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )

            response = client.get("/books/bypublished/")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()) == len(original_books)

            response = client.get("/books/bypublished/?published_date=2022")
            assert response.status_code == status.HTTP_200_OK
            assert [book["id"] for book in response.json()] == [5, 6]
            response = client.get("/books/bypublished/?published_date=2000")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
            assert (
                client.get("/books/bypublished/?published_date=1999").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert (
                client.get("/books/bypublished/?published_date=2100").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )

            response = client.post("/create-book", json=new_book_request)
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json() == {
                "Kreirana knjiga": {"id": 7, "title": "Test Book Seven"}
            }
            assert len(BOOKS) == len(original_books) + 1
            assert client.get("/books/7").json()["published_date"] == 2025

            invalid_book_request = {**new_book_request, "rating": 6}
            response = client.post("/create-book", json=invalid_book_request)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert len(BOOKS) == len(original_books) + 1

            response = client.put("/books/update_book", json=updated_book_request)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["message"] == "Knjiga je ažurirana."
            assert response.json()["book"]["id"] == 1
            assert response.json()["book"]["title"] == "Updated Test Book"
            assert BOOKS[0].id == 1
            assert BOOKS[0].title == "Updated Test Book"

            missing_id_request = {
                key: value for key, value in updated_book_request.items() if key != "id"
            }
            assert (
                client.put("/books/update_book", json=missing_id_request).status_code
                == status.HTTP_400_BAD_REQUEST
            )

            unknown_id_request = {**updated_book_request, "id": 9999}
            assert (
                client.put("/books/update_book", json=unknown_id_request).status_code
                == status.HTTP_404_NOT_FOUND
            )

            invalid_update_request = {**updated_book_request, "rating": 6}
            assert (
                client.put(
                    "/books/update_book", json=invalid_update_request
                ).status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )

            response = client.delete("/books/6")
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.content == b""
            assert client.get("/books/6").status_code == status.HTTP_404_NOT_FOUND
            assert (
                client.delete("/books/0").status_code
                == status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            assert client.delete("/books/9999").status_code == status.HTTP_404_NOT_FOUND

            BOOKS.clear()
            response = client.get("/books")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

            response = client.get("/books/?book_rating=5")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

            response = client.get("/books/bypublished/")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

            response = client.post("/create-book", json=new_book_request)
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["Kreirana knjiga"]["id"] == 1
    finally:
        BOOKS[:] = original_books


if __name__ == "__main__":
    run_assert_tests()
    print("Svi books22 assert testovi su prosli.")
