# 🚀 INSTRUCCIONES PARA DESPLEGAR API EN RAILWAY

## ✅ Paso 1: Código Listo
Tu código ya está en Git con todos los archivos de la API.

## 📝 Paso 2: Ir a Railway

1. Abre tu navegador y ve a: **https://railway.app**
2. Inicia sesión con tu cuenta
3. Abre tu proyecto existente (donde ya tienes Streamlit y PostgreSQL)

## ➕ Paso 3: Crear Nuevo Servicio para la API

1. En tu proyecto de Railway, haz clic en **"+ New"**
2. Selecciona **"GitHub Repo"**
3. Busca y selecciona tu repositorio: **"Streamlit-Sistema Indicadores"**
4. Railway creará un nuevo servicio

## ⚙️ Paso 4: Configurar el Servicio API

### A. Renombrar el Servicio (Opcional pero recomendado)
1. Haz clic en el nuevo servicio
2. En la parte superior, haz clic en el nombre
3. Cámbialo a: **"api"** o **"backend-api"**

### B. Configurar Variables de Entorno
1. En el servicio API, ve a la pestaña **"Variables"**
2. Haz clic en **"+ New Variable"**
3. Agrega:
   ```
   Variable: DATABASE_URL
   Value: ${{Postgres.DATABASE_URL}}
   ```
   (Railway auto-completará la referencia a tu PostgreSQL)

### C. Configurar Start Command
1. Ve a **"Settings"** (⚙️ en la parte superior)
2. Busca la sección **"Deploy"**
3. En **"Start Command"**, ingresa:
   ```
   uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
4. Haz clic en **"Save"** o presiona Enter

## 🚀 Paso 5: Deploy Automático

Railway detectará los cambios y comenzará a desplegar automáticamente.

Verás:
- ⏳ Building...
- ⏳ Deploying...
- ✅ Success!

## 🌐 Paso 6: Obtener la URL de tu API

1. En el servicio API, ve a **"Settings"**
2. Busca la sección **"Networking"**
3. Haz clic en **"Generate Domain"**
4. Railway generará una URL como: `https://backend-api-production-xxxx.up.railway.app`

**¡Guarda esta URL! La necesitarás.**

## 🔍 Paso 7: Verificar que Funciona

Abre en tu navegador:

```
https://tu-api-url.up.railway.app/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T...",
  "database": "connected"
}
```

## 📚 Paso 8: Ver la Documentación

Abre:
```
https://tu-api-url.up.railway.app/docs
```

Verás la interfaz Swagger con todos tus endpoints.

## 🔄 Paso 9: Ejecutar Migraciones (IMPORTANTE)

Necesitas ejecutar las migraciones en la base de datos de producción.

### Opción A: Desde Railway CLI (Recomendado)

```bash
# Instalar Railway CLI si no lo tienes
npm i -g @railway/cli

# Vincular tu proyecto
railway link

# Ejecutar migraciones
railway run python migration_add_responsable_to_hitos.py
railway run python migration_add_actividades_and_avance_mensual.py
```

### Opción B: Desde tu computadora con DATABASE_URL

1. En Railway, copia el `DATABASE_URL` de tu PostgreSQL
2. En tu terminal local:

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://postgres:..."
python migration_add_responsable_to_hitos.py
python migration_add_actividades_and_avance_mensual.py

# Windows CMD
set DATABASE_URL=postgresql://postgres:...
python migration_add_responsable_to_hitos.py
python migration_add_actividades_and_avance_mensual.py
```

## 🔒 Paso 10: Actualizar CORS (IMPORTANTE)

Ahora que tienes la URL de producción, necesitas actualizar el CORS en tu API.

1. Abre el archivo `api.py` en tu editor
2. Busca la línea ~30 donde dice `allow_origins`
3. Actualízala con tu URL de Streamlit en producción:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-streamlit-app.up.railway.app",  # ← Tu Streamlit en Railway
        "http://localhost:8501",  # Para desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

4. Guarda el archivo
5. Haz commit y push:

```bash
git add api.py
git commit -m "Update CORS for production"
git push origin main
```

Railway re-desplegará automáticamente.

## ✅ Paso 11: Verificación Final

### 1. Health Check
```bash
curl https://tu-api-url.up.railway.app/health
```

### 2. Obtener Estadísticas
```bash
curl https://tu-api-url.up.railway.app/api/dashboard/stats
```

### 3. Ver Documentación
Abre: `https://tu-api-url.up.railway.app/docs`

## 🎉 ¡Listo!

Ahora tienes:

1. **Streamlit App**: `https://tu-streamlit.up.railway.app`
   - Interfaz de usuario

2. **API REST**: `https://tu-api.up.railway.app`
   - Backend con endpoints REST
   - Documentación en `/docs`

3. **PostgreSQL**: Base de datos compartida

## 📊 Monitorear tu API

Ver logs en tiempo real:
1. En Railway, haz clic en tu servicio API
2. Ve a la pestaña **"Deployments"**
3. Haz clic en el deployment activo
4. Verás los logs en tiempo real

## ⚠️ Troubleshooting

### Error: "Application failed to respond"
- Verifica que el Start Command sea correcto
- Revisa los logs en Railway

### Error: "Database connection failed"
- Verifica que `DATABASE_URL` esté configurada
- Asegúrate de que PostgreSQL esté corriendo

### Error: CORS en el frontend
- Actualiza `allow_origins` en `api.py` con el dominio correcto
- Haz push de los cambios

## 💡 Consejos

- Los logs son tu mejor amigo para debugging
- Puedes ver métricas de uso en Railway
- El plan gratuito tiene $5 de crédito mensual
- Considera el plan Developer ($5/mes) para proyectos serios

## 📞 Soporte

Si algo no funciona:
1. Revisa los logs en Railway
2. Verifica que todas las variables de entorno estén configuradas
3. Asegúrate de que las migraciones se ejecutaron correctamente
