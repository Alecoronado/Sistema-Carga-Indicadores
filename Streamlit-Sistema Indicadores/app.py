"""
Sistema de Indicadores e Hitos
Modern web-based indicator and milestone tracking system
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database import Database
from styles import get_custom_css, get_status_badge, get_progress_bar

# Page configuration
st.set_page_config(
    page_title="Sistema de Indicadores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize database
db = Database()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'


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
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    # Apply filters
    filter_area = None if selected_area == "Todos" else selected_area
    filter_año = None if selected_año == "Todos" else int(selected_año)
    filter_unidad = None if selected_unidad == "Todos" else selected_unidad
    filter_tipo = None if selected_tipo == "Todos" else selected_tipo
    
    # Get filtered data
    df = db.get_all_indicadores(
        area=filter_area,
        año=filter_año,
        unidad_organizacional=filter_unidad,
        tipo_indicador=filter_tipo
    )
    
    st.markdown("---")
    
    # Display data table
    if len(df) > 0:
        st.subheader(f"📋 Indicadores ({len(df)} registros)")
        
        # Format dataframe for display
        display_columns = ['id', 'id_estrategico', 'indicador', 'tipo_indicador', 
                          'area', 'unidad_organizacional', 'año', 'estado', 
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
            'año': 'Año',
            'estado': 'Estado',
            'avance_porcentaje': 'Avance %',
            'fecha_inicio': 'Inicio',
            'fecha_fin_actual': 'Fin'
        }
        
        display_df.rename(columns=column_names, inplace=True)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay indicadores que coincidan con los filtros seleccionados.")


def render_crear_indicador():
    """Render the create indicator form"""
    st.title("➕ Crear Indicador")
    
    # Card container
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Nuevo Indicador</div>', unsafe_allow_html=True)
        
        with st.form("crear_indicador_form", clear_on_submit=True):
            # Basic Information Section
            st.markdown("### 📋 Información Básica")
            col1, col2 = st.columns(2)
            
            with col1:
                id_estrategico = st.text_input(
                    "ID Estratégico",
                    placeholder="Ej: EST-2024-001",
                    help="Identificador estratégico único"
                )
                
                indicador = st.text_input(
                    "Indicador *",
                    placeholder="Ej: Incremento de ventas digitales",
                    help="Nombre del indicador"
                )
                
                tipo_indicador = st.text_input(
                    "Tipo Indicador *",
                    placeholder="Ej: Estratégico, Operativo, Gestión",
                    help="Tipo o categoría del indicador"
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
                    placeholder="Ej: Ventas, Marketing, Operaciones",
                    help="Área responsable"
                )
                
                unidad_organizacional = st.text_input(
                    "Unidad Organizacional",
                    placeholder="Ej: Dirección Comercial",
                    help="Unidad organizacional responsable"
                )
                
                unidad_organizacional_colaboradora = st.text_input(
                    "Unidad Organizacional Colaboradora",
                    placeholder="Ej: Dirección de TI",
                    help="Unidad que colabora"
                )
                
                lineamientos_estrategicos = st.text_area(
                    "Lineamientos Estratégicos",
                    placeholder="Lineamientos o directrices estratégicas",
                    height=100
                )
            
            st.markdown("---")
            
            # Goals and Metrics Section
            st.markdown("### 🎯 Metas y Medidas")
            col1, col2 = st.columns(2)
            
            with col1:
                meta = st.text_area(
                    "Meta",
                    placeholder="Ej: Incrementar ventas en 15%",
                    help="Meta u objetivo a alcanzar",
                    height=80
                )
                
                medida = st.text_input(
                    "Medida",
                    placeholder="Ej: Porcentaje, Cantidad, Monto",
                    help="Unidad de medida"
                )
            
            with col2:
                avance = st.number_input(
                    "Avance (Valor)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    help="Valor numérico del avance"
                )
                
                avance_porcentaje = st.slider(
                    "Avance %",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5,
                    help="Porcentaje de avance"
                )
                
                estado = st.selectbox(
                    "Estado",
                    ["Por comenzar", "En progreso", "Completado"]
                )
            
            st.markdown("---")
            
            # Dates Section
            st.markdown("### 📅 Fechas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                fecha_inicio = st.date_input(
                    "Fecha Inicio",
                    value=None,
                    help="Fecha de inicio del indicador"
                )
            
            with col2:
                fecha_fin_original = st.date_input(
                    "Fecha Fin Original",
                    value=None,
                    help="Fecha de fin planificada originalmente"
                )
            
            with col3:
                fecha_fin_actual = st.date_input(
                    "Fecha Fin Actual",
                    value=None,
                    help="Fecha de fin actual o reprogramada"
                )
            
            with col4:
                fecha_carga = st.date_input(
                    "Fecha Carga",
                    value=datetime.now().date(),
                    help="Fecha de carga del registro"
                )
            
            st.markdown("---")
            
            # Additional Information
            st.markdown("### 📝 Información Adicional")
            hitos_etapas = st.text_area(
                "Hitos / Etapas",
                placeholder="Descripción de hitos o etapas del indicador",
                height=100,
                help="Hitos, etapas o fases del indicador"
            )
            
            st.markdown("---")
            
            # Submit button
            submitted = st.form_submit_button("✅ Crear Indicador", use_container_width=True)
            
            if submitted:
                # Validate required fields
                if not indicador or not tipo_indicador:
                    st.error("❌ Por favor completa los campos obligatorios: Indicador y Tipo Indicador")
                else:
                    # Create indicator
                    try:
                        record_id = db.create_indicador(
                            id_estrategico=id_estrategico if id_estrategico else None,
                            año=año,
                            indicador=indicador,
                            unidad_organizacional=unidad_organizacional if unidad_organizacional else None,
                            unidad_organizacional_colaboradora=unidad_organizacional_colaboradora if unidad_organizacional_colaboradora else None,
                            area=area if area else None,
                            lineamientos_estrategicos=lineamientos_estrategicos if lineamientos_estrategicos else None,
                            meta=meta if meta else None,
                            medida=medida if medida else None,
                            avance=avance if avance else None,
                            avance_porcentaje=avance_porcentaje,
                            estado=estado,
                            fecha_inicio=str(fecha_inicio) if fecha_inicio else None,
                            fecha_fin_original=str(fecha_fin_original) if fecha_fin_original else None,
                            fecha_fin_actual=str(fecha_fin_actual) if fecha_fin_actual else None,
                            fecha_carga=str(fecha_carga) if fecha_carga else None,
                            tipo_indicador=tipo_indicador,
                            hitos_etapas=hitos_etapas if hitos_etapas else None
                        )
                        st.success(f"✅ Indicador creado exitosamente (ID: {record_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error al crear el indicador: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_actualizar_avance():
    """Render the progress update interface"""
    st.title("🔄 Actualizar Avance")
    
    # Get all indicators
    df = db.get_all_indicadores()
    
    if len(df) == 0:
        st.info("No hay indicadores registrados. Crea uno primero en la sección '➕ Crear Indicador'.")
        return
    
    # Card container
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Seleccionar Indicador</div>', unsafe_allow_html=True)
        
        # Create selection options
        options = []
        for _, row in df.iterrows():
            tipo = row.get('tipo_indicador', 'N/A')
            nombre = row.get('indicador', 'Sin nombre')
            area = row.get('area', 'Sin área')
            año = row.get('año', '')
            label = f"[{tipo}] {nombre} - {area} ({año})"
            options.append((row['id'], label))
        
        selected_id = st.selectbox(
            "Indicador",
            options=[opt[0] for opt in options],
            format_func=lambda x: next(opt[1] for opt in options if opt[0] == x),
            help="Selecciona el indicador que deseas actualizar"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if selected_id:
        # Get selected indicator details
        indicador = db.get_indicador_by_id(selected_id)
        
        if indicador:
            # Display current status
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">Estado Actual</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Avance Actual", f"{indicador.get('avance_porcentaje', 0)}%")
                
                with col2:
                    st.markdown("**Estado:**")
                    st.markdown(get_status_badge(indicador.get('estado', 'Por comenzar')), unsafe_allow_html=True)
                
                with col3:
                    unidad = indicador.get('unidad_organizacional', 'N/A')
                    st.metric("Unidad Organizacional", unidad if unidad else "N/A")
                
                # Show additional info
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Meta:** {indicador.get('meta', 'No definida')}")
                    st.write(f"**Medida:** {indicador.get('medida', 'No definida')}")
                
                with col2:
                    st.write(f"**Fecha Inicio:** {indicador.get('fecha_inicio', 'No definida')}")
                    st.write(f"**Fecha Fin Actual:** {indicador.get('fecha_fin_actual', 'No definida')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Update form
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">Actualizar Progreso</div>', unsafe_allow_html=True)
                
                with st.form("actualizar_avance_form"):
                    nuevo_avance = st.slider(
                        "Nuevo Avance (%)",
                        min_value=0,
                        max_value=100,
                        value=indicador.get('avance_porcentaje', 0),
                        step=5,
                        help="Ajusta el porcentaje de avance"
                    )
                    
                    # Preview new status
                    if nuevo_avance == 0:
                        nuevo_estado = "Por comenzar"
                    elif nuevo_avance < 100:
                        nuevo_estado = "En progreso"
                    else:
                        nuevo_estado = "Completado"
                    
                    st.info(f"ℹ️ El estado se actualizará automáticamente a: **{nuevo_estado}**")
                    
                    st.markdown("---")
                    
                    # Submit button
                    submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                    
                    if submitted:
                        try:
                            success = db.update_avance(selected_id, nuevo_avance)
                            if success:
                                st.success(f"✅ Avance actualizado exitosamente a {nuevo_avance}%")
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar el avance")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                st.markdown('</div>', unsafe_allow_html=True)


def render_gestion():
    """Render the management/deletion interface"""
    st.title("⚙️ Gestión de Indicadores")
    
    # Get all indicators
    df = db.get_all_indicadores()
    
    if len(df) == 0:
        st.info("No hay indicadores registrados.")
        return
    
    # Card container
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Eliminar Indicador</div>', unsafe_allow_html=True)
        
        st.warning("⚠️ Esta acción es permanente y no se puede deshacer.")
        
        # Create selection options
        options = []
        for _, row in df.iterrows():
            tipo = row.get('tipo_indicador', 'N/A')
            nombre = row.get('indicador', 'Sin nombre')
            area = row.get('area', 'Sin área')
            año = row.get('año', '')
            label = f"[{tipo}] {nombre} - {area} ({año})"
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
                st.markdown("**Detalles del indicador:**")
                st.write(f"- **Indicador:** {indicador.get('indicador', 'N/A')}")
                st.write(f"- **Área:** {indicador.get('area', 'N/A')}")
                st.write(f"- **Unidad Organizacional:** {indicador.get('unidad_organizacional', 'N/A')}")
                st.write(f"- **Avance:** {indicador.get('avance_porcentaje', 0)}%")
                
                st.markdown("---")
                
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                        try:
                            success = db.delete_indicador(selected_id)
                            if success:
                                st.success("✅ Indicador eliminado exitosamente")
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar el indicador")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)


# Sidebar navigation
with st.sidebar:
    st.title("🎯 Sistema de Indicadores")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
    
    if st.button("➕ Crear Indicador", use_container_width=True):
        st.session_state.page = 'crear'
    
    if st.button("🔄 Actualizar Avance", use_container_width=True):
        st.session_state.page = 'actualizar'
    
    if st.button("⚙️ Gestión", use_container_width=True):
        st.session_state.page = 'gestion'
    
    st.markdown("---")
    st.caption("v1.0.0 - Sistema de Indicadores e Hitos")


# Render selected page
if st.session_state.page == 'dashboard':
    render_dashboard()
elif st.session_state.page == 'crear':
    render_crear_indicador()
elif st.session_state.page == 'actualizar':
    render_actualizar_avance()
elif st.session_state.page == 'gestion':
    render_gestion()
