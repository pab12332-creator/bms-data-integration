from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Edificio
from schemas.edificios import EdificioResponse

router = APIRouter(tags=["Edificios"])

@router.get("", response_model=List[EdificioResponse])
@router.get("/", response_model=List[EdificioResponse])
def get_edificios(db: Session = Depends(get_db)):
    """ Retornar la lista de edificios con id_edificio y nombre """
    return db.query(Edificio).all()

@router.get("/nombres", response_model=List[str])
@router.get("/nombres/", response_model=List[str])
def get_nombres_edificios(db: Session = Depends(get_db)):
    """
    Retorna un arreglo simple de strings con los nombres únicos de los edificios
    registrados: ["Edificio A", "Edificio B"].
    """
    nombres = db.query(Edificio.nombre).distinct().all()
    # nombres es una lista de tuplas: [("Edificio A",), ("Edificio B",)]
    return [n[0] for n in nombres]


