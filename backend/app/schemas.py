from pydantic import BaseModel
from typing import Optional, List

class TelemetryIn(BaseModel):
    device_id: str
    ts: int
    temp_c: Optional[float] = None
    hum_pct: Optional[float] = None

class TelemetryOut(TelemetryIn):
    id: int

class DeviceOut(BaseModel):
    device_id: str
    online: bool = False