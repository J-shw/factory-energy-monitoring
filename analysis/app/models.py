from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os, logging, datetime

logging.basicConfig(level=logging.INFO)

database_url_env = os.environ.get("DATABASE_URL")

DATABASE_URL = f"postgresql://{database_url_env}/factory_energy"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    deviceId = Column(String)
    timestamp = Column(DateTime)
    amps = Column(Integer)
    volts = Column(Integer)

Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    timestamp: datetime.datetime
    amps: int
    volts: int
    deviceId: str

class ItemCreate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int