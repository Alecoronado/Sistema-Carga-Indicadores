# 🚨 SOLUCIÓN: App no se ve en Railway

## Problema
Cuando entras a la URL de Railway, la aplicación no se ve funcionando, pero localmente sí funciona.

## ✅ Soluciones Implementadas

### 1. Archivo de Configuración Streamlit
**Creado**: `.streamlit/config.toml`

Este archivo es **CRÍTICO** para que Streamlit funcione en Railway. Configura:
- Modo headless (sin interfaz gráfica)
- Puerto correcto
- Dirección del servidor
- Tema personalizado

### 2. Archivo .gitignore
**Creado**: `.gitignore`

Evita subir archivos innecesarios como la base de datos local SQLite.

---

## 🔧 Pasos para Desplegar en Railway

### Paso 1: Verificar Archivos Necesarios

Asegúrate de que tienes estos archivos en tu proyecto:

```
✅ app.py
✅ database.py
✅ styles.py
✅ requirements.txt
✅ Procfile
✅ railway.json
✅ .streamlit/config.toml  ← NUEVO
✅ .gitignore              ← NUEVO
```

### Paso 2: Subir Cambios a GitHub

```bash
# Navegar a tu proyecto
cd "C:\Users\PERSONAL\Downloads\Streamlit-Sistema Indicadores"

# Agregar los nuevos archivos
git add .streamlit/config.toml
git add .gitignore
git add -A

# Hacer commit
git commit -m "Fix: Agregar configuración de Streamlit para Railway"

# Subir a GitHub
git push origin main
```

### Paso 3: Verificar en Railway

1. **Ve a tu proyecto en Railway**
2. **Espera el deploy automático** (2-5 minutos)
3. **Revisa los logs** en la pestaña "Deployments"

### Paso 4: Verificar PostgreSQL

1. En Railway, verifica que tienes **PostgreSQL agregado**
2. Ve a tu servicio de PostgreSQL
3. Verifica que la variable `DATABASE_URL` esté configurada
4. Railway debería conectar automáticamente tu app con PostgreSQL

---

## 🔍 Diagnóstico de Problemas Comunes

### Problema 1: "Application Error" o página en blanco

**Causa**: Falta `.streamlit/config.toml`  
**Solución**: ✅ Ya creado

### Problema 2: "Module not found"

**Causa**: Falta alguna dependencia en `requirements.txt`  
**Solución**: Verifica que `requirements.txt` tenga:

```txt
streamlit>=1.30.0
pandas>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

### Problema 3: "Database connection failed"

**Causa**: PostgreSQL no está configurado o `DATABASE_URL` no existe  
**Solución**:
1. En Railway, click "+ New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway creará automáticamente `DATABASE_URL`

### Problema 4: La app se carga pero no guarda datos

**Causa**: Usando SQLite en lugar de PostgreSQL  
**Solución**: Verifica en los logs que diga:
```
🐘 Using PostgreSQL database
```

Si dice:
```
💾 Using SQLite database
```

Entonces PostgreSQL no está configurado correctamente.

---

## 📊 Verificar que Todo Funciona

### 1. Revisar Logs en Railway

```
# Deberías ver:
🐘 Using PostgreSQL database
You can now view your Streamlit app in your browser.
```

### 2. Probar la Aplicación

1. Abre la URL de Railway
2. Deberías ver el Dashboard de Indicadores
3. Intenta crear un indicador de prueba
4. Recarga la página (F5)
5. El indicador debería seguir ahí ✅

---

## 🚀 Comandos Rápidos

### Ver logs en tiempo real (opcional)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

### Forzar nuevo deploy

```bash
git commit --allow-empty -m "Trigger deploy"
git push origin main
```

---

## 📞 Si Aún No Funciona

### Opción 1: Revisar Logs Detallados

1. En Railway → Tu servicio → "Deployments"
2. Click en el deployment más reciente
3. Ve a "View Logs"
4. Busca mensajes de error en rojo

### Opción 2: Verificar Variables de Entorno

1. En Railway → Tu servicio → "Variables"
2. Deberías ver `DATABASE_URL` (creada automáticamente por PostgreSQL)
3. Si no existe, significa que PostgreSQL no está conectado

### Opción 3: Recrear el Servicio

Si nada funciona:
1. En Railway, elimina el servicio de Streamlit (NO PostgreSQL)
2. Click "+ New" → "GitHub Repo"
3. Selecciona tu repositorio de nuevo
4. Railway detectará automáticamente la configuración

---

## ✅ Checklist Final

Antes de hacer push a GitHub, verifica:

- [ ] `.streamlit/config.toml` existe
- [ ] `.gitignore` existe
- [ ] `Procfile` tiene: `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
- [ ] `requirements.txt` tiene todas las dependencias
- [ ] PostgreSQL está agregado en Railway
- [ ] Has hecho commit y push de los nuevos archivos

---

## 🎉 Resultado Esperado

Después de seguir estos pasos:

1. ✅ La URL de Railway carga correctamente
2. ✅ Ves el Dashboard de Indicadores
3. ✅ Puedes crear y actualizar indicadores
4. ✅ Los datos persisten después de recargar
5. ✅ Los logs muestran "🐘 Using PostgreSQL database"

---

**Última actualización**: Febrero 2026  
**Versión**: 2.1.0 (Railway-ready con config.toml)
