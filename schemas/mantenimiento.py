from pydantic import BaseModel, Field
from typing import List, Optional

class TableroElectrico(BaseModel):
    id: str
    voltaje_ln: str = "127V"
    voltaje_ll: str = "220V"
    amperaje: str = "0A"
    estatus: str = "OK"

class DispositivoMatriz(BaseModel):
    ubicacion_tablero: str
    tipo_dispositivo: str
    cantidad: int = 1
    voltaje: str = "127V"
    temperatura: str = "25C"
    comms_str: str = "OK"
    torque_str: str = "OK"
    estatus_str: str = "OK"

class FallaDetalle(BaseModel):
    componente_id: str
    descripcion: str
    accion: str

class MantenimientoPDFRequest(BaseModel):
    cliente: str = "OXXO"
    edificio: str
    fecha: str
    nombre_tecnico: str
    supervisor_cliente: str = "Supervisor BMS"
    epp: bool = True
    bisagras_ok: bool = True
    suciedad: str = "Baja"
    tableros_electricos: List[TableroElectrico] = []
    matriz_dispositivos: List[DispositivoMatriz] = []
    lista_fallas: List[FallaDetalle] = []

