# API REST - Sistema de Indicadores

## Descripción

API REST construida con FastAPI para el Sistema de Indicadores. Proporciona endpoints para gestionar indicadores, hitos, actividades y reportes mensuales de avance.

## Características

- ✅ **25+ Endpoints** organizados por recurso
- ✅ **Documentación automática** (Swagger UI y ReDoc)
- ✅ **Validación automática** con Pydantic
- ✅ **CORS configurado** para integración con frontends
- ✅ **Respuestas tipadas** con modelos Pydantic
- ✅ **Manejo de errores** con códigos HTTP estándar

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

### Desarrollo (con auto-reload)
```bash
uvicorn api:app --reload --port 8000
```

### Producción
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

## Documentación

Una vez ejecutada la API, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints Principales

### 📊 Indicadores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicadores` | Listar indicadores (con filtros) |
| GET | `/api/indicadores/{id}` | Obtener indicador específico |
| POST | `/api/indicadores` | Crear indicador (Admin) |
| DELETE | `/api/indicadores/{id}` | Eliminar indicador (Admin) |
| GET | `/api/indicadores/{id}/jerarquia` | Jerarquía completa (Indicador → Hitos → Actividades) |

**Filtros disponibles:**
- `area`: Filtrar por área
- `año`: Filtrar por año
- `unidad_organizacional`: Filtrar por unidad organizacional
- `tipo_indicador`: Filtrar por tipo
- `estado`: Filtrar por estado
- `responsable`: Filtrar por responsable

### 🎯 Hitos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/hitos` | Listar hitos |
| GET | `/api/indicadores/{id}/hitos` | Hitos de un indicador |
| POST | `/api/hitos` | Crear hito (Admin) |
| DELETE | `/api/hitos/{id}` | Eliminar hito (Admin) |

### 📋 Actividades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/actividades` | Listar actividades |
| GET | `/api/hitos/{id}/actividades` | Actividades de un hito |
| POST | `/api/actividades` | Crear actividad (Admin) |
| DELETE | `/api/actividades/{id}` | Eliminar actividad (Admin) |

### 📅 Avance Mensual

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/avance-mensual` | Registrar avance mensual (Owner) |
| GET | `/api/avance-mensual/{entidad}/{id}` | Último avance reportado |
| GET | `/api/avance-mensual/{entidad}/{id}/historico` | Histórico completo |

**Nota:** `entidad` debe ser `hito` o `actividad`

### 📈 Dashboard & Seguimiento

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Estadísticas del dashboard |
| GET | `/api/seguimiento/responsable/{nombre}` | Items por responsable |

### 👥 Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/responsables` | Lista de responsables |
| GET | `/api/areas` | Lista de áreas |
| GET | `/api/unidades-organizacionales` | Lista de unidades organizacionales |

### ❤️ Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado de la API |

## Ejemplos de Uso

### Crear un Indicador

```bash
curl -X POST "http://localhost:8000/api/indicadores" \
  -H "Content-Type: application/json" \
  -d '{
    "año": 2026,
    "indicador": "Incremento de ventas digitales",
    "tipo_indicador": "Estratégico",
    "responsable": "Juan Pérez",
    "meta": "100",
    "tiene_hitos": true,
    "estado": "Por comenzar"
  }'
```

### Listar Indicadores con Filtros

```bash
curl "http://localhost:8000/api/indicadores?responsable=Juan%20Pérez&año=2026"
```

### Obtener Jerarquía Completa

```bash
curl "http://localhost:8000/api/indicadores/1/jerarquia"
```

### Registrar Avance Mensual

```bash
curl -X POST "http://localhost:8000/api/avance-mensual" \
  -H "Content-Type: application/json" \
  -d '{
    "entidad": "hito",
    "id_entidad": 1,
    "avance_reportado": 50,
    "usuario": "Juan Pérez"
  }'
```

### Obtener Estadísticas del Dashboard

```bash
curl "http://localhost:8000/api/dashboard/stats"
```

## Modelos de Datos

### IndicadorCreate

```json
{
  "año": 2026,
  "indicador": "string",
  "tipo_indicador": "string",
  "responsable": "string",
  "meta": "string",
  "medida": "string",
  "tiene_hitos": true,
  "estado": "Por comenzar",
  "area": "string",
  "unidad_organizacional": "string",
  "lineamientos_estrategicos": "string",
  "fecha_inicio": "2026-01-01",
  "fecha_fin_original": "2026-12-31"
}
```

### HitoCreate

```json
{
  "indicador_id": 1,
  "nombre": "string",
  "descripcion": "string",
  "responsable": "string",
  "fecha_inicio": "2026-01-01",
  "fecha_fin_planificada": "2026-06-30",
  "estado": "Por comenzar"
}
```

### ActividadCreate

```json
{
  "hito_id": 1,
  "descripcion_actividad": "string",
  "responsable": "string",
  "fecha_inicio_plan": "2026-01-01",
  "fecha_fin_plan": "2026-03-31",
  "estado_actividad": "Por comenzar"
}
```

### AvanceMensualCreate

```json
{
  "entidad": "hito",
  "id_entidad": 1,
  "avance_reportado": 50,
  "usuario": "Juan Pérez",
  "mes": "2026-02"
}
```

## Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

## Integración con Streamlit

La API puede ejecutarse en paralelo con la aplicación Streamlit:

- **Streamlit**: Puerto 8501 (por defecto)
- **API**: Puerto 8000

Ambas aplicaciones comparten la misma base de datos a través de `database.py`.

## Deployment en Railway

### Opción 1: Dos Servicios Separados

```yaml
# railway.toml para Streamlit
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT"

# railway.toml para API
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port=$PORT"
```

### Opción 2: Procfile (Un Solo Servicio)

```
web: streamlit run app.py --server.port=$PORT
api: uvicorn api:app --host 0.0.0.0 --port=8000
```

## Variables de Entorno

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

## Seguridad

### Recomendaciones para Producción

1. **Autenticación**: Implementar JWT tokens
2. **CORS**: Especificar orígenes permitidos
3. **Rate Limiting**: Limitar requests por IP
4. **HTTPS**: Usar certificados SSL
5. **Validación**: Validar todos los inputs

## Soporte

Para más información, consulta la documentación interactiva en `/docs` después de ejecutar la API.
