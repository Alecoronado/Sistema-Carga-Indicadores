import clsx from 'clsx'

interface Props {
  value: number
  size?: 'xs' | 'sm' | 'md'
  showLabel?: boolean
  color?: string
}

function getColor(pct: number) {
  if (pct >= 80) return '#10b981'
  if (pct >= 40) return '#4f46e5'
  if (pct > 0)   return '#f59e0b'
  return '#e2e8f0'
}

export default function ProgressBar({ value, size = 'md', showLabel = true, color }: Props) {
  const pct = Math.min(Math.max(value || 0, 0), 100)
  const barColor = color ?? getColor(pct)
  const heights = { xs: 'h-1', sm: 'h-1.5', md: 'h-2' }

  return (
    <div className="flex items-center gap-2.5 w-full min-w-0">
      <div className={clsx('flex-1 bg-slate-100 rounded-full overflow-hidden', heights[size])}>
        <div
          className={clsx('h-full rounded-full transition-all duration-700')}
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
      {showLabel && (
        <span className="text-xs font-semibold text-slate-500 w-9 text-right shrink-0 tabular-nums">
          {pct.toFixed(0)}%
        </span>
      )}
    </div>
  )
}
