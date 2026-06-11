from pydantic import BaseModel, Field


class SensorDataSchema(BaseModel):
    sensor_id: int
    temperature: float = Field(..., ge=-100)
    humidity: float = Field(..., ge=0)
    door_open: bool