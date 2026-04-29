"""
Sistema de Indicadores e Hitos - Role-Based Version
Modern web-based indicator and milestone tracking system with strict role separation
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import Database
from src.styles import get_custom_css, get_status_badge, get_progress_bar

# Page configuration
st.set_page_config(
    page_title="Sistema de Indicadores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Catálogos de Opciones
# =========================
LINEAMIENTOS_ESTRATEGICOS = [
    "Alineamiento Estratégico",
    "Complementariedad",
    "Eficiencia Operacional",
    "Excelencia Operacional",
    "Solidez Financiera"
]

TIPOS_INDICADOR = [
    "Estratégico",
    "Regular"
]

AREAS = [
    "Efectividad en el Desarrollo",
    "Programacion Financiera y Reporting",
    "Alianzas Estratégicas"
]

UNIDADES_ORGANIZACIONALES = [
    "VPO",
    "VPD",
    "VPE",
    "PRE",
    "VPF",
    "Ninguna"

]

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize database
db = Database()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'


# ==================== DASHBOARD ====================

def render_dashboard():
    """Render the main dashboard with metrics and data table"""
    st.title("📊 Dashboard de Indicadores")
    
    # Get summary statistics
    stats = db.get_summary_stats()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Indicadores",
            value=stats['total'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="🔵 Por Comenzar",
            value=stats['por_comenzar'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="🟡 En Progreso",
            value=stats['en_progreso'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="🟢 Completados",
            value=stats['completado'],
            delta=None
        )
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filtros")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        areas = ["Todos"] + db.get_unique_values('area')
        selected_area = st.selectbox("Área", areas)
    
    with col2:
        años = ["Todos"] + [str(y) for y in db.get_unique_values('año')]
        selected_año = st.selectbox("Año", años)
    
    with col3:
        unidades = ["Todos"] + db.get_unique_values('unidad_organizacional')
        selected_unidad = st.selectbox("Unidad Organizacional", unidades)
    
    with col4:
        tipos = ["Todos"] + db.get_unique_values('tipo_indicador')
        selected_tipo = st.selectbox("Tipo Indicador", tipos)
    
    with col5:
        responsables = ["Todos"] + db.get_unique_values('responsable')
        selected_responsable = st.selectbox("Responsable", responsables)
    
    # Apply filters
    filter_area = None if selected_area == "Todos" else selected_area
    filter_año = None if selected_año == "Todos" else int(selected_año)
    filter_unidad = None if selected_unidad == "Todos" else selected_unidad
    filter_tipo = None if selected_tipo == "Todos" else selected_tipo
    filter_responsable = None if selected_responsable == "Todos" else selected_responsable
    
    # Get filtered data
    df = db.get_all_indicadores(
        area=filter_area,
        año=filter_año,
        unidad_organizacional=filter_unidad,
        tipo_indicador=filter_tipo
    )
    
    # Apply responsable filter manually
    if filter_responsable:
        df = df[df['responsable'] == filter_responsable]
    
    st.markdown("---")
    
    # Display data table
    if len(df) > 0:
        st.subheader(f"📋 Indicadores ({len(df)} registros)")
        
        # Format dataframe for display
        display_columns = ['id', 'id_estrategico', 'indicador', 'tipo_indicador', 
                          'area', 'unidad_organizacional', 'responsable', 'año', 'estado', 
                          'avance_porcentaje', 'fecha_inicio', 'fecha_fin_actual']
        
        # Only include columns that exist in the dataframe
        available_columns = [col for col in display_columns if col in df.columns]
        display_df = df[available_columns].copy()
        
        # Rename columns for display
        column_names = {
            'id': 'ID',
            'id_estrategico': 'ID Estratégico',
            'indicador': 'Indicador',
            'tipo_indicador': 'Tipo',
            'area': 'Área',
            'unidad_organizacional': 'Unidad Org.',
            'responsable': 'Responsable',
            'año': 'Año',
            'estado': 'Estado',
            'avance_porcentaje': 'Avance %',
            'fecha_inicio': 'Inicio',
            'fecha_fin_actual': 'Fin'
        }
        
        display_df.rename(columns=column_names, inplace=True)
        
        # Convert date columns to datetime
        date_columns = ['Inicio', 'Fin']
        for col in date_columns:
            if col in display_df.columns:
                display_df[col] = pd.to_datetime(display_df[col], errors='coerce')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay indicadores que coincidan con los filtros seleccionados.")


# ==================== ADMIN PAGES ====================

def render_gestion_indicadores_admin():
    """Admin page: Manage indicators structure (NO progress fields)"""
    st.title("🛠️ Gestión de Indicadores (Admin)")
    
    st.info("ℹ️ **Rol Admin**: Aquí defines la estructura de los indicadores. Los avances se reportan en la página 'Actualización Mensual'.")
    
    # Tabs for create and manage
    tab1, tab2 = st.tabs(["➕ Crear Indicador", "📝 Editar/Eliminar"])
    
    with tab1:
        with st.container(border=True):
            st.markdown('### Nuevo Indicador')
            
            with st.form("crear_indicador_form", clear_on_submit=True):
                # Basic Information
                st.markdown("### 📋 Información Básica")
                col1, col2 = st.columns(2)
                
                with col1:
                    id_estrategico = st.text_input(
                        "ID Estratégico",
                        placeholder="Ej: EST-2024-001"
                    )
                    
                    indicador = st.text_input(
                        "Indicador *",
                        placeholder="Ej: Incremento de ventas digitales"
                    )
                    
                    tipo_indicador = st.selectbox(
                        "Tipo Indicador *",
                        options=TIPOS_INDICADOR
                    )
                    
                    año = st.number_input(
                        "Año *",
                        min_value=2020,
                        max_value=2030,
                        value=datetime.now().year,
                        step=1
                    )
                
                with col2:
                    area = st.text_input(
                        "Área",
                        placeholder="Ej: Efectividad en el Desarrollo"
                    )
                    
                    unidad_organizacional = st.selectbox(
                        "Unidad Organizacional",
                        options=["Seleccionar..."] + UNIDADES_ORGANIZACIONALES
                    )
                    
                    unidad_organizacional_colaboradora = st.selectbox(
                        "Unidad Organizacional Colaboradora",
                        options=["Seleccionar..."] + UNIDADES_ORGANIZACIONALES
                    )
                    
                    lineamientos_estrategicos = st.selectbox(
                        "Lineamiento Estratégico *",
                        options=LINEAMIENTOS_ESTRATEGICOS
                    )
                    
                    responsable = st.text_input(
                        "Responsable *",
                        placeholder="Ej: Juan Pérez"
                    )
                
                st.markdown("---")
                
                # Goals and Metrics
                st.markdown("### 🎯 Metas y Medidas")
                col1, col2 = st.columns(2)
                
                with col1:
                    meta = st.text_input(
                        "Meta (Valor Objetivo)",
                        placeholder="Ej: 100",
                        help="Valor objetivo a alcanzar"
                    )
                    
                    medida = st.text_input(
                        "Medida",
                        placeholder="Ej: Porcentaje, Cantidad, Monto"
                    )
                
                with col2:
                    estado = st.selectbox(
                        "Estado Inicial",
                        ["Por comenzar", "En progreso", "Completado"],
                        index=0
                    )
                
                st.markdown("---")
                
                # Dates
                st.markdown("### 📅 Fechas Plan")
                col1, col2 = st.columns(2)
                
                with col1:
                    fecha_inicio = st.date_input(
                        "Fecha Inicio Plan",
                        value=None
                    )
                
                with col2:
                    fecha_fin_original = st.date_input(
                        "Fecha Fin Plan",
                        value=None
                    )
                
                st.markdown("---")
                
                # Additional Information
                st.markdown("### 📝 Estructura del Indicador")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    tiene_hitos = st.checkbox(
                        "¿Tiene Hitos/Etapas?",
                        value=True,
                        help="Marca si este indicador se divide en hitos"
                    )
                    
                    if tiene_hitos:
                        st.caption("ℹ️ Podrás agregar hitos en '🎯 Gestión de Hitos'")
                
                with col2:
                    tiene_actividades = st.checkbox(
                        "¿Tiene Actividades?",
                        value=False,
                        help="Marca si los hitos se dividen en actividades"
                    )
                    
                    if tiene_actividades:
                        st.caption("ℹ️ Podrás agregar actividades en '📋 Gestión de Actividades'")
                
                st.markdown("---")
                
                # Submit button
                submitted = st.form_submit_button("✅ Crear Indicador", use_container_width=True)
                
                if submitted:
                    if not indicador or not tipo_indicador or not lineamientos_estrategicos or not responsable:
                        st.error("❌ Por favor completa los campos obligatorios")
                    else:
                        try:
                            record_id = db.create_indicador(
                                id_estrategico=id_estrategico if id_estrategico else None,
                                año=año,
                                indicador=indicador,
                                unidad_organizacional=unidad_organizacional if unidad_organizacional != "Seleccionar..." else None,
                                unidad_organizacional_colaboradora=unidad_organizacional_colaboradora if unidad_organizacional_colaboradora != "Seleccionar..." else None,
                                area=area if area else None,
                                lineamientos_estrategicos=lineamientos_estrategicos,
                                meta=meta if meta else None,
                                medida=medida if medida else None,
                                estado=estado,
                                fecha_inicio=str(fecha_inicio) if fecha_inicio else None,
                                fecha_fin_original=str(fecha_fin_original) if fecha_fin_original else None,
                                tipo_indicador=tipo_indicador,
                                tiene_hitos=tiene_hitos,
                                tiene_actividades=tiene_actividades,
                                responsable=responsable
                            )
                            st.success(f"✅ Indicador creado exitosamente (ID: {record_id})")
                            if tiene_hitos:
                                st.info("💡 Ahora puedes agregar hitos en '🎯 Gestión de Hitos'")
                            if tiene_actividades:
                                st.info("💡 Podrás agregar actividades en '📋 Gestión de Actividades'")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error al crear el indicador: {str(e)}")
            
            
    
    with tab2:
        # Delete indicator section
        df = db.get_all_indicadores()
        
        if len(df) == 0:
            st.info("No hay indicadores registrados.")
        else:
            with st.container(border=True):
                st.markdown('### Eliminar Indicador')
                
                st.warning("⚠️ Esta acción es permanente y no se puede deshacer.")
                
                options = []
                for _, row in df.iterrows():
                    label = f"[{row.get('tipo_indicador', 'N/A')}] {row.get('indicador', 'Sin nombre')} - {row.get('area', 'Sin área')} ({row.get('año', '')})"
                    options.append((row['id'], label))
                
                selected_id = st.selectbox(
                    "Seleccionar Indicador a Eliminar",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: next(opt[1] for opt in options if opt[0] == x)
                )
                
                if selected_id:
                    indicador = db.get_indicador_by_id(selected_id)
                    
                    if indicador:
                        st.markdown("---")
                        st.markdown("**Detalles:**")
                        st.write(f"- **Indicador:** {indicador.get('indicador', 'N/A')}")
                        st.write(f"- **Responsable:** {indicador.get('responsable', 'N/A')}")
                        st.write(f"- **Avance:** {indicador.get('avance_porcentaje', 0)}%")
                        
                        st.markdown("---")
                        
                        if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                            try:
                                if db.delete_indicador(selected_id):
                                    st.success("✅ Indicador eliminado exitosamente")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar el indicador")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                


def render_gestion_hitos_admin():
    """Admin page: Manage hitos structure (NO progress fields)"""
    st.title("🎯 Gestión de Hitos (Admin)")
    
    st.info("ℹ️ **Rol Admin**: Aquí defines la estructura de los hitos. Los avances se reportan en la página 'Actualización Mensual'.")
    
    # Get indicators with hitos
    df = db.get_all_indicadores()
    df_con_hitos = df[df['tiene_hitos'] == 1] if 'tiene_hitos' in df.columns else df
    
    if len(df_con_hitos) == 0:
        st.warning("⚠️ No hay indicadores con hitos habilitados.")
        return
    
    # Select indicator
    with st.container(border=True):
        st.markdown('### Seleccionar Indicador')
        
        options = []
        for _, row in df_con_hitos.iterrows():
            label = f"[{row.get('tipo_indicador', 'N/A')}] {row.get('indicador', 'Sin nombre')} ({row.get('año', '')})"
            options.append((row['id'], label))
        
        selected_id = st.selectbox(
            "Indicador",
            options=[opt[0] for opt in options],
            format_func=lambda x: next(opt[1] for opt in options if opt[0] == x)
        )
        
        
    
    if selected_id:
        # Get hitos for this indicator
        hitos_df = db.get_hitos_by_indicador(selected_id)
        
        # Show existing hitos
        with st.container(border=True):
            st.markdown('### Hitos Existentes')
            
            if len(hitos_df) > 0:
                for _, hito in hitos_df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{hito['nombre']}**")
                        if hito.get('descripcion'):
                            st.caption(hito['descripcion'])
                        if hito.get('responsable'):
                            st.caption(f"👤 {hito['responsable']}")
                    
                    with col2:
                        st.markdown(get_status_badge(hito['estado']), unsafe_allow_html=True)
                    
                    with col3:
                        # Show latest reported progress
                        ultimo_avance = hito.get('ultimo_avance_reportado', hito.get('avance_porcentaje', 0))
                        st.write(f"Último avance: {ultimo_avance}%")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_hito_{hito['id']}", help="Eliminar hito"):
                            if db.delete_hito(hito['id']):
                                db.update_indicador_from_hitos(selected_id)
                                st.success("Hito eliminado")
                                st.rerun()
                    
                    st.markdown("---")
            else:
                st.info("No hay hitos creados para este indicador.")
            
            
        
        # Create new hito
        with st.container(border=True):
            st.markdown('### ➕ Agregar Nuevo Hito')
            
            with st.form("crear_hito_form"):
                nombre_hito = st.text_input(
                    "Nombre del Hito *",
                    placeholder="Ej: Fase 1 - Planificación"
                )
                
                descripcion_hito = st.text_area(
                    "Descripción",
                    placeholder="Descripción detallada del hito (opcional)",
                    height=80
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fecha_inicio_hito = st.date_input(
                        "Fecha Inicio Plan",
                        value=None
                    )
                    
                    responsable_hito = st.text_input(
                        "Responsable *",
                        placeholder="Ej: María García"
                    )
                
                with col2:
                    fecha_fin_planificada_hito = st.date_input(
                        "Fecha Fin Plan",
                        value=None
                    )
                
                submitted = st.form_submit_button("✅ Agregar Hito", use_container_width=True)
                
                if submitted:
                    if not nombre_hito or not responsable_hito:
                        st.error("❌ El nombre y responsable del hito son obligatorios")
                    else:
                        try:
                            hito_id = db.create_hito(
                                indicador_id=selected_id,
                                nombre=nombre_hito,
                                descripcion=descripcion_hito if descripcion_hito else None,
                                fecha_inicio=str(fecha_inicio_hito) if fecha_inicio_hito else None,
                                fecha_fin_planificada=str(fecha_fin_planificada_hito) if fecha_fin_planificada_hito else None,
                                avance_porcentaje=0,
                                estado="Por comenzar",
                                orden=len(hitos_df) + 1,
                                responsable=responsable_hito
                            )
                            
                            st.success(f"✅ Hito creado exitosamente (ID: {hito_id})")
                            st.info("📊 El responsable podrá reportar avances en 'Actualización Mensual'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al crear el hito: {str(e)}")
            
            


def render_gestion_actividades_admin():
    """Admin page: Manage actividades structure (NO progress fields)"""
    st.title("📋 Gestión de Actividades (Admin)")
    
    st.info("ℹ️ **Rol Admin**: Aquí defines las actividades bajo cada hito. Los avances se reportan en la página 'Actualización Mensual'.")
    
    # Get all hitos
    df_indicadores = db.get_all_indicadores()
    df_con_hitos = df_indicadores[df_indicadores['tiene_hitos'] == 1] if 'tiene_hitos' in df_indicadores.columns else df_indicadores
    
    if len(df_con_hitos) == 0:
        st.warning("⚠️ No hay indicadores con hitos.")
        return
    
    # Select indicator first
    with st.container(border=True):
        st.markdown('### Seleccionar Indicador')
        
        options_ind = []
        for _, row in df_con_hitos.iterrows():
            label = f"{row.get('indicador', 'Sin nombre')} ({row.get('año', '')})"
            options_ind.append((row['id'], label))
        
        selected_ind_id = st.selectbox(
            "Indicador",
            options=[opt[0] for opt in options_ind],
            format_func=lambda x: next(opt[1] for opt in options_ind if opt[0] == x)
        )
        
        
    
    if selected_ind_id:
        hitos_df = db.get_hitos_by_indicador(selected_ind_id)
        
        if len(hitos_df) == 0:
            st.warning("⚠️ Este indicador no tiene hitos. Crea hitos primero en 'Gestión de Hitos'.")
            return
        
        # Select hito
        with st.container(border=True):
            st.markdown('### Seleccionar Hito')
            
            options_hito = []
            for _, row in hitos_df.iterrows():
                label = f"{row.get('nombre', 'Sin nombre')}"
                options_hito.append((row['id'], label))
            
            selected_hito_id = st.selectbox(
                "Hito",
                options=[opt[0] for opt in options_hito],
                format_func=lambda x: next(opt[1] for opt in options_hito if opt[0] == x)
            )
            
            
        
        if selected_hito_id:
            # Get actividades for this hito
            actividades_df = db.get_actividades_by_hito(selected_hito_id)
            
            # Show existing actividades
            with st.container(border=True):
                st.markdown('### Actividades Existentes')
                
                if len(actividades_df) > 0:
                    for _, actividad in actividades_df.iterrows():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.write(f"**{actividad['descripcion_actividad']}**")
                            if actividad.get('responsable'):
                                st.caption(f"👤 {actividad['responsable']}")
                        
                        with col2:
                            st.markdown(get_status_badge(actividad['estado_actividad']), unsafe_allow_html=True)
                        
                        with col3:
                            ultimo_avance = actividad.get('ultimo_avance_reportado', 0)
                            st.write(f"Último avance: {ultimo_avance}%")
                        
                        with col4:
                            if st.button("🗑️", key=f"del_act_{actividad['id']}", help="Eliminar actividad"):
                                if db.delete_actividad(actividad['id']):
                                    st.success("Actividad eliminada")
                                    st.rerun()
                        
                        st.markdown("---")
                else:
                    st.info("No hay actividades creadas para este hito.")
                
                
            
            # Create new actividad
            with st.container(border=True):
                st.markdown('### ➕ Agregar Nueva Actividad')
                
                with st.form("crear_actividad_form"):
                    descripcion_actividad = st.text_input(
                        "Descripción de la Actividad *",
                        placeholder="Ej: Definir alcance del proyecto"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fecha_inicio_plan = st.date_input(
                            "Fecha Inicio Plan",
                            value=None
                        )
                        
                        responsable_actividad = st.text_input(
                            "Responsable *",
                            placeholder="Ej: Carlos López"
                        )
                    
                    with col2:
                        fecha_fin_plan = st.date_input(
                            "Fecha Fin Plan",
                            value=None
                        )
                    
                    submitted = st.form_submit_button("✅ Agregar Actividad", use_container_width=True)
                    
                    if submitted:
                        if not descripcion_actividad or not responsable_actividad:
                            st.error("❌ La descripción y responsable son obligatorios")
                        else:
                            try:
                                actividad_id = db.create_actividad(
                                    hito_id=selected_hito_id,
                                    descripcion_actividad=descripcion_actividad,
                                    fecha_inicio_plan=str(fecha_inicio_plan) if fecha_inicio_plan else None,
                                    fecha_fin_plan=str(fecha_fin_plan) if fecha_fin_plan else None,
                                    responsable=responsable_actividad,
                                    estado_actividad="Por comenzar"
                                )
                                
                                st.success(f"✅ Actividad creada exitosamente (ID: {actividad_id})")
                                st.info("📊 El responsable podrá reportar avances en 'Actualización Mensual'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al crear la actividad: {str(e)}")
                
                


# ==================== OWNER PAGE ====================

def render_actualizacion_mensual_owner():
    """⭐ Owner page: Monthly progress reporting (MAIN OWNER PAGE)"""
    st.title("📅 Actualización Mensual (Owner)")
    
    current_month = datetime.now().strftime('%Y-%m')
    st.info(f"ℹ️ **Rol Owner**: Reporta el avance del mes actual ({current_month}). Solo puedes reportar una vez por mes.")
    
    # Get list of all responsables
    responsables = db.get_unique_values('responsable')
    
    if not responsables:
        st.warning("⚠️ No hay responsables asignados en el sistema.")
        return
    
    # Select responsable
    with st.container(border=True):
        st.markdown('### Seleccionar Responsable')
        
        selected_responsable = st.selectbox(
            "Responsable",
            options=responsables,
            help="Selecciona el responsable para ver sus hitos y actividades"
        )
        
        
    
    if selected_responsable:
        # Get hitos and actividades for this responsable
        hitos_df = db.get_hitos_by_responsable(selected_responsable)
        actividades_df = db.get_actividades_by_responsable(selected_responsable)
        
        # Filter by responsable (since get_hitos_by_responsable returns all hitos)
        if 'responsable' in hitos_df.columns:
            hitos_df = hitos_df[hitos_df['responsable'] == selected_responsable]
        
        total_items = len(hitos_df) + len(actividades_df)
        
        if total_items == 0:
            st.info(f"ℹ️ No hay hitos ni actividades asignadas a {selected_responsable}")
            return
        
        st.markdown(f"**Total de items asignados:** {total_items} ({len(hitos_df)} hitos, {len(actividades_df)} actividades)")
        
        # Form to report monthly progress
        with st.container(border=True):
            st.markdown(f'### Reporte Mensual - {current_month}')
            
            with st.form("reporte_mensual_form"):
                reportes = []
                
                # Show hitos
                if len(hitos_df) > 0:
                    st.markdown("### 🎯 Hitos")
                    
                    for idx, hito in hitos_df.iterrows():
                        st.markdown(f"**{hito['nombre']}**")
                        st.caption(f"Indicador: {hito.get('nombre_indicador', 'N/A')}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            ultimo_avance = hito.get('ultimo_avance_reportado', 0)
                            st.info(f"📊 Último avance reportado: {ultimo_avance}%")
                        
                        with col2:
                            nuevo_avance = st.slider(
                                f"Avance % del mes {current_month}",
                                min_value=0,
                                max_value=100,
                                value=int(ultimo_avance),
                                step=5,
                                key=f"hito_{hito['id']}"
                            )
                            
                            reportes.append({
                                'entidad': 'hito',
                                'id_entidad': hito['id'],
                                'avance': nuevo_avance,
                                'nombre': hito['nombre']
                            })
                        
                        st.markdown("---")
                
                # Show actividades
                if len(actividades_df) > 0:
                    st.markdown("### 📋 Actividades")
                    
                    for idx, actividad in actividades_df.iterrows():
                        st.markdown(f"**{actividad['descripcion_actividad']}**")
                        st.caption(f"Hito: {actividad.get('nombre_hito', 'N/A')} | Indicador: {actividad.get('nombre_indicador', 'N/A')}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            ultimo_avance = actividad.get('ultimo_avance_reportado', 0)
                            st.info(f"📊 Último avance reportado: {ultimo_avance}%")
                        
                        with col2:
                            nuevo_avance = st.slider(
                                f"Avance % del mes {current_month}",
                                min_value=0,
                                max_value=100,
                                value=int(ultimo_avance),
                                step=5,
                                key=f"actividad_{actividad['id']}"
                            )
                            
                            reportes.append({
                                'entidad': 'actividad',
                                'id_entidad': actividad['id'],
                                'avance': nuevo_avance,
                                'nombre': actividad['descripcion_actividad']
                            })
                        
                        st.markdown("---")
                
                # Submit button
                submitted = st.form_submit_button("💾 Guardar Reporte Mensual", use_container_width=True)
                
                if submitted:
                    try:
                        success_count = 0
                        already_reported = []
                        errors = []
                        
                        for reporte in reportes:
                            result = db.registrar_avance_mensual(
                                entidad=reporte['entidad'],
                                id_entidad=reporte['id_entidad'],
                                avance_reportado=reporte['avance'],
                                usuario=selected_responsable,
                                mes=current_month
                            )
                            
                            if result:
                                success_count += 1
                            else:
                                already_reported.append(reporte['nombre'])
                        
                        # Update indicator progress for all affected indicators
                        # Get unique indicator IDs from hitos
                        if len(hitos_df) > 0:
                            for indicador_id in hitos_df['indicador_id'].unique():
                                db.update_indicador_from_hitos(indicador_id)
                        
                        if success_count > 0:
                            st.success(f"✅ {success_count} reportes guardados exitosamente")
                            st.info("📊 Los avances de los indicadores se actualizaron automáticamente")
                        
                        if already_reported:
                            st.warning(f"⚠️ Los siguientes items ya fueron reportados este mes: {', '.join(already_reported)}")
                        
                        if success_count > 0:
                            st.balloons()
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error al guardar reportes: {str(e)}")
            
            


# ==================== SEGUIMIENTO PAGE ====================

def render_vista_seguimiento():
    """Read-only tracking view with hierarchy and historical data"""
    st.title("🔍 Vista de Seguimiento")
    
    st.info("ℹ️ Vista de solo lectura con jerarquía completa y avances calculados automáticamente")
    
    # Get all indicators
    df = db.get_all_indicadores()
    
    if len(df) == 0:
        st.info("No hay indicadores registrados.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        responsables = ["Todos"] + db.get_unique_values('responsable')
        selected_responsable = st.selectbox("Filtrar por Responsable", responsables)
    
    with col2:
        años = ["Todos"] + [str(y) for y in db.get_unique_values('año')]
        selected_año = st.selectbox("Filtrar por Año", años)
    
    # Apply filters
    if selected_responsable != "Todos":
        df = df[df['responsable'] == selected_responsable]
    
    if selected_año != "Todos":
        df = df[df['año'] == int(selected_año)]
    
    st.markdown("---")
    
    # Display indicators with hierarchy
    for _, indicador in df.iterrows():
        with st.expander(f"📊 {indicador['indicador']} - {indicador['avance_porcentaje']}%", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avance", f"{indicador['avance_porcentaje']}%")
            
            with col2:
                st.markdown("**Estado:**")
                st.markdown(get_status_badge(indicador['estado']), unsafe_allow_html=True)
            
            with col3:
                st.write(f"**Responsable:** {indicador.get('responsable', 'N/A')}")
            
            # Show hitos if exists
            if indicador.get('tiene_hitos'):
                hitos_df = db.get_hitos_by_indicador(indicador['id'])
                
                if len(hitos_df) > 0:
                    st.markdown("### 🎯 Hitos")
                    
                    for _, hito in hitos_df.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{hito['nombre']}**")
                            if hito.get('responsable'):
                                st.caption(f"👤 {hito['responsable']}")
                        
                        with col2:
                            ultimo_avance = hito.get('ultimo_avance_reportado', hito.get('avance_porcentaje', 0))
                            st.write(f"{ultimo_avance}%")
                        
                        with col3:
                            st.markdown(get_status_badge(hito['estado']), unsafe_allow_html=True)
                        
                        # Show actividades for this hito
                        actividades_df = db.get_actividades_by_hito(hito['id'])
                        
                        if len(actividades_df) > 0:
                            st.markdown("**📋 Actividades:**")
                            
                            for _, actividad in actividades_df.iterrows():
                                col1, col2, col3 = st.columns([3, 1, 1])
                                
                                with col1:
                                    st.caption(f"  • {actividad['descripcion_actividad']}")
                                    if actividad.get('responsable'):
                                        st.caption(f"    👤 {actividad['responsable']}")
                                
                                with col2:
                                    ultimo_avance_act = actividad.get('ultimo_avance_reportado', 0)
                                    st.caption(f"{ultimo_avance_act}%")
                                
                                with col3:
                                    st.markdown(get_status_badge(actividad['estado_actividad']), unsafe_allow_html=True)
                        
                        st.markdown("---")


# ==================== SIDEBAR NAVIGATION ====================

with st.sidebar:
    st.title("🎯 Sistema de Indicadores")
    st.markdown("---")
    
    # Dashboard
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
    
    st.markdown("### 🛠️ Administración (Admin)")
    
    if st.button("📝 Gestión de Indicadores", use_container_width=True):
        st.session_state.page = 'gestion_indicadores'
    
    if st.button("🎯 Gestión de Hitos", use_container_width=True):
        st.session_state.page = 'gestion_hitos'
    
    if st.button("📋 Gestión de Actividades", use_container_width=True):
        st.session_state.page = 'gestion_actividades'
    
    st.markdown("### 👤 Reporte (Owner)")
    
    if st.button("📅 Actualización Mensual ⭐", use_container_width=True):
        st.session_state.page = 'actualizacion_mensual'
    
    st.markdown("### 📈 Seguimiento")
    
    if st.button("🔍 Vista de Seguimiento", use_container_width=True):
        st.session_state.page = 'vista_seguimiento'
    
    st.markdown("---")
    st.caption("v3.0.0 - Sistema de Indicadores con Roles")


# ==================== RENDER SELECTED PAGE ====================

if st.session_state.page == 'dashboard':
    render_dashboard()
elif st.session_state.page == 'gestion_indicadores':
    render_gestion_indicadores_admin()
elif st.session_state.page == 'gestion_hitos':
    render_gestion_hitos_admin()
elif st.session_state.page == 'gestion_actividades':
    render_gestion_actividades_admin()
elif st.session_state.page == 'actualizacion_mensual':
    render_actualizacion_mensual_owner()
elif st.session_state.page == 'vista_seguimiento':
    render_vista_seguimiento()
