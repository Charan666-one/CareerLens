import clsx from "clsx"

interface CardProps {
  children: React.ReactNode
  className?: string
  accent?: "good" | "warn" | "none"
}

export default function Card({ children, className, accent = "none" }: CardProps) {
  return (
    <div
      className={clsx(
        "bg-stone-raised border border-stone-line rounded",
        accent === "good" && "border-l-[3px] border-l-good",
        accent === "warn" && "border-l-[3px] border-l-warn",
        className
      )}
    >
      {children}
    </div>
  )
}
