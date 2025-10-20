from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# Device CRUD operations
def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()

def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(db: Session, device_id: int, device: schemas.DeviceUpdate):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        update_data = device.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_device, field, value)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device

# Stream CRUD operations
def get_stream(db: Session, stream_id: str):
    return db.query(models.Stream).filter(models.Stream.stream_id == stream_id).first()

def get_active_streams(db: Session):
    return db.query(models.Stream).filter(models.Stream.is_active == True).all()

def create_stream(db: Session, stream: schemas.StreamCreate):
    db_stream = models.Stream(**stream.dict())
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)
    return db_stream

def stop_stream(db: Session, stream_id: str):
    db_stream = db.query(models.Stream).filter(models.Stream.stream_id == stream_id).first()
    if db_stream:
        db_stream.is_active = False
        db_stream.stopped_at = datetime.utcnow()
        db.commit()
        db.refresh(db_stream)
    return db_stream

# Recording CRUD operations
def get_recordings(db: Session, device_id: int, start_time: str, end_time: str, channel: int = 1):
    return db.query(models.Recording).filter(
        models.Recording.device_id == device_id,
        models.Recording.channel == channel,
        models.Recording.start_time >= start_time,
        models.Recording.end_time <= end_time
    ).all()

def create_recording(db: Session, recording: schemas.RecordingCreate):
    db_recording = models.Recording(**recording.dict())
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording
