from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main as main_app
from app import models as _models  # noqa: F401
from app.db.base import Base
from app.db.database import get_db


@pytest.fixture(autouse=True)
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main_app.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main_app.app) as test_client:
        yield test_client

    main_app.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_item(client: TestClient) -> None:
    response = client.post("/items/", json={"name": "Book"})
    assert response.status_code == 201
    assert response.json()["name"] == "Book"


def test_list_items(client: TestClient) -> None:
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_item(client: TestClient) -> None:
    created = client.post("/items/", json={"name": "Book"}).json()
    response = client.put(
        f"/items/{created['id']}",
        json={"name": "Updated", "description": "New"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


def test_delete_item(client: TestClient) -> None:
    created = client.post("/items/", json={"name": "Book"}).json()
    response = client.delete(f"/items/{created['id']}")
    assert response.status_code == 204
    follow_up = client.get(f"/items/{created['id']}")
    assert follow_up.status_code == 404


def test_get_item_not_found(client: TestClient) -> None:
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_not_found(client: TestClient) -> None:
    response = client.put("/items/999", json={"name": "Missing"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item_not_found(client: TestClient) -> None:
    response = client.delete("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
