from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Edificio(Base):
    __tablename__ = "edificios"
    __table_args__ = {'extend_existing': True}

    id_edificio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)


class EquipoBMS(Base):
    __tablename__ = "equipos_bms"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    id_equipo = Column(String, index=True)
    descripcion = Column(Text, nullable=True)
    tipo_dispositivo = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    edificio = Column(String, nullable=True)  # Contiene el nombre del edificio (ej: "Edificio Amarillo")
    zona_piso = Column(String, nullable=True)
    ubicacion_fisica = Column(String, nullable=True)
    id_tablero = Column(String, nullable=True)
    fabricante = Column(String, nullable=True)
    sistema_asociado = Column(String, nullable=True)
    zona_confort = Column(String, nullable=True)
    numero_reporte = Column(String, nullable=True)
    mes_reporte = Column(String, nullable=True)
    ano_reporte = Column(Integer, nullable=True)
    identificador_bd = Column(String, nullable=True)
    estado = Column(String, nullable=True)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {'extend_existing': True}

    id_ticket = Column(String, primary_key=True, index=True)
    id_edificio = Column(Integer, ForeignKey("edificios.id_edificio"), nullable=True)
    solicitante = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True)
    accion_correctiva = Column(Text, nullable=True)
    estado = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_cierre = Column(DateTime, nullable=True)
    notas_cierre = Column(Text, nullable=True)
    tipo_dispositivo = Column(String, nullable=True)
    tipo_ticket = Column(String, nullable=True)
    responsable_asignado = Column(String, nullable=True)
    comentario = Column(Text, nullable=True)
    costo_estimado = Column(Integer, nullable=True)
    mes_inicio = Column(String, nullable=True)
    ano_reporte = Column(Integer, nullable=True)
    mes_cierre = Column(String, nullable=True)
    ano_cierre = Column(Integer, nullable=True)

    edificio_rel = relationship("Edificio", foreign_keys=[id_edificio], primaryjoin="Ticket.id_edificio == Edificio.id_edificio")
    equipos_asociados = relationship("Dispositivo", backref="ticket", cascade="all, delete-orphan")

    @property
    def nombre_edificio(self):
        return self.edificio_rel.nombre if self.edificio_rel else "Sin edificio"

    @property
    def edificio(self):
        return self.nombre_edificio

    @property
    def equipos_ids(self):
        return [d.id_equipo for d in self.equipos_asociados] if self.equipos_asociados else []


class Dispositivo(Base):
    __tablename__ = "dispositivos"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_ticket = Column(String, ForeignKey("tickets.id_ticket", ondelete="CASCADE"), nullable=False)
    id_equipo = Column(String, ForeignKey("equipos_bms.id_equipo"), nullable=False)


class Tablero(Base):
    __tablename__ = "tableros"
    __table_args__ = {'extend_existing': True}

    id_tablero = Column(String, primary_key=True, index=True)
    edificio = Column(String, nullable=False)
    contador_mantenimientos = Column(Integer, default=0)
    historial_fechas = Column(Text, nullable=True)


class StockItem(Base):
    __tablename__ = 'stock_bms'
    __table_args__ = {'extend_existing': True}

    id_stock = Column(Integer, primary_key=True, index=True)
    id_equipo = Column(String)
    nombre_item = Column(String)
    modelo = Column(String)
    fabricante = Column(String)
    tipo_dispositivo = Column(String(100), nullable=True)
    cantidad = Column(Integer)
    ubicacion = Column(String)
    estatus = Column(String)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
Stock = StockItem

class Catalogo(Base):
    __tablename__ = "catalogos_bms"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    tipo_dispositivo = Column(String(100), nullable=True)
    zona_confort = Column(String(150), nullable=True)
    ubicacion_fisica = Column(String(100), nullable=True)
