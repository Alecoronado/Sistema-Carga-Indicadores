import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { indicatorsApi, milestonesApi, exportApi } from '../api'
import StatusBadge from '../components/StatusBadge'
import ProgressBar from '../components/ProgressBar'
import { Download, Search } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function HistorialPage() {
  const [selVP, setSelVP] = useState('')
  const [selArea, setSelArea] = useState('')
  const [selIndicador, setSelIndicador] = useState('')
  const [searchText, setSearchText] = useState('')

  const { data: indicators = [] } = useQuery({
    queryKey: ['indicators'],
    queryFn: () => indicatorsApi.list(),
  })

  const { data: milestones = [] } = useQuery({
    queryKey: ['milestones'],
    queryFn: () => milestonesApi.list(),
  })

  const vps = useMemo(() =>
    [...new Set(indicators.map(i => i.unidad_organizacional).filter(Boolean))].sort(), [indicators])

  const areas = useMemo(() =>
    [...new Set(indicators.filter(i => !selVP || i.unidad_organizacional === selVP).map(i => i.division_area).filter(Boolean))].sort(),
    [indicators, selVP])

  const filteredIndicators = useMemo(() =>
    indicators.filter(i => {
      if (selVP && i.unidad_organizacional !== selVP) return false
      if (selArea && i.division_area !== selArea) return false
      return true
    }), [indicators, selVP, selArea])

  const indMap = useMemo(() =>
    Object.fromEntries(indicators.map(i => [i.id_indicador, i])), [indicators])

  // Build full hito list with parent indicator info
  const hitoRows = useMemo(() => {
    return milestones
      .filter(m => {
        const ind = indMap[m.id_indicador]
        if (!ind) return false
        if (selVP && ind.unidad_organizacional !== selVP) return false
        if (selArea && ind.division_area !== selArea) return false
        if (selIndicador && m.id_indicador !== selIndicador) return false
        if (searchText) {
          const s = searchText.toLowerCase()
          return (
            m.id_hito.toLowerCase().includes(s) ||
            (m.nombre_hito ?? '').toLowerCase().includes(s) ||
            (m.responsable ?? '').toLowerCase().includes(s) ||
            m.id_indicador.toLowerCase().includes(s)
          )
        }
        return true
      })
      .map(m => {
        const ind = indMap[m.id_indicador]
        return {
          vp: ind?.unidad_organizacional ?? '—',
          area: ind?.division_area ?? '—',
          indicador_id: m.id_indicador,
          indicador_nombre: ind?.indicador ?? '—',
          hito_id: m.id_hito,
          nombre_hito: m.nombre_hito ?? '—',
          fecha_inicio: m.fecha_inicio,
          fecha_fin: m.fecha_fin_actual,
          avance: m.avance_pct ?? 0,
          estado: m.estado ?? 'Por Comenzar',
          responsable: m.responsable ?? '—',
        }
      })
  }, [milestones, indMap, selVP, selArea, selIndicador, searchText])

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Historial Detallado de Hitos</h1>
          <p className="text-sm text-slate-500 mt-0.5">Consulta y exporta el historial completo de indicadores y sus hitos.</p>
        </div>
        <button onClick={exportApi.excel} className="btn-primary">
          <Download size={15} /> Exportar Excel
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-header"><p className="section-title">Filtros Jerárquicos</p></div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div>
              <label className="field-label">1. Vicepresidencia</label>
              <select value={selVP} onChange={e => { setSelVP(e.target.value); setSelArea(''); setSelIndicador('') }}
                className="field-input">
                <option value="">VPD</option>
                <option value="">Seleccionar VP</option>
                {vps.map(v => <option key={v}>{v}</option>)}
              </select>
            </div>
            <div>
              <label className="field-label">2. Área</label>
              <select value={selArea} onChange={e => { setSelArea(e.target.value); setSelIndicador('') }}
                className="field-input">
                <option value="">Seleccionar Área</option>
                {areas.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="field-label">3. Indicador</label>
              <select value={selIndicador} onChange={e => setSelIndicador(e.target.value)}
                className="field-input" disabled={!selVP && !selArea}>
                <option value="">Primero seleccione Área</option>
                {filteredIndicators.map(i => (
                  <option key={i.id_indicador} value={i.id_indicador}>
                    {i.id_indicador} — {(i.indicador ?? '').slice(0, 45)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="field-label">Búsqueda libre</label>
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input value={searchText} onChange={e => setSearchText(e.target.value)}
                  className="field-input pl-9" placeholder="Buscar hito o responsable" />
              </div>
            </div>
          </div>
          {(selVP || selArea || selIndicador || searchText) && (
            <button onClick={() => { setSelVP(''); setSelArea(''); setSelIndicador(''); setSearchText('') }}
              className="btn-ghost text-xs mt-3">
              Limpiar todos los filtros
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <p className="section-title">Listado de Hitos</p>
          <span className="text-xs text-slate-400">{hitoRows.length} resultado{hitoRows.length !== 1 ? 's' : ''}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-[900px]">
            <thead>
              <tr>
                <th className="th">VP</th>
                <th className="th">Área</th>
                <th className="th">Indicador</th>
                <th className="th">Hito</th>
                <th className="th">Fecha Inicio</th>
                <th className="th">Fecha Fin</th>
                <th className="th w-32">Avance</th>
                <th className="th">Estado</th>
                <th className="th">Responsable</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {hitoRows.length === 0 ? (
                <tr>
                  <td colSpan={9} className="td text-center text-slate-400 py-12">
                    <Search size={24} className="mx-auto mb-2 text-slate-200" />
                    No se encontraron hitos con los filtros seleccionados
                  </td>
                </tr>
              ) : hitoRows.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50 transition-colors">
                  <td className="td">
                    <span className="text-xs font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">{row.vp}</span>
                  </td>
                  <td className="td text-slate-500 text-xs">{row.area !== '—' ? row.area : '—'}</td>
                  <td className="td">
                    <div className="font-mono text-xs font-bold text-indigo-600">{row.indicador_id}</div>
                    <div className="text-xs text-slate-500 line-clamp-1">{row.indicador_nombre}</div>
                  </td>
                  <td className="td">
                    <div className="text-xs text-slate-700 line-clamp-2 max-w-xs">{row.nombre_hito}</div>
                    <div className="text-xs font-mono text-slate-400">{row.hito_id}</div>
                  </td>
                  <td className="td text-xs text-slate-500">{row.fecha_inicio ?? '—'}</td>
                  <td className="td text-xs text-slate-500">{row.fecha_fin ?? '—'}</td>
                  <td className="td w-32"><ProgressBar value={row.avance} size="xs" /></td>
                  <td className="td"><StatusBadge status={row.estado} size="sm" /></td>
                  <td className="td text-xs text-slate-500">{row.responsable}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
