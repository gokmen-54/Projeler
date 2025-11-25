from sqlmodel import Session

from ..models import Alert, Measurement


THRESHOLDS = {
    "voltage_max": 250,
    "current_max": 50,
}


def evaluate_thresholds(session: Session, measurement: Measurement) -> None:
    alerts = []
    if measurement.voltage > THRESHOLDS["voltage_max"]:
        alerts.append(
            Alert(
                device_id=measurement.device_id,
                level="warning",
                message=f"Voltage high ({measurement.voltage}V)",
            )
        )
    if measurement.current > THRESHOLDS["current_max"]:
        alerts.append(
            Alert(
                device_id=measurement.device_id,
                level="warning",
                message=f"Current high ({measurement.current}A)",
            )
        )

    for alert in alerts:
        session.add(alert)
    if alerts:
        session.commit()
