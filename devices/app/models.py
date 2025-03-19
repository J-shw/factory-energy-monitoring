from sqlalchemy import create_engine, Column, Integer, Boolean, String, Float, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os, logging, uuid

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
    description = Column(String)
    type = Column(String)
    voltage = Column(Float, nullable=True)
    current_rating_amps = Column(Float, nullable=True)
    isActive = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)