from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any
from datetime import datetime

class StockBase(BaseModel):
    id_equipo: Optional[str] = None
    nombre_item: Optional[str] = None
    modelo: Optional[str] = None
    fabricante: Optional[str] = None
    tipo_dispositivo: Optional[str] = None
    cantidad: Optional[int] = 0
    ubicacion: Optional[str] = None
    estatus: Optional[str] = None

class StockCreate(StockBase):
    @field_validator('*', mode='before')
    @classmethod
    def empty_string_to_none(cls, v: Any, info: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            # Si el campo es 'cantidad', devolvemos 0 en lugar de None para evitar errores
            if info.field_name == 'cantidad':
                return 0
            return None
        return v

class StockUpdate(BaseModel):
    id_equipo: Optional[str] = None
    nombre_item: Optional[str] = None
    modelo: Optional[str] = None
    fabricante: Optional[str] = None
    cantidad: Optional[int] = None
    ubicacion: Optional[str] = None
    estatus: Optional[str] = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_string_to_none(cls, v: Any, info: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class StockResponse(StockBase):
    id_stock: int
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
