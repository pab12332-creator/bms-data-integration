import logging
import unicodedata
from typing import List, Optional
from urllib.parse import unquote
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Edificio, EquipoBMS


def normalizar_texto(texto: str) -> str:
    """Remueve tildes y normaliza mojibake común de UTF-8/Latin-1"""
    if not texto:
        return ""
    # Corregir mojibake si viene mal codificado de la base de datos
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Quitar tildes y diacríticos para hacer matches limpios
    texto_nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(
        [c for c in texto_nfkd if not unicodedata.combining(c)]
    ).strip()


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Equipos"])


class EquipoResponse(BaseModel):
    id: int
    id_equipo: str
    identificador_bd: str  # <--- Este campo DEBE estar definido explícitamente
    descripcion: Optional[str] = None
    tipo_dispositivo: Optional[str] = None
    modelo: Optional[str] = None
    id_tablero: Optional[str] = None
    ubicacion_fisica: Optional[str] = None
    zona_confort: Optional[str] = None
    edificio: Optional[str] = None
    estado: Optional[str] = None

    class Config:
        from_attributes = True


class EquipoListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[EquipoResponse]
    equipos: List[EquipoResponse]


def _obtener_nombre_edificio(id_or_name: str, db: Session) -> Optional[str]:
    """Resuelve un ID numérico o string al nombre real en la tabla edificios"""
    if not id_or_name:
        return None
    cleaned = unquote(str(id_or_name).replace("+", " ")).strip()
    if cleaned.isdigit():
        edf_obj = (
            db.query(Edificio)
            .filter(Edificio.id_edificio == int(cleaned))
            .first()
        )
        if edf_obj:
            return edf_obj.nombre
    return cleaned


