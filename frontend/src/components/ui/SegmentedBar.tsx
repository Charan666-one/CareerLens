interface Segment {
  /** 0-1 fraction of the bar's total width */
  fraction: number
  colorClass: string
}

interface SegmentedBarProps {
  segments: Segment[]
}

// The suitability role-list's contribution bar: width of each segment is
// its WEIGHTED contribution to final_score, not the raw component score,
// so the bar's total filled width literally sums to final_score.
export default function SegmentedBar({ segments }: SegmentedBarProps) {
  return (
    <div className="h-1.5 rounded-full overflow-hidden flex bg-stone-line">
      {segments.map((seg, i) => (
        <span key={i} className={`block h-full ${seg.colorClass}`} style={{ width: `${seg.fraction * 100}%` }} />
      ))}
    </div>
  )
}
