export interface Objective {
  id: number
  id_objetivo: string
  objetivo_institucional?: string
  objetivo_anual?: string
  lineamiento?: string
  tipo_objetivo?: string
  unidades_organizacionales?: string
  n_indicadores: number
  avance_promedio_pct: number
  indicators?: IndicatorSummary[]
}

export interface IndicatorSummary {
  id: number
  id_indicador: string
  id_objetivo: string
  unidad_organizacional?: string
  division_area?: string
  indicador?: string
  meta?: number
  avance_valor?: number
  avance_pct?: number
  estado?: string
  unidad_medida?: string
  tiene_hitos?: string
  lineamiento?: string
  tipo_objetivo?: string
  clasificacion?: string
  fecha_inicio?: string
  fecha_fin_actual?: string
  responsable?: string
}

export interface Indicator extends IndicatorSummary {
  objetivo_anual?: string
  acciones?: string
  resultado_esperado?: string
  uo_colaboradora?: string
  area_colabora?: string
  fecha_inicio?: string
  fecha_fin_original?: string
  notas?: string
  responsable_carga?: string
  created_at?: string
  updated_at?: string
  milestones: Milestone[]
  history: ProgressHistory[]
}

export interface Milestone {
  id: number
  id_hito: string
  id_indicador: string
  nombre_hito?: string
  orden?: number
  estado?: string
  avance_pct?: number
  fecha_inicio?: string
  fecha_fin_original?: string
  fecha_fin_actual?: string
  responsable?: string
}

export interface MilestoneInline {
  nombre_hito: string
  orden?: number
  estado?: string
  avance_pct?: number
  fecha_inicio?: string
  fecha_fin_original?: string
  fecha_fin_actual?: string
  responsable?: string
}

export interface ProgressHistory {
  id: number
  id_indicador: string
  periodo?: string
  avance_valor?: number
  avance_pct?: number
  estado?: string
  notas?: string
  fecha_actualizacion?: string
}

export interface Snapshot {
  id: number
  periodo: string
  fecha_creacion?: string
  descripcion?: string
}

export interface DashboardStats {
  total_objectives: number
  total_indicators: number
  total_milestones: number
  avance_general: number
  by_estado: Record<string, number>
  by_lineamiento: Record<string, { count: number; avance_pct: number }>
  by_unidad: Record<string, { count: number; avance_pct: number }>
  top_objectives: Array<{
    id_objetivo: string
    objetivo_anual: string
    lineamiento: string
    n_indicadores: number
    avance_promedio_pct: number
  }>
  recent_history: Array<{
    id_indicador: string
    periodo?: string
    avance_pct?: number
    estado?: string
    notas?: string
    fecha_actualizacion?: string
  }>
}

export const ESTADOS = ['Por Comenzar', 'En Progreso', 'Completado', 'Retrasado', 'En Riesgo'] as const
export const LINEAMIENTOS = [
  'Excelencia Operacional',
  'Alineación Estratégica',
  'Eficiencia Organizacional',
  'Solidez Financiera',
  'Complementariedad',
] as const
export const TIPOS_OBJETIVO = ['Estratégico', 'Regular', 'Táctico'] as const
export const UNIDADES_ORG = ['VPO', 'VPD', 'PRE', 'VPF', 'VPE'] as const
export const UNIDADES_MEDIDA = ['#', '%', 'USD', 'M USD'] as const
export const CLASIFICACIONES = ['Prioritarios', 'Tácticos'] as const
