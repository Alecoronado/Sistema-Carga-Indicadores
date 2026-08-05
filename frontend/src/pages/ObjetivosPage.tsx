import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { indicatorsApi, milestonesApi, objectivesApi } from '../api'
import ProgressBar from '../components/ProgressBar'
import StatusBadge from '../components/StatusBadge'
import { ChevronDown, ChevronRight, Target, BarChart2, ListChecks } from 'lucide-react'

const LINEAMIENTO_COLORS: Record<string, { border: string; badge: string; dot: string }> = {
  'Excelencia Operacional':    { border: 'border-l-indigo-400', badge: 'bg-indigo-100 text-indigo-700',  dot: 'bg-indigo-400' },
  'Alineación Estratégica':    { border: 'border-l-violet-400', badge: 'bg-violet-100 text-violet-700',  dot: 'bg-violet-400' },
  'Eficiencia Organizacional': { border: 'border-l-emerald-400',badge: 'bg-emerald-100 text-emerald-700',dot: 'bg-emerald-400' },
  'Solidez Financiera':        { border: 'border-l-amber-400',  badge: 'bg-amber-100 text-amber-700',    dot: 'bg-amber-400' },
  'Complementariedad':         { border: 'border-l-cyan-400',   badge: 'bg-cyan-100 text-cyan-700',      dot: 'bg-cyan-400' },
}

const ALL_LINEAMIENTOS = Object.keys(LINEAMIENTO_COLORS)

function HitoRow({ hito }: { hito: any }) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-slate-50 text-xs border-b border-slate-100 last:border-0">
      <span className="font-mono text-slate-400 w-20 shrink-0">{hito.id_hito}</span>
      <span className="flex-1 text-slate-600">{hito.nombre_hito ?? '—'}</span>
      <div className="w-20 shrink-0"><ProgressBar value={hito.avance_pct ?? 0} size="xs" /></div>
      <StatusBadge status={hito.estado ?? 'Por Comenzar'} size="sm" />
    </div>
  )
}

