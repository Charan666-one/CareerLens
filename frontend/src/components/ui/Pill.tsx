import clsx from "clsx"

interface PillProps {
  children: React.ReactNode
  variant: "matched" | "missing" | "neutral"
}

export default function Pill({ children, variant }: PillProps) {
  return (
    <span
      className={clsx(
        "font-mono text-xs px-2.5 py-0.5 rounded-full border",
        variant === "matched" && "text-good border-good/40",
        variant === "missing" && "text-warn border-warn/35",
        variant === "neutral" && "text-text-dim border-stone-line"
      )}
    >
      {children}
    </span>
  )
}
