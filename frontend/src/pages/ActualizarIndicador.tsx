import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { indicatorsApi, milestonesApi } from '../api'
import { ESTADOS } from '../types'
import ProgressBar from '../components/ProgressBar'
import StatusBadge from '../components/StatusBadge'
import { Filter, RefreshCw, CheckCircle2, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface ProgressFormValues {
  avance_valor: number
  estado: string
  notas: string
  periodo: string
}

function UpdateForm({ id_indicador, currentValor, currentEstado, unidad_medida, meta, onSuccess }: {
  id_indicador: string; currentValor: number; currentEstado: string
  unidad_medida?: string; meta?: number; onSuccess: () => void
}) {
  const qc = useQueryClient()
  const now = new Date()
  const { register, handleSubmit, watch } = useForm<ProgressFormValues>({
    defaultValues: {
      avance_valor: currentValor,
      estado: currentEstado ?? 'Por Comenzar',
      notas: '',
      periodo: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`,
    },
  })
  const avVal = Number(watch('avance_valor')) || 0
  const calcPct = unidad_medida === '%'
    ? Math.min(avVal, 100)
    : meta && meta > 0 ? Math.min((avVal / meta) * 100, 100) : 0

  const mut = useMutation({
    mutationFn: (d: ProgressFormValues) => indicatorsApi.updateProgress(id_indicador, d),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['indicators'] })
      qc.invalidateQueries({ queryKey: ['milestones'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      onSuccess()
    },
  })

  return (
    <form onSubmit={handleSubmit(d => mut.mutate(d))} className="space-y-4 mt-4">
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
        <p className="text-xs font-semibold text-indigo-700 mb-1">Vista previa del nuevo avance</p>
        <div className="flex items-center gap-3">
          <ProgressBar value={calcPct} showLabel={false} />
          <span className="text-lg font-black text-indigo-700 tabular-nums w-16 text-right shrink-0">
            {calcPct.toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="field-label">Período (YYYY-MM)</label>
          <input {...register('periodo')} className="field-input" placeholder="2026-01" />
        </div>
        <div>
          <label className="field-label">Nuevo avance ({unidad_medida ?? '#'})</label>
          <input {...register('avance_valor', { valueAsNumber: true })}
            type="number" step="any" className="field-input font-semibold" />
        </div>
      </div>

      <div>
        <label className="field-label">Estado</label>
        <select {...register('estado')} className="field-input">
          {ESTADOS.map(e => <option key={e}>{e}</option>)}
        </select>
      </div>

      <div>
        <label className="field-label">Notas del período</label>
        <textarea {...register('notas')} rows={3} className="field-input"
          placeholder="¿Qué se logró? ¿Hay algún impedimento u observación?" />
      </div>

      <div className="flex justify-end gap-3">
        <button type="submit" disabled={mut.isPending} className="btn-primary">
          <TrendingUp size={15} />
          {mut.isPending ? 'Guardando...' : 'Registrar Avance'}
        </button>
      </div>

      {mut.isSuccess && (
        <div className="flex items-center gap-2 text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 text-sm">
          <CheckCircle2 size={16} /> Avance registrado exitosamente
        </div>
      )}
    </form>
  )
}

export default function ActualizarIndicador() {
  const [selVP, setSelVP] = useState('')
  const [selArea, setSelArea] = useState('')
  const [selIndicador, setSelIndicador] = useState('')
  const [selHito, setSelHito] = useState('')
  const [selResponsable, setSelResponsable] = useState('')
  const [showSuccess, setShowSuccess] = useState(false)

  const { data: indicators = [] } = useQuery({
    queryKey: ['indicators'],
    queryFn: () => indicatorsApi.list(),
  })

  const { data: milestones = [] } = useQuery({
    queryKey: ['milestones'],
    queryFn: () => milestonesApi.list(),
  })

  // Cascading options
  const vps = useMemo(() => [...new Set(indicators.map(i => i.unidad_organizacional).filter(Boolean))].sort(), [indicators])
  const areas = useMemo(() =>
    [...new Set(indicators.filter(i => i.unidad_organizacional === selVP).map(i => i.division_area).filter(Boolean))].sort(),
    [indicators, selVP])
  const filteredIndicators = useMemo(() =>
    indicators.filter(i => {
      if (selVP && i.unidad_organizacional !== selVP) return false
      if (selArea && i.division_area !== selArea) return false
      return true
    }),
    [indicators, selVP, selArea])
  const hitosForIndicador = useMemo(() =>
    milestones.filter(m => m.id_indicador === selIndicador),
    [milestones, selIndicador])
  const responsables = useMemo(() => {
    const all = hitosForIndicador.map(h => h.responsable).filter(Boolean) as string[]
    return [...new Set(all)].sort()
  }, [hitosForIndicador])

  const selectedIndicadorObj = indicators.find(i => i.id_indicador === selIndicador)
  const selectedHitoObj = milestones.find(m => m.id_hito === selHito)

  const handleVPChange = (val: string) => { setSelVP(val); setSelArea(''); setSelIndicador(''); setSelHito(''); setSelResponsable('') }
  const handleAreaChange = (val: string) => { setSelArea(val); setSelIndicador(''); setSelHito(''); setSelResponsable('') }
  const handleIndicadorChange = (val: string) => { setSelIndicador(val); setSelHito(''); setSelResponsable('') }

  const hasSelection = selVP && selIndicador
  const showHitoUpdate = selHito && selectedHitoObj
  const showIndicadorUpdate = hasSelection && !selectedIndicadorObj?.tiene_hitos?.toLowerCase().includes('si')

  const handleSuccess = () => setShowSuccess(true)

  return (
    <div className="max-w-screen-lg mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900">Actualizar Hitos de Indicadores</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Sigue la jerarquía: VP → Área → Indicador → Hito → Responsable para encontrar el hito a actualizar.
        </p>
      </div>

      {/* Filtros jerárquicos */}
      <div className="card" style={{ borderTop: '3px solid #4f46e5' }}>
        <div className="card-header flex items-center gap-2">
          <Filter size={16} className="text-slate-500" />
          <div>
            <p className="section-title">Filtros Jerárquicos</p>
            <p className="section-sub">Sigue el orden: primero VP, luego Área, después Indicador, luego Hito, y finalmente Responsable.</p>
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
            {/* 1. VP */}
            <div>
              <label className="field-label">1. Vicepresidencia</label>
              <select value={selVP} onChange={e => handleVPChange(e.target.value)} className="field-input">
                <option value="">Seleccionar VP</option>
                {vps.map(v => <option key={v}>{v}</option>)}
              </select>
            </div>

            {/* 2. Área */}
            <div>
              <label className="field-label">2. Área</label>
              <select value={selArea} onChange={e => handleAreaChange(e.target.value)}
                className="field-input" disabled={!selVP}>
                <option value="">Primero seleccione VP</option>
                {areas.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>

            {/* 3. Indicador */}
            <div>
              <label className="field-label">3. Indicador</label>
              <select value={selIndicador} onChange={e => handleIndicadorChange(e.target.value)}
                className="field-input" disabled={!selVP}>
                <option value="">Primero seleccione VP</option>
                {filteredIndicators.map(i => (
                  <option key={i.id_indicador} value={i.id_indicador}>
                    {i.id_indicador} — {(i.indicador ?? '').slice(0, 45)}
                  </option>
                ))}
              </select>
            </div>

            {/* 4. Hito */}
            <div>
              <label className="field-label">4. Hito</label>
              <select value={selHito} onChange={e => setSelHito(e.target.value)}
                className="field-input" disabled={!selIndicador}>
                <option value="">Primero seleccione Indicador</option>
                {hitosForIndicador.map(h => (
                  <option key={h.id_hito} value={h.id_hito}>
                    {h.orden}. {(h.nombre_hito ?? '').slice(0, 40)}
                  </option>
                ))}
              </select>
            </div>

            {/* 5. Responsable */}
            <div>
              <label className="field-label">5. Responsable (opcional)</label>
              <select value={selResponsable} onChange={e => setSelResponsable(e.target.value)}
                className="field-input" disabled={responsables.length === 0}>
                <option value="">Filtrar por Responsable</option>
                {responsables.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
          </div>

          {selVP && (
            <p className="text-xs text-slate-500 mt-3">
              {filteredIndicators.length} indicadores encontrados para <strong>{selVP}</strong>
              {selArea && <> · <strong>{selArea}</strong></>}
            </p>
          )}
          {!selVP && (
            <p className="text-xs text-slate-400 mt-3">Comienza seleccionando una Vicepresidencia</p>
          )}
        </div>
      </div>

      {/* Result area */}
      {!hasSelection ? (
        <div className="card p-10 text-center border-2 border-dashed border-slate-200">
          <Filter size={28} className="text-slate-200 mx-auto mb-3" />
          <p className="font-semibold text-slate-500 mb-2">Sigue la jerarquía de filtros</p>
          <p className="text-sm text-slate-400 mb-4">Para encontrar el hito que deseas actualizar, sigue este orden:</p>
          <div className="flex items-center justify-center gap-2 flex-wrap">
            {['1. VP', '2. Área', '3. Indicador'].map((s, i, arr) => (
              <span key={s} className="flex items-center gap-2">
                <span className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full">{s}</span>
                {i < arr.length - 1 && <span className="text-slate-300">→</span>}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Indicador info */}
          {selectedIndicadorObj && (
            <div className="card p-5 flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                    {selectedIndicadorObj.id_indicador}
                  </span>
                  <StatusBadge status={selectedIndicadorObj.estado} size="sm" />
                </div>
                <p className="text-sm font-semibold text-slate-800">{selectedIndicadorObj.indicador}</p>
                <p className="text-xs text-slate-500 mt-1">
                  Meta: <strong>{selectedIndicadorObj.meta} {selectedIndicadorObj.unidad_medida}</strong>
                  {' · '}Avance actual: <strong>{selectedIndicadorObj.avance_valor ?? 0} {selectedIndicadorObj.unidad_medida}</strong>
                  {' · '}Tiene hitos: <strong>{selectedIndicadorObj.tiene_hitos}</strong>
                </p>
              </div>
              <div className="w-32 shrink-0">
                <ProgressBar value={selectedIndicadorObj.avance_pct ?? 0} size="sm" />
              </div>
            </div>
          )}

          {/* Hitos list (when indicator has hitos) */}
          {hitosForIndicador.length > 0 && !selHito && (
            <div className="card">
              <div className="card-header">
                <p className="section-title">Hitos de {selIndicador}</p>
                <p className="section-sub">Selecciona un hito en el filtro de arriba para actualizarlo</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="th">#</th>
                      <th className="th">Hito</th>
                      <th className="th">Estado</th>
                      <th className="th">Avance</th>
                      <th className="th">Responsable</th>
                      <th className="th">Fecha Fin</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {hitosForIndicador.map(h => (
                      <tr key={h.id_hito}
                        className="hover:bg-indigo-50 cursor-pointer transition-colors"
                        onClick={() => setSelHito(h.id_hito)}>
                        <td className="td font-semibold text-slate-500">{h.orden}</td>
                        <td className="td">
                          <div className="font-medium text-slate-800 line-clamp-1">{h.nombre_hito}</div>
                          <div className="text-xs text-slate-400 font-mono">{h.id_hito}</div>
                        </td>
                        <td className="td"><StatusBadge status={h.estado} size="sm" /></td>
                        <td className="td w-32"><ProgressBar value={h.avance_pct ?? 0} size="xs" /></td>
                        <td className="td text-slate-500">{h.responsable ?? '—'}</td>
                        <td className="td text-slate-500">{h.fecha_fin_actual ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Update form for selected HITO */}
          {showHitoUpdate && selectedIndicadorObj && (
            <div className="card" style={{ borderTop: '3px solid #7c3aed' }}>
              <div className="card-header">
                <div className="flex items-center gap-2">
                  <RefreshCw size={16} className="text-violet-600" />
                  <div>
                    <p className="section-title">Actualizar Hito: {selectedHitoObj.orden}. {(selectedHitoObj.nombre_hito ?? '').slice(0, 50)}</p>
                    <p className="section-sub font-mono text-xs">{selectedHitoObj.id_hito}</p>
                  </div>
                </div>
              </div>
              <div className="card-body">
                <UpdateHitoForm hito={selectedHitoObj} onSuccess={handleSuccess} />
              </div>
            </div>
          )}

          {/* Update form for indicator WITHOUT hitos */}
          {showIndicadorUpdate && selectedIndicadorObj && (
            <div className="card" style={{ borderTop: '3px solid #4f46e5' }}>
              <div className="card-header">
                <div className="flex items-center gap-2">
                  <RefreshCw size={16} className="text-indigo-600" />
                  <div>
                    <p className="section-title">Actualizar Avance del Indicador</p>
                    <p className="section-sub">Este indicador no tiene hitos — actualiza el avance directamente.</p>
                  </div>
                </div>
              </div>
              <div className="card-body">
                <UpdateForm
                  id_indicador={selectedIndicadorObj.id_indicador}
                  currentValor={selectedIndicadorObj.avance_valor ?? 0}
                  currentEstado={selectedIndicadorObj.estado ?? 'Por Comenzar'}
                  unidad_medida={selectedIndicadorObj.unidad_medida}
                  meta={selectedIndicadorObj.meta}
                  onSuccess={handleSuccess}
                />
              </div>
            </div>
          )}

          {showSuccess && (
            <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-xl px-5 py-4">
              <CheckCircle2 size={20} className="text-emerald-600 shrink-0" />
              <div>
                <p className="font-semibold text-emerald-800">¡Actualización registrada exitosamente!</p>
                <p className="text-sm text-emerald-700">El avance ha sido guardado y el historial actualizado.</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function UpdateHitoForm({ hito, onSuccess }: { hito: any; onSuccess: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, watch } = useForm({
    defaultValues: {
      avance_pct: hito.avance_pct ?? 0,
      estado: hito.estado ?? 'Por Comenzar',
    },
  })
  const avancePct = Number(watch('avance_pct')) || 0
  const mut = useMutation({
    mutationFn: (d: any) => milestonesApi.update(hito.id_hito, d),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['milestones'] })
      qc.invalidateQueries({ queryKey: ['indicators'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      onSuccess()
    },
  })

  return (
    <form onSubmit={handleSubmit(d => mut.mutate(d))} className="space-y-4">
      <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
        <p className="text-xs font-semibold text-violet-700 mb-1">Vista previa</p>
        <div className="flex items-center gap-3">
          <ProgressBar value={avancePct} showLabel={false} />
          <span className="text-lg font-black text-violet-700 tabular-nums w-16 text-right shrink-0">
            {avancePct.toFixed(0)}%
          </span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="field-label">Avance (%)</label>
          <input {...register('avance_pct', { valueAsNumber: true })}
            type="number" min={0} max={100} step={5} className="field-input font-semibold" />
        </div>
        <div>
          <label className="field-label">Estado</label>
          <select {...register('estado')} className="field-input">
            {ESTADOS.map(e => <option key={e}>{e}</option>)}
          </select>
        </div>
      </div>
      <div className="flex justify-end">
        <button type="submit" disabled={mut.isPending} className="btn-primary">
          <TrendingUp size={15} />
          {mut.isPending ? 'Guardando...' : 'Actualizar Hito'}
        </button>
      </div>
    </form>
  )
}
