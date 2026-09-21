from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Tablero, Edificio
from schemas.tableros import TableroResponse

router = APIRouter(tags=["Tableros"])

@router.get("/edificio/{identificador}", response_model=List[TableroResponse])
@router.get("/edificio/{identificador}/", response_model=List[TableroResponse])
def get_tableros_por_edificio(identificador: str, db: Session = Depends(get_db)):
    """
    Retorna la lista estructurada de tableros vinculados a un edificio.
    identificador puede ser el id_edificio (int) o el nombre_edificio (str).
    """
    # Join con Edificio para obtener el id_edificio y asegurar el vínculo
    query = db.query(Tablero, Edificio.id_edificio).join(Edificio, Tablero.edificio == Edificio.nombre)

    if identificador.isdigit():
        query = query.filter(Edificio.id_edificio == int(identificador))
    else:
        query = query.filter(Edificio.nombre.ilike(f"%{identificador}%"))

    results = query.all()

    tableros_final = []
    for t, id_ed in results:
        tableros_final.append({
            "id_tablero": t.id_tablero,
            "nombre_tablero": t.id_tablero, # Fallback a id_tablero si no hay nombre_tablero
            "id_edificio": id_ed,
            "estado": "Activo" # Valor por defecto
        })

    return tableros_final
