from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, logging

logging.basicConfig(level=logging.INFO)

database_url_env = os.environ.get("DATABASE_URL")

DATABASE_URL = f"postgresql://{database_url_env}/devices"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    deviceId = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    deviceName = Column(Integer)
    description = Column(Integer)

Base.metadata.create_all(bind=engine)