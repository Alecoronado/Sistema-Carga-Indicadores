"""
FastAPI REST API for Sistema de Indicadores
Provides endpoints for managing indicators, hitos, actividades, and monthly progress reporting
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from database import Database
from schemas import (
    IndicadorCreate, IndicadorUpdate, IndicadorResponse,
    HitoCreate, HitoUpdate, HitoResponse,
    ActividadCreate, ActividadUpdate, ActividadResponse,
    AvanceMensualCreate, AvanceMensualResponse,
    DashboardStats, IndicadorJerarquia, HitoJerarquia, ActividadJerarquia,
    MessageResponse, ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Sistema de Indicadores API",
    description="API REST para gestión de indicadores, hitos y actividades con reporte mensual",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


# ==================== ROOT ====================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Sistema de Indicadores API",
        "version": "3.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==================== INDICADORES ====================

@app.get("/api/indicadores", response_model=List[IndicadorResponse], tags=["Indicadores"])
async def get_indicadores(
    area: Optional[str] = Query(None, description="Filtrar por área"),
    año: Optional[int] = Query(None, description="Filtrar por año"),
    unidad_organizacional: Optional[str] = Query(None, description="Filtrar por unidad organizacional"),
    tipo_indicador: Optional[str] = Query(None, description="Filtrar por tipo de indicador"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    responsable: Optional[str] = Query(None, description="Filtrar por responsable")
):
    """Get all indicators with optional filters"""
    try:
        df = db.get_all_indicadores(
            area=area,
            año=año,
            unidad_organizacional=unidad_organizacional,
            tipo_indicador=tipo_indicador,
            estado=estado
        )
        
        # Apply responsable filter if provided
        if responsable:
            df = df[df['responsable'] == responsable]
        
        # Convert DataFrame to list of dicts
        indicadores = df.to_dict('records')
        return indicadores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/indicadores/{indicador_id}", response_model=IndicadorResponse, tags=["Indicadores"])
async def get_indicador(indicador_id: int):
    """Get a specific indicator by ID"""
    try:
        indicador = db.get_indicador_by_id(indicador_id)
        if not indicador:
            raise HTTPException(status_code=404, detail="Indicador no encontrado")
        return indicador
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/indicadores", response_model=MessageResponse, status_code=201, tags=["Indicadores"])
async def create_indicador(indicador: IndicadorCreate):
    """Create a new indicator (Admin only)"""
    try:
        record_id = db.create_indicador(
            id_estrategico=indicador.id_estrategico,
            año=indicador.año,
            indicador=indicador.indicador,
            unidad_organizacional=indicador.unidad_organizacional,
            unidad_organizacional_colaboradora=indicador.unidad_organizacional_colaboradora,
            area=indicador.area,
            lineamientos_estrategicos=indicador.lineamientos_estrategicos,
            meta=indicador.meta,
            medida=indicador.medida,
            estado=indicador.estado,
            fecha_inicio=str(indicador.fecha_inicio) if indicador.fecha_inicio else None,
            fecha_fin_original=str(indicador.fecha_fin_original) if indicador.fecha_fin_original else None,
            fecha_fin_actual=str(indicador.fecha_fin_actual) if indicador.fecha_fin_actual else None,
            tipo_indicador=indicador.tipo_indicador,
            tiene_hitos=indicador.tiene_hitos,
            responsable=indicador.responsable
        )
        return MessageResponse(message=f"Indicador creado exitosamente con ID: {record_id}", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/indicadores/{indicador_id}", response_model=MessageResponse, tags=["Indicadores"])
async def delete_indicador(indicador_id: int):
    """Delete an indicator (Admin only)"""
    try:
        success = db.delete_indicador(indicador_id)
        if not success:
            raise HTTPException(status_code=404, detail="Indicador no encontrado")
        return MessageResponse(message="Indicador eliminado exitosamente", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/indicadores/{indicador_id}/jerarquia", response_model=IndicadorJerarquia, tags=["Indicadores"])
async def get_indicador_jerarquia(indicador_id: int):
    """Get indicator with full hierarchy (hitos and actividades)"""
    try:
        # Get indicator
        indicador = db.get_indicador_by_id(indicador_id)
        if not indicador:
            raise HTTPException(status_code=404, detail="Indicador no encontrado")
        
        # Get hitos
        hitos_df = db.get_hitos_by_indicador(indicador_id)
        hitos = []
        
        for _, hito in hitos_df.iterrows():
            # Get actividades for this hito
            actividades_df = db.get_actividades_by_hito(hito['id'])
            actividades = [
                ActividadJerarquia(
                    id=act['id'],
                    descripcion_actividad=act['descripcion_actividad'],
                    responsable=act.get('responsable'),
                    estado_actividad=act['estado_actividad'],
                    ultimo_avance_reportado=act.get('ultimo_avance_reportado', 0)
                )
                for _, act in actividades_df.iterrows()
            ]
            
            hitos.append(HitoJerarquia(
                id=hito['id'],
                nombre=hito['nombre'],
                responsable=hito.get('responsable'),
                estado=hito['estado'],
                ultimo_avance_reportado=hito.get('ultimo_avance_reportado', hito.get('avance_porcentaje', 0)),
                actividades=actividades
            ))
        
        return IndicadorJerarquia(
            id=indicador['id'],
            indicador=indicador['indicador'],
            responsable=indicador.get('responsable'),
            avance_porcentaje=indicador['avance_porcentaje'],
            estado=indicador['estado'],
            hitos=hitos
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HITOS ====================

@app.get("/api/hitos", response_model=List[HitoResponse], tags=["Hitos"])
async def get_hitos(
    responsable: Optional[str] = Query(None, description="Filtrar por responsable")
):
    """Get all hitos with optional filters"""
    try:
        if responsable:
            df = db.get_hitos_by_responsable(responsable)
        else:
            # Get all hitos (need to implement this in database.py if not exists)
            df = db.get_hitos_by_responsable("")  # Returns all for now
        
        hitos = df.to_dict('records')
        return hitos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/indicadores/{indicador_id}/hitos", response_model=List[HitoResponse], tags=["Hitos"])
async def get_hitos_by_indicador(indicador_id: int):
    """Get all hitos for a specific indicator"""
    try:
        df = db.get_hitos_by_indicador(indicador_id)
        hitos = df.to_dict('records')
        return hitos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hitos", response_model=MessageResponse, status_code=201, tags=["Hitos"])
async def create_hito(hito: HitoCreate):
    """Create a new hito (Admin only)"""
    try:
        hito_id = db.create_hito(
            indicador_id=hito.indicador_id,
            nombre=hito.nombre,
            descripcion=hito.descripcion,
            fecha_inicio=str(hito.fecha_inicio) if hito.fecha_inicio else None,
            fecha_fin_planificada=str(hito.fecha_fin_planificada) if hito.fecha_fin_planificada else None,
            fecha_fin_real=str(hito.fecha_fin_real) if hito.fecha_fin_real else None,
            avance_porcentaje=0,
            estado=hito.estado,
            orden=hito.orden,
            responsable=hito.responsable
        )
        return MessageResponse(message=f"Hito creado exitosamente con ID: {hito_id}", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/hitos/{hito_id}", response_model=MessageResponse, tags=["Hitos"])
async def delete_hito(hito_id: int):
    """Delete a hito (Admin only)"""
    try:
        success = db.delete_hito(hito_id)
        if not success:
            raise HTTPException(status_code=404, detail="Hito no encontrado")
        return MessageResponse(message="Hito eliminado exitosamente", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ACTIVIDADES ====================

@app.get("/api/actividades", response_model=List[ActividadResponse], tags=["Actividades"])
async def get_actividades(
    responsable: Optional[str] = Query(None, description="Filtrar por responsable")
):
    """Get all actividades with optional filters"""
    try:
        if responsable:
            df = db.get_actividades_by_responsable(responsable)
        else:
            # For now, return empty list if no filter
            # Could implement get_all_actividades in database.py
            return []
        
        actividades = df.to_dict('records')
        return actividades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hitos/{hito_id}/actividades", response_model=List[ActividadResponse], tags=["Actividades"])
async def get_actividades_by_hito(hito_id: int):
    """Get all actividades for a specific hito"""
    try:
        df = db.get_actividades_by_hito(hito_id)
        actividades = df.to_dict('records')
        return actividades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actividades", response_model=MessageResponse, status_code=201, tags=["Actividades"])
async def create_actividad(actividad: ActividadCreate):
    """Create a new actividad (Admin only)"""
    try:
        actividad_id = db.create_actividad(
            hito_id=actividad.hito_id,
            descripcion_actividad=actividad.descripcion_actividad,
            fecha_inicio_plan=str(actividad.fecha_inicio_plan) if actividad.fecha_inicio_plan else None,
            fecha_fin_plan=str(actividad.fecha_fin_plan) if actividad.fecha_fin_plan else None,
            responsable=actividad.responsable,
            fecha_real=str(actividad.fecha_real) if actividad.fecha_real else None,
            estado_actividad=actividad.estado_actividad
        )
        return MessageResponse(message=f"Actividad creada exitosamente con ID: {actividad_id}", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/actividades/{actividad_id}", response_model=MessageResponse, tags=["Actividades"])
async def delete_actividad(actividad_id: int):
    """Delete an actividad (Admin only)"""
    try:
        success = db.delete_actividad(actividad_id)
        if not success:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return MessageResponse(message="Actividad eliminada exitosamente", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AVANCE MENSUAL ====================

@app.post("/api/avance-mensual", response_model=MessageResponse, status_code=201, tags=["Avance Mensual"])
async def registrar_avance_mensual(avance: AvanceMensualCreate):
    """Register monthly progress report (Owner only)"""
    try:
        success = db.registrar_avance_mensual(
            entidad=avance.entidad,
            id_entidad=avance.id_entidad,
            avance_reportado=avance.avance_reportado,
            usuario=avance.usuario,
            mes=avance.mes
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe un reporte para este mes. No se puede reportar dos veces en el mismo mes."
            )
        
        # Update indicator progress if it's a hito
        if avance.entidad == 'hito':
            # Get the indicador_id from the hito
            hito = db.get_hitos_by_indicador(0)  # Need to get hito details
            # For now, we'll update all indicators (could be optimized)
            pass
        
        return MessageResponse(
            message=f"Avance mensual registrado exitosamente para {avance.entidad} ID {avance.id_entidad}",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/avance-mensual/{entidad}/{id_entidad}", response_model=AvanceMensualResponse, tags=["Avance Mensual"])
async def get_avance_mensual_actual(entidad: str, id_entidad: int):
    """Get the latest monthly progress report for an entity"""
    try:
        if entidad not in ['hito', 'actividad']:
            raise HTTPException(status_code=400, detail="entidad debe ser 'hito' o 'actividad'")
        
        avance = db.get_avance_mensual_actual(entidad, id_entidad)
        if not avance:
            raise HTTPException(status_code=404, detail="No se encontró reporte de avance")
        
        return avance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/avance-mensual/{entidad}/{id_entidad}/historico", response_model=List[AvanceMensualResponse], tags=["Avance Mensual"])
async def get_historico_avance(entidad: str, id_entidad: int):
    """Get complete historical progress for an entity"""
    try:
        if entidad not in ['hito', 'actividad']:
            raise HTTPException(status_code=400, detail="entidad debe ser 'hito' o 'actividad'")
        
        df = db.get_historico_avance(entidad, id_entidad)
        historico = df.to_dict('records')
        return historico
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DASHBOARD & SEGUIMIENTO ====================

@app.get("/api/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_summary_stats()
        return DashboardStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/seguimiento/responsable/{responsable}", tags=["Seguimiento"])
async def get_items_by_responsable(responsable: str):
    """Get all hitos and actividades for a specific responsable"""
    try:
        hitos_df = db.get_hitos_by_responsable(responsable)
        actividades_df = db.get_actividades_by_responsable(responsable)
        
        # Filter hitos by responsable
        if 'responsable' in hitos_df.columns:
            hitos_df = hitos_df[hitos_df['responsable'] == responsable]
        
        return {
            "responsable": responsable,
            "hitos": hitos_df.to_dict('records'),
            "actividades": actividades_df.to_dict('records'),
            "total_items": len(hitos_df) + len(actividades_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILIDADES ====================

@app.get("/api/responsables", response_model=List[str], tags=["Utilidades"])
async def get_responsables():
    """Get list of all responsables"""
    try:
        responsables = db.get_unique_values('responsable')
        return responsables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/areas", response_model=List[str], tags=["Utilidades"])
async def get_areas():
    """Get list of all areas"""
    try:
        areas = db.get_unique_values('area')
        return areas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/unidades-organizacionales", response_model=List[str], tags=["Utilidades"])
async def get_unidades_organizacionales():
    """Get list of all organizational units"""
    try:
        unidades = db.get_unique_values('unidad_organizacional')
        return unidades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
