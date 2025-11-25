from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Measurement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str
    phase: str
    voltage: float
    current: float
    active_power: float
    energy_kwh: float
    power_factor: float
    frequency: float
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str
    level: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
