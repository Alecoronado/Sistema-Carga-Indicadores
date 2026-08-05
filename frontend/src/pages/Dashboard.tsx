import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api'
import ProgressBar from '../components/ProgressBar'
import StatusBadge from '../components/StatusBadge'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { TrendingUp, CheckCircle, Clock, AlertCircle, BarChart2, RefreshCw, type LucideIcon } from 'lucide-react'

function KpiCard({
  label, value, icon: Icon, colorClass, textColor
}: {
  label: string; value: number | string
  icon: LucideIcon
  colorClass: string; textColor: string
}) {
  return (
    <div className={`card ${colorClass} flex items-center gap-4 p-5`}>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</p>
        <p className={`text-3xl font-black mt-1 tabular-nums ${textColor}`}>{value}</p>
      </div>
      <Icon size={28} className={`shrink-0 opacity-30 ${textColor}`} />
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.stats,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }
  if (!stats) return null

  const completados = stats.by_estado['Completado'] ?? 0
  const enProgreso = stats.by_estado['En Progreso'] ?? 0
  const porComenzar = stats.by_estado['Por Comenzar'] ?? 0

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">Monitoreo de indicadores y progreso de proyectos</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-white border border-slate-200 rounded-lg px-3 py-2">
          <Clock size={13} />
          {format(new Date(), "d 'de' MMMM yyyy", { locale: es })}
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard label="Total Indicadores" value={stats.total_indicators}
          icon={BarChart2} colorClass="kpi-blue" textColor="text-blue-600" />
        <KpiCard label="Total Hitos" value={stats.total_milestones}
          icon={CheckCircle} colorClass="kpi-violet" textColor="text-violet-600" />
        <KpiCard label="Completados" value={completados}
          icon={CheckCircle} colorClass="kpi-green" textColor="text-emerald-600" />
        <KpiCard label="En Progreso" value={enProgreso}
          icon={TrendingUp} colorClass="kpi-amber" textColor="text-amber-600" />
        <KpiCard label="Por Comenzar" value={porComenzar}
          icon={AlertCircle} colorClass="kpi-slate" textColor="text-slate-500" />
      </div>

      {/* Avance promedio */}
      <div className="card p-6 flex items-center gap-6" style={{ borderLeft: '4px solid #7c3aed' }}>
        <div className="flex-1">
          <p className="text-sm font-semibold text-slate-600 mb-1">Avance Promedio de Indicadores</p>
          <div className="flex items-end gap-3">
            <span className="text-4xl font-black text-violet-600 tabular-nums">
              {stats.avance_general.toFixed(1)}%
            </span>
            <TrendingUp size={20} className="text-violet-400 mb-1.5" />
          </div>
        </div>
        <div className="flex-1">
          <ProgressBar value={stats.avance_general} size="md" color="#7c3aed" />
        </div>
        <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-sm shrink-0">
          {Object.entries(stats.by_unidad).map(([u, v]) => (
            <div key={u} className="flex items-center gap-2">
              <span className="text-slate-500 w-8 font-mono text-xs">{u}</span>
              <span className="font-bold text-slate-800 tabular-nums">{v.avance_pct.toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Recent hitos */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <div>
              <p className="section-title">Hitos Recientes</p>
              <p className="section-sub">Últimas actualizaciones registradas</p>
            </div>
          </div>
          {stats.recent_history.length === 0 ? (
            <div className="card-body text-center py-10">
              <Clock size={24} className="text-slate-200 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No hay actualizaciones registradas</p>
              <button onClick={() => navigate('/actualizar')}
                className="btn-primary mt-4 mx-auto text-xs">
                <RefreshCw size={13} /> Registrar primera actualización
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="th">Indicador</th>
                    <th className="th">Período</th>
                    <th className="th">Avance</th>
                    <th className="th">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats.recent_history.map((h, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="td font-mono text-xs text-indigo-600 font-semibold">{h.id_indicador}</td>
                      <td className="td text-slate-500">{h.periodo ?? '—'}</td>
                      <td className="td font-bold tabular-nums">
                        {h.avance_pct != null ? `${h.avance_pct.toFixed(0)}%` : '—'}
                      </td>
                      <td className="td"><StatusBadge status={h.estado} size="sm" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Quick actions + top objectives */}
        <div className="space-y-4">
          {/* Acciones rápidas */}
          <div className="card">
            <div className="card-header"><p className="section-title">Acciones Rápidas</p></div>
            <div className="card-body space-y-2">
              <button onClick={() => navigate('/nuevo')} className="btn-primary w-full justify-center">
                <span>⊕</span> Crear Nuevo Indicador
              </button>
              <button onClick={() => navigate('/actualizar')} className="btn-secondary w-full justify-center">
                <RefreshCw size={15} /> Actualizar Indicador Existente
              </button>
            </div>
          </div>

          {/* Top por lineamiento */}
          <div className="card">
            <div className="card-header"><p className="section-title">Avance por Lineamiento</p></div>
            <div className="card-body space-y-3">
              {Object.entries(stats.by_lineamiento).map(([lin, v]) => (
                <div key={lin}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-600 font-medium truncate max-w-[220px]">{lin}</span>
                    <span className="font-bold tabular-nums text-slate-700 shrink-0">{v.avance_pct.toFixed(0)}%</span>
                  </div>
                  <ProgressBar value={v.avance_pct} size="sm" showLabel={false} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
