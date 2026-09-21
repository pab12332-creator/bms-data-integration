import os
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Configuración de credenciales de PostgreSQL
USER = "postgres"
PASSWORD = "Admin12345"  # Tu contraseña original
HOST = "localhost"
PORT = 5432
DB_NAME = "BMS_OXXO"

# Conexión mediante pg8000 (evita problemas de codificación de caracteres en Windows)
DATABASE_URL = f"postgresql+pg8000://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 2. Ruta exacta del archivo Excel
archivo_excel = r"C:\Users\JP Carrasco\OneDrive - quantumcontrols.com.mx 1\Documents\Proyecto_BMS\Base de Datos Actualizada\Reporte Agosto 2026.xlsx"

if not os.path.exists(archivo_excel):
    # En caso de que estés ejecutando desde otra máquina o ruta local del proyecto:
    archivo_excel = r"C:\ProyectosBMS\API-BMS\Base de Datos Actualizada\Reporte Agosto 2026.xlsx"

print("Iniciando migración de datos...")

try:
    # Probar conexión y limpiar tablas
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE ticket_equipos, tickets, equipos_bms, edificios RESTART IDENTITY CASCADE;"))
        conn.commit()
        print("Tablas limpiadas para migración desde cero.")

    # ==========================================
    # PASO 1: MIGRAR EDIFICIOS
    # ==========================================
    print("Migrando Edificios...")
    df_bd = pd.read_excel(archivo_excel, sheet_name='BASE_DATOS')
    edificios_unicos = df_bd['Edificio'].dropna().unique()
    
    df_edificios = pd.DataFrame({'nombre': edificios_unicos})
    df_edificios.to_sql('edificios', engine, if_exists='append', index=False, method='multi')
    print("Edificios guardados exitosamente.")

    # Obtener mapeo de edificios
    edificios_sql = pd.read_sql_table('edificios', engine)
    mapa_edificios = dict(zip(edificios_sql['nombre'], edificios_sql['id_edificio']))

    # ==========================================
    # PASO 2: MIGRAR EQUIPOS BMS (INVENTARIO)
    # ==========================================
    print("Migrando Equipos BMS (Inventario)...")
    col_id_equipo = 'Identificador BD' if 'Identificador BD' in df_bd.columns else 'ID'
    
    mapa_columnas_equipos = {
        col_id_equipo: 'id_equipo',
        'Tipo de Dispositivo': 'tipo_dispositivo',
        'Modelo': 'modelo',
        'Zona/Piso': 'zona_piso',
        'Ubicación Física': 'ubicacion_fisica',
        'ID Tablero': 'id_tablero',
        'Fabricante': 'fabricante',
        'Sistema Asociado': 'sistema_asociado',
        'Número de Reporte': 'numero_reporte',
        'Numero de Reporte': 'numero_reporte',
        'Mes de Reporte': 'mes_reporte',
        'Año de Reporte': 'ano_reporte'
    }

    cols_existentes_equipos = [col for col in mapa_columnas_equipos.keys() if col in df_bd.columns]
    df_equipos = df_bd[[col_id_equipo, 'Edificio'] + list(set(cols_existentes_equipos) - {col_id_equipo})].copy()
    df_equipos = df_equipos.loc[:, ~df_equipos.columns.duplicated()]
    
    df_equipos = df_equipos.dropna(subset=[col_id_equipo]).drop_duplicates(subset=[col_id_equipo])
    df_equipos['id_edificio'] = df_equipos['Edificio'].map(mapa_edificios)
    df_equipos = df_equipos.drop(columns=['Edificio'])
    df_equipos = df_equipos.rename(columns=mapa_columnas_equipos)
    df_equipos['id_equipo'] = df_equipos['id_equipo'].astype(str)
    
    df_equipos.to_sql('equipos_bms', engine, if_exists='append', index=False, method='multi')
    print(f"-> {len(df_equipos)} Equipos BMS guardados exitosamente.")

    # ==========================================
    # PASO 3: MIGRAR TICKETS DE SERVICIO (RSS)
    # ==========================================
    print("Migrando Tickets de Servicio...")
    df_rss = pd.read_excel(archivo_excel, sheet_name='Base de Datos RSS')
    df_rss = df_rss.dropna(subset=['ID Ticket'])

    mapa_columnas_tickets = {
        'ID Ticket': 'id_ticket',
        'Solicitante': 'solicitante',
        'Descripción ': 'descripcion',
        'Descripción': 'descripcion',
        'Acción Correctiva': 'accion_correctiva',
        'Estado del Ticket': 'estado',
        'Estado': 'estado',
        'Fecha de Creación': 'fecha_creacion',
        'Fecha Cierre': 'fecha_cierre',
        'Fecha de Cierre': 'fecha_cierre',
        'Notas Cierre': 'notas_cierre',
        'Tipo Dispositivo': 'tipo_dispositivo',
        'Tipo de Dispositivo': 'tipo_dispositivo',
        'Tipo Ticket': 'tipo_ticket',
        'Tipo de Ticket': 'tipo_ticket',
        'Responsable Asignado': 'responsable_asignado',
        'Comentario': 'comentario',
        'Días Respuesta': 'dias_respuesta',
        'Días de Respuesta': 'dias_respuesta',
        'Dias de Respuesta': 'dias_respuesta',
        'Días Ticket Abierto': 'dias_ticket_abierto',
        'Dias del Ticket Abierto': 'dias_ticket_abierto',
        'Mes Inicio': 'mes_inicio',
        'Mes Cierre': 'mes_cierre',
        'Número Reporte': 'numero_reporte',
        'Número de Reporte': 'numero_reporte',
        'Numero de Reporte': 'numero_reporte',
        'Mes Reporte': 'mes_reporte',
        'Mes de Reporte': 'mes_reporte',
        'Año Reporte': 'ano_reporte',
        'Año de Reporte': 'ano_reporte'
    }

    cols_existentes_tickets = [col for col in mapa_columnas_tickets.keys() if col in df_rss.columns]
    df_tickets = df_rss[cols_existentes_tickets].copy()
    
    if 'Edificio' in df_rss.columns:
        df_tickets['id_edificio'] = df_rss['Edificio'].map(mapa_edificios)
        
    df_tickets = df_tickets.rename(columns=mapa_columnas_tickets)
    df_tickets = df_tickets.loc[:, ~df_tickets.columns.duplicated()]

    df_tickets['id_ticket'] = df_tickets['id_ticket'].astype(str)
    if 'fecha_creacion' in df_tickets.columns:
        df_tickets['fecha_creacion'] = pd.to_datetime(df_tickets['fecha_creacion'], errors='coerce')
    if 'fecha_cierre' in df_tickets.columns:
        df_tickets['fecha_cierre'] = pd.to_datetime(df_tickets['fecha_cierre'], errors='coerce')

    df_tickets.to_sql('tickets', engine, if_exists='append', index=False, method='multi')
    print(f"-> {len(df_tickets)} Tickets guardados exitosamente.")

    # ==========================================
    # PASO 4: MIGRAR RELACIÓN TICKET - EQUIPOS
    # ==========================================
    print("Normalizando y migrando relación Ticket-Equipos...")
    cols_dispositivos = [f'Dispositivo {i}' for i in range(1, 13)]
    
    lista_relaciones = []
    for index, row in df_rss.iterrows():
        id_ticket = str(row['ID Ticket']).strip()
        for col in cols_dispositivos:
            if col in row:
                equipo = row[col]
                if pd.notna(equipo) and str(equipo).strip() != '' and str(equipo).lower() != 'nan':
                    equipos_split = [e.strip() for e in str(equipo).split(',') if e.strip()]
                    for eq in equipos_split:
                        lista_relaciones.append({
                            'id_ticket': id_ticket, 
                            'id_equipo': eq
                        })
                
    if lista_relaciones:
        df_ticket_equipos = pd.DataFrame(lista_relaciones).drop_duplicates()
        df_ticket_equipos.to_sql('ticket_equipos', engine, if_exists='append', index=False, method='multi')
        print(f"-> {len(df_ticket_equipos)} Relaciones Ticket-Equipo guardadas.")
    
    print("\n¡Migración ejecutada con éxito!")

except Exception as e:
    print(f"\nOcurrió un error durante la migración: {e}")