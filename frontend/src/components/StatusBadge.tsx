import clsx from 'clsx'

const STATUS_CONFIG: Record<string, { bg: string; text: string; dot: string }> = {
  'Por Comenzar': { bg: 'bg-slate-100',  text: 'text-slate-600',  dot: 'bg-slate-400'  },
  'En Progreso':  { bg: 'bg-blue-50',    text: 'text-blue-700',   dot: 'bg-blue-500'   },
  'Completado':   { bg: 'bg-emerald-50', text: 'text-emerald-700',dot: 'bg-emerald-500'},
  'Retrasado':    { bg: 'bg-red-50',     text: 'text-red-700',    dot: 'bg-red-500'    },
  'En Riesgo':    { bg: 'bg-amber-50',   text: 'text-amber-700',  dot: 'bg-amber-500'  },
}

interface Props {
  status?: string
  size?: 'sm' | 'md'
}

export default function StatusBadge({ status = 'Por Comenzar', size = 'md' }: Props) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG['Por Comenzar']
  return (
    <span className={clsx(
      'inline-flex items-center gap-1.5 rounded-full font-semibold whitespace-nowrap',
      cfg.bg, cfg.text,
      size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
    )}>
      <span className={clsx('rounded-full shrink-0', cfg.dot, size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2')} />
      {status}
    </span>
  )
}
