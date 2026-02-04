# 🚀 Guía de Deployment en Railway

## Resumen

Esta guía te llevará paso a paso para desplegar tu Sistema de Indicadores en Railway con PostgreSQL.

---

## 📋 Pre-requisitos

- [ ] Cuenta de GitHub (gratis)
- [ ] Cuenta de Railway (gratis - $5 crédito mensual)
- [ ] Git instalado en tu computadora

---

## Paso 1: Preparar Repositorio GitHub

### 1.1 Inicializar Git (si aún no lo has hecho)

```bash
cd "C:\Users\PERSONAL\Downloads\Streamlit-Sistema Indicadores"
git init
git add .
git commit -m "Initial commit - Sistema de Indicadores"
```

### 1.2 Crear Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Click en "+" → "New repository"
3. Nombre: `sistema-indicadores-streamlit`
4. Descripción: "Sistema de seguimiento de indicadores e hitos"
5. **Importante**: Deja el repositorio como **Privado** (para proteger tus datos)
6. NO inicialices con README (ya tienes uno)
7. Click "Create repository"

### 1.3 Conectar y Subir Código

```bash
git remote add origin https://github.com/TU-USUARIO/sistema-indicadores-streamlit.git
git branch -M main
git push -u origin main
```

> **Nota**: Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub

---

## Paso 2: Configurar Railway

### 2.1 Crear Cuenta en Railway

1. Ve a [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Inicia sesión con GitHub (recomendado)

### 2.2 Crear Nuevo Proyecto

1. Click "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Autoriza Railway para acceder a tus repositorios
4. Selecciona `sistema-indicadores-streamlit`

### 2.3 Agregar Base de Datos PostgreSQL

1. En tu proyecto de Railway, click "+ New"
2. Selecciona "Database"
3. Selecciona "Add PostgreSQL"
4. Railway creará automáticamente la base de datos

**Railway automáticamente:**
- Crea la variable `DATABASE_URL`
- La conecta con tu aplicación
- Configura el networking

---

## Paso 3: Configurar Variables de Entorno

Railway ya configuró `DATABASE_URL` automáticamente. Si necesitas agregar más variables:

1. Click en tu servicio de Streamlit
2. Ve a "Variables"
3. Agrega cualquier variable adicional que necesites

---

## Paso 4: Deploy

### 4.1 Deploy Automático

Railway detectará automáticamente:
- ✅ `requirements.txt` - Instalará dependencias
- ✅ `Procfile` - Sabrá cómo ejecutar la app
- ✅ `railway.json` - Configuración de build

El deploy iniciará automáticamente.

### 4.2 Monitorear Deploy

1. Ve a la pestaña "Deployments"
2. Verás el progreso en tiempo real
3. Espera a que diga "Success" (puede tomar 2-5 minutos)

### 4.3 Ver Logs

Si hay algún error:
1. Click en el deployment
2. Ve a "View Logs"
3. Revisa los mensajes de error

---

## Paso 5: Acceder a tu Aplicación

### 5.1 Obtener URL

1. En Railway, click en tu servicio de Streamlit
2. Ve a "Settings"
3. En "Domains", click "Generate Domain"
4. Railway te dará una URL como: `tu-app.up.railway.app`

### 5.2 Probar la Aplicación

1. Abre la URL en tu navegador
2. Deberías ver el dashboard de indicadores
3. Verás el mensaje: "🐘 Using PostgreSQL database" en los logs

---

## Paso 6: Verificar Funcionamiento

### 6.1 Crear Indicador de Prueba

1. Ve a "➕ Crear Indicador"
2. Llena el formulario con datos de prueba
3. Click "✅ Crear Indicador"
4. Verifica que aparezca el mensaje de éxito

### 6.2 Verificar Persistencia

1. Recarga la página (F5)
2. Ve al Dashboard
3. Verifica que el indicador sigue ahí
4. Los datos ahora están en PostgreSQL ✅

---

## 🎯 Configuración Opcional

### Dominio Personalizado

1. En Railway → Settings → Domains
2. Click "Custom Domain"
3. Ingresa tu dominio (ej: `indicadores.tuempresa.com`)
4. Configura el DNS según las instrucciones

### Configurar Backups Automáticos

Railway hace backups automáticos de PostgreSQL, pero puedes configurar:

1. Click en tu base de datos PostgreSQL
2. Ve a "Settings"
3. Configura "Backup Schedule" si está disponible

---

## 📊 Costos Estimados

### Plan Hobby (Recomendado para empezar)

- **Crédito Gratis**: $5/mes
- **PostgreSQL**: ~$5/mes
- **Streamlit App**: ~$5/mes (basado en uso)
- **Total**: ~$10/mes ($5 gratis + $5 a pagar)

### Uso Real

Si tu aplicación tiene poco tráfico:
- Puedes quedarte dentro del crédito gratis
- Solo pagas por lo que usas

---

## 🔧 Troubleshooting

### Error: "Application failed to start"

**Solución:**
1. Revisa los logs en Railway
2. Verifica que `requirements.txt` tenga todas las dependencias
3. Asegúrate que `Procfile` esté en la raíz del proyecto

### Error: "Database connection failed"

**Solución:**
1. Verifica que PostgreSQL esté corriendo en Railway
2. Chequea que `DATABASE_URL` esté configurada
3. Revisa los logs para ver el error específico

### La aplicación se ve diferente

**Solución:**
1. Verifica que `.streamlit/config.toml` esté incluido
2. Asegúrate que `styles.py` esté en el repositorio
3. Haz un nuevo deploy

### Cambios no se reflejan

**Solución:**
```bash
git add .
git commit -m "Descripción de cambios"
git push
```
Railway detectará el push y hará deploy automático.

---

## 🔄 Workflow de Desarrollo

### Desarrollo Local

1. Trabaja localmente con SQLite
2. Prueba tus cambios
3. Commit y push a GitHub

### Deploy Automático

1. Railway detecta el push
2. Hace build automático
3. Deploy a producción
4. Usa PostgreSQL automáticamente

---

## 📝 Comandos Útiles

### Ver logs en tiempo real
```bash
# Instala Railway CLI (opcional)
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

### Conectarse a PostgreSQL (opcional)

Railway te da las credenciales en la pestaña "Connect":

```bash
psql postgresql://usuario:password@host:puerto/database
```

---

## 🎓 Próximos Pasos

Una vez desplegado exitosamente:

1. **Configurar usuarios**: Agregar autenticación
2. **Backups**: Configurar exportación automática
3. **Monitoreo**: Configurar alertas
4. **Optimización**: Revisar performance
5. **Documentación**: Crear guía para usuarios finales

---

## 📞 Soporte

### Railway
- Documentación: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)

### Streamlit
- Documentación: [docs.streamlit.io](https://docs.streamlit.io)
- Forum: [discuss.streamlit.io](https://discuss.streamlit.io)

---

## ✅ Checklist Final

Antes de considerar el deployment completo:

- [ ] Aplicación accesible vía URL de Railway
- [ ] Base de datos PostgreSQL funcionando
- [ ] Crear indicador de prueba exitoso
- [ ] Datos persisten después de reload
- [ ] Actualizar avance funciona correctamente
- [ ] Dashboard muestra métricas correctas
- [ ] No hay errores en los logs

---

## 🎉 ¡Felicidades!

Tu Sistema de Indicadores ahora está en producción y accesible desde cualquier lugar del mundo.

**URL de tu aplicación**: `https://tu-app.up.railway.app`

Comparte esta URL con tu equipo para que empiecen a usarla.
