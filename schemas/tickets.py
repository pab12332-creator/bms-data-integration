from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class TicketCreate(BaseModel):
    id_edificio: Optional[int] = None
    solicitante: Optional[str] = None
    tipo_ticket: Optional[str] = None  # Falla, Ajuste, etc.
    tipo_dispositivo: Optional[str] = None
    responsable_asignado: Optional[str] = None
    descripcion: Optional[str] = None
    comentario: Optional[str] = ""
    costo_estimado: Optional[int] = 0
    equipos_ids: List[str] = []  # Lista de id_equipo a vincular en ticket_equipos

class TicketCrearSchema(BaseModel):
    solicitante: str
    id_edificio: Optional[int] = None
    tipo_ticket: str  # ej. "Falla" o "Ajuste"
    prioridad: Optional[str] = "Media"
    descripcion: str
    comentario: Optional[str] = None
    responsable_asignado: Optional[str] = None
    equipos_afectados: List[str]  # Lista con los valores de identificador_bd

class TicketCerrarSchema(BaseModel):
    accion_correctiva: str
    notas_cierre: Optional[str] = None

class TicketUpdate(BaseModel):
    notas_cierre: Optional[str] = None
    estado: Optional[str] = "Cerrado"
    accion_correctiva: Optional[str] = None
    comentario: Optional[str] = None
    costo_estimado: Optional[int] = None

class TicketResponse(BaseModel):
    id_ticket: str
    id_edificio: Optional[int] = None
    nombre_edificio: Optional[str] = None
    edificio: Optional[str] = None
    solicitante: Optional[str] = None
    descripcion: Optional[str] = None
    accion_correctiva: Optional[str] = None
    estado: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    notas_cierre: Optional[str] = None
    tipo_dispositivo: Optional[str] = None
    tipo_ticket: Optional[str] = None
    responsable_asignado: Optional[str] = None
    comentario: Optional[str] = None
    costo_estimado: Optional[int] = None
    mes_inicio: Optional[str] = None
    ano_reporte: Optional[int] = None
    mes_cierre: Optional[str] = None
    ano_cierre: Optional[int] = None
    equipos_ids: List[str] = []

    model_config = ConfigDict(from_attributes=True)


