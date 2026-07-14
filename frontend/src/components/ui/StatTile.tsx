interface StatTileProps {
  label: string
  value: React.ReactNode
  sub?: string
}

export default function StatTile({ label, value, sub }: StatTileProps) {
  return (
    <div className="bg-stone-raised p-5">
      <div className="text-[0.72rem] tracking-wide uppercase text-text-dim mb-2.5">{label}</div>
      <div className="font-display text-3xl leading-none tabular-nums">{value}</div>
      {sub && <div className="mt-2 text-[0.78rem] text-text-dim font-mono">{sub}</div>}
    </div>
  )
}
