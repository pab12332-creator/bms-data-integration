from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List, Optional
from datetime import datetime, timedelta

def get_local_time():
    # Mexico City is UTC-6
    return datetime.utcnow() - timedelta(hours=6)

from backend.database import get_db
from backend.models import Ticket, Dispositivo, EquipoBMS
from schemas.tickets import TicketCreate, TicketUpdate, TicketResponse, TicketCrearSchema, TicketCerrarSchema

router = APIRouter(tags=["Tickets"])

def get_month_name(date: datetime) -> str:
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return months[date.month - 1]

@router.post("", response_model=str)
@router.post("/", response_model=str)
def crear_ticket(payload: TicketCrearSchema, db: Session = Depends(get_db)):
    """
    Crea un ticket con selección múltiple de equipos y sincroniza inventario.
    """
    try:
        # Generar ID de ticket consecutivo
        total_tickets = db.query(Ticket).count()
        consecutivo = total_tickets + 1
        nuevo_id_ticket = f"TKT-{consecutivo:04d}"
        while db.query(Ticket).filter(Ticket.id_ticket == nuevo_id_ticket).first():
            consecutivo += 1
            nuevo_id_ticket = f"TKT-{consecutivo:04d}"

        ahora = get_local_time()

        # Insertar ticket principal
        nuevo_ticket = Ticket(
            id_ticket=nuevo_id_ticket,
            id_edificio=payload.id_edificio,
            solicitante=payload.solicitante,
            tipo_ticket=payload.tipo_ticket,
            prioridad=payload.prioridad,
            descripcion=payload.descripcion,
            comentario=payload.comentario,
            responsable_asignado=payload.responsable_asignado,
            estado="Abierto",
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
            mes_inicio=get_month_name(ahora),
            ano_reporte=ahora.year
        )
        db.add(nuevo_ticket)
        db.flush() # Obtener id_ticket si fuera autoincrement, pero aquí lo generamos nosotros.

        # Procesar equipos afectados
        for item in payload.equipos_afectados:
            # a) Insertar en tabla relacional dispositivos
            relacion = Dispositivo(id_ticket=nuevo_id_ticket, id_equipo=item)
            db.add(relacion)

            # b) Buscar equipo en inventario (Primero por identificador_bd, luego por id_equipo)
            equipo = db.query(EquipoBMS).filter(EquipoBMS.identificador_bd == item).first()
            if not equipo:
                equipo = db.query(EquipoBMS).filter(EquipoBMS.id_equipo == item).first()

            if not equipo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El equipo '{item}' no existe en el catálogo equipos_bms"
                )

            # d) Actualizar estado del equipo
            equipo.estado = payload.tipo_ticket

        db.commit()
        return nuevo_id_ticket

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear ticket: {str(e)}")

