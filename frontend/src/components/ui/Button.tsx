import clsx from "clsx"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "link"
}

export default function Button({ variant = "primary", className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "font-body text-sm rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed",
        variant === "primary" && "bg-brass text-[#1a1207] px-4 py-2 hover:bg-brass-strong",
        variant === "secondary" &&
          "border border-stone-line px-4 py-2 hover:border-brass hover:text-brass-strong",
        variant === "link" && "font-mono text-[0.76rem] text-brass-strong underline underline-offset-2",
        className
      )}
      {...props}
    />
  )
}
