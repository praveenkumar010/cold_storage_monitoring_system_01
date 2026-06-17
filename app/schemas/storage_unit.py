from pydantic import BaseModel

class StorageUnitCreate(BaseModel):
    warehouse_id: int
    name: str
    unit_type: str