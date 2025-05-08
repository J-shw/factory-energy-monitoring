from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import SessionLocal, Entity, EntityCreate, EntityOut, Iot, IotCreate, IotOut
import uvicorn

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Entity APIs - - -

@app.post("/create/entity/", response_model=EntityOut)
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    db_item = Entity(**entity.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/get/iot/{iot_id}/entity/", response_model=list[EntityOut])
def get_entity_by_iot_id(iot_id: str, db: Session = Depends(get_db)):
    iot_exists = db.query(Iot).filter(Iot.id == iot_id).first()
    if iot_exists is None:
        raise HTTPException(status_code=404, detail="Iot not found")

    entity_items = db.query(Entity).filter(Entity.voltageIotId == iot_id or Entity.currentIotId == iot_id).all()
    if entity_items is None:
        raise HTTPException(status_code=404, detail="Iot not used by entity")
    return entity_items

@app.get("/get/entity/{entity_id}", response_model=EntityOut)
def get_enetity_by_id(entity_id: str, db: Session = Depends(get_db)):
    db_item = db.query(Entity).filter(Entity.id == entity_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_item

@app.get("/get/entity/", response_model=list[EntityOut])
def get_entity(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = db.query(Entity).offset(skip).limit(limit).all()
    return entities

# IoT APIs - - -

@app.post("/create/iot/", response_model=IotOut)
def create_iot(iot: IotCreate, db: Session = Depends(get_db)):
    db_item = Iot(**iot.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/get/iot/{iot_id}", response_model=IotOut)
def get_iot_by_id(iot_id: str, db: Session = Depends(get_db)):
    db_item = db.query(Iot).filter(Iot.id == iot_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Iot not found")
    return db_item

@app.get("/get/iot/", response_model=list[IotOut])
def get_iot(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    iots = db.query(Iot).offset(skip).limit(limit).all()
    return iots

@app.get("/")
async def root():
    return {"message": "Device Managemnt System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)