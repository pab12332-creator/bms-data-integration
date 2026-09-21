# BMS Data Integration & REST API

API REST backend diseñada e implementada en **Python (FastAPI)** para la ingesta, consulta y monitoreo en tiempo real de métricas operativas provenientes de sistemas de infraestructura crítica (BMS, controladores HVAC y redes de comunicación industrial).

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Framework Backend:** FastAPI (Endpoints asíncronos)
* **Base de Datos:** PostgreSQL / SQL
* **Integración:** Protocolos de comunicación industrial (BACnet), Power BI
* **Herramientas:** Cursor, Claude Code, Git

## 🎯 Características Principales

* **Ingesta de Datos Asíncrona:** Endpoints optimizados para recibir y procesar métricas de sensores y controladores en tiempo real.
* **Persistencia Relacional:** Esquema de base de datos relacional optimizado en PostgreSQL para consultas rápidas de series de tiempo e indicadores de eficiencia.
* **Monitoreo & Integración:** Capa de comunicación para consumo de dashboards en Power BI y plataformas operativas.

## 🚀 Estructura del Proyecto

```text
├── app/
│   ├── api/          # Endpoints y rutas de FastAPI
│   ├── core/         # Configuraciones principales
│   ├── models/       # Modelos de bases de datos
│   └── services/     # Lógica de negocio y scripts de ingesta
├── main.py           # Punto de entrada de la aplicación
├── requirements.txt  # Dependencias del proyecto
└── README.md
