from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os, logging, datetime

logging.basicConfig(level=logging.INFO)

database_url_env = os.environ.get("DATABASE_URL")

DATABASE_URL = f"postgresql://{database_url_env}/factory_energy_logs"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    iotId = Column(String)
    timestamp = Column(DateTime)
    amps = Column(Float)
    volts = Column(Float)

Base.metadata.create_all(bind=engine)

class LogBase(BaseModel):
    iotId: str
    timestamp: datetime.datetime
    amps: float
    volts: float

class LogCreate(LogBase):
    pass

class LogOut(LogBase):
    id: int