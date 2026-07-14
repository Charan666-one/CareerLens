import clsx from "clsx"

interface NodeBadgeProps {
  children: React.ReactNode
  variant?: "done" | "current" | "upcoming" | "plain"
  size?: number
}

// The numbered/checkmarked circle used both by the stage tracker and the
// roadmap path - same visual object, two contexts.
export default function NodeBadge({ children, variant = "plain", size = 36 }: NodeBadgeProps) {
  return (
    <div
      className={clsx(
        "rounded-full flex items-center justify-center font-mono text-xs flex-none border",
        variant === "done" && "bg-brass border-brass text-[#1a1207]",
        variant === "current" && "border-brass text-brass shadow-[0_0_0_4px_rgba(184,134,63,0.16)]",
        variant === "upcoming" && "bg-ink border-ink-line text-ink-text-dim",
        variant === "plain" && "bg-ink border-ink-line text-brass"
      )}
      style={{ width: size, height: size }}
    >
      {children}
    </div>
  )
}
