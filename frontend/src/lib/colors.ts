export const LINEAMIENTO_COLORS: Record<string, { bg: string; text: string; accent: string; light: string }> = {
  'Excelencia Operacional':   { bg: '#4f46e5', text: '#4f46e5', accent: '#4f46e5', light: '#eef2ff' },
  'Alineación Estratégica':   { bg: '#7c3aed', text: '#7c3aed', accent: '#7c3aed', light: '#f5f3ff' },
  'Eficiencia Organizacional':{ bg: '#059669', text: '#059669', accent: '#059669', light: '#ecfdf5' },
  'Solidez Financiera':       { bg: '#d97706', text: '#d97706', accent: '#d97706', light: '#fffbeb' },
  'Complementariedad':        { bg: '#0891b2', text: '#0891b2', accent: '#0891b2', light: '#ecfeff' },
}

export const DEFAULT_COLOR = { bg: '#94a3b8', text: '#64748b', accent: '#94a3b8', light: '#f8fafc' }

export function lineamientoColor(lin?: string | null) {
  return (lin && LINEAMIENTO_COLORS[lin]) ?? DEFAULT_COLOR
}

export const CHART_COLORS = ['#4f46e5', '#7c3aed', '#059669', '#d97706', '#0891b2', '#64748b']