@router.get("/equipos", response_model=EquipoListResponse)
@router.get("/equipos/", response_model=EquipoListResponse)
@router.get("/equipos_bms", response_model=EquipoListResponse)
@router.get("/equipos_bms/", response_model=EquipoListResponse)
@router.get("/equipos/filtrar", response_model=EquipoListResponse)
@router.get("/equipos/filtrar/", response_model=EquipoListResponse)
def filtrar_equipos(
    q: Optional[str] = Query(None),
    id_edificio: Optional[str] = None,
    edificio: Optional[str] = None,
    tipo_dispositivo: Optional[str] = None,
    tipo_equipo: Optional[str] = None,
    modelo: Optional[str] = None,
    id_tablero: Optional[str] = None,
    ubicacion_fisica: Optional[str] = None,
    zona_confort: Optional[str] = None,
    descripcion: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Endpoint de búsqueda avanzada con lógica AND estricta.
    Filtra por q (búsqueda abierta), edificio, tipo, modelo, tablero, ubicación y zona.
    """
    query = db.query(EquipoBMS)

    def clean_param(p):
        if p is not None:
            return unquote(str(p).replace("+", " ")).strip()
        return None

    # 0. Búsqueda abierta (q)
    q_param = clean_param(q)
    if q_param:
        q_norm = normalizar_texto(q_param)
        query = query.filter(
            (EquipoBMS.identificador_bd.ilike(f"%{q_norm}%")) |
            (EquipoBMS.id_equipo.ilike(f"%{q_norm}%")) |
            (EquipoBMS.descripcion.ilike(f"%{q_norm}%"))
        )

    # 1. Filtro de edificio (Mapeo de ID a Nombre palabra clave)
    param_edf = clean_param(id_edificio or edificio)
    if param_edf:
        nombre_edf = _obtener_nombre_edificio(param_edf, db)
        if nombre_edf:
            palabra_clave = normalizar_texto(nombre_edf).split("/")[0].strip()
            query = query.filter(EquipoBMS.edificio.ilike(f"%{palabra_clave}%"))

    # 2. Tipo de dispositivo (AND)
    tipo = clean_param(tipo_dispositivo or tipo_equipo)
    if tipo:
        tipo_clean = normalizar_texto(tipo)
        query = query.filter(EquipoBMS.tipo_dispositivo.ilike(f"%{tipo_clean}%"))

    # 3. Modelo (AND)
    mod = clean_param(modelo)
    if mod:
        query = query.filter(EquipoBMS.modelo.ilike(f"%{mod}%"))

    # 4. ID Tablero (AND)
    tab = clean_param(id_tablero)
    if tab:
        query = query.filter(EquipoBMS.id_tablero.ilike(f"%{tab}%"))

    # 5. Ubicación Física (AND)
    ubi = clean_param(ubicacion_fisica)
    if ubi:
        ubi_clean = normalizar_texto(ubi)
        query = query.filter(EquipoBMS.ubicacion_fisica.ilike(f"%{ubi_clean}%"))

    # 6. Zona de Confort (AND)
    zona = clean_param(zona_confort)
    if zona:
        zona_clean = normalizar_texto(zona)
        query = query.filter(EquipoBMS.zona_confort.ilike(f"%{zona_clean}%"))

    # 7. Descripción (AND)
    desc = clean_param(descripcion)
    if desc:
        desc_clean = normalizar_texto(desc)
        query = query.filter(EquipoBMS.descripcion.ilike(f"%{desc_clean}%"))

    # Ejecución de conteo y paginación
    total = query.count()
    raw_items = query.offset(skip).limit(limit).all()

    # Garantizar IDENTIFICADOR ÚNICO (identificador_bd) para cada registro
    items_final = []
    for r in raw_items:
        # Extraer datos a un diccionario para asegurar la serialización limpia
        item_dict = {
            "id": int(r.id),
            "id_equipo": str(r.id_equipo),
            "identificador_bd": str(r.identificador_bd) if r.identificador_bd else f"{r.id_equipo}-{r.id_tablero}-{int(r.id)}",
            "descripcion": r.descripcion,
            "tipo_dispositivo": r.tipo_dispositivo,
            "modelo": r.modelo,
            "id_tablero": r.id_tablero,
            "ubicacion_fisica": r.ubicacion_fisica,
            "zona_confort": r.zona_confort,
            "edificio": r.edificio,
            "estado": getattr(r, 'estado', 'OK')
        }
        items_final.append(item_dict)

    # Formateo de respuesta robusto
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items_final,
        "equipos": items_final,
    }


@router.get("/equipos/filtrar-tablero-electrico", response_model=List[str])
@router.get("/equipos/filtrar-tablero-electrico/", response_model=List[str])
@router.get("/filtrar-tablero-electrico", response_model=List[str])
@router.get("/filtrar-tablero-electrico/", response_model=List[str])
def filtrar_por_tablero_electrico(
    id_edificio: str, id_tablero: str, db: Session = Depends(get_db)
):
    """
    Retorna IDs de equipos que coincidan con edificio, tablero y ubicación estricta.
    """
    logger.info(f"AUDITORIA filtrar-tablero-electrico: edificio={id_edificio}, tablero={id_tablero}")

    nombre_edf = _obtener_nombre_edificio(id_edificio, db)
    logger.info(f"Nombre edificio resuelto: {nombre_edf}")

    # Se usa comodín para la tilde en 'eléctrico' para máxima compatibilidad
    query = db.query(EquipoBMS.id_equipo).filter(
        EquipoBMS.id_tablero == id_tablero,
        EquipoBMS.ubicacion_fisica.ilike("%cuarto el%ctrico%"),
    )
    if nombre_edf:
        palabra_clave = normalizar_texto(nombre_edf).split("/")[0].strip()
        query = query.filter(EquipoBMS.edificio.ilike(f"%{palabra_clave}%"))

    results = query.all()
    count = len(results)
    logger.info(f"Resultados encontrados: {count}")

    return [r[0] for r in results]


@router.get("/equipos/edificio/{id_edificio}", response_model=List[EquipoResponse])
@router.get("/equipos/edificio/{id_edificio}/", response_model=List[EquipoResponse])
@router.get("/edificio/{id_edificio}", response_model=List[EquipoResponse])
@router.get("/edificio/{id_edificio}/", response_model=List[EquipoResponse])
def get_equipos_por_edificio(id_edificio: str, db: Session = Depends(get_db)):
    nombre_edf = _obtener_nombre_edificio(id_edificio, db)
    if not nombre_edf:
        return []
    palabra_clave = normalizar_texto(nombre_edf).split("/")[0].strip()
    results = (
        db.query(EquipoBMS)
        .filter(EquipoBMS.edificio.ilike(f"%{palabra_clave}%"))
        .all()
    )

    # Garantizar IDENTIFICADOR ÚNICO (identificador_bd) para cada registro
    final_list = []
    for r in results:
        final_list.append({
            "id": int(r.id),
            "id_equipo": str(r.id_equipo),
            "identificador_bd": str(r.identificador_bd) if r.identificador_bd else f"{r.id_equipo}-{r.id_tablero}-{int(r.id)}",
            "descripcion": r.descripcion,
            "tipo_dispositivo": r.tipo_dispositivo,
            "modelo": r.modelo,
            "id_tablero": r.id_tablero,
            "ubicacion_fisica": r.ubicacion_fisica,
            "zona_confort": r.zona_confort,
            "edificio": r.edificio,
            "estado": getattr(r, 'estado', 'OK')
        })

    return final_list
