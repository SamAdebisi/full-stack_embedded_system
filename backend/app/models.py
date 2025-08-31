from sqlalchemy import Column, Integer, String, Float, Boolean, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from .db import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)
    online = Column(Boolean, default=False)
    telemetry = relationship("Telemetry", back_populates="device", cascade="all, delete-orphan")

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), index=True, nullable=False)
    ts = Column(BigInteger, index=True, nullable=False)
    temp_c = Column(Float)
    hum_pct = Column(Float)
    device = relationship("Device", back_populates="telemetry")

Index("ix_telemetry_device_ts", Telemetry.device_id, Telemetry.ts)