function IndicatorRow({ ind, hitos }: { ind: any; hitos: any[] }) {
  const [open, setOpen] = useState(false)
  const hasHitos = ind.tiene_hitos === 'Si' && hitos.length > 0

  return (
    <div className="border border-slate-100 rounded-xl overflow-hidden mb-2">
      {/* Indicator header row */}
      <div
        className={`flex items-center gap-3 px-4 py-3 bg-white hover:bg-slate-50 transition-colors ${hasHitos ? 'cursor-pointer' : ''}`}
        onClick={() => hasHitos && setOpen(o => !o)}
      >
        {/* expand icon */}
        <div className="w-4 shrink-0 text-slate-300">
          {hasHitos
            ? (open ? <ChevronDown size={14} /> : <ChevronRight size={14} />)
            : <span className="block w-4" />}
        </div>

        <span className="font-mono text-xs font-bold text-indigo-600 w-14 shrink-0">{ind.id_indicador}</span>

        <span className="flex-1 text-sm text-slate-700 line-clamp-2">{ind.indicador}</span>

        <div className="flex items-center gap-4 shrink-0">
          {ind.meta != null && (
            <span className="text-xs text-slate-400">
              Meta: <span className="font-semibold text-slate-600">{ind.meta}{ind.unidad_medida ? ` ${ind.unidad_medida}` : ''}</span>
            </span>
          )}
          <div className="w-24"><ProgressBar value={ind.avance_pct ?? 0} size="xs" /></div>
          <StatusBadge status={ind.estado ?? 'Por Comenzar'} size="sm" />
          {hasHitos && (
            <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">
              {hitos.length} hito{hitos.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Hitos list */}
      {open && hasHitos && (
        <div className="bg-slate-50 border-t border-slate-100 px-4 py-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            <ListChecks size={12} /> Hitos
          </div>
          {hitos.map(h => <HitoRow key={h.id_hito} hito={h} />)}
        </div>
      )}
    </div>
  )
}

function ObjectiveCard({
  obj, indicators, milestonesByIndicator,
}: {
  obj: any
  indicators: any[]
  milestonesByIndicator: Record<string, any[]>
}) {
  const [open, setOpen] = useState(false)
  const colors = LINEAMIENTO_COLORS[obj.lineamiento ?? ''] ?? { border: 'border-l-slate-300', badge: 'bg-slate-100 text-slate-600', dot: 'bg-slate-300' }

  const avance = obj.avance_promedio_pct ?? 0
  const nInd = indicators.length

  return (
    <div className={`card border-l-4 ${colors.border} overflow-hidden`}>
      {/* Objective header */}
      <div
        className="flex items-start gap-4 px-5 py-4 cursor-pointer hover:bg-slate-50 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        <div className="pt-0.5 shrink-0 text-slate-400">
          {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </div>

        <div className="flex-1 min-w-0">
          {/* Top line */}
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-mono text-xs font-black text-slate-500">{obj.id_objetivo}</span>
            {obj.lineamiento && (
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge}`}>
                {obj.lineamiento}
              </span>
            )}
          </div>

          {/* Objetivo institucional */}
          <p className="text-sm font-bold text-slate-800 leading-snug">{obj.objetivo_institucional}</p>

          {/* Objetivo anual */}
          {obj.objetivo_anual && obj.objetivo_anual !== obj.objetivo_institucional && (
            <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{obj.objetivo_anual}</p>
          )}
        </div>

        {/* Stats */}
        <div className="flex items-center gap-5 shrink-0 text-right">
          <div>
            <p className="text-xs text-slate-400">Indicadores</p>
            <p className="text-lg font-black text-slate-700 tabular-nums">{nInd}</p>
          </div>
          <div className="w-28">
            <p className="text-xs text-slate-400 mb-1">Avance</p>
            <ProgressBar value={avance} size="xs" />
            <p className="text-xs font-bold text-slate-600 mt-0.5 tabular-nums text-right">{avance.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Expanded: indicators list */}
      {open && (
        <div className="border-t border-slate-100 px-5 py-4 bg-slate-50/50">
          {indicators.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-4">Sin indicadores registrados</p>
          ) : (
            <div>
              {/* Column headers */}
              <div className="flex items-center gap-3 px-4 mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wide">
                <span className="w-4" />
                <span className="w-14 shrink-0">ID</span>
                <span className="flex-1">Indicador</span>
                <span className="shrink-0 w-72 text-right">Avance · Estado</span>
              </div>
              {indicators.map(ind => (
                <IndicatorRow
                  key={ind.id_indicador}
                  ind={ind}
                  hitos={milestonesByIndicator[ind.id_indicador] ?? []}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function ObjetivosPage() {
  const [selLineamiento, setSelLineamiento] = useState('')

  const { data: objectives = [] } = useQuery({
    queryKey: ['objectives'],
    queryFn: objectivesApi.list,
  })
  const { data: indicators = [] } = useQuery({
    queryKey: ['indicators'],
    queryFn: () => indicatorsApi.list(),
  })
  const { data: milestones = [] } = useQuery({
    queryKey: ['milestones'],
    queryFn: () => milestonesApi.list(),
  })

  // Index indicators by objective
  const indByObj = useMemo(() => {
    const map: Record<string, any[]> = {}
    for (const ind of indicators) {
      if (!map[ind.id_objetivo]) map[ind.id_objetivo] = []
      map[ind.id_objetivo].push(ind)
    }
    return map
  }, [indicators])

  // Index milestones by indicator
  const milestonesByIndicator = useMemo(() => {
    const map: Record<string, any[]> = {}
    for (const m of milestones) {
      if (!map[m.id_indicador]) map[m.id_indicador] = []
      map[m.id_indicador].push(m)
    }
    return map
  }, [milestones])

  // Filtered objectives (exclude placeholder)
  const filtered = useMemo(() =>
    objectives.filter(o =>
      o.id_objetivo !== 'SIN_ASIGNAR' &&
      (!selLineamiento || o.lineamiento === selLineamiento)
    ),
    [objectives, selLineamiento]
  )

  // Stats
  const totalInd = indicators.filter(i => !selLineamiento || i.lineamiento === selLineamiento).length
  const avanceGlobal = filtered.length
    ? filtered.reduce((s, o) => s + (o.avance_promedio_pct ?? 0), 0) / filtered.length
    : 0

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900">Objetivos e Indicadores</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Estructura jerárquica: Objetivo Institucional → Indicadores → Hitos
        </p>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card kpi-blue p-4 flex items-center gap-3">
          <Target size={22} className="text-blue-400 shrink-0" />
          <div>
            <p className="text-xs text-slate-500 uppercase font-semibold tracking-wide">Objetivos</p>
            <p className="text-2xl font-black text-blue-600 tabular-nums">{filtered.length}</p>
          </div>
        </div>
        <div className="card kpi-violet p-4 flex items-center gap-3">
          <BarChart2 size={22} className="text-violet-400 shrink-0" />
          <div>
            <p className="text-xs text-slate-500 uppercase font-semibold tracking-wide">Indicadores</p>
            <p className="text-2xl font-black text-violet-600 tabular-nums">{totalInd}</p>
          </div>
        </div>
        <div className="card kpi-green p-4 flex items-center gap-3">
          <div className="flex-1">
            <p className="text-xs text-slate-500 uppercase font-semibold tracking-wide">Avance Promedio</p>
            <p className="text-2xl font-black text-emerald-600 tabular-nums">{avanceGlobal.toFixed(1)}%</p>
          </div>
          <div className="w-24">
            <ProgressBar value={avanceGlobal} size="sm" showLabel={false} />
          </div>
        </div>
      </div>

      {/* Lineamiento filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelLineamiento('')}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
            selLineamiento === ''
              ? 'bg-slate-700 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          Todos los lineamientos
        </button>
        {ALL_LINEAMIENTOS.map(lin => {
          const c = LINEAMIENTO_COLORS[lin]
          const active = selLineamiento === lin
          return (
            <button
              key={lin}
              onClick={() => setSelLineamiento(l => l === lin ? '' : lin)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                active ? c.badge + ' ring-2 ring-offset-1 ring-current' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${c.dot}`} />
              {lin}
            </button>
          )
        })}
      </div>

      {/* Objective cards */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="card p-12 text-center text-slate-400 text-sm">
            No hay objetivos para mostrar
          </div>
        ) : (
          filtered.map(obj => (
            <ObjectiveCard
              key={obj.id_objetivo}
              obj={obj}
              indicators={indByObj[obj.id_objetivo] ?? []}
              milestonesByIndicator={milestonesByIndicator}
            />
          ))
        )}
      </div>
    </div>
  )
}
