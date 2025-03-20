from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
import os, logging, datetime

logging.basicConfig(level=logging.INFO)

database_url_env = os.environ.get("DATABASE_URL")

DATABASE_URL = f"postgresql://{database_url_env}/factory_energy"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Event(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    logId = Column(Integer) # Needs to correspond to the log entry that was processed
    deviceId = Column(String)
    timestamp = Column(DateTime)
    overCurrent = Column(Boolean, default=False)
    highLowVoltage = Column(Boolean, default=False)
    powerOutage = Column(Boolean, default=False)
    

Base.metadata.create_all(bind=engine)

class EventCreate(BaseModel):
    logId: int
    deviceId: str
    timestamp: datetime.datetime
    overCurrent: Optional[bool] = False
    highLowVoltage: Optional[bool] = False
    powerOutage: Optional[bool] = False

class EventOut(EventCreate):
    id: int

    class Config:
        orm_mode = True