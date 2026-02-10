from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ItemIn(BaseModel):
    name: str
    description: str | None = None


class ItemOut(ItemIn):
    id: int


_items: list[ItemOut] = []


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn) -> ItemOut:
    item = ItemOut(id=len(_items) + 1, **payload.model_dump())
    _items.append(item)
    return item


@router.get("/", response_model=list[ItemOut])
def list_items() -> list[ItemOut]:
    return _items


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int) -> ItemOut:
    for item in _items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemIn) -> ItemOut:
    for index, item in enumerate(_items):
        if item.id == item_id:
            updated = ItemOut(id=item_id, **payload.model_dump())
            _items[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    for index, item in enumerate(_items):
        if item.id == item_id:
            _items.pop(index)
            return None
    raise HTTPException(status_code=404, detail="Item not found")
