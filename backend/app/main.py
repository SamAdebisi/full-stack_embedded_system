from datetime import datetime, timedelta
import anyio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import jwt
from passlib.context import CryptContext
from .config import settings
from .db import Base, engine, SessionLocal
from .models import Device, Telemetry
from .schemas import TelemetryOut, DeviceOut
from .mqtt_worker import start_worker

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="IoT Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[orig.strip() for orig in settings.cors_origins.split(',') if orig],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health():
    return {"ok": True}

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
ADMIN_USERNAME = settings.admin_user
ADMIN_HASH = pwd_ctx.hash(settings.admin_password)

def create_access_token(sub: str, minutes: int) -> str:
    exp = datetime.utcnow() + timedelta(minutes=minutes)
    return jwt.encode({"sub": sub, "exp": exp}, settings.jwt_secret, algorithm="HS256")

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

async def require_user(token: str = Depends(oauth2_scheme)):
    verify_token(token)

# WS hub
class Hub:
    def __init__(self):
        self.clients: List[WebSocket] = []
    async def join(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)
    def leave(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)
    async def broadcast(self, payload: dict):
        for ws in list(self.clients):
            try:
                await ws.send_json(payload)
            except Exception:
                self.leave(ws)

hub = Hub()

# Start MQTT worker only when enabled
if settings.start_mqtt:
    start_worker(lambda payload: anyio.from_thread.run(hub.broadcast, payload))

@app.post("/api/auth/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USERNAME or not pwd_ctx.verify(form.password, ADMIN_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad credentials")
    return {"access_token": create_access_token(form.username, settings.jwt_expire_minutes), "token_type": "bearer"}

@app.get("/api/devices", response_model=List[DeviceOut], dependencies=[Depends(require_user)])
async def list_devices():
    with SessionLocal() as db:
        rows = db.query(Device).all()
        return [DeviceOut(device_id=r.device_id, online=r.online) for r in rows]

@app.get("/api/telemetry", response_model=List[TelemetryOut], dependencies=[Depends(require_user)])
async def list_telemetry(
    device_id: str = Query(...),
    limit: int = Query(200, ge=1, le=5000),
    since_ts: Optional[int] = Query(None),
    until_ts: Optional[int] = Query(None),
):
    with SessionLocal() as db:
        q = db.query(Telemetry).filter(Telemetry.device_id == device_id)
        if since_ts is not None:
            q = q.filter(Telemetry.ts >= since_ts)
        if until_ts is not None:
            q = q.filter(Telemetry.ts <= until_ts)
        rows = list(reversed(q.order_by(Telemetry.ts.desc()).limit(limit).all()))
        return [TelemetryOut(id=r.id, device_id=r.device_id, ts=r.ts, temp_c=r.temp_c, hum_pct=r.hum_pct) for r in rows]

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        return await ws.close(code=4401)
    try:
        verify_token(token)
    except HTTPException:
        return await ws.close(code=4401)
    await hub.join(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        hub.leave(ws)
```

```ini
