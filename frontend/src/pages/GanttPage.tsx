import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { indicatorsApi, milestonesApi } from '../api'
import StatusBadge from '../components/StatusBadge'
import { UNIDADES_ORG } from '../types'

const MONTHS = ['Ene', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
const YEAR = 2026
const STATUS_COLORS: Record<string, string> = {
  'Por Comenzar': '#cbd5e1',
  'En Progreso':  '#60a5fa',
  'Completado':   '#34d399',
  'Retrasado':    '#f87171',
  'En Riesgo':    '#fbbf24',
}

function monthOffset(dateStr?: string | null): number {
  if (!dateStr) return 0
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return 0
    if (d.getFullYear() < YEAR) return 0
    if (d.getFullYear() > YEAR) return 12
    return d.getMonth()
  } catch { return 0 }
}

function monthEnd(dateStr?: string | null): number {
  if (!dateStr) return 12
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return 12
    if (d.getFullYear() < YEAR) return 0
    if (d.getFullYear() > YEAR) return 12
    return d.getMonth() + 1
  } catch { return 12 }
}

export default function GanttPage() {
  const [selVP, setSelVP] = useState('')
  const [groupBy, setGroupBy] = useState<'indicator' | 'hito'>('indicator')

  const { data: indicators = [] } = useQuery({
    queryKey: ['indicators'],
    queryFn: () => indicatorsApi.list(),
  })
  const { data: milestones = [] } = useQuery({
    queryKey: ['milestones'],
    queryFn: () => milestonesApi.list(),
  })

  const filtered = useMemo(() =>
    indicators.filter(i => !selVP || i.unidad_organizacional === selVP), [indicators, selVP])

  const rows: { id: string; label: string; sub: string; start: number; end: number; avance: number; estado: string }[] = useMemo(() => {
    if (groupBy === 'indicator') {
      return filtered.map(ind => ({
        id: ind.id_indicador,
        label: ind.id_indicador,
        sub: (ind.indicador ?? '').slice(0, 60),
        start: monthOffset(ind.fecha_inicio),
        end: monthEnd(ind.fecha_fin_actual),
        avance: ind.avance_pct ?? 0,
        estado: ind.estado ?? 'Por Comenzar',
      }))
    } else {
      const filteredIds = new Set(filtered.map(i => i.id_indicador))
      return milestones
        .filter(m => filteredIds.has(m.id_indicador))
        .map(m => ({
          id: m.id_hito,
          label: m.id_hito,
          sub: (m.nombre_hito ?? '').slice(0, 60),
          start: monthOffset(m.fecha_inicio),
          end: monthEnd(m.fecha_fin_actual),
          avance: m.avance_pct ?? 0,
          estado: m.estado ?? 'Por Comenzar',
        }))
    }
  }, [filtered, milestones, groupBy])

  const CELL_WIDTH = 60

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Gantt — Plan 2026</h1>
          <p className="text-sm text-slate-500 mt-0.5">Visualización temporal de indicadores y hitos</p>
        </div>
      </div>

      {/* Controls */}
      <div className="card p-4 flex flex-wrap gap-4">
        <div>
          <label className="field-label">Vicepresidencia</label>
          <select value={selVP} onChange={e => setSelVP(e.target.value)} className="field-input w-36">
            <option value="">Todas</option>
            {UNIDADES_ORG.map(u => <option key={u}>{u}</option>)}
          </select>
        </div>
        <div>
          <label className="field-label">Agrupar por</label>
          <div className="flex rounded-lg border border-slate-200 overflow-hidden">
            <button
              onClick={() => setGroupBy('indicator')}
              className={`px-4 py-2.5 text-sm font-medium transition-colors ${groupBy === 'indicator' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
            >
              Indicadores
            </button>
            <button
              onClick={() => setGroupBy('hito')}
              className={`px-4 py-2.5 text-sm font-medium transition-colors ${groupBy === 'hito' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
            >
              Hitos
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-end gap-4 ml-auto flex-wrap">
          {Object.entries(STATUS_COLORS).map(([status, color]) => (
            <div key={status} className="flex items-center gap-1.5 text-xs text-slate-500">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
              {status}
            </div>
          ))}
        </div>
      </div>

      {/* Gantt chart */}
      <div className="card overflow-x-auto">
        <div style={{ minWidth: 240 + CELL_WIDTH * 12 }}>
          {/* Header months */}
          <div className="flex border-b border-slate-200 bg-slate-50 sticky top-0 z-10">
            <div className="w-60 shrink-0 px-4 py-3 text-xs font-semibold text-slate-500 uppercase border-r border-slate-200">
              {groupBy === 'indicator' ? 'Indicador' : 'Hito'}
            </div>
            {MONTHS.map((m, i) => (
              <div key={i} style={{ width: CELL_WIDTH }} className="text-center py-3 text-xs font-semibold text-slate-500 border-r border-slate-100 shrink-0">
                {m}
              </div>
            ))}
          </div>

          {/* Rows */}
          {rows.length === 0 ? (
            <div className="py-16 text-center text-slate-400 text-sm">No hay datos para mostrar</div>
          ) : (
            rows.map(row => {
              const barStart = row.start
              const barSpan = Math.max(row.end - row.start, 0.5)
              const color = STATUS_COLORS[row.estado] ?? '#cbd5e1'
              return (
                <div key={row.id} className="flex items-center border-b border-slate-100 hover:bg-slate-50 transition-colors group">
                  {/* Label */}
                  <div className="w-60 shrink-0 px-4 py-2.5 border-r border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-indigo-600">{row.label}</span>
                      <StatusBadge status={row.estado} size="sm" />
                    </div>
                    <div className="text-xs text-slate-500 line-clamp-1 mt-0.5">{row.sub}</div>
                  </div>

                  {/* Timeline cells */}
                  <div className="flex relative" style={{ position: 'relative' }}>
                    {MONTHS.map((_, mi) => (
                      <div key={mi}
                        className="border-r border-slate-100 shrink-0"
                        style={{ height: 52, width: CELL_WIDTH }}>
                      </div>
                    ))}

                    {/* Gantt bar */}
                    <div
                      className="absolute rounded-md flex items-center px-2 text-xs font-semibold text-white overflow-hidden"
                      style={{
                        left: barStart * CELL_WIDTH + 4,
                        width: Math.max(barSpan * CELL_WIDTH - 8, 8),
                        top: 10,
                        height: 32,
                        backgroundColor: color,
                        opacity: 0.9,
                      }}
                      title={`${row.label}: ${row.avance.toFixed(0)}% — ${row.estado}`}
                    >
                      {barSpan > 1.5 && (
                        <>
                          <div
                            className="absolute left-0 top-0 h-full rounded-l-md opacity-40"
                            style={{ width: `${row.avance}%`, backgroundColor: 'rgba(0,0,0,0.3)' }}
                          />
                          <span className="relative z-10 truncate">{row.avance.toFixed(0)}%</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      <p className="text-xs text-slate-400 text-center">
        Mostrando {rows.length} {groupBy === 'indicator' ? 'indicadores' : 'hitos'}
        {selVP ? ` · VP: ${selVP}` : ''}
      </p>
    </div>
  )
}
