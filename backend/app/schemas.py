from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeasurementBase(BaseModel):
    device_id: str
    phase: str
    voltage: float
    current: float
    active_power: float
    energy_kwh: float
    power_factor: float
    frequency: float
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="timestamp")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class MeasurementIn(MeasurementBase):
    pass


class MeasurementOut(MeasurementBase):
    id: int


class AlertOut(BaseModel):
    id: int
    device_id: str
    level: str
    message: str
    created_at: datetime


class ForecastResponse(BaseModel):
    horizon_minutes: int
    predicted_kw: float


class AnomalyResponse(BaseModel):
    score: float
    is_anomaly: bool
