from sqlalchemy import Column, Integer, Float, String
from app.db.base import Base

class Rule(Base):
    __tablename__="rules"

    id=Column(Integer, primary_key=True)
    sensor_type=Column(String(100))
    min_value=Column(Float)
    max_value=Column(Float)
    severity=Column(String(100))
    