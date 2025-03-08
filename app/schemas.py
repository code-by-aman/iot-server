from pydantic import BaseModel, EmailStr
from typing import Optional

class SensorDataRequest(BaseModel):
    device_id: str
    ph: float
    ph_limit: float
    tds: float
    tds_limit: float
    orp: float
    orp_limit: float
    ph_dose_type: float
    time_based_dose_start_seconds: float
    time_based_dose_stop_seconds: float
    timestamp: Optional[str]

class UserRequest(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    number: Optional[str] = None

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    number: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    device_id: Optional[str] = None
    is_active: bool
    is_superuser: bool
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    number: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LoginData(BaseModel):
    username: str
    password: str

class WaterQualityData(BaseModel):
    pH: float
    TDS: float
    ORP: float