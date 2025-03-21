from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Event, SessionLocal, EventCreate, EventOut, Limit, LimitOut, LimitCreate
import uvicorn

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/", response_model=EventOut)
def create_event(item: EventCreate, db: Session = Depends(get_db)):
    db_item = Event(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/events/{event_id}", response_model=EventOut)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Event).filter(Event.id == event_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_item

@app.get("/events/", response_model=list[EventOut])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Event).offset(skip).limit(limit).all()
    return items

@app.post("/limits/", response_model=LimitOut)
def create_limit(item: LimitCreate, db: Session = Depends(get_db)):
    db_item = Limit(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/limits/{limit_id}", response_model=LimitOut)
def read_limit(limit_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Limit).filter(Limit.id == limit_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Limit not found")
    return db_item

@app.get("/limits/", response_model=list[LimitOut])
def read_limits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Limit).offset(skip).limit(limit).all()
    return items

@app.get("/")
async def root():
    return {"message": "Analysis - System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)