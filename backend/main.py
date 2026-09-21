from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine
from backend import models
from api.endpoints import edificios, tickets, stock, mantenimiento, equipos, tableros, catalogos

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BMS Quantum OXXO API",
    version="1.0.0",
    description="API backend para la gestion de mantenimiento, inventario y tickets de BMS y HVAC.",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(edificios.router, prefix="/edificios", tags=["Edificios"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(stock.router, prefix="/stock", tags=["Stock"])
app.include_router(mantenimiento.router, prefix="/mantenimiento", tags=["Mantenimiento"])
app.include_router(equipos.router, tags=["Equipos"])
app.include_router(tableros.router, prefix="/tableros", tags=["Tableros"])
app.include_router(catalogos.router, prefix="/catalogos", tags=["Catalogos"])

@app.get("/")
def read_root():
    return {"mensaje": "Servidor BMS activo y operando correctamente"}

@app.get("/health")
@app.head("/health")
def health_check():
    return {"status": "ok"}
