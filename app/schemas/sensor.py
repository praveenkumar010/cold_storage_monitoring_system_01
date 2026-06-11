from pydantic import BaseModel

class SensorCreate(BaseModel):
    storage_unit_id: int
    sensor_type:str
    source:str