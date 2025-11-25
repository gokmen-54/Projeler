from datetime import datetime, timedelta

from sqlmodel import Session, select

from ..models import Measurement


def aggregate_energy(session: Session, window_minutes: int = 15) -> dict:
    since = datetime.utcnow() - timedelta(minutes=window_minutes)
    statement = select(Measurement).where(Measurement.created_at >= since)
    rows = session.exec(statement).all()

    count = len(rows)
    total_kwh = sum(m.energy_kwh for m in rows)
    average_pf = sum(m.power_factor for m in rows) / count if count else 0.0

    return {
        "since": since,
        "total_kwh": total_kwh,
        "average_power_factor": average_pf,
        "count": count,
    }
