interface PrerequisiteNoticeProps {
  missing: string[]
  action?: React.ReactNode
}

// The one component for "you're missing X" - fed either proactively by
// useStageGate (before a request is attempted) or reactively by a caught
// 409's missingPrerequisite, so the message reads identically either way.
export default function PrerequisiteNotice({ missing, action }: PrerequisiteNoticeProps) {
  if (missing.length === 0) return null
  return (
    <div className="border border-warn/35 bg-warn/10 rounded px-4 py-3 text-sm text-warn flex items-center gap-3 flex-wrap">
      <span>
        Run {missing.join(", ")} first — this stage needs {missing.length > 1 ? "them" : "it"} to run.
      </span>
      {action}
    </div>
  )
}
