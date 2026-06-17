
from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, DateTime
from datetime import datetime
from app.db.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))

    message = Column(String(200), nullable=False)
    severity = Column(String(20), default="medium")

    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)