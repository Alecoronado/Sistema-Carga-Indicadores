interface Props {
  value: number
  size?: number
  strokeWidth?: number
  color?: string
  bgColor?: string
  showLabel?: boolean
  fontSize?: number
}

export default function CircularProgress({
  value,
  size = 64,
  strokeWidth = 5,
  color = '#4f46e5',
  bgColor = '#e2e8f0',
  showLabel = true,
  fontSize = 12,
}: Props) {
  const pct = Math.min(Math.max(value || 0, 0), 100)
  const r = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * r
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={bgColor} strokeWidth={strokeWidth} />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      {showLabel && (
        <span
          className="absolute font-bold"
          style={{ color, fontSize }}
        >
          {pct.toFixed(0)}%
        </span>
      )}
    </div>
  )
}
