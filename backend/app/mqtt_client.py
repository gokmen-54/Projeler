import json
import logging
from typing import Callable

import paho.mqtt.client as mqtt
from sqlmodel import Session

from .models import Measurement

logger = logging.getLogger(__name__)


class MQTTIngestor:
    def __init__(
        self,
        broker_url: str,
        broker_port: int,
        topic: str,
        session_factory: Callable[[], Session],
        username: str | None = None,
        password: str | None = None,
        tls: bool = False,
    ) -> None:
        self.client = mqtt.Client()
        if username:
            self.client.username_pw_set(username=username, password=password)
        if tls:
            self.client.tls_set()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.broker_url = broker_url
        self.broker_port = broker_port
        self.topic = topic
        self.session_factory = session_factory

    def start(self) -> None:
        logger.info("Connecting to MQTT broker %s:%s", self.broker_url, self.broker_port)
        self.client.connect(self.broker_url, self.broker_port, 60)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    # MQTT callbacks
    def on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:  # type: ignore[override]
        if rc == 0:
            logger.info("MQTT connected, subscribing to %s", self.topic)
            client.subscribe(self.topic)
        else:
            logger.error("MQTT connection failed with code %s", rc)

    def on_disconnect(self, client: mqtt.Client, userdata, rc) -> None:  # type: ignore[override]
        logger.warning("MQTT disconnected with code %s", rc)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:  # type: ignore[override]
        try:
            payload = json.loads(msg.payload.decode())
            measurement = Measurement(
                device_id=payload["device_id"],
                phase=payload.get("phase", "A"),
                voltage=float(payload["voltage"]),
                current=float(payload["current"]),
                active_power=float(payload.get("active_power", 0)),
                energy_kwh=float(payload.get("energy_kwh", 0)),
                power_factor=float(payload.get("power_factor", 1)),
                frequency=float(payload.get("frequency", 50)),
            )
            with self.session_factory() as session:
                session.add(measurement)
                session.commit()
                logger.info("Stored measurement from %s", measurement.device_id)
        except Exception:
            logger.exception("Failed to ingest MQTT message: %s", msg.payload)
