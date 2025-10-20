from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Device schemas
class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., regex="^(hikvision|dahua)$")
    ip: str = Field(..., regex="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    port: int = Field(default=80, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=255)
    channels: int = Field(default=16, ge=1, le=64)
    meta: Optional[Dict[str, Any]] = Field(default={})

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, regex="^(hikvision|dahua)$")
    ip: Optional[str] = Field(None, regex="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1, max_length=255)
    channels: Optional[int] = Field(None, ge=1, le=64)
    is_active: Optional[bool] = None
    meta: Optional[Dict[str, Any]] = None

class Device(DeviceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Stream schemas
class StreamCreate(BaseModel):
    device_id: int
    channel: int = Field(default=1, ge=1, le=64)
    sub_stream: int = Field(default=0, ge=0, le=1)
    rtsp_url: Optional[str] = None
    hls_url: Optional[str] = None

class Stream(BaseModel):
    id: int
    stream_id: str
    device_id: int
    channel: int
    sub_stream: int
    rtsp_url: Optional[str]
    hls_url: Optional[str]
    is_active: bool
    started_at: datetime
    stopped_at: Optional[datetime]

    class Config:
        from_attributes = True

# Recording schemas
class RecordingCreate(BaseModel):
    device_id: int
    channel: int
    start_time: datetime
    end_time: datetime
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    recording_type: str = Field(default="normal", regex="^(normal|alarm|motion)$")
    meta: Optional[Dict[str, Any]] = Field(default={})

class Recording(BaseModel):
    id: int
    device_id: int
    channel: int
    start_time: datetime
    end_time: datetime
    file_path: Optional[str]
    file_size: Optional[int]
    recording_type: str
    meta: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str
