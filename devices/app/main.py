from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Device, SessionLocal
from typing import Optional
from uuid import UUID
import datetime, uvicorn

app = FastAPI()

class DeviceCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DeviceOut(DeviceCreate):
    id: UUID
    dateCreated: datetime.datetime

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/device/", response_model=DeviceOut)
def create_item(item: DeviceCreate, db: Session = Depends(get_db)):
    db_item = Device(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/devices/{item_id}", response_model=DeviceOut)
def read_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(Device).filter(Device.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/devices/", response_model=list[DeviceOut])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Device).offset(skip).limit(limit).all()
    return items

@app.get("/")
async def root():
    return {"message": "Devices - System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)