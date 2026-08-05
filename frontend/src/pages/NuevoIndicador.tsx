import { useFieldArray, useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { indicatorsApi, objectivesApi } from '../api'
import { ESTADOS, LINEAMIENTOS, TIPOS_OBJETIVO, UNIDADES_ORG, UNIDADES_MEDIDA, CLASIFICACIONES } from '../types'
import { Plus, Trash2, ChevronLeft, Save } from 'lucide-react'

interface FormValues {
  id_indicador: string
  id_objetivo: string
  unidad_organizacional: string
  division_area: string
  tipo_objetivo: string
  indicador: string
  fecha_inicio: string
  fecha_fin_actual: string
  responsable: string
  responsable_carga: string
  lineamiento: string
  clasificacion: string
  unidad_medida: string
  meta: number
  estado: string
  acciones: string
  resultado_esperado: string
  notas: string
  milestones: {
    nombre_hito: string
    fecha_inicio: string
    fecha_fin_actual: string
    avance_pct: number
    estado: string
    responsable: string
  }[]
}

export default function NuevoIndicador() {
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: objectives = [] } = useQuery({
    queryKey: ['objectives'],
    queryFn: objectivesApi.list,
  })

  const { register, control, handleSubmit, watch, formState: { errors } } = useForm<FormValues>({
    defaultValues: {
      estado: 'Por Comenzar',
      milestones: [],
      meta: 0,
      avance_pct: 0,
    } as any,
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'milestones' })

  const createMut = useMutation({
    mutationFn: (data: FormValues) => {
      const payload = {
        ...data,
        meta: Number(data.meta) || 0,
        avance_valor: 0,
        avance_pct: 0,
        milestones: data.milestones.map((m, i) => ({
          ...m,
          orden: i + 1,
          avance_pct: Number(m.avance_pct) || 0,
        })),
      }
      return indicatorsApi.createWithMilestones(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['indicators'] })
      qc.invalidateQueries({ queryKey: ['milestones'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      navigate('/historial')
    },
  })

  const addHito = () => {
    append({ nombre_hito: '', fecha_inicio: '', fecha_fin_actual: '', avance_pct: 0, estado: 'Por Comenzar', responsable: '' })
  }

  return (
    <div className="max-w-screen-lg mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="btn-ghost text-sm p-2">
          <ChevronLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-900">Nuevo Indicador</h1>
          <p className="text-sm text-slate-500 mt-0.5">Registra un nuevo indicador y sus hitos asociados</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(d => createMut.mutate(d))} className="space-y-5">
        {/* ── Sección 1: Información General ── */}
        <div className="card" style={{ borderTop: '3px solid #4f46e5' }}>
          <div className="card-header">
            <p className="section-title">Información General del Indicador</p>
            <p className="section-sub">Complete los detalles generales del indicador.</p>
          </div>
          <div className="card-body space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="field-label">VP (Vicepresidencia) *</label>
                <select {...register('unidad_organizacional', { required: true })} className="field-input">
                  <option value="">Seleccione un VP</option>
                  {UNIDADES_ORG.map(u => <option key={u}>{u}</option>)}
                </select>
                {errors.unidad_organizacional && <p className="field-error">Requerido</p>}
              </div>
              <div>
                <label className="field-label">Área</label>
                <input {...register('division_area')} className="field-input" placeholder="Ej: Operaciones País" />
              </div>
              <div>
                <label className="field-label">Tipo de Indicador</label>
                <select {...register('tipo_objetivo')} className="field-input">
                  <option value="">Seleccione un tipo</option>
                  {TIPOS_OBJETIVO.map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-1">
                <label className="field-label">ID Indicador *</label>
                <input {...register('id_indicador', { required: true })} className="field-input" placeholder="Ej: E110" />
                {errors.id_indicador && <p className="field-error">Requerido</p>}
              </div>
              <div>
                <label className="field-label">Fecha de Inicio General</label>
                <input {...register('fecha_inicio')} type="date" className="field-input" />
              </div>
              <div>
                <label className="field-label">Fecha de Finalización General</label>
                <input {...register('fecha_fin_actual')} type="date" className="field-input" />
              </div>
            </div>

            <div>
              <label className="field-label">Nombre del Indicador *</label>
              <input {...register('indicador', { required: true })} className="field-input"
                placeholder="Ej: Número de reuniones de revisión de cartera realizadas" />
              {errors.indicador && <p className="field-error">Requerido</p>}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="field-label">Responsable General</label>
                <input {...register('responsable')} className="field-input" placeholder="Ej: Juan Pérez" />
              </div>
              <div>
                <label className="field-label">Responsable de Carga General</label>
                <input {...register('responsable_carga')} className="field-input" placeholder="Ej: María García" />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="field-label">Objetivo vinculado *</label>
                <select {...register('id_objetivo', { required: true })} className="field-input">
                  <option value="">Seleccione un objetivo</option>
                  {objectives.map(o => (
                    <option key={o.id_objetivo} value={o.id_objetivo}>
                      {o.id_objetivo} — {(o.objetivo_anual ?? '').slice(0, 60)}
                    </option>
                  ))}
                </select>
                {errors.id_objetivo && <p className="field-error">Requerido</p>}
              </div>
              <div>
                <label className="field-label">Lineamiento</label>
                <select {...register('lineamiento')} className="field-input">
                  <option value="">—</option>
                  {LINEAMIENTOS.map(l => <option key={l}>{l}</option>)}
                </select>
              </div>
              <div>
                <label className="field-label">Clasificación</label>
                <select {...register('clasificacion')} className="field-input">
                  <option value="">—</option>
                  {CLASIFICACIONES.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="field-label">Unidad de Medida</label>
                <select {...register('unidad_medida')} className="field-input">
                  <option value="">—</option>
                  {UNIDADES_MEDIDA.map(u => <option key={u}>{u}</option>)}
                </select>
              </div>
              <div>
                <label className="field-label">Meta</label>
                <input {...register('meta', { valueAsNumber: true })} type="number" step="any" className="field-input" placeholder="0" />
              </div>
              <div>
                <label className="field-label">Estado Inicial</label>
                <select {...register('estado')} className="field-input">
                  {ESTADOS.map(e => <option key={e}>{e}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="field-label">Acciones / Descripción</label>
              <textarea {...register('acciones')} rows={2} className="field-input"
                placeholder="Describe las acciones a realizar para cumplir este indicador..." />
            </div>

            <div>
              <label className="field-label">Resultado Esperado</label>
              <textarea {...register('resultado_esperado')} rows={2} className="field-input" />
            </div>

            <div>
              <label className="field-label">Notas adicionales</label>
              <textarea {...register('notas')} rows={2} className="field-input"
                placeholder="Observaciones iniciales..." />
            </div>
          </div>
        </div>

        {/* ── Sección 2: Hitos ── */}
        <div className="card" style={{ borderTop: '3px solid #7c3aed' }}>
          <div className="card-header flex items-center justify-between">
            <div>
              <p className="section-title">Hitos del Indicador</p>
              <p className="section-sub">Añada uno o más hitos para este indicador.</p>
            </div>
            <button type="button" onClick={addHito} className="btn-primary text-sm">
              <Plus size={15} /> Añadir Hito
            </button>
          </div>
          <div className="card-body">
            {fields.length === 0 ? (
              <div className="text-center py-8 border-2 border-dashed border-slate-200 rounded-xl">
                <p className="text-sm text-slate-400 mb-3">Este indicador no tiene hitos definidos.</p>
                <button type="button" onClick={addHito} className="btn-secondary text-sm">
                  <Plus size={14} /> Añadir primer hito
                </button>
              </div>
            ) : (
              <div className="space-y-5">
                {fields.map((field, i) => (
                  <div key={field.id} className="border border-slate-200 rounded-xl p-5 bg-slate-50 relative">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm font-bold text-violet-700">Hito {i + 1}</span>
                      <button type="button" onClick={() => remove(i)}
                        className="text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg p-1.5 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="sm:col-span-3">
                        <label className="field-label">Nombre del Hito *</label>
                        <input {...register(`milestones.${i}.nombre_hito`, { required: true })}
                          className="field-input" placeholder="Ej: Optimización de línea A" />
                      </div>
                      <div>
                        <label className="field-label">Fecha de Inicio Hito</label>
                        <input {...register(`milestones.${i}.fecha_inicio`)} type="date" className="field-input" />
                      </div>
                      <div>
                        <label className="field-label">Fecha de Finalización Hito</label>
                        <input {...register(`milestones.${i}.fecha_fin_actual`)} type="date" className="field-input" />
                      </div>
                      <div>
                        <label className="field-label">Responsable Hito</label>
                        <input {...register(`milestones.${i}.responsable`)}
                          className="field-input" placeholder="Ej: Ana Torres" />
                      </div>
                      <div>
                        <label className="field-label">Avance Hito (%)</label>
                        <input {...register(`milestones.${i}.avance_pct`, { valueAsNumber: true })}
                          type="number" min={0} max={100} step={5} className="field-input" defaultValue={0} />
                      </div>
                      <div>
                        <label className="field-label">Estado Hito</label>
                        <select {...register(`milestones.${i}.estado`)} className="field-input">
                          {ESTADOS.map(e => <option key={e}>{e}</option>)}
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-3 pb-4">
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" disabled={createMut.isPending} className="btn-primary px-8">
            <Save size={16} />
            {createMut.isPending ? 'Guardando...' : 'Guardar Indicador y Hitos'}
          </button>
        </div>

        {createMut.isError && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
            Error al guardar. Verifique que el ID no exista ya en el sistema.
          </div>
        )}
      </form>
    </div>
  )
}
