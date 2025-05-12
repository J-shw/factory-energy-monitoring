import logging
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Log, LogOut, SessionLocal

_logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_app():
    app = FastAPI()
    
    @app.get("/logs", response_model=List[LogOut])
    def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        _logger.debug(f"Fetching logs with skip={skip}, limit={limit}")
        logs = db.query(Log).offset(skip).limit(limit).all()
        _logger.debug(f"Found {len(logs)} logs.")
        return logs

    @app.get("/logs/{log_id}", response_model=LogOut)
    def get_log_by_id(log_id: int, db: Session = Depends(get_db)):
        _logger.debug(f"Fetching log with ID={log_id}")
        log_entry = db.query(Log).filter(Log.id == log_id).first()
        if log_entry is None:
            _logger.warning(f"Log with ID={log_id} not found.")
            raise HTTPException(status_code=404, detail="Log not found")
        _logger.debug(f"Found log with ID={log_id}.")
        return log_entry

    return app