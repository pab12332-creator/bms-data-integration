from pydantic import BaseModel
from typing import Optional

class TableroResponse(BaseModel):
    id_tablero: str
    nombre_tablero: Optional[str] = None
    id_edificio: Optional[int] = None
    estado: Optional[str] = "Activo"

    class Config:
        from_attributes = True
