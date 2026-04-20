# 🚀 EJECUTAR MIGRACIÓN EN RAILWAY - INSTRUCCIONES SIMPLES

## ✅ Migración Consolidada Creada

He creado `migration_completa.py` que hace TODO en un solo script:
- ✅ Agrega columna `responsable` a `hitos`
- ✅ Crea tabla `actividades`
- ✅ Crea tabla `avance_mensual`
- ✅ Migra datos existentes
- ✅ Agrega columna `tiene_actividades` a `indicadores`

## 📋 PASOS PARA EJECUTAR EN RAILWAY

### Paso 1: Obtener DATABASE_URL

1. Ve a https://railway.app
2. Abre tu proyecto
3. Haz clic en **Postgres**
4. Ve a **Variables**
5. Copia el valor completo de `DATABASE_URL`

### Paso 2: Ejecutar Migración

Abre PowerShell en tu proyecto y ejecuta:

```powershell
# Activar entorno virtual
.venv\Scripts\activate

# Configurar DATABASE_URL (pega tu URL aquí)
$env:DATABASE_URL="postgresql://postgres:TU_PASSWORD@containers-us-west-XXX.railway.app:XXXX/railway"

# Ejecutar migración completa
python migration_completa.py
```

### Paso 3: Verificar

Deberías ver:

```
✅ MIGRACIÓN POSTGRESQL COMPLETADA EXITOSAMENTE

Tablas creadas/actualizadas:
  ✅ indicadores (con tiene_actividades)
  ✅ hitos (con responsable)
  ✅ actividades
  ✅ avance_mensual
```

## 🎯 Resultado Final

Tu PostgreSQL en Railway tendrá:

1. **indicadores** - Tabla principal con columna `tiene_actividades`
2. **hitos** - Con columna `responsable`
3. **actividades** - Nueva tabla para actividades de hitos
4. **avance_mensual** - Nueva tabla para reportes mensuales

## 💡 Ventajas de esta Migración

- ✅ **Segura**: Verifica si cada cambio ya existe antes de aplicarlo
- ✅ **Idempotente**: Puedes ejecutarla múltiples veces sin problemas
- ✅ **Completa**: Hace todas las migraciones en un solo paso
- ✅ **Migra datos**: Preserva los datos existentes de avance

## ⚠️ Importante

- Esta migración es **segura** y **no borra datos**
- Si una tabla/columna ya existe, simplemente la omite
- Migra automáticamente los datos de avance existentes

## 🔍 Verificar en Railway

Después de ejecutar, puedes verificar en Railway:
1. Ve a tu servicio Postgres
2. Haz clic en **Data**
3. Verás las 4 tablas listadas
