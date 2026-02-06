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
    "VPF"
]
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
    
    # Apply responsable filter manually (since get_all_indicadores doesn't have this param yet)
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
                
                tipo_indicador = st.selectbox(
                    "Tipo Indicador *",
                    options=TIPOS_INDICADOR,
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
                    placeholder="Ej: Efectividad en el Desarrollo, Programacion Financiera y Reporting, Alianzas Estratégicas",
                    help="Área responsable"
                )
                
                unidad_organizacional = st.selectbox(
                    "Unidad Organizacional",
                    options=["Seleccionar..."] + UNIDADES_ORGANIZACIONALES,
                    help="Unidad organizacional responsable"
                )
                
                unidad_organizacional_colaboradora = st.selectbox(
                    "Unidad Organizacional Colaboradora",
                    options=["Seleccionar..."] + UNIDADES_ORGANIZACIONALES,
                    help="Unidad que colabora"
                )
                
                lineamientos_estrategicos = st.selectbox(
                    "Lineamiento Estratégico *",
                    options=LINEAMIENTOS_ESTRATEGICOS,
                    help="Selecciona el lineamiento estratégico"
                )
                
                responsable = st.text_input(
                    "Responsable",
                    placeholder="Ej: Juan Pérez",
                    help="Persona responsable del indicador"
                )
            
            st.markdown("---")
            
            # Goals and Metrics Section
            st.markdown("### 🎯 Metas y Medidas")
            col1, col2 = st.columns(2)
            
            with col1:
                meta = st.number_input(
                    "Meta (Valor Objetivo)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    help="Valor numérico objetivo a alcanzar (para calcular Avance%)"
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
                    help="Valor numérico del avance (para indicadores cuantitativos)"
                )
                
                estado = st.selectbox(
                    "Estado",
                    ["Por comenzar", "En progreso", "Completado"]
                )
            st.markdown("---")
            
            # Dates Section
            st.markdown("### 📅 Fechas")
            col1, col2, col3 = st.columns(3)
            
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
            
            st.markdown("---")
            
            # Additional Information
            st.markdown("### 📝 Información Adicional")
            
            tiene_hitos = st.checkbox(
                "¿Tiene Hitos/Etapas?",
                value=False,
                help="Marca esta casilla si este indicador tiene hitos o etapas que gestionar"
            )
            
            if tiene_hitos:
                st.info("ℹ️ Podrás agregar y gestionar los hitos desde la sección '🎯 Gestionar Hitos' después de crear el indicador.")
            
            st.markdown("---")
            
            # Submit button
            submitted = st.form_submit_button("✅ Crear Indicador", use_container_width=True)
            
            if submitted:
                # Validate required fields
                if not indicador or not tipo_indicador or not lineamientos_estrategicos:
                    st.error("❌ Por favor completa los campos obligatorios: Indicador, Tipo Indicador y Lineamiento Estratégico")
                else:
                    # Create indicator
                    try:
                        record_id = db.create_indicador(
                            id_estrategico=id_estrategico if id_estrategico else None,
                            año=año,
                            indicador=indicador,
                            unidad_organizacional=unidad_organizacional if unidad_organizacional != "Seleccionar..." else None,
                            unidad_organizacional_colaboradora=unidad_organizacional_colaboradora if unidad_organizacional_colaboradora != "Seleccionar..." else None,
                            area=area if area else None,
                            lineamientos_estrategicos=lineamientos_estrategicos if lineamientos_estrategicos else None,
                            meta=str(meta) if meta > 0 else None,
                            medida=medida if medida else None,
                            avance=avance,
                            estado=estado,
                            fecha_inicio=str(fecha_inicio) if fecha_inicio else None,
                            fecha_fin_original=str(fecha_fin_original) if fecha_fin_original else None,
                            fecha_fin_actual=str(fecha_fin_actual) if fecha_fin_actual else None,
                            tipo_indicador=tipo_indicador,
                            tiene_hitos=tiene_hitos,
                            responsable=responsable if responsable else None
                        )
                        st.success(f"✅ Indicador creado exitosamente (ID: {record_id})")
                        if tiene_hitos:
                            st.info("💡 Ahora puedes agregar hitos en la sección '🎯 Gestionar Hitos'")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error al crear el indicador: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_actualizar_avance():
    """Render the progress update interface for QUANTITATIVE indicators (without hitos)"""
    st.title("🔄 Actualizar Avance Estratégico")
    
    st.info("ℹ️ Esta sección es para **indicadores cuantitativos** (sin hitos). El avance % se calcula automáticamente: (Avance / Meta) × 100")
    
    # Get all indicators WITHOUT hitos
    df = db.get_all_indicadores()
    
    if len(df) == 0:
        st.info("No hay indicadores registrados. Crea uno primero en la sección '➕ Crear Indicador'.")
        return
    
    # Filter indicators WITHOUT hitos (quantitative)
    df_sin_hitos = df[df['tiene_hitos'] == 0] if 'tiene_hitos' in df.columns else df
    
    if len(df_sin_hitos) == 0:
        st.warning("⚠️ No hay indicadores cuantitativos (sin hitos). Los indicadores con hitos se actualizan automáticamente según el promedio de sus hitos.")
        return
    
    # Card container
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Seleccionar Indicador</div>', unsafe_allow_html=True)
        
        # Create selection options
        options = []
        for _, row in df_sin_hitos.iterrows():
            tipo = row.get('tipo_indicador', 'N/A')
            nombre = row.get('indicador', 'Sin nombre')
            area = row.get('area', 'Sin área')
            año = row.get('año', '')
            label = f"[{tipo}] {nombre} - {area} ({año})"
            options.append((row['id'], label))
        
        selected_id = st.selectbox(
            "Indicador Cuantitativo",
            options=[opt[0] for opt in options],
            format_func=lambda x: next(opt[1] for opt in options if opt[0] == x),
            help="Selecciona el indicador cuantitativo que deseas actualizar"
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
                    meta_valor = indicador.get('meta', 'No definida')
                    st.metric("Meta", meta_valor)
                
                # Show additional info
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Avance (Valor):** {indicador.get('avance', 0)}")
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
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Update meta if needed
                        current_meta = indicador.get('meta', '0')
                        try:
                            meta_value = float(current_meta) if current_meta else 0.0
                        except (ValueError, TypeError):
                            meta_value = 0.0
                        
                        nueva_meta = st.number_input(
                            "Meta (Valor Objetivo)",
                            min_value=0.0,
                            value=meta_value,
                            step=0.1,
                            help="Valor objetivo a alcanzar"
                        )
                    
                    with col2:
                        # Update avance value
                        nuevo_avance_valor = st.number_input(
                            "Avance (Valor Actual)",
                            min_value=0.0,
                            value=float(indicador.get('avance', 0)),
                            step=0.1,
                            help="Valor actual alcanzado"
                        )
                    
                    # Calculate percentage automatically for preview
                    try:
                        meta_num = float(nueva_meta) if nueva_meta else 1
                        if meta_num > 0:
                            nuevo_avance_porcentaje = min(100, int((nuevo_avance_valor / meta_num) * 100))
                        else:
                            nuevo_avance_porcentaje = 0
                    except (ValueError, ZeroDivisionError):
                        nuevo_avance_porcentaje = 0
                    
                    st.markdown("---")
                    st.info(f"📊 **Avance Calculado:** {nuevo_avance_porcentaje}% = ({nuevo_avance_valor} / {nueva_meta}) × 100")
                    
                    # Preview new status
                    if nuevo_avance_porcentaje == 0:
                        nuevo_estado = "Por comenzar"
                    elif nuevo_avance_porcentaje < 100:
                        nuevo_estado = "En progreso"
                    else:
                        nuevo_estado = "Completado"
                    
                    st.info(f"ℹ️ El estado se actualizará automáticamente a: **{nuevo_estado}**")
                    
                    st.markdown("---")
                    
                    # Submit button
                    submitted = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                    
                    if submitted:
                        try:
                            # Update indicator using the database method (calculates avance_porcentaje automatically)
                            success = db.update_avance(
                                indicador_id=selected_id,
                                nuevo_avance=nuevo_avance_valor,
                                nueva_meta=str(nueva_meta) if nueva_meta > 0 else None,
                                nuevo_estado=nuevo_estado
                            )
                            
                            if success:
                                st.success(f"✅ Indicador actualizado: {nuevo_avance_porcentaje}% ({nuevo_avance_valor}/{nueva_meta})")
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar el indicador")
                        except Exception as e:
                            st.error(f"❌ Error al actualizar: {str(e)}")
                
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


def render_gestionar_hitos():
    """Render the hitos management interface for QUALITATIVE indicators"""
    st.title("🎯 Gestionar Hitos")
    
    st.info("ℹ️ Esta sección es para **indicadores cualitativos** (con hitos). El avance del indicador se calcula automáticamente como el promedio de sus hitos.")
    
    # Get all indicators that have hitos
    df = db.get_all_indicadores()
    
    if len(df) == 0:
        st.info("No hay indicadores registrados.")
        return
    
    # Filter indicators with hitos
    df_con_hitos = df[df['tiene_hitos'] == 1] if 'tiene_hitos' in df.columns else df
    
    if len(df_con_hitos) == 0:
        st.warning("⚠️ No hay indicadores con hitos habilitados. Crea un indicador y marca '¿Tiene Hitos/Etapas?' para comenzar.")
        return
    
    # Select indicator
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Seleccionar Indicador</div>', unsafe_allow_html=True)
        
        options = []
        for _, row in df_con_hitos.iterrows():
            tipo = row.get('tipo_indicador', 'N/A')
            nombre = row.get('indicador', 'Sin nombre')
            año = row.get('año', '')
            avance = row.get('avance_porcentaje', 0)
            label = f"[{tipo}] {nombre} ({año}) - {avance}%"
            options.append((row['id'], label))
        
        selected_id = st.selectbox(
            "Indicador Cualitativo",
            options=[opt[0] for opt in options],
            format_func=lambda x: next(opt[1] for opt in options if opt[0] == x),
            help="Selecciona el indicador para gestionar sus hitos"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if selected_id:
        # Get hitos for this indicator
        hitos_df = db.get_hitos_by_indicador(selected_id)
        
        # Show indicator progress (calculated from hitos)
        indicador = db.get_indicador_by_id(selected_id)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">Avance del Indicador (Calculado)</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avance Total", f"{indicador.get('avance_porcentaje', 0)}%")
            
            with col2:
                st.markdown("**Estado:**")
                st.markdown(get_status_badge(indicador.get('estado', 'Por comenzar')), unsafe_allow_html=True)
            
            with col3:
                st.metric("Total Hitos", len(hitos_df))
            
            if len(hitos_df) > 0:
                st.info(f"📊 El avance se calcula automáticamente como el promedio de los {len(hitos_df)} hitos")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show existing hitos
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">Hitos Existentes</div>', unsafe_allow_html=True)
            
            if len(hitos_df) > 0:
                for _, hito in hitos_df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{hito['nombre']}**")
                        if hito.get('descripcion'):
                            st.caption(hito['descripcion'])
                    
                    with col2:
                        st.markdown(get_status_badge(hito['estado']), unsafe_allow_html=True)
                    
                    with col3:
                        st.write(f"Avance: {hito['avance_porcentaje']}%")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_hito_{hito['id']}", help="Eliminar hito"):
                            if db.delete_hito(hito['id']):
                                # Update indicator progress
                                db.update_indicador_from_hitos(selected_id)
                                st.success("Hito eliminado")
                                st.rerun()
                    
                    st.markdown("---")
            else:
                st.info("No hay hitos creados para este indicador.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Create new hito (SIMPLIFIED FORM)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">➕ Agregar Nuevo Hito</div>', unsafe_allow_html=True)
            
            with st.form("crear_hito_form"):
                nombre_hito = st.text_input(
                    "Nombre del Hito *",
                    placeholder="Ej: Fase 1 - Planificación",
                    help="Nombre descriptivo del hito"
                )
                
                descripcion_hito = st.text_area(
                    "Descripción",
                    placeholder="Descripción detallada del hito (opcional)",
                    height=80
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fecha_inicio_hito = st.date_input(
                        "Fecha Inicio",
                        value=None,
                        help="Fecha de inicio del hito"
                    )
                
                with col2:
                    fecha_fin_planificada_hito = st.date_input(
                        "Fecha Fin Planificada",
                        value=None,
                        help="Fecha planificada de finalización"
                    )
                
                avance_hito = st.slider(
                    "Avance % *",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5,
                    help="Porcentaje de avance del hito"
                )
                
                submitted = st.form_submit_button("✅ Agregar Hito", use_container_width=True)
                
                if submitted:
                    if not nombre_hito:
                        st.error("❌ El nombre del hito es obligatorio")
                    else:
                        try:
                            # Determine status
                            if avance_hito == 0:
                                estado_hito = "Por comenzar"
                            elif avance_hito < 100:
                                estado_hito = "En progreso"
                            else:
                                estado_hito = "Completado"
                            
                            hito_id = db.create_hito(
                                indicador_id=selected_id,
                                nombre=nombre_hito,
                                descripcion=descripcion_hito if descripcion_hito else None,
                                fecha_inicio=str(fecha_inicio_hito) if fecha_inicio_hito else None,
                                fecha_fin_planificada=str(fecha_fin_planificada_hito) if fecha_fin_planificada_hito else None,
                                avance_porcentaje=avance_hito,
                                estado=estado_hito,
                                orden=len(hitos_df) + 1
                            )
                            
                            # Update indicator progress automatically
                            db.update_indicador_from_hitos(selected_id)
                            
                            st.success(f"✅ Hito creado exitosamente (ID: {hito_id})")
                            st.info("📊 El avance del indicador se actualizó automáticamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al crear el hito: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Update hito progress
        if len(hitos_df) > 0:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">🔄 Actualizar Avance de Hito</div>', unsafe_allow_html=True)
                
                hito_options = [(row['id'], f"{row['nombre']} ({row['avance_porcentaje']}%)") 
                               for _, row in hitos_df.iterrows()]
                
                selected_hito_id = st.selectbox(
                    "Seleccionar Hito",
                    options=[opt[0] for opt in hito_options],
                    format_func=lambda x: next(opt[1] for opt in hito_options if opt[0] == x)
                )
                
                if selected_hito_id:
                    hito_actual = hitos_df[hitos_df['id'] == selected_hito_id].iloc[0]
                    
                    with st.form("actualizar_hito_form"):
                        nuevo_avance_hito = st.slider(
                            "Nuevo Avance (%)",
                            min_value=0,
                            max_value=100,
                            value=int(hito_actual['avance_porcentaje']),
                            step=5
                        )
                        
                        # Preview new status
                        if nuevo_avance_hito == 0:
                            nuevo_estado_hito = "Por comenzar"
                        elif nuevo_avance_hito < 100:
                            nuevo_estado_hito = "En progreso"
                        else:
                            nuevo_estado_hito = "Completado"
                        
                        st.info(f"ℹ️ El estado del hito se actualizará a: **{nuevo_estado_hito}**")
                        st.info(f"📊 El avance del indicador se recalculará automáticamente")
                        
                        submitted_update = st.form_submit_button("💾 Actualizar Hito", use_container_width=True)
                        
                        if submitted_update:
                            try:
                                if db.update_hito_avance(selected_hito_id, nuevo_avance_hito):
                                    # Update indicator progress automatically
                                    db.update_indicador_from_hitos(selected_id)
                                    
                                    st.success(f"✅ Hito actualizado a {nuevo_avance_hito}%")
                                    st.success("📊 Avance del indicador actualizado automáticamente")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al actualizar el hito")
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
    
    if st.button("🎯 Gestionar Hitos", use_container_width=True):
        st.session_state.page = 'hitos'
    
    if st.button("⚙️ Gestión", use_container_width=True):
        st.session_state.page = 'gestion'
    
    st.markdown("---")
    st.caption("v2.0.0 - Sistema de Indicadores e Hitos")


# Render selected page
if st.session_state.page == 'dashboard':
    render_dashboard()
elif st.session_state.page == 'crear':
    render_crear_indicador()
elif st.session_state.page == 'actualizar':
    render_actualizar_avance()
elif st.session_state.page == 'hitos':
    render_gestionar_hitos()
elif st.session_state.page == 'gestion':
    render_gestion()
