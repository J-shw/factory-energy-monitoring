from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Event, SessionLocal, EventCreate, EventOut, EnergyDataInput
import modules.process as process
from datetime import datetime, timezone
import uvicorn, logging, json, requests

app = FastAPI()

logging.basicConfig(level=logging.INFO)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create/event/", response_model=EventOut)
def create_event(item: EventCreate, db: Session = Depends(get_db)):
    db_item = Event(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/get/event/{event_id}", response_model=EventOut)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Event).filter(Event.id == event_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_item

@app.get("/get/event/", response_model=list[EventOut])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Event).offset(skip).limit(limit).all()
    return items

@app.post("/process/")
def process_data(energy_data: EnergyDataInput, db: Session = Depends(get_db)):
    try:
        url = "http://device-management-system:9002/get/entity/" + energy_data.deviceId
        response = requests.get(url)
        response.raise_for_status()

        entity = response.json()

        highLowVoltage, overCurrent = process.energy_data(energy_data.volts, energy_data.amps, entity)
        db_event = Event(
            logId=energy_data.id,
            entityId=entity.entityId,
            overCurrent=overCurrent,
            highLowVoltage=highLowVoltage,
            timestamp=datetime.now(timezone.utc)
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        logging.error(f"Failed to process data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Analysis - System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)