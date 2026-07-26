interface ProgressBarProps {
  /** 0-1 */
  fraction: number
  colorClass?: string
}

export default function ProgressBar({ fraction, colorClass = "bg-brass" }: ProgressBarProps) {
  // Math.min/max propagate NaN, which yields width:"NaN%" - invalid CSS, so
  // the declaration is dropped and the bar renders FULL. Unknown data must
  // read as 0%, not 100%.
  const safe = Number.isFinite(fraction) ? fraction : 0
  const pct = Math.max(0, Math.min(1, safe)) * 100
  return (
    <div className="h-[5px] bg-stone-line rounded-[3px] overflow-hidden">
      <div className={`h-full rounded-[3px] ${colorClass}`} style={{ width: `${pct}%` }} />
    </div>
  )
}
