from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Event, SessionLocal, EventCreate, EventOut
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

@app.get("/events/{item_id}", response_model=EventOut)
def read_event(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Event).filter(Event.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_item

@app.get("/events/", response_model=list[EventOut])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Event).offset(skip).limit(limit).all()
    return items

@app.get("/")
async def root():
    return {"message": "Analysis - System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)