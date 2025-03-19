from sqlalchemy import create_engine, Column, PickleType, Boolean, String, Float, DateTime, UUID
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

class Device(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    dateCreated = Column(DateTime(timezone=True), default=func.now())
    name = Column(String)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    voltage = Column(Float, nullable=True)
    currentRatingAmps = Column(Float, nullable=True)
    isActive = Column(Boolean, default=True)
    alertsConfiguration = Column(PickleType, nullable=True)
# "alertsConfiguration": {
#         "high_low_voltage": true,
#         "overcurrent": true,
#         "power_outage": true,
#     },
Base.metadata.create_all(bind=engine)

class DeviceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    voltage: Optional[float] = None
    currentRatingAmps: Optional[float] = None
    alertsConfiguration: Optional[dict] = None

class DeviceOut(DeviceCreate):
    id: uuid.UUID
    dateCreated: datetime.datetime

    class Config:
        orm_mode = True