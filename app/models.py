from pydantic import BaseModel, EmailStr
from typing import List, Optional

class SensorData(BaseModel):
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

class User(BaseModel):
    username: str
    hashed_password: str
    device_id: Optional[str]
    name: str
    email: EmailStr
    number: str
    is_active: bool = True
    is_superuser: bool
