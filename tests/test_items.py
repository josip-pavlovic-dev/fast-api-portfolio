import pytest
from fastapi.testclient import TestClient

from app.api.routes import items
from app.main import app


@pytest.fixture(autouse=True)
def clear_items() -> None:
    items._items.clear()


def test_create_item() -> None:
    client = TestClient(app)
    response = client.post("/items/", json={"name": "Book"})
    assert response.status_code == 201
    assert response.json()["name"] == "Book"


def test_list_items() -> None:
    client = TestClient(app)
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_item() -> None:
    client = TestClient(app)
    created = client.post("/items/", json={"name": "Book"}).json()
    response = client.put(
        f"/items/{created['id']}",
        json={"name": "Updated", "description": "New"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


def test_delete_item() -> None:
    client = TestClient(app)
    created = client.post("/items/", json={"name": "Book"}).json()
    response = client.delete(f"/items/{created['id']}")
    assert response.status_code == 204
    follow_up = client.get(f"/items/{created['id']}")
    assert follow_up.status_code == 404


def test_get_item_not_found() -> None:
    client = TestClient(app)
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_not_found() -> None:
    client = TestClient(app)
    response = client.put("/items/999", json={"name": "Missing"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item_not_found() -> None:
    client = TestClient(app)
    response = client.delete("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
