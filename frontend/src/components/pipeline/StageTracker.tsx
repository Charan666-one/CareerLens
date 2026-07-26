import { useShallow } from "zustand/react/shallow"
import NodeBadge from "@/components/ui/NodeBadge"
import { usePipelineStore, type StageStatus } from "@/store/pipeline"

const STAGES: { key: keyof ReturnType<typeof useTrackerStatuses>; label: string }[] = [
  { key: "profile", label: "Profile" },
  { key: "strengths", label: "Strengths" },
  { key: "suitability", label: "Suitability" },
  { key: "skillGap", label: "Skill Gap" },
  { key: "roadmap", label: "Roadmap" },
  { key: "resumeScore", label: "Resume Score" },
  { key: "recommendations", label: "Recommend" },
]

function useTrackerStatuses() {
  return usePipelineStore(
    useShallow((s) => ({
      profile: s.profile.status,
      strengths: s.strengths.status,
      suitability: s.suitability.status,
      skillGap: s.skillGap.status,
      roadmap: s.roadmap.status,
      resumeScore: s.resumeScore.status,
      recommendations: s.recommendations.status,
    }))
  )
}

function nodeVariant(status: StageStatus, isFirstNonDone: boolean): "done" | "current" | "upcoming" {
  if (status === "success") return "done"
  if (status === "loading" || (isFirstNonDone && status !== "error")) return "current"
  return "upcoming"
}

export default function StageTracker() {
  const statuses = useTrackerStatuses()
  const doneCount = STAGES.filter((s) => statuses[s.key] === "success").length
  const firstNonDoneIndex = STAGES.findIndex((s) => statuses[s.key] !== "success")

  // The connecting line is drawn across the GAPS between nodes, so 7 nodes
  // means 6 gaps. It also advances only through the leading run of finished
  // stages: resume_score is independent of the main chain, so finishing it
  // first must not drag the line past stages that haven't run.
  const gapCount = STAGES.length - 1
  const leadingDone = firstNonDoneIndex === -1 ? STAGES.length : firstNonDoneIndex
  const filledGaps = Math.max(0, Math.min(leadingDone - 1, gapCount))

  return (
    <div className="bg-ink text-ink-text pt-7 pb-8">
      <div className="max-w-[1180px] mx-auto px-8">
        <div className="flex items-baseline justify-between mb-5">
          <div>
            <span className="block text-[0.72rem] tracking-[0.14em] uppercase text-brass mb-2">
              Analysis pipeline
            </span>
            <h1 className="font-display text-2xl text-balance">Your career analysis</h1>
          </div>
          <span className="text-[0.82rem] text-ink-text-dim font-mono">
            {doneCount} of {STAGES.length} complete
          </span>
        </div>

        <div className="relative flex justify-between">
          <div className="absolute left-[18px] right-[18px] top-[18px] h-px bg-ink-line" />
          <div
            className="absolute left-[18px] top-[18px] h-px bg-brass"
            style={{ width: `calc(${filledGaps}/${gapCount} * (100% - 36px))` }}
          />
          {STAGES.map((stage, i) => {
            const status = statuses[stage.key]
            const variant = nodeVariant(status, i === firstNonDoneIndex)
            return (
              <div key={stage.key} className="relative flex flex-col items-center gap-2.5 w-[90px] text-center">
                <NodeBadge variant={variant}>{status === "success" ? "✓" : i + 1}</NodeBadge>
                <span
                  className={`text-[0.74rem] ${
                    variant === "upcoming" ? "text-ink-text-dim" : "text-ink-text"
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
