interface ProgressBarProps {
  /** 0-1 */
  fraction: number
  colorClass?: string
}

export default function ProgressBar({ fraction, colorClass = "bg-brass" }: ProgressBarProps) {
  const pct = Math.max(0, Math.min(1, fraction)) * 100
  return (
    <div className="h-[5px] bg-stone-line rounded-[3px] overflow-hidden">
      <div className={`h-full rounded-[3px] ${colorClass}`} style={{ width: `${pct}%` }} />
    </div>
  )
}
