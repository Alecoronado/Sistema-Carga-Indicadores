# Railway Deployment Guide - Sistema de Indicadores

## Arquitectura en Railway

El sistema se despliega con **2 servicios separados** que comparten la misma base de datos PostgreSQL:

1. **Servicio Streamlit** (Puerto dinámico $PORT)
2. **Servicio API FastAPI** (Puerto dinámico $PORT)
3. **Base de datos PostgreSQL** (compartida)

## Opción 1: Dos Servicios Separados (Recomendado)

### Paso 1: Crear Servicio para Streamlit

1. En Railway, crea un nuevo servicio desde tu repositorio
2. Configura las variables de entorno:
   ```
   DATABASE_URL=<tu_postgresql_url>
   ```
3. Railway detectará automáticamente el `Procfile` para Streamlit

### Paso 2: Crear Servicio para API

1. Crea otro servicio desde el **mismo repositorio**
2. Configura las mismas variables de entorno:
   ```
   DATABASE_URL=<tu_postgresql_url>
   ```
3. En **Settings → Deploy**, cambia el **Start Command** a:
   ```
   uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

### Paso 3: Configurar CORS en la API

Una vez desplegada la API, actualiza el archivo `api.py` con el dominio de Streamlit:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-app-streamlit.up.railway.app",
        "http://localhost:8501"  # Para desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Opción 2: Archivo railway.toml (Alternativa)

Si prefieres usar `railway.toml` para configuración:

### Para Servicio Streamlit

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Para Servicio API

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port=$PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## Variables de Entorno Requeridas

Ambos servicios necesitan:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

Railway proporciona esta variable automáticamente si usas PostgreSQL de Railway.

## URLs Resultantes

Después del deployment tendrás:

- **Streamlit App**: `https://tu-app-streamlit.up.railway.app`
- **API REST**: `https://tu-api.up.railway.app`
- **API Docs**: `https://tu-api.up.railway.app/docs`

## Verificación Post-Deployment

### 1. Verificar API

```bash
curl https://tu-api.up.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T...",
  "database": "connected"
}
```

### 2. Verificar Endpoints

```bash
# Obtener estadísticas
curl https://tu-api.up.railway.app/api/dashboard/stats

# Listar indicadores
curl https://tu-api.up.railway.app/api/indicadores
```

### 3. Verificar Streamlit

Accede a `https://tu-app-streamlit.up.railway.app` y verifica que:
- ✅ Dashboard carga correctamente
- ✅ Datos se muestran desde PostgreSQL
- ✅ Todas las páginas funcionan

## Migraciones en Producción

Antes de usar la aplicación en producción, ejecuta las migraciones:

### Opción A: Desde Railway CLI

```bash
railway run python migration_add_responsable_to_hitos.py
railway run python migration_add_actividades_and_avance_mensual.py
```

### Opción B: Desde Conexión Directa

1. Obtén el `DATABASE_URL` de Railway
2. Ejecuta localmente:
   ```bash
   export DATABASE_URL="postgresql://..."
   python migration_add_responsable_to_hitos.py
   python migration_add_actividades_and_avance_mensual.py
   ```

## Monitoreo

### Logs de Streamlit
```bash
railway logs --service streamlit-service
```

### Logs de API
```bash
railway logs --service api-service
```

## Troubleshooting

### Error: "Port already in use"
- Railway asigna automáticamente `$PORT`
- Asegúrate de usar `--port $PORT` en los comandos

### Error: "Database connection failed"
- Verifica que `DATABASE_URL` esté configurada
- Confirma que PostgreSQL esté activo en Railway

### Error: CORS
- Actualiza `allow_origins` en `api.py` con el dominio correcto
- Redeploy el servicio API

## Costos Estimados

Railway ofrece:
- **Plan Free**: $5 de crédito mensual
- **Plan Developer**: $5/mes + uso

Con 2 servicios + PostgreSQL:
- Estimado: ~$10-15/mes en plan Developer

## Alternativa: Un Solo Servicio con Nginx

Si prefieres un solo servicio, puedes usar Nginx como reverse proxy:

```nginx
server {
    location / {
        proxy_pass http://localhost:8501;  # Streamlit
    }
    
    location /api {
        proxy_pass http://localhost:8000;  # FastAPI
    }
}
```

Pero la opción de 2 servicios separados es más simple y escalable.

## Próximos Pasos

1. ✅ Crear servicio Streamlit en Railway
2. ✅ Crear servicio API en Railway
3. ✅ Configurar variables de entorno
4. ✅ Ejecutar migraciones
5. ✅ Actualizar CORS con dominios de producción
6. ✅ Probar todos los endpoints
