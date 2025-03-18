from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Item, SessionLocal
import datetime, uvicorn

app = FastAPI()

class ItemBase(BaseModel):
    timestamp: datetime.datetime
    amps: int
    volts: int

class ItemCreate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/device/", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/devices/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/devices/", response_model=list[ItemOut])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@app.get("/")
async def root():
    return {"message": "Devices - System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)