# Sistema de Indicadores e Hitos

[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-blueviolet)](https://railway.app)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)](https://postgresql.org)

Sistema moderno de seguimiento de indicadores e hitos con interfaz web intuitiva y base de datos robusta.

## 🚀 Deployment Rápido

### Opción 1: Railway (Recomendado para Producción)

1. Haz fork de este repositorio
2. Crea cuenta en [Railway](https://railway.app)
3. Click en "Deploy from GitHub"
4. Agrega PostgreSQL database
5. ¡Listo! Tu app estará en línea

📖 **[Guía Completa de Deployment](DEPLOYMENT.md)**

### Opción 2: Local (Desarrollo)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-indicadores-streamlit.git
cd sistema-indicadores-streamlit

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## ✨ Características

- 📊 **Dashboard Interactivo** - Métricas en tiempo real y visualización de datos
- ➕ **Creación Intuitiva** - Formularios organizados por secciones
- 🔄 **Actualización Simple** - Slider para ajustar progreso
- 💾 **Persistencia Robusta** - PostgreSQL en producción, SQLite en desarrollo
- 🎨 **Diseño Moderno** - UI tipo card con jerarquía visual clara
- 🔐 **Listo para Producción** - Configurado para Railway deployment

## 📋 Campos Soportados

El sistema maneja **18+ campos** por indicador:

- ID Estratégico
- Año
- Indicador
- Unidad Organizacional
- Unidad Organizacional Colaboradora
- Área
- Lineamientos Estratégicos
- Meta
- Medida
- Avance (valor numérico)
- Avance % (porcentaje)
- Estado (automático según avance)
- Fecha Inicio
- Fecha Fin Original
- Fecha Fin Actual
- Fecha Carga
- Tipo Indicador
- Hitos/Etapas

## 🛠️ Stack Tecnológico

- **Frontend/Backend**: Streamlit
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Deployment**: Railway
- **Lenguaje**: Python 3.8+

## 📁 Estructura del Proyecto

```
sistema-indicadores-streamlit/
├── app.py                  # Aplicación principal
├── database.py             # Capa de base de datos (dual: SQLite/PostgreSQL)
├── styles.py               # Estilos CSS personalizados
├── requirements.txt        # Dependencias Python
├── Procfile               # Configuración Railway
├── railway.json           # Settings de deployment
├── .streamlit/
│   └── config.toml        # Configuración Streamlit
├── DEPLOYMENT.md          # Guía de deployment
└── README.md              # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

El sistema detecta automáticamente el entorno:

- **Desarrollo**: Sin `DATABASE_URL` → usa SQLite
- **Producción**: Con `DATABASE_URL` → usa PostgreSQL

Railway configura `DATABASE_URL` automáticamente al agregar PostgreSQL.

### Desarrollo Local con PostgreSQL (Opcional)

```bash
# Crear archivo .env
cp .env.example .env

# Editar .env y agregar tu connection string
DATABASE_URL=postgresql://user:password@localhost:5432/indicadores
```

## 📊 Integración con Power BI

El sistema está diseñado para integrarse fácilmente con Power BI:

1. **Conexión Directa**: Power BI → PostgreSQL
2. **Export Manual**: Agregar funcionalidad de export a CSV/Excel
3. **API REST**: Crear endpoints para consultas (futuro)

## 🎯 Roadmap

- [ ] Autenticación de usuarios
- [ ] Roles y permisos
- [ ] Export a Excel/CSV
- [ ] Gráficos avanzados
- [ ] API REST
- [ ] Notificaciones por email
- [ ] Adjuntar archivos
- [ ] Historial de cambios

## 📝 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

## 🤝 Contribuir

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📞 Soporte

Para preguntas o problemas:

1. Revisa [DEPLOYMENT.md](DEPLOYMENT.md) para guías de deployment
2. Consulta la documentación de [Streamlit](https://docs.streamlit.io)
3. Revisa los [issues](https://github.com/tu-usuario/sistema-indicadores-streamlit/issues) existentes

---

**Versión**: 2.0.0 (Railway-ready)  
**Última actualización**: Febrero 2026
