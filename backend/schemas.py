from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from typing import Literal

# -------------------------------------------------------------
# ESQUEMAS DE CATÁLOGOS (EDIFICIOS)
# -------------------------------------------------------------
class EdificioCreate(BaseModel):
    nombre: str

class EdificioResponse(BaseModel):
    id_edificio: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# ESQUEMAS DE EQUIPOS BMS
# -------------------------------------------------------------
class EquipoResponse(BaseModel):
    id_equipo: str
    tipo_dispositivo: Optional[str] = None
    modelo: Optional[str] = None
    id_edificio: Optional[int] = None
    zona_piso: Optional[str] = None
    ubicacion_fisica: Optional[str] = None
    id_tablero: Optional[str] = None
    fabricante: Optional[str] = None
    sistema_asociado: Optional[str] = None
    numero_reporte: Optional[str] = None
    mes_reporte: Optional[str] = None
    ano_reporte: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------
# ESQUEMAS DE TICKETS Y RELACIONES
# -------------------------------------------------------------
class TicketCreate(BaseModel):
    id_ticket: str
    id_edificio: Optional[int] = None
    solicitante: Optional[str] = None
    descripcion: Optional[str] = None
    accion_correctiva: Optional[str] = None
    estatus: Optional[str] = "Abierto"
    tipo_dispositivo: Optional[str] = None
    tipo_ticket: Optional[str] = None
    responsable_asignado: Optional[str] = None
    comentario: Optional[str] = None
    numero_reporte: Optional[str] = None
    mes_reporte: Optional[str] = None
    ano_reporte: Optional[int] = None

class TicketUpdate(BaseModel):
    estatus: Optional[str] = None
    notas_cierre: Optional[str] = None
    accion_correctiva: Optional[str] = None
    responsable_asignado: Optional[str] = None

class TicketResponse(TicketCreate):
    fecha_creacion: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    notas_cierre: Optional[str] = None
    dias_respuesta: Optional[int] = None
    dias_ticket_abierto: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class RelacionTicketEquipo(BaseModel):
    id_ticket: str
    id_equipo: str

# -------------------------------------------------------------
# ESQUEMAS PARA GENERACIÓN DE REPORTES PDF
# -------------------------------------------------------------
class DispositivoReporte(BaseModel):
    tipo_dispositivo: str
    cantidad: int
    voltaje: float
    temperatura: float
    comms_ok: bool = True
    torque: bool = True
    estatus_ok: bool = True

class FallaReporte(BaseModel):
    id_equipo: str
    falla: str
    accion: str

class GenerarReporteRequest(BaseModel):
    cliente: str = "Oxxo Corporativo"
    id_tablero: str
    ubicacion: str
    fecha: str
    nombre_tecnico: str
    epp: bool = True
    bisagras_ok: bool = True
    suciedad: str = "Bajo"  # Opciones: 'Bajo', 'Medio', 'Alto'
    voltaje_ln: float
    voltaje_ll: float
    amperaje_total: float
    dispositivos: List[DispositivoReporte]
    fallas: Optional[List[FallaReporte]] = []

class TableroElectricoData(BaseModel):
    id: str  # Se valida contra PostgreSQL
    voltaje_ln: str
    voltaje_ll: str
    amperaje: str
    estatus: str  # Debe ser solo texto

class DispositivoData(BaseModel):
    ubicacion_tablero: str  # Debe existir en la tabla tableros
    tipo_dispositivo: str    # Debe existir en la columna tipo_dispositivo de equipos_bms
    cantidad: int            # Numérico sin unidad
    voltaje: str
    temperatura: str
    comms_str: Literal["OK", "N/A"]   # Solo acepta OK o N/A
    torque_str: Literal["OK", "N/A"]  # Solo acepta OK o N/A
    estatus_str: Literal["OK", "N/A"] # Solo acepta OK o N/A

class FallaData(BaseModel):
    componente_id: str  # Debe existir en id_equipo de equipos_bms
    descripcion: str    # Texto
    accion: str         # Texto

# -------------------------------------------------------------
# ESQUEMAS DE CATÁLOGOS (CATALOGOS_BMS)
# -------------------------------------------------------------
class CatalogoResponse(BaseModel):
    id: Optional[int] = None
    tipo_dispositivo: Optional[str] = None
    zona_confort: Optional[str] = None
    ubicacion_fisica: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)