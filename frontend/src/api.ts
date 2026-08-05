import axios from 'axios'
import type {
  Objective, Indicator, IndicatorSummary, Milestone,
  ProgressHistory, Snapshot, DashboardStats
} from './types'

const http = axios.create({ baseURL: '/api' })

// ── Objectives ───────────────────────────────────────────────────────────────
export const objectivesApi = {
  list: () => http.get<Objective[]>('/objectives/').then(r => r.data),
  get: (id: string) => http.get<Objective>(`/objectives/${id}`).then(r => r.data),
  create: (data: Partial<Objective>) => http.post<Objective>('/objectives/', data).then(r => r.data),
  update: (id: string, data: Partial<Objective>) =>
    http.put<Objective>(`/objectives/${id}`, data).then(r => r.data),
  delete: (id: string) => http.delete(`/objectives/${id}`),
}

// ── Indicators ───────────────────────────────────────────────────────────────
export const indicatorsApi = {
  list: (params?: {
    id_objetivo?: string
    unidad_organizacional?: string
    estado?: string
    lineamiento?: string
    clasificacion?: string
    search?: string
  }) => http.get<IndicatorSummary[]>('/indicators/', { params }).then(r => r.data),
  get: (id: string) => http.get<Indicator>(`/indicators/${id}`).then(r => r.data),
  createWithMilestones: (data: any) => http.post<Indicator>('/indicators/with-milestones', data).then(r => r.data),
  create: (data: Partial<Indicator>) => http.post<Indicator>('/indicators/', data).then(r => r.data),
  update: (id: string, data: Partial<Indicator>) =>
    http.put<Indicator>(`/indicators/${id}`, data).then(r => r.data),
  updateProgress: (id: string, data: { avance_valor?: number; estado?: string; notas?: string; periodo?: string }) =>
    http.post<Indicator>(`/indicators/${id}/progress`, data).then(r => r.data),
  delete: (id: string) => http.delete(`/indicators/${id}`),
  history: (id: string) => http.get<ProgressHistory[]>(`/indicators/${id}/history`).then(r => r.data),
}

// ── Milestones ───────────────────────────────────────────────────────────────
export const milestonesApi = {
  list: (id_indicador?: string) =>
    http.get<Milestone[]>('/milestones/', { params: id_indicador ? { id_indicador } : {} }).then(r => r.data),
  get: (id: string) => http.get<Milestone>(`/milestones/${id}`).then(r => r.data),
  create: (data: Partial<Milestone>) => http.post<Milestone>('/milestones/', data).then(r => r.data),
  update: (id: string, data: Partial<Milestone>) =>
    http.put<Milestone>(`/milestones/${id}`, data).then(r => r.data),
  delete: (id: string) => http.delete(`/milestones/${id}`),
}

// ── Snapshots ────────────────────────────────────────────────────────────────
export const snapshotsApi = {
  list: () => http.get<Snapshot[]>('/snapshots/').then(r => r.data),
  get: (id: number) => http.get(`/snapshots/${id}`).then(r => r.data),
  create: (data: { periodo: string; descripcion?: string }) =>
    http.post<Snapshot>('/snapshots/', data).then(r => r.data),
  delete: (id: number) => http.delete(`/snapshots/${id}`),
  exportExcel: (id: number) => {
    window.open(`/api/export/snapshot/${id}/excel`, '_blank')
  },
}

// ── Export ───────────────────────────────────────────────────────────────────
export const exportApi = {
  excel: () => { window.open('/api/export/excel', '_blank') },
}

// ── Dashboard ────────────────────────────────────────────────────────────────
export const dashboardApi = {
  stats: () => http.get<DashboardStats>('/dashboard/stats').then(r => r.data),
}
