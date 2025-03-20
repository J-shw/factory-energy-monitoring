from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    deviceId = Column(String)
    timestamp = Column(DateTime)
    amps = Column(Integer)
    volts = Column(Integer)

Base.metadata.create_all(bind=engine)

class LogBase(BaseModel):
    deviceId: str
    timestamp: datetime.datetime
    amps: int
    volts: int

class LogCreate(LogBase):
    pass

class LogOut(LogBase):
    id: int