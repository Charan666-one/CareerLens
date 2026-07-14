interface DonutSegment {
  /** 0-1 fraction of the ring this segment occupies */
  fraction: number
  colorVar: string
}

interface DonutProps {
  segments: DonutSegment[]
  centerValue: string
  centerLabel: string
  size?: number
}

// CSS conic-gradient ring, not a charting library - this exact
// implementation was already signed off in the approved mockup, and a
// static 3-segment ring doesn't need recharts'/d3's overhead.
export default function Donut({ segments, centerValue, centerLabel, size = 118 }: DonutProps) {
  let cursor = 0
  const stops = segments
    .map((seg) => {
      const start = cursor * 360
      cursor += seg.fraction
      const end = cursor * 360
      return `${seg.colorVar} ${start}deg ${end}deg`
    })
    .join(", ")
  const gradient = `conic-gradient(${stops}, var(--stone-line) ${cursor * 360}deg 360deg)`

  return (
    <div
      className="relative rounded-full flex items-center justify-center flex-none"
      style={{ width: size, height: size, background: gradient }}
    >
      <div
        className="absolute rounded-full bg-stone-raised flex items-center justify-center"
        style={{ inset: size * 0.12 }}
      >
        <div className="text-center font-display relative z-10">
          <span className="block text-2xl leading-none">{centerValue}</span>
          <span className="text-[0.62rem] text-text-dim tracking-wide">{centerLabel}</span>
        </div>
      </div>
    </div>
  )
}
