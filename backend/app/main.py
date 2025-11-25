import logging
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from .ai.anomaly import SimpleAnomalyDetector
from .ai.forecast import naive_forecast
from .db import get_session, init_db
from .models import Measurement
from .schemas import (
    AlertOut,
    AnomalyResponse,
    ForecastResponse,
    MeasurementIn,
    MeasurementOut,
)
from .services.aggregation import aggregate_energy
from .services.alerts import evaluate_thresholds

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Energy AI Backend", version="0.1.0")

detector = SimpleAnomalyDetector()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow()}


@app.post("/measurements", response_model=MeasurementOut)
def create_measurement(
    payload: MeasurementIn, session: Annotated[Session, Depends(get_session)]
) -> MeasurementOut:
    measurement = Measurement(
        device_id=payload.device_id,
        phase=payload.phase,
        voltage=payload.voltage,
        current=payload.current,
        active_power=payload.active_power,
        energy_kwh=payload.energy_kwh,
        power_factor=payload.power_factor,
        frequency=payload.frequency,
        created_at=payload.created_at,
    )
    session.add(measurement)
    session.commit()
    session.refresh(measurement)

    evaluate_thresholds(session, measurement)

    # Update anomaly model using recent active power values
    recent = session.exec(
        select(Measurement.active_power)
        .order_by(Measurement.created_at.desc())
        .limit(200)
    ).all()
    if len(recent) >= 10:
        detector.fit([float(v) for v in recent])

    return MeasurementOut.model_validate(measurement)


@app.get("/measurements", response_model=list[MeasurementOut])
def list_measurements(session: Annotated[Session, Depends(get_session)]) -> list[MeasurementOut]:
    rows = session.exec(
        select(Measurement).order_by(Measurement.created_at.desc()).limit(50)
    ).all()
    return [MeasurementOut.model_validate(row) for row in rows]


@app.get("/aggregates")
def aggregates(session: Annotated[Session, Depends(get_session)]) -> dict:
    return aggregate_energy(session)


@app.get("/ai/forecast", response_model=ForecastResponse)
def forecast(
    device_id: str, session: Annotated[Session, Depends(get_session)], horizon_minutes: int = 60
) -> ForecastResponse:
    predicted_kw = naive_forecast(session, device_id, horizon_minutes)
    return ForecastResponse(horizon_minutes=horizon_minutes, predicted_kw=predicted_kw)


@app.get("/ai/anomaly", response_model=AnomalyResponse)
def anomaly(score_value: float, session: Annotated[Session, Depends(get_session)]) -> AnomalyResponse:
    recent = session.exec(
        select(Measurement.active_power)
        .order_by(Measurement.created_at.desc())
        .limit(200)
    ).all()
    if len(recent) >= 10:
        detector.fit([float(v) for v in recent])
    score, is_anomaly = detector.score(score_value)
    return AnomalyResponse(score=score, is_anomaly=is_anomaly)


@app.get("/alerts", response_model=list[AlertOut])
def alerts(session: Annotated[Session, Depends(get_session)]) -> list[AlertOut]:
    # simple joinless retrieval to keep the demo light
    from .models import Alert

    rows = session.exec(select(Alert).order_by(Alert.created_at.desc()).limit(50)).all()
    return [AlertOut(**row.dict()) for row in rows]
