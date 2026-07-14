interface EmptyStateProps {
  title: string
  message: string
  action?: React.ReactNode
}

export default function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <div className="text-center py-20 px-6">
      <h2 className="font-display text-xl mb-2">{title}</h2>
      <p className="text-text-dim text-sm max-w-md mx-auto mb-6">{message}</p>
      {action}
    </div>
  )
}
