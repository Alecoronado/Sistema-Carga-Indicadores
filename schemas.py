"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ==================== INDICADORES ====================

class IndicadorBase(BaseModel):
    id_estrategico: Optional[str] = None
    año: int = Field(..., ge=2020, le=2030)
    indicador: str = Field(..., min_length=1)
    unidad_organizacional: Optional[str] = None
    unidad_organizacional_colaboradora: Optional[str] = None
    area: Optional[str] = None
    lineamientos_estrategicos: Optional[str] = None
    meta: Optional[str] = None
    medida: Optional[str] = None
    estado: str = "Por comenzar"
    fecha_inicio: Optional[date] = None
    fecha_fin_original: Optional[date] = None
    fecha_fin_actual: Optional[date] = None
    tipo_indicador: str
    tiene_hitos: bool = False
    responsable: Optional[str] = None


class IndicadorCreate(IndicadorBase):
    """Schema for creating a new indicator"""
    pass


class IndicadorUpdate(BaseModel):
    """Schema for updating an indicator (all fields optional)"""
    id_estrategico: Optional[str] = None
    año: Optional[int] = Field(None, ge=2020, le=2030)
    indicador: Optional[str] = None
    unidad_organizacional: Optional[str] = None
    unidad_organizacional_colaboradora: Optional[str] = None
    area: Optional[str] = None
    lineamientos_estrategicos: Optional[str] = None
    meta: Optional[str] = None
    medida: Optional[str] = None
    estado: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin_original: Optional[date] = None
    fecha_fin_actual: Optional[date] = None
    tipo_indicador: Optional[str] = None
    tiene_hitos: Optional[bool] = None
    responsable: Optional[str] = None


class IndicadorResponse(IndicadorBase):
    """Schema for indicator response"""
    id: int
    avance: Optional[float] = None
    avance_porcentaje: int = 0
    fecha_carga: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== HITOS ====================

class HitoBase(BaseModel):
    indicador_id: int
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin_planificada: Optional[date] = None
    fecha_fin_real: Optional[date] = None
    estado: str = "Por comenzar"
    orden: Optional[int] = None
    responsable: Optional[str] = None


class HitoCreate(HitoBase):
    """Schema for creating a new hito"""
    pass


class HitoUpdate(BaseModel):
    """Schema for updating a hito (all fields optional)"""
    indicador_id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin_planificada: Optional[date] = None
    fecha_fin_real: Optional[date] = None
    estado: Optional[str] = None
    orden: Optional[int] = None
    responsable: Optional[str] = None


class HitoResponse(HitoBase):
    """Schema for hito response"""
    id: int
    avance_porcentaje: int = 0
    fecha_carga: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ultimo_avance_reportado: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== ACTIVIDADES ====================

class ActividadBase(BaseModel):
    hito_id: int
    descripcion_actividad: str = Field(..., min_length=1)
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable: Optional[str] = None
    fecha_real: Optional[date] = None
    estado_actividad: str = "Por comenzar"


class ActividadCreate(ActividadBase):
    """Schema for creating a new actividad"""
    pass


class ActividadUpdate(BaseModel):
    """Schema for updating an actividad (all fields optional)"""
    hito_id: Optional[int] = None
    descripcion_actividad: Optional[str] = None
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable: Optional[str] = None
    fecha_real: Optional[date] = None
    estado_actividad: Optional[str] = None


class ActividadResponse(ActividadBase):
    """Schema for actividad response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ultimo_avance_reportado: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== AVANCE MENSUAL ====================

class AvanceMensualCreate(BaseModel):
    """Schema for creating a monthly progress report"""
    entidad: str = Field(..., pattern="^(hito|actividad)$")
    id_entidad: int
    avance_reportado: int = Field(..., ge=0, le=100)
    usuario: Optional[str] = None
    mes: Optional[str] = None  # YYYY-MM format, defaults to current month


class AvanceMensualResponse(BaseModel):
    """Schema for monthly progress response"""
    id: int
    entidad: str
    id_entidad: int
    mes: str
    avance_reportado: int
    fecha_reporte: Optional[date] = None
    usuario: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== DASHBOARD & STATS ====================

class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total: int
    por_comenzar: int
    en_progreso: int
    completado: int
    avg_avance: float


# ==================== JERARQUIA ====================

class ActividadJerarquia(BaseModel):
    """Actividad with hierarchy info"""
    id: int
    descripcion_actividad: str
    responsable: Optional[str] = None
    estado_actividad: str
    ultimo_avance_reportado: int


class HitoJerarquia(BaseModel):
    """Hito with hierarchy info including actividades"""
    id: int
    nombre: str
    responsable: Optional[str] = None
    estado: str
    ultimo_avance_reportado: int
    actividades: List[ActividadJerarquia] = []


class IndicadorJerarquia(BaseModel):
    """Indicador with full hierarchy"""
    id: int
    indicador: str
    responsable: Optional[str] = None
    avance_porcentaje: int
    estado: str
    hitos: List[HitoJerarquia] = []


# ==================== UTILITY RESPONSES ====================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error: bool = True
