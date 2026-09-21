from fastapi import APIRouter
from .endpoints import edificios, tickets, stock, mantenimiento, equipos, tableros

router = APIRouter()

router.include_router(edificios.router, prefix="/edificios", tags=["edificios"])
router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
router.include_router(stock.router, prefix="/stock", tags=["stock"])
router.include_router(mantenimiento.router, prefix="/mantenimiento", tags=["mantenimiento"])
router.include_router(equipos.router, prefix="/equipos", tags=["equipos"])
router.include_router(tableros.router, prefix="/tableros", tags=["tableros"])
