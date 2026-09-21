from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Tablero
from fastapi.responses import FileResponse
from schemas.mantenimiento import MantenimientoPDFRequest
from pathlib import Path
import os
import re
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
from backend.checkboxes import checkbox_si_no, checkbox_ok_fallo
from backend.llenar_datos import llenar_tablas_reporte

router = APIRouter(tags=["Mantenimiento"])

@router.post("/pdf")
@router.post("/pdf/")
def generar_pdf_reporte(datos: MantenimientoPDFRequest, db: Session = Depends(get_db)):
    """
    Recibe MantenimientoPDFRequest, procesa la generación del reporte
    y actualiza el contador/historial de los tableros involucrados.
    """
    # --- LOGICA DE PERSISTENCIA (TABLEROS) ---
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')
    for tab_info in datos.tableros_electricos:
        db_tablero = db.query(Tablero).filter(Tablero.id_tablero == tab_info.id).first()
        if db_tablero:
            # Incrementar contador
            if db_tablero.contador_mantenimientos is None:
                db_tablero.contador_mantenimientos = 1
            else:
                db_tablero.contador_mantenimientos += 1

            # Concatenar historial de fechas
            if db_tablero.historial_fechas and db_tablero.historial_fechas.strip():
                db_tablero.historial_fechas += f" | {fecha_hoy}"
            else:
                db_tablero.historial_fechas = fecha_hoy

    db.commit()

    # --- LOGICA DE GENERACIÓN DE PDF ---
    ruta_plantilla = Path(r"C:\ProyectosBMS\API-BMS\Base de Datos Actualizada\reporte_mantenimiento_template.docx")

    if not os.path.exists(ruta_plantilla):
        # Intentar ruta relativa si la absoluta falla
        ruta_plantilla = Path("Base de Datos Actualizada") / "reporte_mantenimiento_template.docx"
    
    if not os.path.exists(ruta_plantilla):
        raise HTTPException(
            status_code=500, 
            detail=f"No se encontró la plantilla en la ruta: {ruta_plantilla}"
        )

    doc = DocxTemplate(ruta_plantilla)
    
    # Preparar contexto para docxtpl
    contexto = datos.model_dump(exclude={"tableros_electricos", "matriz_dispositivos", "lista_fallas"})
    contexto["epp_str"] = checkbox_si_no(datos.epp)
    contexto["bisagras_str"] = checkbox_ok_fallo(datos.bisagras_ok)
    
    doc.render(contexto)

    # Limpiar nombre de archivo
    nombre_base = re.sub(r'[\/\\?%*:|"<>]+', '_', datos.edificio).replace(" ", "_")
    fichero_docx_temp = f"Reporte_Consolidado_{nombre_base}.docx"
    fichero_pdf_salida = f"Reporte_Consolidado_{nombre_base}.pdf"
    
    doc.save(fichero_docx_temp)
    
    try:
        # Llenar tablas complejas con python-docx directamente
        llenar_tablas_reporte(fichero_docx_temp, datos)
    except Exception as e:
        if os.path.exists(fichero_docx_temp):
            os.remove(fichero_docx_temp)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al llenar las tablas del documento: {str(e)}"
        )
    
    try:
        # Convertir a PDF
        convert(fichero_docx_temp, fichero_pdf_salida)
    except Exception as e:
        if os.path.exists(fichero_docx_temp):
            os.remove(fichero_docx_temp)
        raise HTTPException(
            status_code=500, 
            detail=f"Error durante la conversión a PDF: {str(e)}"
        )
        
    if os.path.exists(fichero_docx_temp):
        os.remove(fichero_docx_temp)

    return FileResponse(
        path=fichero_pdf_salida,
        filename=fichero_pdf_salida,
        media_type="application/pdf"
    )
