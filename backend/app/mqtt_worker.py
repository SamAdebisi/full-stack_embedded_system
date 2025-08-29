import json, threading
from typing import Callable
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from .config import settings
from .models import Device, Telemetry
from .db import SessionLocal
def _ensure_device(db: Session, device_id: str) -> Device:
    dev = db.query(Device).filter(Device.device_id == device_id).one_or_none()
    if not dev:
        dev = Device(device_id=device_id, online=False); db.add(dev)
    return dev
class MqttBridge:
    def __init__(self, on_telemetry: Callable[[dict], None], on_status: Callable[[str, bool], None]):
        self.client = mqtt.Client(client_id=settings.mqtt_client_id, clean_session=True)
        if settings.mqtt_tls:
            self.client.tls_set(ca_certs=settings.mqtt_ca_cert)
            self.client.tls_insecure_set(False)
        if settings.mqtt_username:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.on_telemetry = on_telemetry
        self.on_status = on_status
    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("devices/+/telemetry"); client.subscribe("devices/+/status")
    def _on_message(self, client, userdata, msg):
        t = msg.topic
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            return
        if t.endswith("/telemetry"):
            self.on_telemetry(payload)
        elif t.endswith("/status"):
            did = payload.get("device_id"); online = bool(payload.get("online"))
            if did: self.on_status(did, online)
    def run_forever(self):
        self.client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=30)
        self.client.loop_forever(retry_first_connection=True)
def start_worker(broadcast_fn: Callable[[dict], None]):
    def on_telemetry(p: dict):
        with SessionLocal() as db:
            _ensure_device(db, p["device_id"])
            db.add(Telemetry(device_id=p["device_id"], ts=int(p["ts"]), temp_c=p.get("temp_c"), hum_pct=p.get("hum_pct")))
            db.commit()
        broadcast_fn({"type":"telemetry","data":p})
    def on_status(device_id: str, online: bool):
        with SessionLocal() as db:
            dev = _ensure_device(db, device_id); dev.online = online; db.commit()
        broadcast_fn({"type":"status","data":{"device_id":device_id,"online":online}})
    th = threading.Thread(target=MqttBridge(on_telemetry,on_status).run_forever, daemon=True); th.start(); return th

