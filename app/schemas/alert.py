from pydantic import BaseModel

class AlertSchema(BaseModel):
    sensor_id:int
    value:float
    message:str
    severity:str
    