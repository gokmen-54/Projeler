from datetime import datetime, timedelta
from statistics import mean
from typing import Iterable

from sqlmodel import Session, select

from ..models import Measurement


def naive_forecast(session: Session, device_id: str, horizon_minutes: int = 60) -> float:
    since = datetime.utcnow() - timedelta(hours=24)
    rows: Iterable[Measurement] = session.exec(
        select(Measurement).where(
            Measurement.device_id == device_id, Measurement.created_at >= since
        )
    )
    powers = [m.active_power for m in rows]
    if not powers:
        return 0.0
    return float(mean(powers))
