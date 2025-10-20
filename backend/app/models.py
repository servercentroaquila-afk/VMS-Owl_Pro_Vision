from sqlalchemy import Column, Integer, String, Boolean, JSON, TIMESTAMP, Text
from .database import Base
import datetime

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(50), nullable=False)  # 'hikvision' | 'dahua'
    ip = Column(String(45), nullable=False)  # IPv4/IPv6
    port = Column(Integer, default=80)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)  # en prod: cifrar/usar vault
    channels = Column(Integer, default=16)
    is_active = Column(Boolean, default=True)
    meta = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Stream(Base):
    __tablename__ = "streams"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String(255), unique=True, nullable=False)
    device_id = Column(Integer, nullable=False)
    channel = Column(Integer, default=1)
    sub_stream = Column(Integer, default=0)
    rtsp_url = Column(Text)
    hls_url = Column(Text)
    is_active = Column(Boolean, default=True)
    started_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    stopped_at = Column(TIMESTAMP)

class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, nullable=False)
    channel = Column(Integer, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    file_path = Column(Text)
    file_size = Column(Integer)
    recording_type = Column(String(50), default="normal")  # normal, alarm, motion
    meta = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