@router.get("", response_model=List[TicketResponse])
@router.get("/", response_model=List[TicketResponse])
def listar_tickets(
    id_edificio: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    solicitante: Optional[str] = Query(None),
    descripcion: Optional[str] = Query(None),
    mes: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista tickets con filtrado acumulativo.
    - id_edificio: Búsqueda exacta.
    - estado: Búsqueda exacta (insensible a mayúsculas si se desea, pero aquí se pide validación strip).
    - solicitante, descripcion: Búsqueda parcial (ilike).
    - mes, ano: Basado en fecha_creacion.
    """
    query = db.query(Ticket)

    if id_edificio is not None:
        query = query.filter(Ticket.id_edificio == id_edificio)

    if estado and estado.strip():
        # Búsqueda exacta según requerimiento (comparación ==)
        query = query.filter(Ticket.estado == estado.strip())

    if solicitante and solicitante.strip():
        query = query.filter(Ticket.solicitante.ilike(f"%{solicitante.strip()}%"))

    if descripcion and descripcion.strip():
        query = query.filter(Ticket.descripcion.ilike(f"%{descripcion.strip()}%"))

    if mes is not None:
        query = query.filter(extract('month', Ticket.fecha_creacion) == mes)

    if ano is not None:
        query = query.filter(extract('year', Ticket.fecha_creacion) == ano)

    return query.order_by(Ticket.id_ticket.desc()).all()

@router.patch("/{ticket_id}/actualizar", response_model=TicketResponse)
def actualizar_avance_ticket(ticket_id: str, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    """
    Actualiza notas o avances sin cambiar necesariamente el estatus.
    """
    db_ticket = db.query(Ticket).filter(Ticket.id_ticket == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    ahora = get_local_time()
    db_ticket.fecha_actualizacion = ahora

    timestamp = ahora.strftime('%d/%m/%Y %H:%M')

    if ticket_data.comentario is not None:
        nueva_nota = ticket_data.comentario.strip()
        if nueva_nota:
            formato_nota = f"[{timestamp}] {nueva_nota}"
            if db_ticket.comentario and db_ticket.comentario.strip():
                db_ticket.comentario += f"\n{formato_nota}"
            else:
                db_ticket.comentario = formato_nota

    if ticket_data.costo_estimado is not None:
        db_ticket.costo_estimado = ticket_data.costo_estimado

    if ticket_data.accion_correctiva is not None:
        nueva_accion = ticket_data.accion_correctiva.strip()
        if nueva_accion:
            formato_accion = f"[{timestamp}] {nueva_accion}"
            if db_ticket.accion_correctiva and db_ticket.accion_correctiva.strip():
                db_ticket.accion_correctiva += f"\n{formato_accion}"
            else:
                db_ticket.accion_correctiva = formato_accion

    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.put("/{ticket_id}/cerrar")
def cerrar_ticket_completo(ticket_id: str, payload: TicketCerrarSchema, db: Session = Depends(get_db)):
    """
    Cierra el ticket y restablece el estado de los equipos asociados a 'OK'.
    """
    try:
        # 1. Buscar y actualizar el ticket
        db_ticket = db.query(Ticket).filter(Ticket.id_ticket == ticket_id).first()
        if not db_ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        ahora = get_local_time()
        db_ticket.estado = "Cerrado"
        db_ticket.fecha_cierre = ahora
        db_ticket.mes_cierre = get_month_name(ahora)
        db_ticket.ano_cierre = ahora.year
        db_ticket.fecha_actualizacion = ahora
        db_ticket.accion_correctiva = payload.accion_correctiva
        db_ticket.notas_cierre = payload.notas_cierre

        # 2. Consultar dispositivos asociados
        viculos = db.query(Dispositivo).filter(Dispositivo.id_ticket == ticket_id).all()

        # 3. Restablecer estado de equipos
        for vinculo in viculos:
            equipo = db.query(EquipoBMS).filter(EquipoBMS.identificador_bd == vinculo.id_equipo).first()
            if equipo:
                equipo.estado = "OK"

        db.commit()
        return {"mensaje": f"Ticket {ticket_id} cerrado exitosamente y equipos sincronizados."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cerrar ticket: {str(e)}")

@router.patch("/{ticket_id}/cerrar", response_model=TicketResponse)
def cerrar_ticket_endpoint(ticket_id: str, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    """
    Registra nota final y actualiza el estatus a CERRADO.
    """
    db_ticket = db.query(Ticket).filter(Ticket.id_ticket == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    ahora = get_local_time()
    db_ticket.fecha_actualizacion = ahora
    db_ticket.estado = "Cerrado"
    db_ticket.fecha_cierre = ahora
    db_ticket.mes_cierre = get_month_name(ahora)
    db_ticket.ano_cierre = ahora.year

    timestamp = ahora.strftime('%d/%m/%Y %H:%M')

    if ticket_data.notas_cierre is not None:
        nueva_nota = ticket_data.notas_cierre.strip()
        if nueva_nota:
            formato_nota = f"[{timestamp}] {nueva_nota}"
            if db_ticket.notas_cierre and db_ticket.notas_cierre.strip():
                db_ticket.notas_cierre += f"\n{formato_nota}"
            else:
                db_ticket.notas_cierre = formato_nota

    if ticket_data.accion_correctiva is not None:
        nueva_accion = ticket_data.accion_correctiva.strip()
        if nueva_accion:
            formato_accion = f"[{timestamp}] {nueva_accion}"
            if db_ticket.accion_correctiva and db_ticket.accion_correctiva.strip():
                db_ticket.accion_correctiva += f"\n{formato_accion}"
            else:
                db_ticket.accion_correctiva = formato_accion

    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.patch("/{ticket_id}/notas", response_model=TicketResponse)
@router.post("/{ticket_id}/notas", response_model=TicketResponse)
def agregar_nota_ticket(ticket_id: str, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    """
    Endpoint específico para agregar notas o comentarios al historial del ticket.
    Concatena la nueva nota con timestamp y salto de línea.
    """
    db_ticket = db.query(Ticket).filter(Ticket.id_ticket == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    ahora = get_local_time()
    db_ticket.fecha_actualizacion = ahora
    timestamp = ahora.strftime('%d/%m/%Y %H:%M')

    # Priorizamos comentario o notas_cierre como fuente de la "nota"
    nueva_nota = (ticket_data.comentario or ticket_data.notas_cierre or "").strip()

    if nueva_nota:
        formato_nota = f"[{timestamp}] {nueva_nota}"
        if db_ticket.comentario and db_ticket.comentario.strip():
            db_ticket.comentario += f"\n{formato_nota}"
        else:
            db_ticket.comentario = formato_nota

    db.commit()
    db.refresh(db_ticket)
    return db_ticket


