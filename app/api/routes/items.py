from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemOut, ItemUpdate

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)) -> list[Item]:
    return db.query(Item).all()


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)
) -> Item:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.name = payload.name
        item.description = payload.description
        db.commit()
        db.refresh(item)
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return None
    raise HTTPException(status_code=404, detail="Item not found")
