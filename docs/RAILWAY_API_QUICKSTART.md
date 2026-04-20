# Guía Rápida: Desplegar API en Railway

## 🎯 Objetivo
Desplegar la API FastAPI como un servicio separado en Railway con su propio dominio.

## 📋 Pre-requisitos
- ✅ Código de la API en el repositorio (api.py, schemas.py)
- ✅ requirements.txt actualizado con FastAPI
- ✅ PostgreSQL ya desplegado en Railway

## 🚀 Pasos para Deployment

### 1. Subir Cambios a Git

```bash
git add .
git commit -m "Add FastAPI REST API"
git push origin main
```

### 2. Crear Nuevo Servicio en Railway

1. Ve a tu proyecto en Railway: https://railway.app
2. Click en **"+ New Service"**
3. Selecciona **"GitHub Repo"**
4. Elige tu repositorio: `Streamlit-Sistema Indicadores`
5. Railway creará un nuevo servicio

### 3. Configurar el Servicio API

#### A. Variables de Entorno

En el nuevo servicio, ve a **Variables** y agrega:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

(Railway auto-completa la referencia a tu PostgreSQL existente)

#### B. Configurar Start Command

Ve a **Settings → Deploy → Start Command** y configura:

```
uvicorn api:app --host 0.0.0.0 --port $PORT
```

#### C. Configurar Root Directory (Opcional)

Si tu código está en la raíz, déjalo vacío. Si está en una subcarpeta, especifícala.

### 4. Deploy

Railway automáticamente:
1. Detectará los cambios
2. Instalará dependencias de `requirements.txt`
3. Ejecutará el comando de inicio
4. Asignará un dominio público

### 5. Obtener URL de la API

Una vez desplegado:
1. Ve a **Settings → Networking**
2. Verás tu dominio: `https://tu-api-nombre.up.railway.app`
3. También puedes configurar un **dominio personalizado**

### 6. Verificar Deployment

Abre en tu navegador:

```
https://tu-api-nombre.up.railway.app/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "database": "connected"
}
```

### 7. Acceder a la Documentación

```
https://tu-api-nombre.up.railway.app/docs
```

### 8. Ejecutar Migraciones

Desde Railway CLI o localmente con la DATABASE_URL de producción:

```bash
# Opción 1: Railway CLI
railway link
railway run python migration_add_responsable_to_hitos.py
railway run python migration_add_actividades_and_avance_mensual.py

# Opción 2: Local con DATABASE_URL
export DATABASE_URL="postgresql://..."
python migration_add_responsable_to_hitos.py
python migration_add_actividades_and_avance_mensual.py
```

### 9. Actualizar CORS (Importante)

Edita `api.py` línea ~30:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-app-streamlit.up.railway.app",  # Tu Streamlit en producción
        "http://localhost:8501",  # Para desarrollo local
        "http://localhost:3000",  # Si usas otro frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Luego:
```bash
git add api.py
git commit -m "Update CORS for production"
git push
```

Railway re-desplegará automáticamente.

## 🎉 Resultado Final

Tendrás 2 servicios independientes:

1. **Streamlit App**: `https://tu-streamlit.up.railway.app`
   - Interfaz de usuario
   - Puerto: $PORT (asignado por Railway)

2. **API REST**: `https://tu-api.up.railway.app`
   - Endpoints REST
   - Puerto: $PORT (asignado por Railway)
   - Docs: `/docs`

Ambos conectados a la misma PostgreSQL.

## 🔍 Verificación

### Health Check
```bash
curl https://tu-api.up.railway.app/health
```

### Obtener Indicadores
```bash
curl https://tu-api.up.railway.app/api/indicadores
```

### Ver Documentación
Abre: `https://tu-api.up.railway.app/docs`

## 📊 Monitoreo

Ver logs en tiempo real:
```bash
railway logs --service <nombre-servicio-api>
```

## 💰 Costos

- **Free Tier**: $5 de crédito mensual
- **Developer Plan**: $5/mes + uso
- Estimado con 2 servicios + PostgreSQL: ~$10-15/mes

## ⚠️ Troubleshooting

### Error: "Application startup failed"
- Verifica que `DATABASE_URL` esté configurada
- Revisa logs: `railway logs`

### Error: CORS
- Asegúrate de actualizar `allow_origins` con el dominio correcto

### Error: "Module not found"
- Verifica que `requirements.txt` tenga todas las dependencias
- Redeploy: `railway up`

## 📝 Comandos Útiles

```bash
# Ver servicios
railway status

# Ver logs
railway logs

# Conectar a PostgreSQL
railway connect postgres

# Redeploy
railway up
```

## ✅ Checklist Final

- [ ] Código subido a Git
- [ ] Servicio API creado en Railway
- [ ] DATABASE_URL configurada
- [ ] Start command configurado
- [ ] Migraciones ejecutadas
- [ ] CORS actualizado
- [ ] Health check funciona
- [ ] Documentación accesible en /docs
