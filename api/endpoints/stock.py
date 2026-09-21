from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models import StockItem
from schemas.stock import StockCreate, StockUpdate, StockResponse

router = APIRouter(tags=["Stock"])

@router.get("", response_model=List[StockResponse])
@router.get("/", response_model=List[StockResponse])
def get_stock(
    nombre_item: Optional[str] = None,
    id_equipo: Optional[str] = None,
    ubicacion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    GET /stock/
    Soporta filtrado por nombre_item (ilike), id_equipo y ubicacion.
    Asegura que nombre_item e id_equipo tengan etiquetas claras si son nulos.
    """
    query = db.query(StockItem)
    if nombre_item:
        query = query.filter(StockItem.nombre_item.ilike(f"%{nombre_item}%"))
    if id_equipo:
        query = query.filter(StockItem.id_equipo.ilike(f"%{id_equipo}%"))
    if ubicacion:
        query = query.filter(StockItem.ubicacion.ilike(f"%{ubicacion}%"))

    items = query.all()

    # Mapeo de datos para asegurar etiquetas claras
    for item in items:
        fabricante = item.fabricante or ""
        modelo = item.modelo or ""
        tag_default = f"{fabricante} {modelo}".strip() or "Sin descripción"

        if not item.nombre_item:
            item.nombre_item = tag_default
        if not item.id_equipo:
            item.id_equipo = tag_default

    return items

@router.post("", response_model=StockResponse)
@router.post("/", response_model=StockResponse)
def create_stock(item: StockCreate, db: Session = Depends(get_db)):
    """
    POST /stock/
    Crea un nuevo registro e inicializa la fecha de actualización.
    Si nombre_item está vacío pero fabricante y modelo existen, se autogenera.
    """
    data = item.model_dump()

    # Lógica de autogeneración de nombre_item
    if not data.get("nombre_item") and data.get("fabricante") and data.get("modelo"):
        data["nombre_item"] = f"{data['fabricante']} - {data['modelo']}"

    nuevo_item = StockItem(
        **data,
        fecha_actualizacion=datetime.utcnow()
    )
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    return nuevo_item

@router.patch("/{id_stock}", response_model=StockResponse)
@router.put("/{id_stock}", response_model=StockResponse)
def update_stock(id_stock: int, item_data: StockUpdate, db: Session = Depends(get_db)):
    """
    PATCH /stock/{id_stock}
    Actualiza campos específicos y refresca fecha_actualizacion.
    """
    db_item = db.query(StockItem).filter(StockItem.id_stock == id_stock).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item de stock no encontrado")
    
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db_item.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{id_stock}")
def delete_stock(id_stock: int, db: Session = Depends(get_db)):
    """
    DELETE /stock/{id_stock}
    Elimina el registro e incluye manejo de error 404.
    """
    db_item = db.query(StockItem).filter(StockItem.id_stock == id_stock).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item de stock no encontrado")
    
    db.delete(db_item)
    db.commit()
    return {"mensaje": "Item eliminado correctamente"}

