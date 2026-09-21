from pydantic import BaseModel, ConfigDict
from typing import Optional

class EdificioBase(BaseModel):
    nombre: str

class EdificioResponse(BaseModel):
    id_edificio: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)

