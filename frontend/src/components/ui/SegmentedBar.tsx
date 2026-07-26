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
        <span
          key={i}
          className={`block h-full ${seg.colorClass}`}
          // NaN would yield width:"NaN%" - invalid CSS, dropped, so the
          // segment would stretch to fill the bar instead of collapsing.
          style={{ width: `${Number.isFinite(seg.fraction) ? Math.max(0, Math.min(1, seg.fraction)) * 100 : 0}%` }}
        />
      ))}
    </div>
  )
}
