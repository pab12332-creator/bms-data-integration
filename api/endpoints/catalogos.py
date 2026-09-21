from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Catalogo, EquipoBMS, Edificio
import logging
from urllib.parse import unquote

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Catalogos"])

def _obtener_nombre_edificio(id_or_name: str, db: Session) -> Optional[str]:
    if not id_or_name:
        return None
    cleaned = unquote(str(id_or_name).replace('+', ' ')).strip()
    if cleaned.isdigit():
        edf_obj = db.query(Edificio).filter(Edificio.id_edificio == int(cleaned)).first()
        if edf_obj:
            return edf_obj.nombre
    return cleaned

@router.get("/tipos-equipo", response_model=List[str])
@router.get("/tipos-equipo/", response_model=List[str])
def get_catalogos_tipos(q: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Catalogo.tipo_dispositivo).filter(Catalogo.tipo_dispositivo != None)
    if q:
        q_clean = unquote(str(q).replace('+', ' ')).strip()
        if q_clean:
            query = query.filter(Catalogo.tipo_dispositivo.ilike(f"%{q_clean}%"))
    results = query.distinct().all()
    return sorted([r[0] for r in results if r[0]])

@router.get("/ubicaciones/{edificio_id}", response_model=List[str])
def get_catalogos_ubicaciones(edificio_id: str, db: Session = Depends(get_db)):
    nombre_edf = _obtener_nombre_edificio(edificio_id, db)
    if not nombre_edf:
        return []
    results = (
        db.query(EquipoBMS.ubicacion_fisica)
        .filter(EquipoBMS.edificio.ilike(f"%{nombre_edf}%"))
        .distinct()
        .all()
    )
    return [r[0] for r in results if r[0]]

@router.get("/zonas-confort", response_model=List[str])
@router.get("/zonas-confort/", response_model=List[str])
@router.get("/zonas", response_model=List[str])
@router.get("/zonas/", response_model=List[str])
def get_catalogos_zonas(db: Session = Depends(get_db)):
    results = db.query(Catalogo.zona_confort).filter(Catalogo.zona_confort != None).distinct().all()
    return [r[0] for r in results if r[0]]

@router.get("/zonas/{id_edificio}", response_model=List[str])
def get_catalogos_zonas_por_edificio(id_edificio: str, ubicacion: Optional[str] = Query(None), db: Session = Depends(get_db)):
    nombre_edf = _obtener_nombre_edificio(id_edificio, db)
    if not nombre_edf:
        return []

    query = db.query(EquipoBMS.zona_confort).filter(EquipoBMS.edificio.ilike(f"%{nombre_edf}%"))

    if ubicacion:
        ubi_clean = unquote(str(ubicacion).replace('+', ' ')).strip()
        if ubi_clean:
            query = query.filter(EquipoBMS.ubicacion_fisica.ilike(f"%{ubi_clean}%"))

    results = query.distinct().all()
    return sorted(list(set(r[0].strip() for r in results if r[0] and r[0].strip())))

import unicodedata

def normalizar_texto_comodines(texto: str) -> str:
    """Remueve tildes o las reemplaza por % para búsqueda segura"""
    if not texto:
        return ""
    # Reemplazar vocales acentuadas por % para búsqueda flexible en SQL
    vowels = {'a': 'aá', 'e': 'eé', 'i': 'ií', 'o': 'oó', 'u': 'uú'}
    res = texto.lower()
    for v, replacements in vowels.items():
        for r in replacements:
            res = res.replace(r, '%')
    return f"%{res}%"

@router.get("/equipos-tablero", response_model=List[dict])
@router.get("/equipos-tablero/", response_model=List[dict])
def get_equipos_por_tablero(
    id_edificio: str,
    id_tablero: str,
    filtro_interno: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retorna IDs de equipos filtrados por edificio, tablero y ubicación estricta.
    """
    logger.info("--- INICIO AUDITORÍA /equipos-tablero ---")
    logger.info(f"RECIBIDOS: id_edificio={id_edificio} ({type(id_edificio)}), "
                f"id_tablero={id_tablero} ({type(id_tablero)}), "
                f"filtro_interno={filtro_interno} ({type(filtro_interno)})")

    nombre_edf = _obtener_nombre_edificio(id_edificio, db)
    logger.info(f"PROCESADOS: nombre_edf={nombre_edf}, id_tablero={id_tablero}")

    # 1. Normalización de filtro_interno para ubicación física
    # Si viene "cuarto eléctrico", lo convertimos a algo como "%cuarto el%ctrico%"
    filtro_ubi = normalizar_texto_comodines(filtro_interno or "cuarto electrico")
    logger.info(f"FILTRO SQL UBICACIÓN: {filtro_ubi}")

    # 2. Construcción de Query
    query = db.query(EquipoBMS).filter(
        EquipoBMS.id_tablero == id_tablero,
        EquipoBMS.ubicacion_fisica.ilike(filtro_ubi)
    )

    if nombre_edf:
        query = query.filter(EquipoBMS.edificio.ilike(f"%{nombre_edf}%"))

    # 3. Ejecución y Auditoría
    results = query.all()
    count = len(results)
    logger.info(f"RESULTADOS BD: {count}")


    # 5. Formateo de respuesta (devolvemos objetos dict para cumplir con el requerimiento de Section 5)
    return [{
        "id_equipo": r.id_equipo,
        "descripcion": getattr(r, 'descripcion', 'Sin descripción'),
        "modelo": getattr(r, 'modelo', 'N/A')
    } for r in results]

@router.get("/modelos", response_model=List[str])
@router.get("/modelos/", response_model=List[str])
def get_catalogos_modelos(db: Session = Depends(get_db)):
    """ Retorna una lista de modelos únicos registrados en el inventario. """
    results = db.query(EquipoBMS.modelo).filter(EquipoBMS.modelo != None).distinct().all()
    return sorted([r[0] for r in results if r[0]])

@router.get("/tableros", response_model=List[str])
@router.get("/tableros/", response_model=List[str])
def get_catalogos_tableros(id_edificio: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """ Retorna una lista de tableros únicos, opcionalmente filtrados por edificio. """
    query = db.query(EquipoBMS.id_tablero).filter(EquipoBMS.id_tablero != None)

    if id_edificio:
        nombre_edf = _obtener_nombre_edificio(id_edificio, db)
        if nombre_edf:
            palabra_clave = nombre_edf.split("/")[0].strip()
            query = query.filter(EquipoBMS.edificio.ilike(f"%{palabra_clave}%"))

    results = query.distinct().all()
    return sorted([r[0] for r in results if r[0]])

# Endpoints de compatibilidad
@router.get("/tipo-dispositivo", response_model=List[str])
def get_catalogo_tipo_dispositivo(db: Session = Depends(get_db)):
    return get_catalogos_tipos(None, db)

@router.get("/ubicacion-fisica", response_model=List[str])
def get_catalogo_ubicacion(db: Session = Depends(get_db)):
    results = db.query(Catalogo.ubicacion_fisica).filter(Catalogo.ubicacion_fisica != None).distinct().all()
    return [r[0] for r in results if r[0]]

@router.get("/zona-confort", response_model=List[str])
def get_catalogo_zona_confort(db: Session = Depends(get_db)):
    return get_catalogos_zonas(db)