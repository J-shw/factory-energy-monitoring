from sqlalchemy import create_engine, Column, PickleType, Boolean, String, Float, DateTime, UUID, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
import os, logging, uuid, datetime

logging.basicConfig(level=logging.INFO)

database_url_env = os.environ.get("DATABASE_URL")

DATABASE_URL = f"postgresql://{database_url_env}/devices"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Entity(Base):
    __tablename__ = "Entity"

    id = Column(Integer, primary_key=True, index=True)
    dateCreated = Column(DateTime(timezone=True), default=func.now())
    voltageIotId = Column(UUID(as_uuid=True), ForeignKey("Iot.id"))
    currentIotId = Column(UUID(as_uuid=True), ForeignKey("Iot.id"))
    name = Column(String)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    voltageRating = Column(Float, nullable=True)
    currentRating = Column(Float, nullable=True)
    highLowVoltage = Column(Boolean, default=False)
    overCurrent = Column(Boolean, default=False)
    powerOutage = Column(Boolean, default=False)
    overCurrentValue = Column(Float, nullable=True)
    lowVoltageValue = Column(Float, nullable=True)
    highVoltageValue = Column(Float, nullable=True)

    isActive = Column(Boolean, default=True)

class Iot(Base):
    __tablename__ = "Iot"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    dateCreated = Column(DateTime(timezone=True), default=func.now())
    name = Column(String)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    protocol = Column(String) # opc or mqtt
    voltage = Column(Boolean)
    current = Column(Boolean)
    
    isActive = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class EntityCreate(BaseModel):
    voltageIotId: uuid.UUID
    currentIotId: uuid.UUID
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    voltageRating: Optional[float] = None
    currentRating: Optional[float] = None
    highLowVoltage: Optional[bool] = False
    overCurrent: Optional[bool] = False
    powerOutage: Optional[bool] = False
    overCurrentValue: Optional[float] = None
    lowVoltageValue: Optional[float] = None
    highVoltageValue: Optional[float] = None
    

class EntityOut(EntityCreate):
    id: int
    dateCreated: datetime.datetime

    class Config:
        orm_mode = True

class IotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    connectionType: str
    protocol: str
    voltage: bool
    current: bool

class IotOut(IotCreate):
    id: uuid.UUID
    dateCreated: datetime.datetime

    class Config:
        orm_mode = True