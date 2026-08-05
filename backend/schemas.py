from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Milestones ──────────────────────────────────────────────────────────────

class MilestoneBase(BaseModel):
    id_hito: str
    id_indicador: str
    nombre_hito: Optional[str] = None
    orden: Optional[int] = 1
    estado: Optional[str] = "Por Comenzar"
    avance_pct: Optional[float] = 0
    fecha_inicio: Optional[str] = None
    fecha_fin_original: Optional[str] = None
    fecha_fin_actual: Optional[str] = None
    responsable: Optional[str] = None


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    nombre_hito: Optional[str] = None
    orden: Optional[int] = None
    estado: Optional[str] = None
    avance_pct: Optional[float] = None
    fecha_inicio: Optional[str] = None
    fecha_fin_original: Optional[str] = None
    fecha_fin_actual: Optional[str] = None


class Milestone(MilestoneBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ── Progress History ─────────────────────────────────────────────────────────

class ProgressHistoryBase(BaseModel):
    id_indicador: str
    periodo: Optional[str] = None
    avance_valor: Optional[float] = None
    avance_pct: Optional[float] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


class ProgressHistoryCreate(ProgressHistoryBase):
    pass


class ProgressHistory(ProgressHistoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_actualizacion: Optional[datetime] = None


# ── Indicators ───────────────────────────────────────────────────────────────

class IndicatorBase(BaseModel):
    id_indicador: str
    id_objetivo: str
    unidad_organizacional: Optional[str] = None
    division_area: Optional[str] = None
    lineamiento: Optional[str] = None
    objetivo_anual: Optional[str] = None
    indicador: Optional[str] = None
    acciones: Optional[str] = None
    resultado_esperado: Optional[str] = None
    tipo_objetivo: Optional[str] = None
    clasificacion: Optional[str] = None
    unidad_medida: Optional[str] = None
    meta: Optional[float] = None
    avance_valor: Optional[float] = 0
    avance_pct: Optional[float] = 0
    estado: Optional[str] = "Por Comenzar"
    uo_colaboradora: Optional[str] = None
    area_colabora: Optional[str] = None
    tiene_hitos: Optional[str] = "No"
    fecha_inicio: Optional[str] = None
    fecha_fin_original: Optional[str] = None
    fecha_fin_actual: Optional[str] = None
    notas: Optional[str] = None
    responsable: Optional[str] = None
    responsable_carga: Optional[str] = None


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    id_objetivo: Optional[str] = None
    unidad_organizacional: Optional[str] = None
    division_area: Optional[str] = None
    lineamiento: Optional[str] = None
    objetivo_anual: Optional[str] = None
    indicador: Optional[str] = None
    acciones: Optional[str] = None
    resultado_esperado: Optional[str] = None
    tipo_objetivo: Optional[str] = None
    clasificacion: Optional[str] = None
    unidad_medida: Optional[str] = None
    meta: Optional[float] = None
    avance_valor: Optional[float] = None
    avance_pct: Optional[float] = None
    estado: Optional[str] = None
    uo_colaboradora: Optional[str] = None
    area_colabora: Optional[str] = None
    tiene_hitos: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin_original: Optional[str] = None
    fecha_fin_actual: Optional[str] = None
    notas: Optional[str] = None
    responsable: Optional[str] = None
    responsable_carga: Optional[str] = None


class ProgressUpdate(BaseModel):
    avance_valor: Optional[float] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    periodo: Optional[str] = None


class Indicator(IndicatorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    milestones: List[Milestone] = []
    history: List[ProgressHistory] = []


class IndicatorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_indicador: str
    id_objetivo: str
    unidad_organizacional: Optional[str] = None
    division_area: Optional[str] = None
    indicador: Optional[str] = None
    meta: Optional[float] = None
    avance_valor: Optional[float] = None
    avance_pct: Optional[float] = None
    estado: Optional[str] = None
    unidad_medida: Optional[str] = None
    tiene_hitos: Optional[str] = None
    lineamiento: Optional[str] = None
    tipo_objetivo: Optional[str] = None
    clasificacion: Optional[str] = None
    fecha_fin_actual: Optional[str] = None


# ── Combined create ──────────────────────────────────────────────────────────

class MilestoneInline(BaseModel):
    nombre_hito: str
    orden: Optional[int] = 1
    estado: Optional[str] = "Por Comenzar"
    avance_pct: Optional[float] = 0
    fecha_inicio: Optional[str] = None
    fecha_fin_original: Optional[str] = None
    fecha_fin_actual: Optional[str] = None
    responsable: Optional[str] = None


class IndicatorWithMilestonesCreate(IndicatorBase):
    milestones: Optional[List[MilestoneInline]] = []


# ── Objectives ───────────────────────────────────────────────────────────────

class ObjectiveBase(BaseModel):
    id_objetivo: str
    objetivo_institucional: Optional[str] = None
    objetivo_anual: Optional[str] = None
    lineamiento: Optional[str] = None
    tipo_objetivo: Optional[str] = None
    unidades_organizacionales: Optional[str] = None


class ObjectiveCreate(ObjectiveBase):
    pass


class ObjectiveUpdate(BaseModel):
    objetivo_institucional: Optional[str] = None
    objetivo_anual: Optional[str] = None
    lineamiento: Optional[str] = None
    tipo_objetivo: Optional[str] = None
    unidades_organizacionales: Optional[str] = None


class Objective(ObjectiveBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    n_indicadores: Optional[int] = 0
    avance_promedio_pct: Optional[float] = 0


class ObjectiveWithIndicators(Objective):
    indicators: List[IndicatorSummary] = []


# ── Snapshots ────────────────────────────────────────────────────────────────

class SnapshotCreate(BaseModel):
    periodo: str
    descripcion: Optional[str] = None


class Snapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    periodo: str
    fecha_creacion: Optional[datetime] = None
    descripcion: Optional[str] = None


# ── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_objectives: int
    total_indicators: int
    total_milestones: int
    avance_general: float
    by_estado: dict
    by_lineamiento: dict
    by_unidad: dict
    top_objectives: list
    recent_history: list
